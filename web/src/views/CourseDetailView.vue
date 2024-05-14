<template>
  <ContentBase>
    <div v-if="course" class="container my-2">
      <div class="card mb-5">
        <div class="card-header">{{ course.name }}</div>
        <div class="card-body d-flex">
          <!-- 图片占据左侧固定最大宽度 -->
          <img decoding="async" :src="course.photo" alt="图片暂时无法显示！" class="img-fluid me-3" style="max-width: 50%; height: auto;">
          <!-- 由于使用了d-flex，右侧内容现通过flex-grow控制宽度 -->
          <div class="d-flex flex-column justify-content-center ms-auto pe-3 flex-grow-1">
            <h5 class="mb-4">课程名: {{ course.name }}</h5>
            <p class="mb-4">主讲人：{{ course.teachers }}</p>
            <p class="mb-4">开课时间: {{ formattedCreateTime }}</p>
            <button v-if="isNewCourse" type="button" class="btn btn-outline-success" @click="handleFetchRecommendations">加入学习</button>
            <button v-else type="button" class="btn btn-outline-success" @click="handleFetchRecommendations">继续学习</button>
          </div>
        </div>
        <div class="card-footer text-end text-muted small">已有{{ course.total_count }}人正在学习ing...</div>
      </div>

      <div v-if="isNewCourse" class="mb-4 tool-div">
        <div class="card mb-3">
          <div class="card-header">课程详情</div>
          <div class="card-body">{{ course.description }}</div>
        </div>

        <div class="card">
          <div class="card-header">章节目录</div>
          <ul class="list-group list-group-flush">
            <li v-for="chapter in organizedChapters" :key="chapter.seq" class="list-group-item">
              <h5 class="mb-2">第{{ chapter.number }}章——{{ chapter.title }}</h5>
              <ul class="mb-2">
                <li v-if="!chapter.units.length">{{ chapter.title }}</li>
                <li v-else v-for="unit in chapter.units" :key="unit.seq">{{ unit.title }}</li>
              </ul>
            </li>
          </ul>
          <div class="card-footer text-center">
            <button type="button" class="btn btn-outline-success w-50 mx-auto" @click="handleFetchRecommendations">加入学习</button>
          </div>
        </div>
      </div>

      <div v-else class="tool-div">
        <!-- 课程及任务板块 -->
        <div class="row">
          <!-- Lessons Section -->
          <div class="col-md-6">
            <h3>所有课程</h3>
            <div class="row">
              <div v-for="lesson in organizedLessons" :key="lesson.seq" class="col-12 mb-2">
                <div class="card">
                  <div class="card-body">
                    {{ lesson.title }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Tasks Section -->
          <div class="col-md-6">
            <h3>待完成的任务</h3>
            <div class="row">
              <div v-for="task in tasks" :key="task.seq" class="col-12 mb-2">
                <div class="card">
                  <div class="card-body d-flex justify-content-between">
                    <span>{{ task.title }}</span>
                    <span :class="['badge', typeToBadgeClass(task.type)]">{{ task.type }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 推荐结果列表 -->
        <div class="row" id="recommendations">
          <div class="col">
            <div class="card mt-3">
              <div class="card-header">
                推荐你和他们一起学
              </div>
              <!-- 使用v-if在is_recommending为true时显示加载指示器 -->
              <div class="text-center" v-if="is_recommending">
                <br>
                <span class="spinner-border text-primary" role="status" aria-hidden="true"></span>
                <br>
                <span>稍等一会...</span>
              </div>

              <div class="card-body" v-else>
                <!-- 共同体列表 -->
                <div class="card" v-if="r_communities.length">
                  <div class="card-header">你可以加入他们...</div>
                  <div class="card-body">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th scope="col" class="text-center">小组ID</th>
                          <th scope="col" class="text-center">小组名称</th>
                          <th scope="col" class="text-center">小组人数</th>
                          <th scope="col" class="text-center">匹配度</th>
                          <th scope="col" class="text-center">操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="community in r_communities" :key="community.id">
                          <td class="text-center">{{ community.id }}</td>
                          <td class="text-center">{{ community.name }}</td>
                          <td class="text-center">{{ community.members_count }}</td>
                          <td class="text-center">
                            {{ typeof community.similarity === 'number' ? community.similarity.toFixed(2) : '' }}
                          </td>
                          <td class="text-center">
                            <button type="button" class="btn btn-outline-secondary me-2"
                              @click="goToCommunityDetail(community.id)">查看信息</button>
                            <button type="button" class="btn btn-outline-secondary"
                              @click="handleJoinOrLeaveCommunity(community.id, community.joined ? 'leave' : 'join')"
                              :disabled="community.joined"
                            >
                              {{ community.joined ? '已加入' : '加入小组' }}
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <br>
                <!-- 个人列表 -->
                <div class="card" v-if="r_person.length">
                  <div class="card-header">或者和Ta一起学...</div>
                  <div class="card-body">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th scope="col" class="text-center">ID</th>
                          <th scope="col" class="text-center">姓名</th>
                          <th scope="col" class="text-center">性别</th>
                          <th scope="col" class="text-center">已学/正在学</th>
                          <th scope="col" class="text-center">相似度</th>
                          <th scope="col" class="text-center">操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="person in r_person" :key="person.members.id">
                          <td class="text-center">{{ person.members.id }}</td>
                          <td class="text-center">{{ person.members.name }}</td>
                          <td class="text-center">{{ person.members.gender }}</td>
                          <td class="text-center">{{ person.members.completed_count }} / {{ person.members.wish_count }}</td>
                          <td class="text-center">
                            {{ typeof person.similarity === 'number' ? person.similarity.toFixed(2) : '' }}
                          </td>
                          <td class="text-center">
                            <button type="button" class="btn btn-outline-secondary me-2" @click="goToStudentDetail(person.members.id)">查看信息</button>
                            <button type="button" class="btn btn-outline-secondary" @click="handleJoinOrLeaveCommunity(person.id, person.joined ? 'leave' : 'join')" :disabled="person.joined">
                              {{ person.joined ? '快去聊天吧' : '组成小组' }}
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="text-center my-5">
      Loading course information...
    </div>
    <!-- 聊天室图标及下拉菜单容器 -->
    <div class="chat-icon-wrapper">
      <div class="chat-icon" @click="toggleChatMenu">
        <!-- 这里添加图标 -->
        <!-- <i class="fa fa-comments" aria-hidden="true">Chat</i> -->
        <svg xmlns="http://www.w3.org/2000/svg" class="ionicon" viewBox="0 0 512 512"><path d="M431 320.6c-1-3.6 1.2-8.6 3.3-12.2a33.68 33.68 0 012.1-3.1A162 162 0 00464 215c.3-92.2-77.5-167-173.7-167-83.9 0-153.9 57.1-170.3 132.9a160.7 160.7 0 00-3.7 34.2c0 92.3 74.8 169.1 171 169.1 15.3 0 35.9-4.6 47.2-7.7s22.5-7.2 25.4-8.3a26.44 26.44 0 019.3-1.7 26 26 0 0110.1 2l56.7 20.1a13.52 13.52 0 003.9 1 8 8 0 008-8 12.85 12.85 0 00-.5-2.7z" fill="none" stroke="currentColor" stroke-linecap="round" stroke-miterlimit="10" stroke-width="32"/><path d="M66.46 232a146.23 146.23 0 006.39 152.67c2.31 3.49 3.61 6.19 3.21 8s-11.93 61.87-11.93 61.87a8 8 0 002.71 7.68A8.17 8.17 0 0072 464a7.26 7.26 0 002.91-.6l56.21-22a15.7 15.7 0 0112 .2c18.94 7.38 39.88 12 60.83 12A159.21 159.21 0 00284 432.11" fill="none" stroke="currentColor" stroke-linecap="round" stroke-miterlimit="10" stroke-width="32"/></svg>
      </div>
      <div class="chat-menu" v-if="showChatMenu">
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col" class="text-center">小组ID</th>
              <th scope="col" class="text-center">小组名称</th>
              <th scope="col" class="text-center">成员人数</th>
              <th scope="col" class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="community in communities" :key="community.id">
              <td class="text-center">{{ community.id }}</td>
              <td class="text-center">{{ community.name }}</td>
              <td class="text-center">{{ community.count }}</td>
              <td class="text-center">
                <button type="button" class="btn btn-outline-secondary me-2" @click="handleViewCommunity(community.id)">聊天</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <ModalContext :isVisible="isChatModalVisible" @update:isVisible="isChatModalVisible = $event">
      <ChatMessages 
        v-if="isChatModalVisible"
        :studentId="studentId" 
        :communityId="selectedCommunityId" 
        @close="isChatModalVisible = false">
      </ChatMessages>
    </ModalContext>
  </ContentBase>
</template>

<script>
import ContentBase from '@/components/ContentBase';
import axios from 'axios';
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import { useStore } from 'vuex';
import ChatMessages from '@/components/ChatMessages.vue'
import ModalContext from '@/components/ModalContext.vue'
import router from '@/router/index';

export default {
  name: 'CourseDetail',
  components: {
    ContentBase,
    ChatMessages,
    ModalContext
  },
  setup() {
    const store = useStore();
    const route = useRoute();
    const course = ref(null);
    const chapters = ref([]);
    const tasks = ref([]);
    const showChatMenu = ref(false);
    const communities = computed(() => store.state.user.communities); 
    const studentId = computed(() => store.state.user.id);
    const is_recommending = computed(() => store.state.user.is_recommending);
    const recommendedCommunities = computed(() => store.state.user.recommendedCommunities);
    const r_communities = computed(() => recommendedCommunities.value.filter(community => !community.is_a_person));
    const r_person = computed(() => 
      recommendedCommunities.value
        .filter(community => community.is_a_person)
        .map(community => ({ ...community, members: community.members[0] }) )
    );

    const goToCommunityDetail = (communityId) => {
      router.push({ name: 'vis', params: { community_id: communityId } });
    }
    const goToStudentDetail = (studentId) => {
      router.push({name: 'userprofile', params: { userId: studentId }});
    }

    // 异步加载课程详情数据
    const loadCourseDetails = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/courses/?course_id=${route.params.course_id}`);
        course.value = response.data.course;
        chapters.value = response.data.chapters;
        tasks.value = response.data.tasks;
      } catch (error) {
        console.error('There was an error fetching the course details:', error);
      }
    };
    
    onMounted(loadCourseDetails);

    // 使用computed属性计算课程是否为新课程
    const isNewCourse = computed(() => {
      const courseId = parseInt(route.params.course_id);
      const completedCourses = store.state.user.completedCourses || [];
      const wishCourses = store.state.user.wishCourses || [];
      return !completedCourses.some(course => course.id === courseId) && !wishCourses.some(course => course.id === courseId);
    });

    // 组织章节数据
    const organizedChapters = computed(() => chapters.value.filter(c => c.type === 'chapter').map(chapter => ({
      ...chapter,
      units: chapters.value.filter(unit => unit.type === 'unit' && unit.number === chapter.number).sort((a, b) => a.seq - b.seq),
    })));

    // 组织课程列表
    const organizedLessons = computed(() => chapters.value.filter(lesson => lesson.type === 'lesson').sort((a, b) => a.number === b.number ? a.seq - b.seq : a.number - b.number));

    // 格式化创建时间
    const formattedCreateTime = computed(() => {
      if (course.value && course.value.created_time) {
        const date = new Date(course.value.created_time);
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
      } else {
        return '';
      }
    });

    const typeToBadgeClass = (type) => {
      const badgeClasses = {
        '讨论': 'bg-info',
        '完成文档': 'bg-success',
        '实践': 'bg-warning text-dark',
        'ppt汇报': 'bg-danger',
        '视频任务': 'bg-primary',
        '自我完成': 'bg-secondary',
        '需要下载': 'bg-light text-dark',
        '考试': 'bg-dark',
        '课后作业': 'bg-success',
        '未知': 'bg-secondary',
      };
      return badgeClasses[type] || 'bg-secondary';
    };

    const toggleChatMenu = () => {
      showChatMenu.value = !showChatMenu.value;
    };

    const handleOutsideClick = (event) => {
      // 获取聊天图标和下拉菜单的DOM元素
      const chatIconEl = document.querySelector('.chat-icon-wrapper');
      if (chatIconEl && !chatIconEl.contains(event.target)) {
        // 如果点击不在聊天图标或下拉菜单内部，则隐藏下拉菜单
        showChatMenu.value = false;
      }
    };

    onMounted(() => {
      // 当组件挂载后，添加点击事件监听器到document
      document.addEventListener('click', handleOutsideClick);
    });

    onBeforeUnmount(() => {
      // 组件卸载前移除事件监听器
      document.removeEventListener('click', handleOutsideClick);
    });

    // 控制聊天框显示的reactive property
    const isChatModalVisible = ref(false);
    const selectedCommunityId = ref(null); // 新增一个变量用于存储当前选中的社区ID

    function handleViewCommunity(communityId) {
      selectedCommunityId.value = communityId;
      isChatModalVisible.value = true; // 显示聊天框
    }

    function handleCloseChatModal() {
      isChatModalVisible.value = false; // 隐藏聊天框
    }

    const handleFetchRecommendations = async () => {
      store.commit('user/updateWishCourses', {
        id: course.value.course_id,
        name: course.value.name
      });
      store.commit('user/updateIsrecommending', true);
      try {
        // 直接调用store的dispatch函数来触发一个action
        await store.dispatch('user/fetchRecommendations', {
          student_id: store.state.user.id,
          course_id: course.value.course_id
        });

        // 再次调用dispatch来更新学生愿望列表
        await store.dispatch('user/fetchUser', store.state.user.id);
      } catch (error) {
        alert(error.message);
      } finally {
        store.commit('user/updateIsrecommending', false); // 无论成功还是失败，结束加载状态
        console.log(recommendedCommunities);
      }      
    };

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


    return {
      studentId,
      course,
      organizedChapters,
      organizedLessons,
      tasks,
      isNewCourse,
      formattedCreateTime,
      typeToBadgeClass,
      showChatMenu,
      toggleChatMenu,
      communities,
      isChatModalVisible,
      selectedCommunityId,
      handleViewCommunity,
      handleCloseChatModal,
      recommendedCommunities,
      r_communities,
      r_person,
      handleFetchRecommendations,
      is_recommending,
      handleJoinOrLeaveCommunity,
      goToCommunityDetail,
      goToStudentDetail
    };
  }
};
</script>

<style scoped>
  h2, h3 {
    margin-top: 0.5em;
  }
  ul {
    list-style-type: none;
    padding: 0;
  }
  li {
    margin-bottom: 0.5em;
  }
  .tool-div {
    margin: 0;
    padding: 0;
  }

  .cursor-pointer {
  cursor: pointer;
  }

  /* 聊天室图标及下拉菜单样式 */
  .chat-icon-wrapper {
    position: fixed; /* 固定位置，不随页面滚动改变 */
    bottom: 40px;    /* 离底部20px */
    right: 40px;     /* 离右边20px */
    z-index: 1050;   /* 层叠顺序设置得略高，以确保能覆盖大多数元素 */
  }

  .chat-icon svg {
    width: 40px; /* 或其他适合的尺寸 */
    height: 40px; /* 或其他适合的尺寸 */
  }

  .chat-icon {
    cursor: pointer;
    /* 可以根据需要添加其他样式，如背景色、边框等 */
  }

  .chat-menu {
    display: block;
    position: absolute;
    bottom: 100%; /* 使下拉菜单显示在图标上方 */
    right: 0;
    width: 500px; /* 扩大下拉菜单的宽度 */
    background-color: #fff; /* 添加纯色背景板 */
    border: 1px solid #ddd; /* 添加边框 */
    box-shadow: 0 2px 5px rgba(0,0,0,.2); /* 添加轻微的阴影，增加立体感 */
    border-radius: .25rem; /* 轻微的圆角 */
    overflow: hidden; /* 防止子元素溢出 */
  }

  .chat-room {
    padding: .5rem 1rem; /* 聊天室信息的内边距 */
    border-bottom: 1px solid #ddd; /* 聊天室之间的分隔线 */
  }

  .chat-room:last-child {
    border-bottom: none; /* 最后一个聊天室不显示分隔线 */
  }

  /* 添加悬停效果 */
  .chat-room:hover {
    background-color: #f8f9fa;
  }
</style>