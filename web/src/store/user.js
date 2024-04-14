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
    is_login: false,  // 登录状态由是否有有效的用户 ID 决定
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
    },
    clearUser(state) {
        state.id = "";
        state.name = "";
        state.completedCourses = [];
        state.wishCourses = [];
        state.communities = [];
        state.is_login = false;
    }
  },
  actions: {
    fetchUser({ commit }, userId) {
        return new Promise((resolve, reject) => {
          axios.get(`http://localhost:8000/getinfo/${userId}/`)  // 确保 URL 与后端 API 对应
            .then(response => {
                commit('updateUser', response.data);  // 提交 mutation 来更新用户数据和状态
                resolve(response);  // 解析 promise 表明操作成功
            })
            .catch(error => {
                console.error('Error fetching user data:', error);
                commit('clearUser');  // 如果获取数据出错，则清除用户状态
                reject(error);  // 拒绝 promise 表明操作失败
            });
        });
    },
    changeUser({ dispatch }, userId) {
        // 可以调用 fetchUser 动作重新获取用户数据，相当于切换用户
        dispatch('fetchUser', userId);
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