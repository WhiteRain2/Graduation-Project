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
            <ul>
              <li v-for="community in communities" :key="community.id">
                {{ community.name }} - {{ community.description }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </ContentBase>
</template>

<script>
import ContentBase from '../components/ContentBase';
import { computed } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'HomeView',
  components: {
    ContentBase,
  },
  setup() {
    const store = useStore();
    

    // 计算属性获取学生名称、已完成课程和愿望课程列表
    const studentName = computed(() => store.state.user.name);
    const completedCourses = computed(() => store.state.user.completedCourses);
    const wishCourses = computed(() => store.state.user.wishCourses);
    // 新增了一个计算属性以从 store 中获取社区数据
    const communities = computed(() => store.state.user.communities);
    
    // ...其余方法和逻辑...

    // 返回给组件使用的属性和方法
    return {
      studentName,
      completedCourses,
      wishCourses,
      communities,
      // ... 其余返回对象内容...
    }
  }
};
</script>

<style scoped>
  /* 你的样式代码 */
</style>
