<template>
  <div class="teachers">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>老師列表</h2>
      <div class="d-flex">
        <input type="text" v-model="searchQuery" placeholder="搜尋老師姓名" class="form-control me-2">
        <button @click="fetchTeachers" class="btn btn-outline-secondary">搜尋</button>
        <button @click="addNewTeacher" class="btn btn-success ms-2">新增老師</button>
      </div>
    </div>
    <table class="teacher-table">
      <thead>
        <tr>
          <th>姓名</th>
          <th>電子郵件</th>
          <th>電話</th>
          <th>時薪</th>
          <th>專長風格</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="teacher in teachers" :key="teacher.id">
          <td>{{ teacher.name }}</td>
          <td>{{ teacher.email }}</td>
          <td>{{ teacher.phone }}</td>
          <td>{{ teacher.hourly_rate }}</td>
          <td>
            <ul>
              <li v-for="style in teacher.styles" :key="style.id">{{ style.name }}</li>
            </ul>
          </td>
          <td>
            <button @click="editTeacher(teacher.id)" class="btn btn-primary btn-sm">編輯</button>
            <button @click="deleteTeacher(teacher.id)" class="btn btn-danger btn-sm">移除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Bootstrap Modal for adding/editing teacher -->
    <div class="modal fade" id="editTeacherModal" tabindex="-1" aria-labelledby="editTeacherModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editTeacherModalLabel">{{ editingTeacherId ? '編輯老師' : '新增老師' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddTeacher v-if="showEditModal" :teacherId="editingTeacherId" @teacher-updated="handleTeacherUpdated" @close-modal="closeEditModal" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '@/utils/api';
import AddTeacher from '../forms/AddTeacher.vue'; // 引入 AddTeacher 組件
import { Modal } from 'bootstrap'; // 引入 Bootstrap Modal JS

export default {
  components: {
    AddTeacher
  },
  data() {
    return {
      teachers: [],
      searchQuery: '',
      showEditModal: false, // 控制 AddTeacher 組件的渲染
      editingTeacherId: null,
      editModal: null // 用於儲存 Bootstrap Modal 實例
    };
  },
  mounted() {
    // 在組件掛載後初始化 Bootstrap Modal
    this.editModal = new Modal(document.getElementById('editTeacherModal'));
    // 監聽 modal 關閉事件，以便重置狀態
    document.getElementById('editTeacherModal').addEventListener('hidden.bs.modal', () => {
      this.showEditModal = false;
      this.editingTeacherId = null;
    });
  },
  created() {
    this.fetchTeachers();
  },
  methods: {
    fetchTeachers() {
      let endpoint = 'teachers';
      if (this.searchQuery) {
        endpoint += `?name=${this.searchQuery}`;
      }
      apiService.get(endpoint)
        .then(response => response.json())
        .then(data => {
          this.teachers = data.teachers;
        })
        .catch(error => {
          console.error('獲取老師列表失敗:', error);
        });
    },
    addNewTeacher() {
      this.editingTeacherId = null; // 設定為 null 表示新增模式
      this.showEditModal = true; // 渲染 AddTeacher 組件
      this.editModal.show(); // 顯示 Bootstrap Modal
    },
    editTeacher(id) {
      this.editingTeacherId = id;
      this.showEditModal = true; // 渲染 AddTeacher 組件
      this.editModal.show(); // 顯示 Bootstrap Modal
    },
    deleteTeacher(id) {
      if (confirm('確定要刪除這位老師嗎？')) {
        apiService.delete(`teachers/${id}`)
          .then(response => response.json())
          .then(() => {
            this.fetchTeachers(); // Refresh the list after deletion
          })
          .catch(error => {
            console.error('刪除老師失敗:', error);
          });
      }
    },
    handleTeacherUpdated() {
      this.fetchTeachers(); // 老師數據更新後刷新列表
      this.editModal.hide(); // 關閉 Bootstrap Modal
    },
    closeEditModal() {
      // 由 AddTeacher 組件發出，用於取消或錯誤時關閉 modal
      this.editModal.hide();
    }
  }
};
</script>

<style scoped>
.teachers {
  padding: 20px;
}
.teacher-table {
  width: 100%;
  border-collapse: collapse;
}
.teacher-table th, .teacher-table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}
.teacher-table th {
  background-color: #f2f2f2;
}
.teacher-table button {
  margin-right: 5px;
}
.teacher-table ul {
  padding-left: 20px;
  margin-bottom: 0;
}
</style>
