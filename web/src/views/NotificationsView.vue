<template>
  <ContentBase>
    <div class="container py-5">
      <div class="card">
        <div class="card-header">
          <h1 class="text-center">消息中心</h1>
        </div>
        <div class="card-body">
          <div class="row">
            <!-- 假设用户已登录，因此只使用了if的一个分支来展示数据 -->
            <div class="col-md-6">
              <!-- 当前用户的社区申请显示区 -->
              <div class="card">
                <div class="card-body">
                  <h2 class="h5 card-title">你的加入请求</h2>
                  <!-- 徽标右对齐：静态测试数据1 -->
                  <div class="card mb-2">
                    <div class="d-flex justify-content-between card-body">
                      <span class="card-text">天天向上</span>
                      <span class="badge bg-primary">已接受</span>
                    </div>
                  </div>
                  <!-- 徽标右对齐：静态测试数据2 -->
                  <div class="card mb-3">
                    <div class="d-flex justify-content-between card-body">
                      <span class="card-text">我爱学习</span>
                      <span class="badge bg-warning">待审核</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <!-- 针对用户所在共同体的申请显示区 -->
              <div class="card">
                <div class="card-body">
                  <h2 class="h5 card-title">其他用户加入你的共同体请求</h2>
                  <!-- 按钮组右对齐：静态测试数据3 -->
                  <div class="card mb-3">
                    <div class="card-body">
                      <h5 class="card-title">好好学习小组</h5>
                      <div class="d-flex justify-content-between align-items-center">
                        <p class="card-text">张三 - 想要加入</p>
                        <div>
                          <div v-if="b!=1">
                            <button class="btn btn-success btn-sm me-2" @click="show(1)">同意</button>
                            <button class="btn btn-danger btn-sm" @click="show(1)">拒绝</button>
                          </div>
                          <div v-else>
                            <button class="btn btn-secondary btn-sm me-2" :disabled="true">已处理</button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- 按钮组右对齐：静态测试数据4 -->
                  <div class="card mb-3">
                    <div class="card-body">
                      <h5 class="card-title">爱好者协会</h5>
                      <div class="d-flex justify-content-between align-items-center">
                        <p class="card-text">独木舟 - 想要加入</p>
                        <div>
                          <button class="btn btn-success btn-sm me-2">同意</button>
                          <button class="btn btn-danger btn-sm">拒绝</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- 其他逻辑代码 -->
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
  
  export default {
    name: 'NotificationsView',
    components: {
      ContentBase,
    },
    setup() {
      const store = useStore();
      const studentJoinRequests = computed(() => store.state.user.studentJoinRequests); // 加入请求
      const communitiesApplications = computed(() => store.state.user.communitiesApplications); //所在共同体的消息
      const isLogin = computed(() => store.state.user.is_login);
      let b = ref(-1);

      const show = (n) => {
        b = n;
      };

      // 定义处理加入请求的方法，调用 Vuex action
      const handleJoinRequest = (joinRequestId, actionType) => {
        store.dispatch('user/handleJoinRequest', { joinRequestId, actionType })
          .then(() => {
            alert('操作成功');
            // 此处可以添加更多的响应逻辑，比如重新获取请求列表
          })
          .catch(error => {
            console.error('操作失败:', error);
            alert('操作失败');
          });
      };
  
      return {
        studentJoinRequests,
        communitiesApplications,
        isLogin,
        handleJoinRequest,
        show,
        b
      };
    },
  };
</script>
  
<style scoped>
/* 其他样式 */

/* 加入请求和按钮的对齐样式 */
.d-flex {
  display: flex; /* 启用Flexbox布局 */
}

.justify-content-between {
  justify-content: space-between; /* 两端对齐，项目之间的间隔都相等 */
}

.align-items-center {
  align-items: center; /* 交叉轴的中点对齐 */
}

.ms-2 {
  margin-left: .5rem; /* 为拒绝按钮添加一些左边距，确保它和同意按钮有间隔 */
}

</style>