<template>
  <content-base>
    <div class="chat-container">
      <div class="messages">
        <div v-for="(msg, index) in messages" :key="index" class="message-item">
          <div class="message-header">
            <span class="sender">{{ msg.sender }}</span>
            <span class="timestamp">{{ msg.created_at }}</span>
          </div>
          <div class="message-body">{{ msg.text }}</div>
        </div>
    </div>
      <div class="send-message">
        <input v-model="message" type="text" placeholder="输入消息" @keyup.enter="send">
        <button @click="send">发送</button>
      </div>
    </div>
  </content-base>
</template>

<script>
import ContentBase from '../components/ContentBase';
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'ChatRoom',
  components: {
    ContentBase,
  },
  setup() {

    const store = useStore();
    const ws = ref(null);
    const message = ref('');
    const messages = ref([]);

    const studentId = computed(() => store.state.user.id);
    const communityId = '0'; // 需要根据实际情况替换或者从 props/vue-router 中获取

    onMounted(() => {
      ws.value = new WebSocket(`ws://120.26.228.25:8000/ws/community/${communityId}_${studentId.value}/`);

      ws.value.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.messages) {
          // 接收到初始的消息列表，直接覆盖 messages 数组内容
          messages.value = data.messages.map(msg => ({
            sender: msg.sender_name,
            text: msg.text,
            created_at: msg.created_at
          }));
        } else {
          // 单条新消息，添加到 messages 数组
          const receivedMsg = {
            sender: data.sender, // 根据实际情况修改或从 data 中获取 sender 信息
            text: data.message,
            created_at: data.created_at
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
      }
    });

  const send = () => {
    if (ws.value.readyState === WebSocket.OPEN && message.value.trim()) {
      ws.value.send(JSON.stringify({ message: message.value }));
      message.value = ''; // 清空输入框
    } else {
      console.error("WebSocket 还未准备好发送数据");
    }
  };

    // 使 send 方法在模板中可用
    return { message, messages, send };
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
}

.messages {
  flex-grow: 1;
  overflow-y: auto;
}

.message {
  margin: 0.5em 0;
}

.send-message {
  display: flex;
  margin-top: 1em;
}

.send-message input {
  flex-grow: 1;
  padding: 0.5em;
}

.send-message button {
  padding: 0.5em 1em;
}
</style>