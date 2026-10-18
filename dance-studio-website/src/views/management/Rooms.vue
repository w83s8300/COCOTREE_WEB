<template>
  <div class="rooms">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>教室列表</h2>
      <button @click="openCreate" class="btn btn-success">
        <i class="bi bi-plus-lg me-1"></i>新增教室
      </button>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入教室資料...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button @click="fetchRooms" class="btn btn-outline-danger btn-sm">重新嘗試</button>
    </div>

    <!-- 空資料狀態 -->
    <div v-else-if="rooms.length === 0" class="text-center py-5 text-muted">
      <p>目前尚無教室資料，請點擊上方按鈕新增。</p>
    </div>

    <!-- 表格內容 -->
    <div v-else class="table-responsive">
      <table class="table table-hover table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col">名稱</th>
            <th scope="col">容納人數</th>
            <th scope="col">設備</th>
            <th scope="col">描述</th>
            <th scope="col">時租費率</th>
            <th scope="col">狀態</th>
            <th scope="col" class="text-center" style="width: 150px;">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="room in rooms" :key="room.id">
            <td class="fw-bold">{{ room.name }}</td>
            <td>{{ room.capacity }} 人</td>
            <td>{{ room.equipment || '無特殊設備' }}</td>
            <td>{{ room.description || '-' }}</td>
            <td>${{ room.hourly_rate }}/hr</td>
            <td>
              <span class="badge" :class="room.is_available ? 'bg-success' : 'bg-secondary'">
                {{ room.is_available ? '可用' : '維護中 / 不可用' }}
              </span>
            </td>
            <td class="text-center">
              <button @click="openEdit(room.id)" class="btn btn-primary btn-sm me-1">編輯</button>
              <button @click="deleteRoom(room.id)" class="btn btn-danger btn-sm">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bootstrap Modal for adding/editing room -->
    <div class="modal fade" id="editRoomModal" tabindex="-1" aria-labelledby="editRoomModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editRoomModalLabel">{{ editingId ? '編輯教室' : '新增教室' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddRoom
              v-if="showForm"
              :roomId="editingId"
              @room-updated="handleRoomUpdated"
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
import AddRoom from '../forms/AddRoom.vue';
import { useCrudModal } from '@/composables/useCrudModal';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';

export default {
  name: 'Rooms',
  components: {
    AddRoom
  },
  setup() {
    const { showForm, editingId, initModal, openCreate, openEdit, closeModal } = useCrudModal('editRoomModal');
    return { showForm, editingId, initModal, openCreate, openEdit, closeModal };
  },
  data() {
    return {
      rooms: [],
      loading: false,
      error: null
    };
  },
  mounted() {
    this.initModal();
  },
  created() {
    this.fetchRooms();
  },
  methods: {
    async fetchRooms() {
      this.loading = true;
      this.error = null;
      try {
        const data = await api.get(API_ENDPOINTS.ROOMS);
        this.rooms = data.rooms || [];
      } catch (err) {
        console.error('獲取教室列表失敗:', err);
        this.error = '獲取教室列表失敗，請稍後再試。';
      } finally {
        this.loading = false;
      }
    },
    async deleteRoom(id) {
      const confirmed = await showConfirm('確定要刪除這間教室嗎？');
      if (!confirmed) return;

      try {
        await api.delete(`${API_ENDPOINTS.ROOMS}/${id}`);
        showToast('教室已成功刪除！', 'success');
        this.fetchRooms();
      } catch (err) {
        console.error('刪除教室失敗:', err);
        showToast('刪除教室失敗，請重試。', 'error');
      }
    },
    handleRoomUpdated() {
      this.fetchRooms();
      this.closeModal();
    }
  }
};
</script>

<style scoped>
.rooms {
  padding: 10px;
}
</style>
