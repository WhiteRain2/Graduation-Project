<template>
  <ContentBase>
    <div class="row justify-content-md-center">
      <div class="col-3">
        <form @submit.prevent="login">
          <div class="mb-3">
            <input v-model="studentId" type="text" class="form-control" id="studentId" placeholder="请输入学生ID">
          </div>
          <div class="error-message">{{ errorMessage }}</div>
          <button type="submit" class="btn btn-primary">进入</button>
        </form>
      </div>
    </div>
  </ContentBase>
</template>

<script>
import ContentBase from '../components/ContentBase';
import { ref } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'LoginView',
  components: {
    ContentBase,
  },
  setup() {
    const store = useStore();
    const studentId = ref('');
    const errorMessage = ref('');

    const login = async () => {
      errorMessage.value = "";
      try {
        // 使用学生ID进行登录，并等待返回结果
        await store.dispatch("user/fetchUser", studentId.value);
        // 验证用户是否已经登录
        if (store.state.user.is_login) {
          localStorage.setItem('studentId', studentId.value);
          localStorage.setItem('isUserLoggedIn', 'true');
          console.log(localStorage);
          window.location.reload(); // 强制页面刷新
        } else {
          // 如果没有返回有效的用户数据，设置错误消息
          errorMessage.value = "无效的学生ID";
        }
      } catch (error) {
        // 可能是网络错误或后端错误，因此设置通用的登录失败消息
        errorMessage.value = "登录失败，请重试";
      }
    };

    return {
      studentId,
      errorMessage,
      login,
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