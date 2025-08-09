<template>
  <div class="styles">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>風格管理</h2>
      <button @click="addNewStyle" class="btn btn-success">新增風格</button>
    </div>
    <table class="style-table">
      <thead>
        <tr>
          <th>名稱</th>
          <th>描述</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="style in styles" :key="style.id">
          <td>{{ style.name }}</td>
          <td>{{ style.description }}</td>
          <td>
            <button @click="editStyle(style.id)" class="btn btn-primary btn-sm">編輯</button>
            <button @click="deleteStyle(style.id)" class="btn btn-danger btn-sm">移除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Bootstrap Modal for adding/editing style -->
    <div class="modal fade" id="editStyleModal" tabindex="-1" aria-labelledby="editStyleModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editStyleModalLabel">{{ editingStyleId ? '編輯風格' : '新增風格' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddStyle v-if="showEditModal" :styleId="editingStyleId" @style-updated="handleStyleUpdated" @close-modal="closeEditModal" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from '@/utils/api';
import AddStyle from '../forms/AddStyle.vue'; // 引入 AddStyle 組件
import { Modal } from 'bootstrap'; // 引入 Bootstrap Modal JS

export default {
  components: {
    AddStyle
  },
  data() {
    return {
      styles: [],
      showEditModal: false, // 控制 AddStyle 組件的渲染
      editingStyleId: null,
      editModal: null // 用於儲存 Bootstrap Modal 實例
    };
  },
  mounted() {
    // 在組件掛載後初始化 Bootstrap Modal
    this.editModal = new Modal(document.getElementById('editStyleModal'));
    // 監聽 modal 關閉事件，以便重置狀態
    document.getElementById('editStyleModal').addEventListener('hidden.bs.modal', () => {
      this.showEditModal = false;
      this.editingStyleId = null;
    });
  },
  created() {
    this.fetchStyles();
  },
  methods: {
    fetchStyles() {
      apiService.get('styles')
        .then(response => response.json())
        .then(data => {
          this.styles = data.styles;
        })
        .catch(error => {
          console.error('獲取風格列表失敗:', error);
        });
    },
    addNewStyle() {
      this.editingStyleId = null; // 設定為 null 表示新增模式
      this.showEditModal = true; // 渲染 AddStyle 組件
      this.editModal.show(); // 顯示 Bootstrap Modal
    },
    editStyle(id) {
      this.editingStyleId = id;
      this.showEditModal = true; // 渲染 AddStyle 組件
      this.editModal.show(); // 顯示 Bootstrap Modal
    },
    deleteStyle(id) {
      if (confirm('確定要刪除這個風格嗎？')) {
        apiService.delete(`styles/${id}`)
          .then(response => response.json())
          .then(() => {
            this.fetchStyles(); // Refresh the list after deletion
          })
          .catch(error => {
            console.error('刪除風格失敗:', error);
          });
      }
    },
    handleStyleUpdated() {
      this.fetchStyles(); // 風格數據更新後刷新列表
      this.editModal.hide(); // 關閉 Bootstrap Modal
    },
    closeEditModal() {
      // 由 AddStyle 組件發出，用於取消或錯誤時關閉 modal
      this.editModal.hide();
    }
  }
};
</script>

<style scoped>
.styles {
  padding: 20px;
}
.style-table {
  width: 100%;
  border-collapse: collapse;
}
.style-table th, .style-table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}
.style-table th {
  background-color: #f2f2f2;
}
.style-table button {
  margin-right: 5px;
}
</style>
