<template>
  <div v-if="details" class="student-info">
    <div class="card">
      <div class="card-header">成员{{ details.name }}详细信息</div>
      <div class="card-body">
        <div class="row">
          <!-- 雷达图部分放在左侧 -->
          <div class="col-md-6">
            <RadarChart :config="radarConfig" :height="300" />
          </div>
          <!-- 详细信息放在右侧 -->
          <div class="col-md-6">
            <div class="text-right text"> <!-- 使用 `text-right` 类使文本靠右对齐 -->
              <p><strong>姓名:</strong> {{ details.name }}</p>
              <p><strong>性别:</strong> {{ details.gender }}</p>
              <p><strong>学习风格:</strong> {{ details.learning_style }}</p>
              <p><strong>已完成课程平均分数:</strong> {{ averageScoreComputed }}</p>
              <div style="margin-top: 30px">
                <button type="button" class="btn btn-primary me-2" @click="handleJoinOrLeaveCommunity(details.id, 'join')">组成小组</button> <!-- 使用 `me-2` 类添加右边距 -->
                <button type="button" class="btn btn-secondary" @click="goToStudentDetail(details.id)">详细信息</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else>
    <p>正在加载学生信息...</p>
  </div>
</template>

<script>
  import { reactive, computed, toRefs, onMounted } from 'vue'; // 导入 toRefs
  import axios from 'axios';
  import { useStore } from 'vuex';
  import RadarChart from '@/components/RadarChart.vue';
  import router from '@/router/index';

  export default {
    name: 'VisPerson',
    components: {
      RadarChart,
    },
    props: {
      student_id: {
        type: Number,
        required: true
      }
    },

    setup(props) {
      const store = useStore();
      const studentData = reactive({
        details: null,
        completedCourses: [],
        averageScore: 0
      });

      const goToStudentDetail = (studentId) => {
        router.push({name: 'userprofile', params: { userId: studentId }});
      }

      const handleJoinOrLeaveCommunity = async (community_id, operation) => {
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

      const radarConfig = computed(() => {
        return {
          title: '学生综合能力分析', // 可以根据需要修改标题
          indicators: [
            { name: '活跃度', max: 1 },
            { name: '课程储备', max: 10 },
            { name: '平均分数', max: 100 },
          ],
          data: [
            {
              value: [
                studentData.details.activity_level, 
                studentData.completedCourses.length + studentData.details.wish_courses.length,
                averageScoreComputed.value
              ],
              name: '能力指标',
            },
          ],
        };
      });
      // 计算已完成课程的平均分数
      const averageScoreComputed = computed(() => {
        if (studentData.completedCourses.length === 0) {
          return  Math.floor(Math.random() * (50 - 10 + 1)) + 10;
        }
        const totalScore = studentData.completedCourses.reduce((sum, course) => sum + course.score, 0);
        return (totalScore / studentData.completedCourses.length).toFixed(2);
      });

      async function fetchStudentInfo() {
        try {
          const response = await axios.get("http://localhost:8000/getinfo/", {
            headers: {
              'Authorization': `Bearer ${store.state.user.access}`
            },
            params: {
              type: 'student',
              id: props.student_id,
            }
          });

          studentData.details = response.data;
          studentData.completedCourses = response.data.completed_courses;
        } catch (error) {
          console.error('Error fetching student information:', error);
        }
      }

      onMounted(fetchStudentInfo);

      return {
        ...toRefs(studentData), // 使用 toRefs 保持响应性
        averageScoreComputed,
        radarConfig,
        goToStudentDetail, 
        handleJoinOrLeaveCommunity
      };
    },
  };
</script>

<style scoped>
.text {
  margin-top: 10%;
}
</style>