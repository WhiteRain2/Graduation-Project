<template>
  <div class="chat-container flex-column p-4">
    <div class="messages flex-grow-1 overflow-auto mb-3">
      <div v-for="(msg, index) in messages" :key="index" class="d-flex mb-2" :class="{'justify-content-end': msg.isOwnMessage, 'justify-content-start': !msg.isOwnMessage}">
        <!-- 对他人发送的消息，将sender和timestamp放在message的左边 -->
        <div v-if="!msg.isOwnMessage" class="metadata me-2">
          <div class="sender-name">{{ msg.sender }}</div>
          <div class="timestamp">{{ formatTimestamp(msg.created_at) }}</div>
        </div>
        <!-- 消息本身 -->
        <div :class="['message-item', msg.isOwnMessage ? 'bg-info text-white' : 'bg-light']">
          <div class="message-body">{{ msg.text }}</div>
        </div>
        <!-- 对自己发送的消息，将sender和timestamp放在message的右边 -->
        <div v-if="msg.isOwnMessage" class="metadata ms-2">
          <div class="sender-name">{{ msg.sender }}</div>
          <div class="timestamp">{{ formatTimestamp(msg.created_at) }}</div>
        </div>
      </div>
    </div>
    <!-- 消息发送区域 -->
    <div class="send-message">
      <input type="text" v-model="message" class="form-control" placeholder="输入消息">
      <button class="btn btn-primary" @click="send">发送</button>
    </div>
  </div>
</template>
  
  <script>
  import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
  import { useStore } from 'vuex';

  export default {
    name: 'ChatMessages',
    props: {
      studentId: {
        type: [String, Number],
        required: true
      },
      communityId: {
        type: [String, Number],
        required: true
      }
    },
    setup(props) {
      const store = useStore();
      const ws = ref(null);
      const message = ref('');
      const messages = ref([]);
      const name = computed(() => store.state.user.name);
      const formatTimestamp = (timestamp) => {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }); // 或者按您的需求来调整格式
      };

      onMounted(() => {
        const wsHost = `ws://localhost:8000/ws/community/${props.communityId}_${props.studentId}/`;
        ws.value = new WebSocket(wsHost);
  
        ws.value.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.messages) {
            messages.value = data.messages.map(msg => ({
              sender: msg.sender_name,
              text: msg.text,
              created_at: msg.created_at,
              isOwnMessage: msg.sender_name == name.value
            }));
          } else {
            const receivedMsg = {
              sender: data.sender,
              text: data.message,
              created_at: data.created_at,
              isOwnMessage: data.sender == name.value
            };
            messages.value.push(receivedMsg);
          }
        };
  
        ws.value.onclose = () => {
          console.log('WebSocket is closed now.');
        };
  
        ws.value.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      });
  
      onBeforeUnmount(() => {
        if (ws.value) {
          ws.value.close();
          ws.value = null;
        }
      });
  
      const send = () => {
        if (ws.value && ws.value.readyState === WebSocket.OPEN && message.value.trim()) {
          ws.value.send(JSON.stringify({ message: message.value }));
          message.value = ''; // 清空输入框
        } else {
          console.error("WebSocket 还未准备好发送数据");
        }
      };
  
      return { message, messages, send,  formatTimestamp};
    }
  };
  </script>
  
  <style scoped>
  .chat-container {
    border: 1px solid #ced4da;
    border-radius: 0.25rem;
    margin-bottom: 1rem;
  }
  
  .messages {
    display: flex;
    flex-direction: column;
    gap: 10px;
    overflow-y: auto;
    margin-bottom: 1rem;
  }
  
  /* 对消息本身的布局样式 */
  .d-flex {
    display: flex;
    align-items: flex-end; /* 使得消息和元数据底部对齐 */
  }
  
  /* 消息是自己发送的 */
  .justify-content-end {
    justify-content: flex-end;
  }
  
  /* 消息是他人发送的 */
  .justify-content-start {
    justify-content: flex-start;
  }
  
  /* 对话气泡的基本样式 */
  .message-item {
    padding: 10px 15px;
    border-radius: 20px;
    max-width: 70%;
    word-wrap: break-word; /* 防止长单词/URL破坏布局 */
  }
  
  /* 自己的消息的样式 */
  .message-own.bg-info {
    background-color: #17a2b8;
  }
  
  /* 自己的消息气泡的布局调整，使得元数据显示在右侧 */
  .message-own {
    order: 1;
    margin-left: 10px;
  }
  
  /* 他人的消息 */
  .bg-light {
    background-color: #f8f9fa;
  }
  
  /* 消息旁边的元数据内容 */
  .metadata {
    padding: 4px 8px;
    background-color: #f0f0f0; /* 背景色与消息略有区别 */
    border-radius: 10px;
    font-size: 0.75rem;
    text-align: center; /* 使名称和时间居中 */
  }
  
  .sender-name {
    font-weight: bold;
  }
  
  .timestamp {
    color: #6c757d;
  }
  
  /* 调整输入区域的样式 */
  .send-message {
    display: flex;
    gap: 10px;
  }
  
  .form-control {
    flex-grow: 1;
  }
  
  .btn-primary {
    white-space: nowrap; /* 避免按钮文本折行 */
  }
  
  @media (min-width: 768px) {
    .chat-container {
      max-width: 50%;
      margin: auto;
    }
  }
  </style>