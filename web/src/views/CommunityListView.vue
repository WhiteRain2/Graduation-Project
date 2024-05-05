<template>
  <ContentBase>
    <!-- 用户输入卡片 -->
    <div class="row mb-3">
      <div class="col">
        <div class="card">
          <div class="card-header">
            你加入的社区
          </div>
          <div class="card-body">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th scope="col" class="text-center">小组ID</th>
                  <th scope="col" class="text-center">小组名称</th>
                  <th scope="col" class="text-center">描述</th>
                  <th scope="col" class="text-center">成员人数</th>
                  <th scope="col" class="text-center">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="community in communities" :key="community.id">
                  <td class="text-center">{{ community.id }}</td>
                  <td class="text-center">{{ community.name }}</td>
                  <td class="text-center">{{ community.description }}</td>
                  <td class="text-center">{{ community.count }}</td>
                  <td class="text-center">
                    <button type="button" class="btn btn-outline-secondary me-2" @click="handleViewCommunity(community.id)">聊天</button>
                    <button type="button" class="btn btn-outline-danger"
                      @click="handleJoinOrLeaveCommunity(community.id, 'leave')"
                    >
                      退出
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  <ModalContext :isVisible="isChatModalVisible" @update:isVisible="isChatModalVisible = $event">
    <ChatMessages 
      v-if="isChatModalVisible"
      :studentId="studentId" 
      :communityId="selectedCommunityId" 
      @close="isChatModalVisible = false">
    </ChatMessages>
  </ModalContext>
  </ContentBase>
</template>

<script>
import ContentBase from '../components/ContentBase';
import ChatMessages from '@/components/ChatMessages.vue'
import ModalContext from '@/components/ModalContext.vue'
import { computed, ref } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'HomeView',
  components: {
    ContentBase,
    ChatMessages,
    ModalContext
  },
  setup() {
    const store = useStore();
    
    // 计算属性获取学生名称、已完成课程和愿望课程列表
    const studentName = computed(() => store.state.user.name);
    const studentId = computed(() => store.state.user.id);
    const completedCourses = computed(() => store.state.user.completedCourses);
    const wishCourses = computed(() => store.state.user.wishCourses);
    // 新增了一个计算属性以从 store 中获取社区数据
    const communities = computed(() => store.state.user.communities);

    // 控制聊天框显示的reactive property
    const isChatModalVisible = ref(false);
    const selectedCommunityId = ref(null); // 新增一个变量用于存储当前选中的社区ID

    function handleViewCommunity(communityId) {
      selectedCommunityId.value = communityId;
      isChatModalVisible.value = true; // 显示聊天框
    }

    function handleCloseChatModal() {
      isChatModalVisible.value = false; // 隐藏聊天框
    }

    // ...其余方法和逻辑...
    const handleJoinOrLeaveCommunity = async (community_id, operation) => {
      try {
        await store.dispatch('user/joinOrLeaveCommunity', {
          student_id: store.state.user.id,
          community_id: community_id,
          operation
        });
      } catch (error) {
        alert(error.message);
      }
    };
    // 返回给组件使用的属性和方法
    return {
      studentId,
      studentName,
      completedCourses,
      wishCourses,
      communities,
      isChatModalVisible,
      selectedCommunityId,
      handleJoinOrLeaveCommunity,
      handleViewCommunity,
      handleCloseChatModal
      // ... 其余返回对象内容...
    }
  }
};
</script>

<style scoped>
</style>
