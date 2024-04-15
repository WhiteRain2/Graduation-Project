// store/user.js

import axios from 'axios';
import router from '@/router';

const ModuleUser = {
  namespaced: true,
  state: {
    id: "",
    name: "",  // 修改为 'name' 以匹配后端返回的 'name' 字段
    completedCourses: [],  // 添加已完成课程的数组
    wishCourses: [],  // 添加愿望课程的数组
    communities: [],  // 添加已加入的共同体数组
    recommendedCommunities: [],  //保存最近的共同体推荐结果
    is_login: false,  // 登录状态由是否有有效的用户 ID 决定
    is_recommending: false, //是否正在拉取推荐列表
  },
  getters: {
    // 添加 getters，以便组件能够访问和派生这些数据
  },
  mutations: {
    updateUser(state, userData) {
        state.id = userData.id;
        state.name = userData.name;
        state.completedCourses = userData.completed_courses;  // 更新已完成课程数据
        state.wishCourses = userData.wish_courses;  // 更新愿望课程数据
        state.communities = userData.communities;  // 更新共同体数据
        state.is_login = Boolean(userData.id);  // 更新登录状态
        state.is_recommending = false;
    },
    clearUser(state) {
        state.id = "";
        state.name = "";
        state.completedCourses = [];
        state.wishCourses = [];
        state.communities = [];
        state.is_login = false;
        state.is_recommending = false;
    },
    updateRecommendedCommunities(state, communities) {
      state.recommendedCommunities = communities;
    },
    clearRecommendedCommunities(state) {
      state.recommendedCommunities = [];  // 清除推荐列表
    },
    updateIsrecommending(state, b) {
      state.is_recommending = b
    }
  },
  actions: {
    fetchUser: async ({ commit }, userId) => {
      try {
        const response = await axios.get(`http://localhost:8000/getinfo/${userId}/`); // 确保 URL 与后端 API 对应
        commit('updateUser', response.data); // 提交 mutation 来更新用户数据和状态
        return response; // 返回响应对象
      } catch (error) {
        console.error('Error fetching user data:', error);
        commit('clearUser'); // 如果获取数据出错，则清除用户状态
        throw error; // 抛出错误以在调用链上标记失败
      }
    },
    fetchRecommendations: async ({ commit, state }, { student_id, course_id }) => {
      const response = await axios.post('http://localhost:8000/getrecommend/', {
        student_id,
        course_id
      });
      if (response.data.error) {
        throw new Error(response.data.error);
      } else {
        let recommendedCommunities = response.data;
    
        // 通过检查每一个推荐的共同体是否在用户已加入的共同体列表中来确定 joined 属性的值
        recommendedCommunities = recommendedCommunities.map(community => ({
          ...community,
          joined: !!state.communities.find(c => c.id === community.id)
        }));
    
        commit('updateRecommendedCommunities', recommendedCommunities);
      }
    },
    joinOrLeaveCommunity: async ({ commit, dispatch, state }, { student_id, community_id, operation }) => {
      try {
        const response = await axios.post('http://localhost:8000/operation/', {
          student_id,
          community_id,
          operation
        });
        if (response.data.error) {
          throw new Error(response.data.error);
        } else {
          // 重新获取用户数据来确保状态的实时性
          dispatch('fetchUser', student_id);
          
          // 更新推荐的共同体
          let updatedCommunities = state.recommendedCommunities.map(community => ({
            ...community,
            joined: community.id === community_id ? operation === 'join' : community.joined
          }));
          commit('updateRecommendedCommunities', updatedCommunities);
        }
      } catch (error) {
        console.error(error);
        throw error;
      }
    },
    logout({ commit }) {
        commit('clearUser');  // 调用 mutation 来清除用户数据
        localStorage.removeItem('studentId');  // 清除localStorage中保存的用户ID
        localStorage.removeItem('isUserLoggedIn');  // 清除localStorage中保存的登录状态
        router.push({ name: 'login' });
    }
  }
};

export default ModuleUser;