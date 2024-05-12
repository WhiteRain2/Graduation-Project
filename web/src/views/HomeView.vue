<template>
  <ContentBase>
    <!-- 用户输入卡片 -->
    <div class="row mb-3">
    <div class="col">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Hi {{ studentName }}, 今天想学哪门课?</h5>
          <br>
          <form @submit.prevent="handleCourseSearch">
            <div class="input-group mb-3 dropdown" style="position: relative;">
              <input type="text"
                    class="form-control"
                    placeholder="输入课程ID或名称"
                    v-model="query"
                    @input="searchCourse"
                    @focus="isDropdownActive = true"
                    @blur="handleBlur"
                    :disabled="is_recommending">
              <button class="btn btn-outline-secondary" type="submit" :disabled="is_recommending">搜索</button>

              <!-- 下拉列表 -->
              <ul class="dropdown-menu w-100 cursor-pointer"
                  v-if="searchResults.length && query.trim().length && isDropdownActive"
                  style="display: block; position: absolute; top: 100%; left: 0px; z-index: 1000;">
                <li v-if="searchResults.length === 0" class="dropdown-item">搜索中...</li>
                <li v-else-if="searchResults[0].noResults" class="dropdown-item">无相关课程信息</li>
                <li v-else class="dropdown-item"
                    v-for="result in searchResults" :key="result.id" @mousedown.prevent="selectCourse(result)">
                  ({{ result.course_id }}){{ result.name }}
                </li>
              </ul>
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
                <tr v-for="course in completedCourses" :key="course.id" @click="goToCourseDetail(course.id)" class="cursor-pointer">
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
            你最近正在学的课程
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
                <tr v-for="course in wishCourses" :key="course.id" @click="goToCourseDetail(course.id)" class="cursor-pointer">
                  <td>{{ course.id }}</td>
                  <td>{{ course.name }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    <!-- 搜索课程结构卡片 -->
    <div class="row">
      <div class="col">
        <div class="card mt-3">
          <div class="card-header">
            相关课程
          </div>
          <!-- 使用v-if在is_recommending为true时显示加载指示器 -->
          <div class="text-center" v-if="is_recommending">
            <br>
            <span class="spinner-border text-primary" role="status" aria-hidden="true"></span>
            <br>
            <span>稍等一会...</span>
          </div>
          <div class="card-body" v-else>
            <table class="table table-hover" v-if="isSearch">
              <thead>
                <tr>
                  <th scope="col" class="text-center">课程ID</th>
                  <th scope="col" class="text-center">课程名称</th>
                  <th scope="col" class="text-center">教师团队</th>
                  <th scope="col" class="text-center">开课时间</th>
                  <th scope="col" class="text-center">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="result in searchResults" :key="result.id">
                  <td class="text-center">{{ result.course_id }}</td>
                  <td class="text-center">{{ result.name }}</td>
                  <td class="text-center">{{ result.teachers }}</td>
                  <td class="text-center">{{ formattedCreateTime(result.created_time) }}</td>
                  <td class="text-center">
                    <button type="button" class="btn btn-outline-secondary" @click="goToCourseDetail(result.course_id)">
                      查看详情
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
import router from '@/router/index';

export default {
  name: 'HomeView',
  components: {
    ContentBase,
  },
  setup() {
    const store = useStore();
    const query = ref('');
    const searchResults = ref([]);
    const isSearch = ref(false);
    const studentName = computed(() => store.state.user.name);
    const completedCourses = computed(() => store.state.user.completedCourses);
    const wishCourses = computed(() => store.state.user.wishCourses);
    const recommendedCommunities = computed(() => store.state.user.recommendedCommunities);
    const is_recommending = computed(() => store.state.user.is_recommending);
    const isDropdownActive = ref(false); 

    const goToCourseDetail = (courseId) => {
      router.push({ name: 'CourseDetail', params: { course_id: courseId } });
    }

    const handleCourseSearch = async () => {
      if (query.value.trim() === '') {
        alert('请输入课程ID或名称!');
        return;
      }
      isSearch.value = true;
      store.commit('user/updateIsrecommending', true);
      try {
        const response = await fetch(`http://localhost:8000/search-courses/?keyword=${encodeURIComponent(query.value)}&ct=10`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        const data = await response.json();
        console.log(data);
        if (data.error){
          searchResults.value = [{ message: '无相关课程信息', noResults: true }]; // 显示无结果消息
        } else if (data.courses && data.courses.length > 0) {
          searchResults.value = data.courses; // 更新搜索结果
        }
      } catch (error) {
        console.error('搜索课程出错: ', error);
        // 这里我们不使用alert
      } finally {
        store.commit('user/updateIsrecommending', false); // 无论成功还是失败，结束加载状态
      }
    };

    const handleBlur = () => {
      // 小技巧: 使用setTimeout来延时关闭下拉菜单，允许点击事件先发生
      setTimeout(() => {
        isDropdownActive.value = false;
      }, 500);
    };

    const searchCourse = async () => {
      isSearch.value = false;
      if (!query.value.trim()) {
        searchResults.value = [];
        return;
      }
      try {
        const response = await fetch(`http://localhost:8000/search-courses/?keyword=${encodeURIComponent(query.value)}&ct=10`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        const data = await response.json();
        console.log(data);
        if (data.error){
          searchResults.value = [{ message: '无相关课程信息', noResults: true }]; // 显示无结果消息
        } else if (data.courses && data.courses.length > 0) {
          searchResults.value = data.courses; // 更新搜索结果
        }
      } catch (error) {
        console.error('搜索课程出错: ', error);
        // 这里我们不使用alert
      }
    };

    const selectCourse = (course) => {
     router.push({ name: 'CourseDetail', params: { course_id: course.course_id } });
    };

    const formattedCreateTime = (time) => {
      if (time) {
        const date = new Date(time);
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
      } else {
        return '';
      }
    };

    // 返回组件所需的响应式属性和方法
    return {
      studentName,
      completedCourses,
      wishCourses,
      query,
      recommendedCommunities, // 直接从Vuex state获取
      handleCourseSearch,
      is_recommending,
      goToCourseDetail,
      isDropdownActive,
      handleBlur,
      searchCourse,
      searchResults,
      selectCourse,
      isSearch,
      formattedCreateTime,
    }
  }
};
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
</style>