<template>
  <div class="courses">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>課程列表</h2>
      <button @click="addNewCourse" class="btn btn-success">新增課程</button>
    </div>
    <table class="course-table">
      <thead>
        <tr>
          <th>課程名稱</th>
          <th>難度</th>
          <th>風格</th>
          <th>時長</th>
          <th>人數上限</th>
          <th>扣堂數</th>
          <th>老師</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="course in courses" :key="course.id">
          <td>{{ course.name }}</td>
          <td>{{ course.level }}</td>
          <td>{{ course.style_name }}</td>
          <td>{{ course.duration_minutes }} 分鐘</td>
          <td>{{ course.max_students }}</td>
          <td>{{ course.price }} 堂</td>
          <td>{{ course.teacher_name }}</td>
          <td>
            <button @click="editCourse(course.id)" class="btn btn-primary btn-sm">編輯</button>
            <button @click="deleteCourse(course.id)" class="btn btn-danger btn-sm">移除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Bootstrap Modal for adding/editing course -->
    <div class="modal fade" id="editCourseModal" tabindex="-1" aria-labelledby="editCourseModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editCourseModalLabel">{{ editingCourseId ? '編輯課程' : '新增課程' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddCourse v-if="showEditModal" :courseId="editingCourseId" @course-updated="handleCourseUpdated" @close-modal="closeEditModal" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '@/utils/api';
import AddCourse from '../forms/AddCourse.vue'; // 引入 AddCourse 組件
import { Modal } from 'bootstrap'; // 引入 Bootstrap Modal JS

export default {
  components: {
    AddCourse
  },
  data() {
    return {
      courses: [],
      showEditModal: false, // 控制 AddCourse 組件的渲染
      editingCourseId: null,
      editModal: null // 用於儲存 Bootstrap Modal 實例
    };
  },
  mounted() {
    // 在組件掛載後初始化 Bootstrap Modal
    this.editModal = new Modal(document.getElementById('editCourseModal'));
    // 監聽 modal 關閉事件，以便重置狀態
    document.getElementById('editCourseModal').addEventListener('hidden.bs.modal', () => {
      this.showEditModal = false;
      this.editingCourseId = null;
    });
  },
  created() {
    this.fetchCourses();
  },
  methods: {
    fetchCourses() {
      apiService.get('courses')
        .then(response => response.json())
        .then(data => {
          this.courses = data.courses;
        })
        .catch(error => {
          console.error('獲取課程列表失敗:', error);
        });
    },
    addNewCourse() {
      this.editingCourseId = null; // 設定為 null 表示新增模式
      this.showEditModal = true; // 渲染 AddCourse 組件
      this.editModal.show(); // 顯示 Bootstrap Modal
    },
    editCourse(id) {
      this.editingCourseId = id;
      this.showEditModal = true; // 渲染 AddCourse 組件
      this.editModal.show(); // 顯示 Bootstrap Modal
    },
    deleteCourse(id) {
      if (confirm('確定要刪除這個課程嗎？')) {
        apiService.delete(`courses/${id}`)
          .then(response => response.json())
          .then(() => {
            this.fetchCourses(); // Refresh the list after deletion
          })
          .catch(error => {
            console.error('刪除課程失敗:', error);
          });
      }
    },
    handleCourseUpdated() {
      this.fetchCourses(); // 課程數據更新後刷新列表
      this.editModal.hide(); // 關閉 Bootstrap Modal
    },
    closeEditModal() {
      // 由 AddCourse 組件發出，用於取消或錯誤時關閉 modal
      this.editModal.hide();
    }
  }
};
</script>

<style scoped>
.courses {
  padding: 20px;
}
.course-table {
  width: 100%;
  border-collapse: collapse;
}
.course-table th, .course-table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}
.course-table th {
  background-color: #f2f2f2;
}
.course-table button {
  margin-right: 5px;
}
</style>
