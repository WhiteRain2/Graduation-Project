<template>
  <!-- 外层大card -->
  <div class="card">
    <div class="card-header">信息对比</div>
    <div class="card-body" style="padding-bottom: 0;">
      <div class="row">
        <!-- 左侧自我雷达图的card -->
        <div class="col-lg-6 mb-4 d-flex">
          <div class="card w-100 chart-container">
            <VisPerson :student_id="userId"></VisPerson>
          </div>
        </div>
        <!-- 右侧好友雷达图区域 -->
        <div class="col-lg-6 mb-4 d-flex">
          <div class="card w-100 chart-container">
            <VisPerson :student_id="friendId"></VisPerson>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import VisPerson from '@/components/VisPerson';
  import { useStore } from 'vuex';
  import { computed } from 'vue';

  export default {
    components: {
      VisPerson
    },
    props: {
      friendId: {
        type: Number,
        required: true
      }
    },
    setup() {
      const store = useStore();

      // 从vuex store获取用户ID，这次我们使用 computed 来创建一个响应式值
      const userId = computed(() => store.state.user.id);

      // 注意：这里我们不需要再把props的值包含在setup的返回对象里
      // 只需要从setup参数提取并使用它们就可以了
      return {
        userId, // 只返回 userId，props 中的 friendId 会自动可用于模板中
      };
    },
  };
</script>

<style scoped>
</style>