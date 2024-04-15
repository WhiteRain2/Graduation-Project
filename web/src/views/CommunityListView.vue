<template>
  <ContentBase>
    <div class="col-12 mb-3">
        <div class="card">
          <div class="card-header">
            所属共同体
          </div>
          <div class="card-body">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th scope="col" class="text-center">小组ID</th>
                  <th scope="col" class="text-center">小组名称</th>
                  <th scope="col" class="text-center">描述</th>
                  <th scope="col" class="text-center">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="community in communities" :key="community.id">
                  <td class="text-center">{{ community.id }}</td>
                  <td class="text-center">{{ community.name }}</td>
                  <td class="text-center">{{ community.description }}</td>
                  <td class="text-center">
                    <button type="button" class="btn btn-outline-secondary me-2">查看</button>
                    <button type="button" 
                            class="btn btn-outline-secondary" 
                            @click="handleLeaveCommunity(community.id)"
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
  </ContentBase>
</template>

<script>
  import ContentBase from '../components/ContentBase'
  import { computed } from 'vue';
  import { useStore } from 'vuex';

  export default {
    name: 'CommunityList',
    components: {
      ContentBase,
    },
    setup() {
      const store = useStore();
      const communities = computed(() => store.state.user.communities);

      // 添加 handleLeaveCommunity 函数
      const handleLeaveCommunity = async (community_id) => {
        try {
          await store.dispatch('user/joinOrLeaveCommunity', {
            student_id: store.state.user.id,
            community_id: community_id,
            operation: 'leave'
          });
        } catch (error) {
          alert(error.message);
        }
      };

      return {
        communities,
        handleLeaveCommunity  // 这个函数会在模板中被使用
      };
    }
  }
</script>

<style scoped>
</style>