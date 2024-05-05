<template>
  <ContentBase>
    <!-- 用户输入卡片 -->
    <div class="row mb-3">
    <div class="col">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Hi {{ studentName }}, 今天想学哪门课?</h5>
          <br>
          <form @submit.prevent="handleFetchRecommendations">
            <div class="input-group mb-3">
              <input type="text" class="form-control" placeholder="输入课程ID或名称" v-model="query" :disabled="is_recommending">
              <button class="btn btn-outline-secondary" type="submit" :disabled="is_recommending">搜索</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
    <!-- 已完成课程和愿望课程列表并排 -->
    <div class="row">
      <div class="col-sm-6 mb-3">
        <div class="card">
          <div class="card-header">
            你已完成的课程
          </div>
          <div class="card-body">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th scope="col">课程ID</th>
                  <th scope="col">课程名称</th>
                  <th scope="col">成绩</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="course in completedCourses" :key="course.id">
                  <td>{{ course.id }}</td>
                  <td>{{ course.name }}</td>
                  <td>{{ course.score }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="col-sm-6">
        <div class="card">
          <div class="card-header">
            你最近感兴趣的课程
          </div>
          <div class="card-body">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th scope="col">课程ID</th>
                  <th scope="col">课程名称</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="course in wishCourses" :key="course">
                  <td>{{ course.id }}</td>
                  <td>{{ course.name }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    <!-- 推荐共同体结果卡片 -->
    <div class="row">
      <div class="col">
        <div class="card mt-3">
          <div class="card-header">
            推荐你和他们一起学
          </div>
          <!-- 使用v-if在is_recommending为true时显示加载指示器 -->
          <div class="text-center" v-if="is_recommending">
            <br>
            <span class="spinner-border text-primary" role="status" aria-hidden="true"></span>
            <br>
            <span>稍等一会...</span>
          </div>
          <div class="card-body" v-else>
            <table class="table table-hover">
              <thead>
                <tr>
                  <th scope="col" class="text-center">小组ID</th>
                  <th scope="col" class="text-center">小组名称</th>
                  <th scope="col" class="text-center">描述</th>
                  <th scope="col" class="text-center">匹配度</th>
                  <th scope="col" class="text-center">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="community in recommendedCommunities" :key="community.id">
                  <td class="text-center">{{ community.id }}</td>
                  <td class="text-center">{{ community.name }}</td>
                  <td class="text-center">{{ community.description }}</td>
                  <td class="text-center">
                    {{ typeof community.similarity === 'number' ? community.similarity.toFixed(2) : '' }} -- {{ typeof community.com_sim === 'number' ? community.com_sim.toFixed(2) : '' }} + {{ typeof community.std_sim === 'number' ? community.std_sim.toFixed(2) : '' }}
                  </td>
                  <td class="text-center">
                    <button type="button" class="btn btn-outline-secondary me-2">查看</button>
                    <button type="button" class="btn btn-outline-secondary"
                      @click="handleJoinOrLeaveCommunity(community.id, community.joined ? 'leave' : 'join')"
                      :disabled="community.joined"
                    >
                      {{ community.joined ? '已加入' : '加入' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </ContentBase>
</template>


<script>
import ContentBase from '../components/ContentBase';
import { computed, ref } from 'vue';
import { useStore } from 'vuex';
// 不再需要单独的 axios 导入，因为现在我们从Vuex调用fetchRecommendations action

export default {
  name: 'HomeView',
  components: {
    ContentBase,
  },
  setup() {
    const store = useStore();
    const query = ref('');

    const studentName = computed(() => store.state.user.name);
    const completedCourses = computed(() => store.state.user.completedCourses);
    const wishCourses = computed(() => store.state.user.wishCourses);
    const recommendedCommunities = computed(() => store.state.user.recommendedCommunities);
    const is_recommending = computed(() => store.state.user.is_recommending);


    const handleFetchRecommendations = async () => {
      if (query.value.trim() === '') {
        alert('请输入课程ID或名称!');
        return;
      }
      console.log(store.state.user)
      store.commit('user/updateIsrecommending', true);
      try {
        // 直接调用store的dispatch函数来触发一个action
        await store.dispatch('user/fetchRecommendations', {
          student_id: store.state.user.id,
          course_id: query.value.trim()
        });

        // 再次调用dispatch来更新学生愿望列表
        await store.dispatch('user/fetchUser', store.state.user.id);
      } catch (error) {
        alert(error.message);
      } finally {
        store.commit('user/updateIsrecommending', false); // 无论成功还是失败，结束加载状态
      }
    };

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

    // 返回组件所需的响应式属性和方法
    return {
      studentName,
      completedCourses,
      wishCourses,
      query,
      recommendedCommunities, // 直接从Vuex state获取
      handleFetchRecommendations,
      is_recommending,
      handleJoinOrLeaveCommunity,
    }
  }
};
</script>

<style scoped>
</style>