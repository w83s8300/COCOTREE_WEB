<template>
  <div class="rooms">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>教室列表</h2>
      <button @click="addNewRoom" class="btn btn-success">新增教室</button>
    </div>
    <table class="room-table">
      <thead>
        <tr>
          <th>名稱</th>
          <th>容量</th>
          <th>設備</th>
          <th>描述</th>
          <th>時租費率</th>
          <th>狀態</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="room in rooms" :key="room.id">
          <td>{{ room.name }}</td>
          <td>{{ room.capacity }}</td>
          <td>{{ room.equipment }}</td>
          <td>{{ room.description }}</td>
          <td>{{ room.hourly_rate }}</td>
          <td>{{ room.is_available ? '可用' : '不可用' }}</td>
          <td>
            <button @click="editRoom(room.id)" class="btn btn-primary btn-sm">編輯</button>
            <button @click="deleteRoom(room.id)" class="btn btn-danger btn-sm">移除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Bootstrap Modal for adding/editing room -->
    <div class="modal fade" id="editRoomModal" tabindex="-1" aria-labelledby="editRoomModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editRoomModalLabel">{{ editingRoomId ? '編輯教室' : '新增教室' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddRoom v-if="showEditModal" :roomId="editingRoomId" @room-updated="handleRoomUpdated" @close-modal="closeEditModal" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import AddRoom from './AddRoom.vue'; // 引入 AddRoom 組件
import { Modal } from 'bootstrap'; // 引入 Bootstrap Modal JS
import { API_ENDPOINTS, buildApiUrl } from '@/utils/api.js';

export default {
  components: {
    AddRoom
  },
  data() {
    return {
      rooms: [],
      showEditModal: false, // 控制 AddRoom 組件的渲染
      editingRoomId: null,
      editModal: null // 用於儲存 Bootstrap Modal 實例
    };
  },
  mounted() {
    // 在組件掛載後初始化 Bootstrap Modal
    this.editModal = new Modal(document.getElementById('editRoomModal'));
    // 監聽 modal 關閉事件，以便重置狀態
    document.getElementById('editRoomModal').addEventListener('hidden.bs.modal', () => {
      this.showEditModal = false;
      this.editingRoomId = null;
    });
  },
  created() {
    this.fetchRooms();
  },
  methods: {
    fetchRooms() {
      axios.get(API_ENDPOINTS.ROOMS)
        .then(response => {
          this.rooms = response.data.rooms;
        })
        .catch(error => {
          console.error('獲取教室列表失敗:', error);
        });
    },
    addNewRoom() {
      this.editingRoomId = null; // 設定為 null 表示新增模式
      this.showEditModal = true; // 渲染 AddRoom 組件
      this.editModal.show(); // 顯示 Bootstrap Modal
    },
    editRoom(id) {
      this.editingRoomId = id;
      this.showEditModal = true; // 渲染 AddRoom 組件
      this.editModal.show(); // 顯示 Bootstrap Modal
    },
    deleteRoom(id) {
      if (confirm('確定要刪除這間教室嗎？')) {
        axios.delete(`${API_ENDPOINTS.ROOMS}/${id}`)
          .then(() => {
            this.fetchRooms(); // Refresh the list after deletion
          })
          .catch(error => {
            console.error('刪除教室失敗:', error);
          });
      }
    },
    handleRoomUpdated() {
      this.fetchRooms(); // 教室數據更新後刷新列表
      this.editModal.hide(); // 關閉 Bootstrap Modal
    },
    closeEditModal() {
      // 由 AddRoom 組件發出，用於取消或錯誤時關閉 modal
      this.editModal.hide();
    }
  }
};
</script>

<style scoped>
.rooms {
  padding: 20px;
}
.room-table {
  width: 100%;
  border-collapse: collapse;
}
.room-table th, .room-table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}
.room-table th {
  background-color: #f2f2f2;
}
.room-table button {
  margin-right: 5px;
}
</style>
