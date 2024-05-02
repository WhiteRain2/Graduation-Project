<template>
  <ContentBase>
    <div class="row">
      <div class="col-12 mb-3">
        <div class="card">
          <div class="card-header">
            用户基本资料
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-6">ID: {{ studentId }}</div>
              <div class="col-6">姓名: {{ studentName }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 已完成课程和愿望课程卡片并排 -->
      <div class="col-sm-6 mb-3">
        <div class="card">
          <div class="card-header">
            已完成课程
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
            愿望课程
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
      
      <div class="col-12 mb-3">
        <div class="card">
          <div class="card-header">
            所属共同体
          </div>
          <div class="card-body">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th scope="col">共同体ID</th>
                  <th scope="col">共同体名称</th>
                  <th scope="col">描述</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="community in communities" :key="community.id">
                  <td>{{ community.id }}</td>
                  <td>{{ community.name }}</td>
                  <td>{{ community.description }}</td>
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
import ContentBase from '../components/ContentBase'
import { computed } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'UserProfile',
  components: {
    ContentBase,
  },
  setup() {
    const store = useStore();
    // 根据 Vuex store 中的数据引用计算属性
    const studentId = computed(() => store.state.user.id);
    const studentName = computed(() => store.state.user.name);
    const completedCourses = computed(() => store.state.user.completedCourses);
    const wishCourses = computed(() => store.state.user.wishCourses);
    const communities = computed(() => store.state.user.communities);

    return {
      studentId,
      studentName,
      completedCourses,
      wishCourses,
      communities,
    }
  }
}
</script>

<style scoped>
/* 这里可以增加自定义样式 */
</style>