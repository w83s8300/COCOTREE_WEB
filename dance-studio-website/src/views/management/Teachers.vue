<template>
  <div class="teachers">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>老師列表</h2>
      <div class="d-flex">
        <input
          type="text"
          v-model="searchQuery"
          @keyup.enter="fetchTeachers"
          placeholder="搜尋老師姓名"
          class="form-control me-2"
        />
        <button @click="fetchTeachers" class="btn btn-outline-secondary text-nowrap">
          <i class="bi bi-search me-1"></i>搜尋
        </button>
        <button @click="openCreate" class="btn btn-success ms-2 text-nowrap">
          <i class="bi bi-plus-lg me-1"></i>新增老師
        </button>
      </div>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入老師資料...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button @click="fetchTeachers" class="btn btn-outline-danger btn-sm">重新嘗試</button>
    </div>

    <!-- 空資料狀態 -->
    <div v-else-if="teachers.length === 0" class="text-center py-5 text-muted">
      <p>找不到符合條件的老師資料。</p>
    </div>

    <!-- 表格內容 -->
    <div v-else class="table-responsive">
      <table class="table table-hover table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col">姓名</th>
            <th scope="col">電子郵件</th>
            <th scope="col">電話</th>
            <th scope="col">時薪費率</th>
            <th scope="col">專長舞風</th>
            <th scope="col" class="text-center" style="width: 150px;">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="teacher in teachers" :key="teacher.id">
            <td class="fw-bold">{{ teacher.name }}</td>
            <td>{{ teacher.email || '-' }}</td>
            <td>{{ teacher.phone || '-' }}</td>
            <td>${{ teacher.hourly_rate }}</td>
            <td>
              <div v-if="teacher.styles && teacher.styles.length > 0" class="d-flex flex-wrap gap-1">
                <span v-for="style in teacher.styles" :key="style.id" class="badge bg-info text-dark">
                  {{ style.name }}
                </span>
              </div>
              <span v-else class="text-muted small">無專長舞風</span>
            </td>
            <td class="text-center">
              <button @click="openEdit(teacher.id)" class="btn btn-primary btn-sm me-1">編輯</button>
              <button @click="deleteTeacher(teacher.id)" class="btn btn-danger btn-sm">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bootstrap Modal for adding/editing teacher -->
    <div class="modal fade" id="editTeacherModal" tabindex="-1" aria-labelledby="editTeacherModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editTeacherModalLabel">{{ editingId ? '編輯老師' : '新增老師' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddTeacher
              v-if="showForm"
              :teacherId="editingId"
              @teacher-updated="handleTeacherUpdated"
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
import AddTeacher from '../forms/AddTeacher.vue';
import { useCrudModal } from '@/composables/useCrudModal';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';

export default {
  name: 'Teachers',
  components: {
    AddTeacher
  },
  setup() {
    const { showForm, editingId, initModal, openCreate, openEdit, closeModal } = useCrudModal('editTeacherModal');
    return { showForm, editingId, initModal, openCreate, openEdit, closeModal };
  },
  data() {
    return {
      teachers: [],
      searchQuery: '',
      loading: false,
      error: null
    };
  },
  mounted() {
    this.initModal();
  },
  created() {
    this.fetchTeachers();
  },
  methods: {
    async fetchTeachers() {
      this.loading = true;
      this.error = null;
      try {
        let endpoint = API_ENDPOINTS.TEACHERS;
        if (this.searchQuery.trim()) {
          endpoint += `?name=${encodeURIComponent(this.searchQuery.trim())}`;
        }
        const data = await api.get(endpoint);
        this.teachers = data.teachers || [];
      } catch (err) {
        console.error('獲取老師列表失敗:', err);
        this.error = '獲取老師列表失敗，請稍後再試。';
      } finally {
        this.loading = false;
      }
    },
    async deleteTeacher(id) {
      const confirmed = await showConfirm('確定要刪除這位老師嗎？');
      if (!confirmed) return;

      try {
        await api.delete(`${API_ENDPOINTS.TEACHERS}/${id}`);
        showToast('老師已成功刪除！', 'success');
        this.fetchTeachers();
      } catch (err) {
        console.error('刪除老師失敗:', err);
        showToast('刪除老師失敗，請重試。', 'error');
      }
    },
    handleTeacherUpdated() {
      this.fetchTeachers();
      this.closeModal();
    }
  }
};
</script>

<style scoped>
.teachers {
  padding: 10px;
}
</style>
