<template>
  <div class="instructors-page">
    <!-- 1. Banner -->
    <div class="banner">
      <img src="https://picsum.photos/1920/500?random=14" alt="Instructors Banner" class="banner-img">
      <div class="banner-text">
        <h1>師資團隊 / INSTRUCTORS</h1>
      </div>
    </div>

    <!-- 2. Instructors Grid -->
    <div class="container my-5">
      <!-- Loading State -->
      <div v-if="loading" class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
        <p class="mt-2">載入老師資料中...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
        <button @click="fetchTeachers" class="btn btn-outline-danger btn-sm ms-2">重新載入</button>
      </div>
      
      <!-- Teachers Grid -->
      <div v-else class="row">
        <!-- No Teachers Message -->
        <div v-if="teachers.length === 0" class="col-12 text-center">
          <p class="text-muted">目前沒有老師資料</p>
        </div>
        
        <!-- Instructor -->
        <div v-else class="col-12 col-sm-6 col-md-4 mb-4" v-for="teacher in teachers" :key="teacher.id">
          <div class="card instructor-card">
            <img src="https://picsum.photos/600/400?random=teacher" class="card-img-top" :alt="teacher.name">
            <div class="card-body">
              <h5 class="card-title">{{ teacher.name }}</h5>
              <p class="card-text">
                <span v-if="teacher.styles && teacher.styles.length > 0">
                  {{ teacher.styles.map(style => style.name).join(' / ') }}
                </span>
                <span v-else>專長風格待更新</span>
              </p>
              <button type="button" class="btn btn-outline-dark btn-sm" data-bs-toggle="modal"
                data-bs-target="#instructorModal" @click="showInstructorDetail(teacher)">
                View Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Modal -->
  <div class="modal fade" id="instructorModal" tabindex="-1" aria-labelledby="instructorModalLabel"
    aria-hidden="true">
    <div class="modal-dialog modal-xl">
      <div class="modal-content ">
        <div class="modal-header">
          <h5 class="modal-title" id="instructorModalLabel">{{ selectedInstructor.name }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" @click="hideModal"></button>
        </div>
        <div class="modal-body">
          <div class="container-fluid">
            <div class="row">
              <div class="col-12 col-sm-6 col-md-4">
                <img src="https://picsum.photos/600/400?random=instructor" class="card-img-top" :alt="selectedInstructor.name">
              </div>
              <div class="col-12 col-sm-6 col-md-8">
                <h6><strong>姓名：</strong>{{ selectedInstructor.name }}</h6>
                <h6><strong>簡介：</strong></h6>
                <p>{{ selectedInstructor.bio || '老師簡介待更新' }}</p>
                <h6><strong>專長風格：</strong></h6>
                <ul v-if="selectedInstructor.styles && selectedInstructor.styles.length > 0">
                  <li v-for="style in selectedInstructor.styles" :key="style.id">{{ style.name }}</li>
                </ul>
                <p v-else>專長風格待更新</p>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" @click="hideModal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import apiService from '@/utils/api';

export default {
  name: 'Instructors',
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
    // 初始化 Modal 實例
    this.modalInstance = new Modal(document.getElementById('instructorModal'), {
      keyboard: true,
      backdrop: true
    });
  },
  beforeUnmount() {
    // 清理 Modal 實例
    if (this.modalInstance) {
      this.modalInstance.dispose();
    }
  },
  methods: {
    fetchTeachers() {
      this.loading = true;
      this.error = null;
      
      apiService.get('teachers')
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            this.teachers = data.teachers;
          } else {
            this.error = '無法載入老師資料';
          }
        })
        .catch(error => {
          console.error('載入老師資料失敗:', error);
          this.error = '載入老師資料失敗';
        })
        .finally(() => {
          this.loading = false;
        });
    },
    showInstructorDetail(teacher) {
      this.selectedInstructor = teacher;
      if (this.modalInstance) {
        this.modalInstance.show();
      }
    },
    hideModal() {
      if (this.modalInstance) {
        this.modalInstance.hide();
      }
    }
  }
};
</script>

<style src="../../assets/css/Instructors.css"></style>