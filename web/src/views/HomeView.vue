<template>
  <ContentBase>
    <!-- 用户输入卡片 -->
    <div class="row mb-3">
    <div class="col">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Hi {{ studentName }}, 今天想学哪门课?</h5>
          <br>
          <form @submit.prevent="fetchRecommendations">
            <div class="input-group mb-3">
              <input type="text" class="form-control" placeholder="输入课程ID或名称" v-model="query" :disabled="isLoading">
              <button class="btn btn-outline-secondary" type="submit" :disabled="isLoading">搜索</button>
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
          <!-- 使用v-if在isLoading为true时显示加载指示器 -->
          <div class="text-center" v-if="isLoading">
            <br>
            <span class="spinner-border text-primary" role="status" aria-hidden="true"></span>
            <br>
            <span>正在获取推荐...</span>
          </div>
          <div class="card-body" v-else>
            <table class="table table-hover">
              <thead>
                <tr>
                  <th scope="col">共同体ID</th>
                  <th scope="col">共同体名称</th>
                  <th scope="col">描述</th>
                  <th scope="col">匹配度</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="community in recommendedCommunities" :key="community.id">
                  <td>{{ community.id }}</td>
                  <td>{{ community.name }}</td>
                  <td>{{ community.description }}</td>
                  <td>{{ community.similarity }}</td>
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
import axios from 'axios';

export default {
  name: 'HomeView',
  components: {
    ContentBase,
  },
  setup() {
    const store = useStore();
    const query = ref('');
    const recommendedCommunities = ref([]);
    const isLoading = ref(false); // 添加isLoading状态

    const studentName = computed(() => store.state.user.name);
    const completedCourses = computed(() => store.state.user.completedCourses);
    const wishCourses = computed(() => store.state.user.wishCourses);

    const fetchRecommendations = async () => {
      if (query.value.trim() === '') {
        alert('请输入课程ID或名称!');
        return;
      }

      isLoading.value = true; // 设置加载状态
      try {
        const response = await axios.post('http://localhost:8000/getrecommend/', {
          student_id: store.state.user.id, // 获取学生 ID
          course_id: query.value.trim()
        });

        if (response.data.error) {
          alert(response.data.error);
        } else {
          recommendedCommunities.value = response.data;
          // 请求学生的愿望课程列表数据更新
          await store.dispatch('user/fetchUser', store.state.user.id);
        }
      } catch (error) {
        console.error('推荐共同体请求失败', error);
        alert('推荐共同体请求失败，请重试。');
      } finally {
        isLoading.value = false; // 无论成功还是失败，结束加载状态
      }
    }

    // 不要忘记返回的组件所需的响应式属性和方法
    return {
      studentName,
      completedCourses,
      wishCourses,
      query,
      recommendedCommunities,
      fetchRecommendations,
      isLoading // 返回isLoading状态供模板使用
    }
  }
};
</script>

<style scoped>
</style>