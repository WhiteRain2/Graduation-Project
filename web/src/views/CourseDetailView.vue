<template>
  <ContentBase>
    <div v-if="course" class="container my-5">
      <div class="card mb-5">
        <div class="card-body">
          <h2 class="card-title">{{ course.name }}</h2>
          <p class="card-text">{{ course.description }}</p>
        </div>
      </div>

      <!-- Chapters & Units -->
      <h3>章节目录</h3>
      <div class="row">
        <div v-for="chapter in organizedChapters" :key="chapter.seq" class="col-12 mb-4">
          <div class="card">
            <div class="card-header">{{ chapter.title }}</div>
            <div class="card-body">
              <ul>
                <li v-for="unit in chapter.units" :key="unit.seq" class="mb-2">
                  {{ unit.title }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Lessons & Tasks in Grid Layout -->
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
                <div class="card-body">
                  {{ task.title }} ({{ task.type }})
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
  </ContentBase>
</template>

<script>
import ContentBase from '@/components/ContentBase';
import axios from 'axios';
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';

export default {
  name: 'CourseDetail',
  components: {
    ContentBase,
  },
  setup() {
    const route = useRoute();
    const course = ref(null);
    const chapters = ref([]);
    const tasks = ref([]);

    const organizedChapters = computed(() => {
      return chapters.value.filter(ch => ch.type === 'chapter').map(chapter => ({
        ...chapter,
        units: chapters.value.filter(unit => unit.type === 'unit' && unit.number === chapter.number).sort((a, b) => a.seq - b.seq)
      }));
    });

    const organizedLessons = computed(() => {
      return chapters.value.filter(lesson => lesson.type === 'lesson').sort((a, b) => a.number === b.number ? a.seq - b.seq : a.number - b.number);
    });
    
    const loadCourseDetails = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/courses/${route.params.course_id}`);
        course.value = response.data.course;
        chapters.value = response.data.chapters;
        tasks.value = response.data.tasks;
      } catch (error) {
        console.error('There was an error fetching the course details:', error);
      }
    };

    onMounted(() => {
      loadCourseDetails();
    });

    return {
      course,
      organizedChapters,
      organizedLessons,
      tasks,
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
</style>