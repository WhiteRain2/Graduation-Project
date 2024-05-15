<template>
  <ContentBase>
    <!-- 外层大card -->
    <div class="card">
      <div class="card-header">共同体属性概览</div>
      <div class="card-body" style="padding-bottom: 0;">
        <div class="row">
          <!-- 左侧雷达图的card -->
          <div class="col-lg-6 mb-4 d-flex">
            <div class="card w-100 chart-container">
              <radar-chart 
                v-if="community_chart_config" 
                :config="community_chart_config" 
                :height="500"
              />
            </div>
          </div>
          <!-- 右侧饼图区域 -->
          <div class="col-lg-6 mb-4">
            <div class="row">
              <!-- 性别信息饼图的card -->
              <div class="col-md-6 mb-4">
                <div class="card w-100 chart-container">
                  <pie-chart 
                    v-if="gender_chart_config" 
                    :config="gender_chart_config" 
                    :height="250"
                  />
                </div>
              </div>
              <!-- 学习风格信息饼图的card -->
              <div class="col-md-6 mb-4">
                <div class="card w-100 chart-container">
                  <pie-chart 
                    v-if="activity_level_chart_config" 
                    :config="activity_level_chart_config" 
                    :height="250"
                  />
                </div>
              </div>
              <!-- 活跃度信息饼图的card -->
              <div class="col-12">
                <div class="card w-100 chart-container">
                  <pie-chart 
                    v-if="learning_style_chart_config" 
                    :config="learning_style_chart_config" 
                    :height="250"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header">成员情况概览</div>
        <div class="card-body">
          <div v-for="student in students" :key="student.id" class="mb-2">
            <VisPerson :student_id="student.id"></VisPerson>
          </div>
        </div>
      </div>
    </div>
    <br>
    <div class="row">
      <button v-if="isNew" type="button" class="btn btn-outline-success col-lg-5 mb-2 mx-auto"
       @click="handleJoinOrLeaveCommunity('join')">加入共同体</button>
      <button v-else type="button" class="btn btn-outline-danger col-lg-5 mb-2 mx-auto"
       @click="handleJoinOrLeaveCommunity('leave')">退出共同体</button> <!-- 编写退出共同体的按钮逻辑 -->
      <button type="button" class="btn btn-outline-success col-lg-5 mb-2 mx-auto"
       @click="$router.go(-1)">返回前页</button>
    </div>
  </ContentBase>
</template>

<script>
import ContentBase from '../components/ContentBase';
import RadarChart from '@/components/RadarChart.vue';
import PieChart from '@/components/PieChart.vue';
import VisPerson from '@/components/VisPerson.vue';
import { onMounted, ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useRoute } from 'vue-router';
import axios from 'axios';
import router from '@/router/index';

export default {
  components: {
    ContentBase,
    RadarChart,
    PieChart,
    VisPerson
  },
  setup() {
    const store = useStore();
    const route = useRoute();
    const community_id = route.params.community_id;
    const gender_chart_config = ref();
    const learning_style_chart_config = ref();
    const activity_level_chart_config = ref();
    const students = ref([]);
    const communities = computed(() => store.state.user.communities);
    const community_chart_config = ref({
      title: '',
      indicators: [
        { name: '性别比例', max: 1 },
        { name: '学习风格', max: 1 },
        { name: '活跃度', max: 1 },
        { name: '成员数', max: 8 },
        { name: '课程储备', max: 10 },
      ],
      data: [
      ],
    });
    const isNew = computed(() => {
      if (!communities.value) return false;
      return !communities.value.some(community => Number(community.id) === Number(community_id));
    });
    onMounted(async () => {
      if (store.state.user.is_login && community_id) {
        try {
          const response = await axios.get("http://localhost:8000/getinfo/", {
            headers: {
              'Authorization': `Bearer ${store.state.user.access}`
            },
            params: {
              type: 'community',
              id: community_id,
            }
          });
          if (!response.data.error) {
            const data = response.data;
            community_chart_config.value.title = response.data.name;
            community_chart_config.value.data = [{
              value: [
                data.gender_ratio,
                data.learning_style,
                data.activity_level,
                data.members_count,
                data.completed_courses.length,
              ],
              name: String('Id:'+data.id),
            }];
            // Prepare the gender chart config
            gender_chart_config.value = {
              title: '性别比例',
              data: Object.keys(data.gender_details).map(key => ({
                name: key,
                value: data.gender_details[key],
              })),
            };
            // Prepare the learning style chart config
            learning_style_chart_config.value = {
              title: '学习风格',
              data: Object.keys(data.learning_style_details).map(key => ({
                name: key,
                value: data.learning_style_details[key],
              })),
            };
            
            // Prepare the activity level chart config
            activity_level_chart_config.value = {
              title: '活跃度',
              data: [
                { name: '活跃', value: data.active_members_count },
                { name: '不活跃', value: data.members_count - data.active_members_count },
              ],
            };

            students.value = data.members;
          }
        } catch (error) {
          console.error('Error fetching community data:', error);
        }
      } else {
        router.push({name: 'login'});
        console.error('Access token or community ID is missing');
      }
    });

        // ...其余方法和逻辑...
    const handleJoinOrLeaveCommunity = async (operation) => {
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

    return {
      community_chart_config,
      gender_chart_config,
      learning_style_chart_config,
      activity_level_chart_config,
      isNew,
      handleJoinOrLeaveCommunity,
      students
    };
  },
};
</script>

<style scoped>
.chart-container {
  padding: 5px;
}
</style>