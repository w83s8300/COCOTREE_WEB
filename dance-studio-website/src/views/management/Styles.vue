<template>
  <div class="styles">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>舞風管理</h2>
      <button @click="openCreate" class="btn btn-success">
        <i class="bi bi-plus-lg me-1"></i>新增舞風
      </button>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入舞風資料...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button @click="fetchStyles" class="btn btn-outline-danger btn-sm">重新嘗試</button>
    </div>

    <!-- 空資料狀態 -->
    <div v-else-if="styles.length === 0" class="text-center py-5 text-muted">
      <p>目前尚無舞風資料，請點擊上方按鈕新增。</p>
    </div>

    <!-- 表格內容 -->
    <div v-else class="table-responsive">
      <table class="table table-hover table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col" style="width: 250px;">名稱</th>
            <th scope="col">描述</th>
            <th scope="col" class="text-center" style="width: 150px;">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="style in styles" :key="style.id">
            <td class="fw-bold">{{ style.name }}</td>
            <td>{{ style.description || '暫無描述' }}</td>
            <td class="text-center">
              <button @click="openEdit(style.id)" class="btn btn-primary btn-sm me-1">編輯</button>
              <button @click="deleteStyle(style.id)" class="btn btn-danger btn-sm">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bootstrap Modal for adding/editing style -->
    <div class="modal fade" id="editStyleModal" tabindex="-1" aria-labelledby="editStyleModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editStyleModalLabel">{{ editingId ? '編輯風格' : '新增風格' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddStyle
              v-if="showForm"
              :styleId="editingId"
              @style-updated="handleStyleUpdated"
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
import AddStyle from '../forms/AddStyle.vue';
import { useCrudModal } from '@/composables/useCrudModal';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';

export default {
  name: 'Styles',
  components: {
    AddStyle
  },
  setup() {
    const { showForm, editingId, initModal, openCreate, openEdit, closeModal } = useCrudModal('editStyleModal');
    return { showForm, editingId, initModal, openCreate, openEdit, closeModal };
  },
  data() {
    return {
      styles: [],
      loading: false,
      error: null
    };
  },
  mounted() {
    this.initModal();
  },
  created() {
    this.fetchStyles();
  },
  methods: {
    async fetchStyles() {
      this.loading = true;
      this.error = null;
      try {
        const data = await api.get(API_ENDPOINTS.STYLES);
        this.styles = data.styles || [];
      } catch (err) {
        console.error('獲取舞風列表失敗:', err);
        this.error = '獲取舞風列表失敗，請稍後再試。';
      } finally {
        this.loading = false;
      }
    },
    async deleteStyle(id) {
      const confirmed = await showConfirm('確定要刪除這個舞風嗎？此操作可能會影響關聯的課程與老師。');
      if (!confirmed) return;

      try {
        await api.delete(`${API_ENDPOINTS.STYLES}/${id}`);
        showToast('風格已成功刪除！', 'success');
        this.fetchStyles();
      } catch (err) {
        console.error('刪除風格失敗:', err);
        showToast('刪除風格失敗，請重試。', 'error');
      }
    },
    handleStyleUpdated() {
      this.fetchStyles();
      this.closeModal();
    }
  }
};
</script>

<style scoped>
.styles {
  padding: 10px;
}
</style>
