# demo/consumers.py
import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.community_group_name = None
        self.student_id = None
        self.community_id = None

    async def connect(self):
        self.community_id = self.scope['url_route']['kwargs']['community_id']
        self.student_id = self.scope['url_route']['kwargs']['student_id']
        self.community_group_name = 'chat_%s' % self.community_id

        # 加入聊天室组
        await self.channel_layer.group_add(
            self.community_group_name,
            self.channel_name
        )

        await self.accept()
        # 查询最新的50条消息并发送
        latest_messages = await self.get_latest_messages()
        await self.send(text_data=json.dumps({
            'messages': latest_messages
        }))


    async def disconnect(self, close_code):
        # 离开聊天室组
        await self.channel_layer.group_discard(
            self.community_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message']
        now = timezone.now()

        msg = await self.store_or_handle_message(message_text, now)
        sender_name = msg.sender.name

        # 发送消息到聊天室组
        await self.channel_layer.group_send(
            self.community_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'text': message_text,
                    'sender_name': sender_name
                },
                'created_at': now.isoformat(),
            }
        )

    async def chat_message(self, event):
        message = event['message']['text']
        sender = event['message']['sender_name']
        created_at = event['created_at']

        # 发送消息到 WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'created_at': created_at,
        }))

    # 数据库操作均移至 database_sync_to_async 方法中以避免阻塞
    @database_sync_to_async
    def store_or_handle_message(self, text, created_at):
        from demo.repositories.message_repository import MessageRepository
        return MessageRepository.store_or_handle_message(self.community_id, self.student_id, text, created_at)

    # 在 ChatConsumer 内
    @database_sync_to_async
    def get_latest_messages(self, limit=50):
        from demo.models.message import Message
        if self.community_id == '0':
            # 公共聊天信息
            messages = Message.objects.filter(community__isnull=True).order_by('created_at')[:limit]
        else:
            # 根据 community_id 查询特定共同体的消息
            messages = Message.objects.filter(community__id=self.community_id).order_by('-created_at')[:limit]

        # 我们需要序列化消息，因为异步方法不能直接返回复杂的数据类型
        return [{
            'sender_id': message.sender.student_id,
            'sender_name': message.sender.name,
            'text': message.text,
            'created_at': message.created_at.isoformat(),
        } for message in messages]