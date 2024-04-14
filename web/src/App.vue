<template>
  <NavBar />
  <router-view :key="$route.fullPath"/>
</template>

<script>
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap';
import NavBar from './components/NavBar';
import { mapActions } from 'vuex';
import router from './router';

export default {
  name: "App",
  components: {
    NavBar,
  },
  methods: {
    ...mapActions('user', ['fetchUser']),
  },
  mounted() {
    // 检查是否在localStorage中存储了登录状态
    const isLoggedIn = localStorage.getItem('isUserLoggedIn');
    if (isLoggedIn) {
      // 用户已登录，同步用户数据
      const userId = localStorage.getItem('studentId');
      this.fetchUser(userId); // 通过 Vuex action 更新用户状态
      router.push({name: 'home'})
    }
  }
}
</script>

<style>
</style>