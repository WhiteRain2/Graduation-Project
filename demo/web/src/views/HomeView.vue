<template>
  <div class="home">
    <form @submit.prevent="submitForm">
        <label for="student_id">Student ID:</label>
        <input type="text" id="student_id" v-model="studentId" required>

        <label for="course_id">Wish Course ID:</label>
        <input type="text" id="course_id" v-model="courseId" required>

        <input type="submit" value="Recommend Communities">
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios';

export default {
  name: 'HomeView',
  setup() {
    // 创建响应式引用
    const studentId = ref('');
    const courseId = ref('');

    // 处理表单提交
    const submitForm = () => {
      // 构造请求的数据
      const requestData = {
        student_id: studentId.value,
        course_id: courseId.value
      };

      // 使用 axios 发送 POST 请求
      axios.post('http://localhost:8000/demo/', requestData)
        .then(response => {
          console.log(response.data);
          // 处理响应数据
        })
        .catch(error => {
          console.error('Error:', error);
          // 处理错误
        });
    }
    
    // 返回提交方法和数据绑定
    return {
      studentId,
      courseId,
      submitForm
    }
  }
}
</script>