<template>
  <div class="chat-container flex-column p-4">
    <div class="messages flex-grow-1  mb-3" ref="messageContainer">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message-row', { 'own-message': msg.isOwnMessage, 'other-message': !msg.isOwnMessage }]"
      >
        <!-- 对他人发送的消息，将sender和timestamp放在message的左边 -->
        <div v-if="!msg.isOwnMessage" class="metadata me-2">
          <div class="sender-name">{{ msg.sender }}</div>
          <div class="timestamp">{{ formatDateTime(msg.created_at) }}</div>
        </div>
        <!-- 消息本身 -->
        <div :class="['message-item', msg.isOwnMessage ? 'own' : 'other']">
          <div class="message-body">{{ msg.text }}</div>
        </div>
        <!-- 对自己发送的消息，将sender和timestamp放在message的右边 -->
        <div v-if="msg.isOwnMessage" class="metadata ms-2">
          <div class="sender-name">{{ msg.sender }}</div>
          <div class="timestamp">{{ formatDateTime(msg.created_at) }}</div>
        </div>
      </div>
    </div>
    <!-- 消息发送区域 -->
    <div class="send-message-area mt-auto">
      <input type="text" v-model="message" class="form-control" placeholder="输入消息" @keyup.enter="send">
      <button class="btn btn-primary" @click="send">发送</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue';
import { useStore } from 'vuex';


export default {
  name: 'ChatMessages',
  props: {
    studentId: {
      type: [String, Number],
      required: true,
    },
    communityId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const store = useStore();
    const ws = ref(null);
    const message = ref('');
    const messages = ref([]);
    const messageContainer = ref(null);
    const name = computed(() => store.state.user.name);
    const formatDateTime = (timestamp) => {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const date = new Date(timestamp);
      const msgDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
      // 检查消息日期是否是今天
      // 检查消息日期是否是今天
      if (msgDate.getTime() === today.getTime()) {
       // 如果是今天，则只显示时间，且确保小时和分钟为两位数
       return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
      } else {
       // 如果不是今天，则显示完整的年月日和时间，同样确保小时和分钟为两位数
       return `${date.getFullYear()}/${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  }
};

    const scrollToBottom = () => {
      nextTick(() => {
        if (messageContainer.value) {
          messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
        }
      });
    };

    onMounted(() => {
      const wsHost = `ws://localhost:8000/ws/community/${props.communityId}_${props.studentId}/`;
      ws.value = new WebSocket(wsHost);

      ws.value.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.messages) {
          messages.value = data.messages.map((msg) => ({
            sender: msg.sender_name,
            text: msg.text,
            created_at: msg.created_at,
            isOwnMessage: msg.sender_name === name.value,
          }));
        } else {
          messages.value.push({
            sender: data.sender,
            text: data.message,
            created_at: data.created_at,
            isOwnMessage: data.sender === name.value,
          });
        }
        scrollToBottom();
      };

      ws.value.onopen = () => {
        console.log('WebSocket is open now.');
      };

      ws.value.onclose = (event) => {
        console.log('WebSocket is closed now.', event);
      };

      ws.value.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    });

    onBeforeUnmount(() => {
      if (ws.value) {
        ws.value.close();
      }
    });

    const send = () => {
      if (ws.value && ws.value.readyState === WebSocket.OPEN && message.value.trim()) {
        ws.value.send(JSON.stringify({ message: message.value.trim() }));
        message.value = '';
      }
    };

    watch(messages, scrollToBottom, { deep: true });

    return {
      message,
      messages,
      send,
      formatDateTime,
      messageContainer,
    };
  },
};
</script>

<style scoped lang="scss">
.chat-container {
  display: flex;
  flex-direction: column; // 注意这里已经做了调整
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  margin-bottom: 1rem;
  height: 100%;
}

.messages {
  overflow-y: auto;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding-right: 15px; // 为滚动条预留空间
}


.message-row {
  display: flex;
  align-items: flex-end;
  margin-bottom: 15px; // 增加消息间隔
}

.own-message {
  justify-content: flex-end;
}

.other-message {
  justify-content: flex-start;
}

.message-item {
  max-width: 70%;
  word-wrap: break-word;
  padding: 10px 15px;
  border-radius: 20px;
  background-color: #f8f9fa;
  color: #000;
}

.own-message > .message-item {
  background-color: #17a2b8;
  color: #fff;
  align-self: flex-end;
  border-top-right-radius: 0;
}

.other-message > .message-item {
  align-self: flex-start;
  border-top-left-radius: 0;
}

.metadata {
  padding: 4px 8px;
  background-color: #f0f0f0;
  border-radius: 10px;
  font-size: 0.75rem;
  text-align: center;
}

.sender-name {
  font-weight: bold;
}

.timestamp {
  color: #6c757d;
}

.send-message-area {
  display: flex;
  gap: 10px;
  padding-top: 10%;
  // margin-bottom: 14%;
}

.form-control {
  flex-grow: 1;
}

.btn-primary {
  white-space: nowrap;
}



@media (min-width: 768px) {
  .chat-container {
    max-width: 60%;
    margin: auto;
  }
}
</style>