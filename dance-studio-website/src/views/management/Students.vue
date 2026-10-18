<template>
  <div class="students">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>學生列表</h2>
      <div class="d-flex">
        <input
          type="text"
          v-model="searchQuery"
          @keyup.enter="fetchStudents"
          placeholder="搜尋學生姓名"
          class="form-control me-2"
        />
        <button @click="fetchStudents" class="btn btn-outline-secondary text-nowrap">
          <i class="bi bi-search me-1"></i>搜尋
        </button>
        <button @click="openCreate" class="btn btn-success ms-2 text-nowrap">
          <i class="bi bi-plus-lg me-1"></i>新增學生
        </button>
      </div>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入學生資料...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button @click="fetchStudents" class="btn btn-outline-danger btn-sm">重新嘗試</button>
    </div>

    <!-- 空資料狀態 -->
    <div v-else-if="students.length === 0" class="text-center py-5 text-muted">
      <p>找不到符合條件的學生資料。</p>
    </div>

    <!-- 表格內容 -->
    <div v-else class="table-responsive">
      <table class="table table-hover table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col">姓名</th>
            <th scope="col">電子郵件</th>
            <th scope="col">電話</th>
            <th scope="col">出生年月日</th>
            <th scope="col">剩餘堂數</th>
            <th scope="col">會員到期日</th>
            <th scope="col">緊急聯絡人</th>
            <th scope="col">緊急聯絡電話</th>
            <th scope="col">醫療備註</th>
            <th scope="col" class="text-center" style="width: 150px;">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in students" :key="student.id">
            <td class="fw-bold">{{ student.name }}</td>
            <td>{{ student.email || '-' }}</td>
            <td>{{ student.phone || '-' }}</td>
            <td>{{ formatDate(student.date_of_birth) }}</td>
            <td>
              <span class="badge" :class="student.remaining_classes > 0 ? 'bg-success' : 'bg-warning text-dark'">
                {{ student.remaining_classes || 0 }} 堂
              </span>
            </td>
            <td>{{ formatDate(student.membership_expiry) }}</td>
            <td>{{ student.emergency_contact || '-' }}</td>
            <td>{{ student.emergency_phone || '-' }}</td>
            <td>{{ student.medical_notes || '無' }}</td>
            <td class="text-center">
              <button @click="openEdit(student.id)" class="btn btn-primary btn-sm me-1">編輯</button>
              <button @click="deleteStudent(student.id)" class="btn btn-danger btn-sm">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bootstrap Modal for adding/editing student -->
    <div class="modal fade" id="editStudentModal" tabindex="-1" aria-labelledby="editStudentModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editStudentModalLabel">{{ editingId ? '編輯學生' : '新增學生' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddStudent
              v-if="showForm"
              :studentId="editingId"
              @student-updated="handleStudentUpdated"
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
import AddStudent from '../forms/AddStudent.vue';
import { useCrudModal } from '@/composables/useCrudModal';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';

export default {
  name: 'Students',
  components: {
    AddStudent
  },
  setup() {
    const { showForm, editingId, initModal, openCreate, openEdit, closeModal } = useCrudModal('editStudentModal');
    return { showForm, editingId, initModal, openCreate, openEdit, closeModal };
  },
  data() {
    return {
      students: [],
      searchQuery: '',
      loading: false,
      error: null
    };
  },
  mounted() {
    this.initModal();
  },
  created() {
    this.fetchStudents();
  },
  methods: {
    async fetchStudents() {
      this.loading = true;
      this.error = null;
      try {
        let endpoint = API_ENDPOINTS.STUDENTS;
        if (this.searchQuery.trim()) {
          endpoint += `?name=${encodeURIComponent(this.searchQuery.trim())}`;
        }
        const data = await api.get(endpoint);
        this.students = data.students || [];
      } catch (err) {
        console.error('獲取學生列表失敗:', err);
        this.error = '獲取學生列表失敗，請稍後再試。';
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString || dateString === '1911-01-01' || dateString === '0000-00-00') return '未設定';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '未設定';
      return date.toLocaleDateString('zh-TW');
    },
    async deleteStudent(id) {
      const confirmed = await showConfirm('確定要刪除這位學生嗎？此動作將移除該學生的所有修課紀錄。');
      if (!confirmed) return;

      try {
        await api.delete(`${API_ENDPOINTS.STUDENTS}/${id}`);
        showToast('學生已成功刪除！', 'success');
        this.fetchStudents();
      } catch (err) {
        console.error('刪除學生失敗:', err);
        showToast('刪除學生失敗，請重試。', 'error');
      }
    },
    handleStudentUpdated() {
      this.fetchStudents();
      this.closeModal();
    }
  }
};
</script>

<style scoped>
.students {
  padding: 10px;
}
</style>
