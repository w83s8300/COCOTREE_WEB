<template>
  <div class="courses">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>課程列表</h2>
      <button @click="openCreate" class="btn btn-success">
        <i class="bi bi-plus-lg me-1"></i>新增課程
      </button>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入課程資料...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button @click="fetchCourses" class="btn btn-outline-danger btn-sm">重新嘗試</button>
    </div>

    <!-- 空資料狀態 -->
    <div v-else-if="courses.length === 0" class="text-center py-5 text-muted">
      <p>目前尚無課程資料，請點擊上方按鈕新增。</p>
    </div>

    <!-- 表格內容 -->
    <div v-else class="table-responsive">
      <table class="table table-hover table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col">課程名稱</th>
            <th scope="col">難度</th>
            <th scope="col">舞風</th>
            <th scope="col">時長</th>
            <th scope="col">人數上限</th>
            <th scope="col">扣堂數</th>
            <th scope="col">授課老師</th>
            <th scope="col" class="text-center" style="width: 150px;">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="course in courses" :key="course.id">
            <td class="fw-bold">{{ course.name }}</td>
            <td><span class="badge bg-secondary">{{ course.level }}</span></td>
            <td>{{ course.style_name || '未指定' }}</td>
            <td>{{ course.duration_minutes }} 分鐘</td>
            <td>{{ course.max_students }} 人</td>
            <td>{{ course.price ? `${course.price} 堂` : '-' }}</td>
            <td>{{ course.teacher_name || '未指定' }}</td>
            <td class="text-center">
              <button @click="openEdit(course.id)" class="btn btn-primary btn-sm me-1">編輯</button>
              <button @click="deleteCourse(course.id)" class="btn btn-danger btn-sm">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bootstrap Modal for adding/editing course -->
    <div class="modal fade" id="editCourseModal" tabindex="-1" aria-labelledby="editCourseModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editCourseModalLabel">{{ editingId ? '編輯課程' : '新增課程' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddCourse
              v-if="showForm"
              :courseId="editingId"
              @course-updated="handleCourseUpdated"
              @close-modal="closeModal"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api, { API_ENDPOINTS } from '@/utils/api';
import AddCourse from '../forms/AddCourse.vue';
import { useCrudModal } from '@/composables/useCrudModal';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';

export default {
  name: 'Courses',
  components: {
    AddCourse
  },
  setup() {
    const { showForm, editingId, initModal, openCreate, openEdit, closeModal } = useCrudModal('editCourseModal');
    return { showForm, editingId, initModal, openCreate, openEdit, closeModal };
  },
  data() {
    return {
      courses: [],
      loading: false,
      error: null
    };
  },
  mounted() {
    this.initModal();
  },
  created() {
    this.fetchCourses();
  },
  methods: {
    async fetchCourses() {
      this.loading = true;
      this.error = null;
      try {
        const data = await api.get(API_ENDPOINTS.COURSES);
        this.courses = data.courses || [];
      } catch (err) {
        console.error('獲取課程列表失敗:', err);
        this.error = '獲取課程列表失敗，請稍後再試。';
      } finally {
        this.loading = false;
      }
    },
    async deleteCourse(id) {
      const confirmed = await showConfirm('確定要刪除這個課程嗎？此動作無法復原。');
      if (!confirmed) return;

      try {
        await api.delete(`${API_ENDPOINTS.COURSES}/${id}`);
        showToast('課程已成功刪除！', 'success');
        this.fetchCourses();
      } catch (err) {
        console.error('刪除課程失敗:', err);
        showToast('刪除課程失敗，請重試。', 'error');
      }
    },
    handleCourseUpdated() {
      this.fetchCourses();
      this.closeModal();
    }
  }
};
</script>

<style scoped>
.courses {
  padding: 10px;
}
</style>
