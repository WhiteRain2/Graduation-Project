<template>
  <ContentBase>
    <div class="row justify-content-md-center">
      <div class="col-3">
        <form @submit.prevent="register">
          <div class="mb-3">
            <label for="username" class="form-label">用户名</label>
            <input v-model="username" type="text" class="form-control" id="username">
          </div>
          <div class="mb-3">
            <label for="password" class="form-label">密码</label>
            <input v-model="password" type="password" class="form-control" id="password">
          </div>
          <div class="mb-3">
            <label for="password_confirm" class="form-label">确认密码</label>
            <input v-model="password_confirm" type="password" class="form-control" id="password_confirm">
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">邮箱</label>
            <input v-model="email" type="text" class="form-control" id="email">
          </div>
          <div class="error-message">{{ error_message }}</div>
          <button type="submit" class="btn btn-primary">注册</button>
        </form>
      </div>
    </div>
  </ContentBase>
</template>

<script>
import ContentBase from '../components/ContentBase'
import { ref } from 'vue';
import router from '@/router/index';
import axios from 'axios';

export default {
  name: 'RegisterView',
  components: {
      ContentBase,
  },
  setup() {
    let username = ref('');
    let password = ref('');
    let password_confirm = ref('');
    let email = ref('')
    let error_message = ref('');
    
    const register = async () => {
      // 校验前端输入的数据是否合法
      if (!username.value || !password.value || !email.value) {
        error_message.value = "用户名、密码和邮箱都是必需的。";
        return;
      }

      if (password.value !== password_confirm.value) {
        error_message.value = "两次输入的密码不一致。";
        return;
      }

      try {
        // 发送POST请求到服务器注册新用户
        const response = await axios.post('http://localhost:8000/register/', {
          username: username.value,
          password: password.value,
          email: email.value
        });

        if (response.data.success) {
          // 注册成功后的操作，比如跳转到登录页或其他页面
          router.push({name: 'login'});
        }
      } catch (error) {
        if (error.response && error.response.data.error) {
          // 显示来自后端的错误信息
          error_message.value = error.response.data.error;
        } else {
          // 显示通用错误信息
          error_message.value = "注册失败，请稍后再试。";
        }
      }
    };

    return {
      username,
      password,
      password_confirm,
      error_message,
      email,
      register,
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
}
</style>