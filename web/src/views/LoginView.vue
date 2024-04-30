<template>
  <ContentBase>
    <div class="row justify-content-md-center">
      <div class="col-3">
        <form @submit.prevent="login">
          <div class="mb-3">
            <label for="username" class="form-label">用户名</label>
            <input v-model="username" type="text" class="form-control" id="username" required>
          </div>
          <div class="mb-3">
            <label for="password" class="form-label">密码</label>
            <input v-model="password" type="password" class="form-control" id="password" required>
          </div>
          <div class="error-message">{{ errorMessage }}</div>
          <button type="submit" class="btn btn-primary" :disabled="isLoggingIn">登录</button>
        </form>
      </div>
    </div>
  </ContentBase>
</template>

<script>
import ContentBase from '../components/ContentBase'
import { ref } from 'vue';
import { useStore } from 'vuex';
import router from '@/router/index';

export default {
  name: 'LoginView',
  components: {
    ContentBase,
  },
  setup() {
    const store = useStore();
    const username = ref('');
    const password = ref('');
    const errorMessage = ref('');
    const isLoggingIn = ref(false); // 新增，用于表示正在登录

    const login = async () => {
      errorMessage.value = "";
      isLoggingIn.value = true;
      try {
        await store.dispatch("user/login", {
          username: username.value,
          password: password.value,
        });
        router.push({name: 'home'});
      } catch (error) {
        errorMessage.value = error.message;
      } finally {
        isLoggingIn.value = false;
      }
    };

    return {
      username,
      password,
      errorMessage,
      login,
      isLoggingIn,
    }
  }
}
</script>

<style scoped>
button {
  width: 100%;
}

.error-message {
  color: red;
  margin-top: 0.5rem;
}
</style>