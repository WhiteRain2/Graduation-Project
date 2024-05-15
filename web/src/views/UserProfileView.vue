<template>
  <ContentBase>
    <div v-if="studentInfo.studentName !== ''">
      <div class="row">
        <div class="col-12 mb-3">
          <div class="card">
            <div class="card-header">
              用户基本资料
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-2">ID: {{ studentInfo.studentId }}</div>
                <div class="col-2">姓名: {{ studentInfo.studentName }}</div>
                <div class="col-2">性别: {{ studentInfo.gender }}</div>
                <div class="col-3">学习风格: {{ studentInfo.learning_style }}</div>
                <div class="col-3">
                  活跃度:
                  <span v-if="isMe">{{ typeof studentInfo.activity_level === 'number' ? studentInfo.activity_level.toFixed(2) : '' }}</span>
                  <span v-else>
                    <span v-if="studentInfo.activity_level>=0.5">活跃</span>
                    <span v-else>一般</span>
                  </span>
                </div>
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
                    <th v-if="isMe" scope="col">成绩</th>
                    <th v-else>评价</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="course in studentInfo.completedCourses" :key="course.id" @click="goToCourseDetail(course.id)" class="cursor-pointer">
                    <td>{{ course.id }}</td>
                    <td>{{ course.name }}</td>
                    <td v-if="isMe">{{ course.score }}</td>
                    <td v-else>
                      <span v-if="course.score > 79">优秀</span>
                      <span v-else-if="course.score < 60">一般</span>
                      <span v-else>良好</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="col-sm-6">
          <div class="card">
            <div class="card-header">
              正在学的课程
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
                  <tr v-for="course in studentInfo.wishCourses" :key="course.id" @click="goToCourseDetail(course.id)" class="cursor-pointer">
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
                    <th scope="col" class="text-center">共同体ID</th>
                    <th scope="col" class="text-center">共同体名称</th>
                    <th scope="col" class="text-center">成员人数</th>
                    <th scope="col" class="text-center">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="community in studentInfo.communities" :key="community.id">
                    <td class="text-center">{{ community.id }}</td>
                    <td class="text-center">{{ community.name }}</td>
                    <td class="text-center">{{ community.count }}</td>
                    <td class="text-center">
                      <button type="button" class="btn btn-outline-secondary me-2"
                        @click="goToCommunityDetail(community.id)">查看
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="card-footer text-end text-muted small">
              已经加入了{{ studentInfo.communities_count }}个共同体。
            </div>
          </div>
        </div>
        <div class="row" v-if="!isMe">
          <button type="button" class="btn btn-outline-success col-lg-5 mb-2 mx-auto"
          @click="$router.go(-1)">返回前页</button>
        </div>
      </div>
    </div>
    <div v-else class="text-center my-5">
      Loading person information...
    </div>
  </ContentBase>
</template>

<script>
import { onMounted, ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import axios from 'axios';
import ContentBase from '@/components/ContentBase.vue'; // 假设ContentBase组件存在于指定路径

export default {
  name: 'UserProfile',
  components: {
    ContentBase,
  },
  setup() {
    const store = useStore();
    const router = useRouter();
    const userId = router.currentRoute.value.params.userId;    
    const isMe = ref(store.state.user.id === userId);
    console.log(isMe.value);
    // 使用ref创建响应式引用
    const studentInfo = ref({
      studentId: '',
      studentName: '',
      gender: '',
      learning_style: '',
      activity_level: '',
      completedCourses: [],
      wishCourses: [],
      communities: [],
      communities_count: 0,
    });

    const fetchData = async () => {
      // 以下为请求携带的授权令牌
      const accessToken = store.state.user.access;

      try {
        const response = await axios.get('http://localhost:8000/getinfo/', {
          params: { type: 'student', id: userId },
          headers: { Authorization: `Bearer ${accessToken}` },
        });

        const data = response.data;
        studentInfo.value = {
          studentId: data.id, // 映射后端返回的'id'到前端的'studentId'
          studentName: data.name, // 映射'name'
          gender: data.gender, // 映射'gender'
          learning_style: data.learning_style, // 映射'learning_style'
          activity_level: data.activity_level, // 映射'activity_level'
          self_description: data.self_description, // 映射'self_description'
          completedCourses: data.completed_courses, // 映射'completed_courses'
          wishCourses: data.wish_courses, // 映射'wish_courses'
          communities_count: data.communities_count, // 映射'communities_count'
          communities: data.communities, // 映射'communities'
        };
      } catch (error) {
        console.error('Failed to fetch user profile data:', error);
      }
    };

    onMounted(fetchData);

    // 在模板中需要函数时返回它们
    const goToCourseDetail = (courseId) => {
      router.push({ name: 'CourseDetail', params: { course_id: courseId } });
    };

    const goToCommunityDetail = (communityId) => {
      router.push({ name: 'vis', params: { community_id: communityId } });
    }


    // 返回要在模板中使用的响应式数据和函数
    return {
      studentInfo,
      goToCourseDetail,
      goToCommunityDetail,
      isMe
    };
  },
};
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
</style>