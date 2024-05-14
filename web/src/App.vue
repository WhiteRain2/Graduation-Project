<template>
  <NavBar />
  <router-view :key="$route.fullPath"/>
</template>

<script>
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap';
import NavBar from './components/NavBar';

export default {
  name: "App",
  components: {
    NavBar,
  },
  // 使用 created 钩子保证在组件实例被完全创建之后立即执行。
  created() {
    // 通过调用 Vuex action 来恢复认证状态
    this.$store.dispatch('user/restoreAuthState');
  }
}
</script>

<style>
</style>