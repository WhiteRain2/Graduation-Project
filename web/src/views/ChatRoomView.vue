<template>
  <content-base>
    <chat-messages :studentId="studentId" :communityId="communityId"></chat-messages>
  </content-base>
</template>

<script>
import ContentBase from '../components/ContentBase';
import ChatMessages from '@/components/ChatMessages.vue'
import { computed } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'ChatRoom',
  components: {
    ContentBase,
    ChatMessages
  },
  setup() {
    const store = useStore();
    const studentId = computed(() => store.state.user.id);
    const communityId = '0';

    return { studentId, communityId };
  }
};
</script>

<style scoped>

</style>