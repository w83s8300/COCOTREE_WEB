<template>
  <div class="students">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>學生列表</h2>
      <div class="d-flex">
        <input type="text" v-model="searchQuery" placeholder="搜尋學生姓名" class="form-control me-2">
        <button @click="fetchStudents" class="btn btn-outline-secondary">搜尋</button>
        <button @click="addNewStudent" class="btn btn-success ms-2">新增學生</button>
      </div>
    </div>
    <table class="student-table">
      <thead>
        <tr>
          <th>姓名</th>
          <th>電子郵件</th>
          <th>電話</th>
          <th>出生年月日</th>
          <th>剩餘堂數</th>
          <th>會員到期日</th>
          <th>緊急聯絡人</th>
          <th>緊急聯絡人電話</th>
          <th>醫療備註</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in students" :key="student.id">
          <td>{{ student.name }}</td>
          <td>{{ student.email }}</td>
          <td>{{ student.phone }}</td>
          <td>{{ formatDate(student.date_of_birth) }}</td>
          <td>{{ student.remaining_classes || 0 }}</td>
          <td>{{ formatDate(student.membership_expiry) }}</td>
          <td>{{ student.emergency_contact }}</td>
          <td>{{ student.emergency_phone }}</td>
          <td>{{ student.medical_notes }}</td>
          <td>
            <button @click="editStudent(student.id)" class="btn btn-primary btn-sm">編輯</button>
            <button @click="deleteStudent(student.id)" class="btn btn-danger btn-sm">移除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Bootstrap Modal for adding/editing student -->
    <div class="modal fade" id="editStudentModal" tabindex="-1" aria-labelledby="editStudentModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editStudentModalLabel">{{ editingStudentId ? '編輯學生' : '新增學生' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddStudent v-if="showEditModal" :studentId="editingStudentId" @student-updated="handleStudentUpdated" @close-modal="closeEditModal" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '@/utils/api';
import AddStudent from '../forms/AddStudent.vue'; // 更新導入路徑
import { Modal } from 'bootstrap'; // 引入 Bootstrap Modal JS

export default {
  components: {
    AddStudent
  },
  data() {
    return {
      students: [],
      searchQuery: '',
      showEditModal: false, // 控制 AddStudent 組件的渲染
      editingStudentId: null,
      editModal: null // 用於儲存 Bootstrap Modal 實例
    };
  },
  mounted() {
    // 在組件掛載後初始化 Bootstrap Modal
    this.editModal = new Modal(document.getElementById('editStudentModal'));
    // 監聽 modal 關閉事件，以便重置狀態
    document.getElementById('editStudentModal').addEventListener('hidden.bs.modal', () => {
      this.showEditModal = false;
      this.editingStudentId = null;
    });
  },
  created() {
    this.fetchStudents();
  },
  methods: {
    fetchStudents() {
      let endpoint = 'students';
      if (this.searchQuery) {
        endpoint += `?name=${this.searchQuery}`;
      }
      apiService.get(endpoint)
        .then(response => response.json())
        .then(data => {
          this.students = data.students;
        })
        .catch(error => {
          console.error('獲取學生列表失敗:', error);
        });
    },
    formatDate(dateString) {
      if (!dateString) return '未設定';
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-TW');
    },
    addNewStudent() {
      this.editingStudentId = null; // 設定為 null 表示新增模式
      this.showEditModal = true; // 渲染 AddStudent 組件
      this.editModal.show(); // 顯示 Bootstrap Modal
    },
    editStudent(id) {
      this.editingStudentId = id;
      this.showEditModal = true; // 渲染 AddStudent 組件
      this.editModal.show(); // 顯示 Bootstrap Modal
    },
    deleteStudent(id) {
      if (confirm('確定要刪除這位學生嗎？')) {
        apiService.delete(`students/${id}`)
          .then(response => response.json())
          .then(() => {
            this.fetchStudents(); // Refresh the list after deletion
          })
          .catch(error => {
            console.error('刪除學生失敗:', error);
          });
      }
    },
    handleStudentUpdated() {
      this.fetchStudents(); // 學生數據更新後刷新列表
      this.editModal.hide(); // 關閉 Bootstrap Modal
    },
    closeEditModal() {
      // 由 AddStudent 組件發出，用於取消或錯誤時關閉 modal
      this.editModal.hide();
    }
  }
};
</script>

<style scoped>
.students {
  padding: 20px;
}
.student-table {
  width: 100%;
  border-collapse: collapse;
}
.student-table th, .student-table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}
.student-table th {
  background-color: #f2f2f2;
}
.student-table button {
  margin-right: 5px;
}
</style>
