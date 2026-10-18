<template>
  <div class="bg-light py-5">
    <div class="container">
      <h2 class="text-center mb-4">本月主打星</h2>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
      </div>

      <!-- Content -->
      <div v-else class="row align-items-center">
        <div class="col-md-4">
          <img :src="instructor.image" class="img-fluid rounded-circle" :alt="instructor.name" loading="lazy">
        </div>
        <div class="col-md-8">
          <h3>{{ instructor.name }}</h3>
          <p class="lead">專長：{{ instructor.specialty }}</p>
          <p>{{ instructor.bio }}</p>
          <router-link to="/instructors" class="btn btn-outline-dark">了解更多</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/utils/api';

const FALLBACK_INSTRUCTOR = {
  name: 'Teacher Name',
  specialty: 'Hip Hop, Locking',
  bio: '老師擁有超過十年的舞蹈經驗，活躍於各大舞蹈比賽與商業演出。教學風格風趣幽默，深受學生喜愛。老師相信，舞蹈不僅是技巧的展現，更是情感的表達，希望能帶領學生找到屬於自己的舞蹈靈魂。',
  image: 'https://picsum.photos/800/800?random=4',
};

export default {
  name: 'FeaturedInstructor',
  data() {
    return {
      loading: false,
      instructor: { ...FALLBACK_INSTRUCTOR },
    };
  },
  created() {
    this.fetchFeaturedTeacher();
  },
  methods: {
    async fetchFeaturedTeacher() {
      this.loading = true;
      try {
        const data = await api.get('/teachers');
        if (data.success && data.teachers && data.teachers.length > 0) {
          // Pick a random teacher as the featured instructor
          const randomIndex = Math.floor(Math.random() * data.teachers.length);
          const teacher = data.teachers[randomIndex];
          this.instructor = {
            name: teacher.name,
            specialty: teacher.styles && teacher.styles.length > 0
              ? teacher.styles.map(s => s.name).join(', ')
              : 'Hip Hop, Locking',
            bio: teacher.bio || FALLBACK_INSTRUCTOR.bio,
            image: teacher.image || `https://picsum.photos/800/800?random=${teacher.id || 4}`,
          };
        }
        // If no teachers, keep fallback
      } catch {
        // API failed — keep fallback content
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
/* Add any specific styles for FeaturedInstructor here if needed */
</style>
