<template>
  <ContentBase>
    <!-- 外层大card -->
    <div class="card">
      <div class="card-header">信息对比</div>
      <div class="card-body" style="padding-bottom: 0;">
        <div class="row">
          <!-- 左侧自我雷达图的card -->
          <div class="col-lg-6 mb-4 d-flex">
            <div class="card w-100 chart-container">
              <VisPerson :student_id="store.state.user.id"></VisPerson>
            </div>
          </div>
            <!-- 右侧好友雷达图区域 -->
          <div class="col-lg-6 mb-4">
          </div>
        </div>
      </div>
    </div>
  </ContentBase>
</template>
  
<script>
  import VisPerson from '@/components/VisPerson';
  import ContentBase from '../components/ContentBase';
  import { useStore } from 'vuex';

  export default {
    components: {
      ContentBase,
      VisPerson
    },
    setup() {
      const store = useStore;
  
      return {
      };
    },
  };
</script>
  
<style scoped>
</style>