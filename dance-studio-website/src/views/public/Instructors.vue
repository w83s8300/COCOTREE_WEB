<template>
  <div class="instructors-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=14" title="師資團隊 / INSTRUCTORS" />

    <!-- 2. Instructors Grid -->
    <div class="container my-5">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
        <p class="mt-2 text-muted">正在載入師資陣容...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
        <span>{{ error }}</span>
        <button @click="fetchTeachers" class="btn btn-outline-danger btn-sm">重新載入</button>
      </div>
      
      <!-- Teachers Grid -->
      <div v-else class="row">
        <!-- No Teachers Message -->
        <div v-if="teachers.length === 0" class="col-12 text-center py-5 text-muted">
          <p>目前尚無老師資料。</p>
        </div>
        
        <!-- Instructor Card -->
        <div v-else class="col-12 col-sm-6 col-md-4 mb-4" v-for="teacher in teachers" :key="teacher.id" data-aos="fade-up">
          <div class="card instructor-card h-100 shadow-sm">
            <img :src="teacher.avatar_url || ('https://picsum.photos/600/400?random=' + teacher.id)" class="card-img-top teacher-img" :alt="teacher.name" loading="lazy">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title fw-bold">{{ teacher.name }}</h5>
              <p class="card-text text-muted mb-3 flex-grow-1">
                <span v-if="teacher.styles && teacher.styles.length > 0">
                  {{ teacher.styles.map(style => style.name).join(' / ') }}
                </span>
                <span v-else>專長舞風整理中</span>
              </p>
              <button 
                type="button" 
                class="btn btn-outline-dark btn-sm w-100"
                @click="showInstructorDetail(teacher)"
              >
                查看師資介紹
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Instructor Detail Modal -->
    <div class="modal fade" id="instructorModal" tabindex="-1" aria-labelledby="instructorModalLabel" aria-hidden="true" ref="modalEl">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold" id="instructorModalLabel">{{ selectedInstructor.name }} 老師</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="container-fluid">
              <div class="row align-items-center">
                <div class="col-12 col-md-5 mb-3 mb-md-0">
                  <img :src="selectedInstructor.avatar_url || ('https://picsum.photos/600/600?random=' + (selectedInstructor.id || 1))" class="img-fluid rounded shadow-sm w-100" style="max-height: 380px; object-fit: cover;" :alt="selectedInstructor.name">
                </div>
                <div class="col-12 col-md-7 text-start">
                  <h4 class="fw-bold mb-2">{{ selectedInstructor.name }}</h4>
                  <div class="mb-3">
                    <span v-for="style in selectedInstructor.styles" :key="style.id" class="badge bg-primary me-1">
                      {{ style.name }}
                    </span>
                  </div>
                  <h6 class="fw-bold text-secondary mb-2">老師簡介</h6>
                  <p class="text-muted lh-base">{{ selectedInstructor.bio || '老師個人簡介目前正在準備中。' }}</p>
                  <p v-if="selectedInstructor.experience_years" class="text-muted small">
                    教學資歷：{{ selectedInstructor.experience_years }} 年
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">關閉</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import api from '@/utils/api';
import PageBanner from '@/components/PageBanner.vue';

export default {
  name: 'Instructors',
  components: {
    PageBanner
  },
  data() {
    return {
      teachers: [],
      selectedInstructor: {},
      loading: false,
      error: null,
      modalInstance: null
    };
  },
  created() {
    this.fetchTeachers();
  },
  mounted() {
    const el = document.getElementById('instructorModal');
    if (el) {
      this.modalInstance = new Modal(el);
    }
  },
  beforeUnmount() {
    if (this.modalInstance) {
      this.modalInstance.dispose();
    }
  },
  methods: {
    async fetchTeachers() {
      this.loading = true;
      this.error = null;
      try {
        const data = await api.get('/teachers');
        if (data.success) {
          this.teachers = data.teachers || [];
        } else {
          this.error = '無法載入老師資料';
        }
      } catch (err) {
        console.error('載入老師資料失敗:', err);
        this.error = '載入老師資料失敗，請稍後重試。';
      } finally {
        this.loading = false;
      }
    },
    showInstructorDetail(teacher) {
      this.selectedInstructor = teacher;
      this.modalInstance?.show();
    }
  }
};
</script>

<style scoped>
.teacher-img {
  height: 280px;
  object-fit: cover;
}

.instructor-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.instructor-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}
</style>