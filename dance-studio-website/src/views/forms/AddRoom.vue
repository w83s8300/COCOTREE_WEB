<template>
  <div class="add-room">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="name" class="form-label">教室名稱:</label>
        <input type="text" id="name" class="form-control" v-model="room.name" required>
      </div>
      <div class="form-group">
        <label for="capacity" class="form-label">容量:</label>
        <input type="number" id="capacity" class="form-control" v-model="room.capacity">
      </div>
      <div class="form-group">
        <label for="equipment" class="form-label">設備:</label>
        <textarea id="equipment" class="form-control" v-model="room.equipment"></textarea>
      </div>
      <div class="form-group">
        <label for="description" class="form-label">描述:</label>
        <textarea id="description" class="form-control" v-model="room.description"></textarea>
      </div>
      <div class="form-group">
        <label for="hourly_rate" class="form-label">時租費率:</label>
        <input type="number" id="hourly_rate" class="form-control" v-model="room.hourly_rate">
      </div>
      <div class="form-group">
        <div class="form-check">
          <input type="checkbox" id="is_available" class="form-check-input" v-model="room.is_available">
          <label for="is_available" class="form-check-label">是否可用</label>
        </div>
      </div>
      <button type="submit" class="btn btn-primary" :disabled="submitting">
        <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
        {{ isEditMode ? '更新' : '新增' }}
      </button>
      <button type="button" class="btn btn-secondary ms-2" @click="closeModal">取消</button>
    </form>
  </div>
</template>

<script>
import api, { API_ENDPOINTS } from '@/utils/api';
import { showToast } from '@/utils/toast';

export default {
  props: {
    roomId: {
      type: Number,
      default: null
    }
  },
  emits: ['room-updated', 'close-modal'],
  data() {
    return {
      room: {
        name: '',
        capacity: 20,
        equipment: '',
        description: '',
        hourly_rate: null,
        is_available: true
      },
      isEditMode: false,
      submitting: false
    };
  },
  watch: {
    roomId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.isEditMode = true;
          this.fetchRoom(newId);
        } else {
          this.isEditMode = false;
          this.resetForm();
        }
      }
    }
  },
  methods: {
    resetForm() {
      this.room = {
        name: '',
        capacity: 20,
        equipment: '',
        description: '',
        hourly_rate: null,
        is_available: true
      };
    },
    fetchRoom(id) {
      api.get(`${API_ENDPOINTS.ROOMS}/${id}`)
        .then(data => {
          this.room = data.room;
        })
        .catch(error => {
          console.error('獲取教室資料失敗:', error);
        });
    },
    submitForm() {
      if (this.isEditMode) {
        this.updateRoom();
      } else {
        this.addRoom();
      }
    },
    addRoom() {
      this.submitting = true;
      api.post(API_ENDPOINTS.ROOMS, this.room)
        .then(() => {
          showToast('教室新增成功！', 'success');
          this.$emit('room-updated');
        })
        .catch(error => {
          console.error(error);
          showToast('新增教室失敗！', 'error');
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    updateRoom() {
      this.submitting = true;
      api.put(`${API_ENDPOINTS.ROOMS}/${this.room.id}`, this.room)
        .then(() => {
          showToast('教室更新成功！', 'success');
          this.$emit('room-updated');
        })
        .catch(error => {
          console.error(error);
          showToast('更新教室失敗！', 'error');
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    closeModal() {
      this.$emit('close-modal');
    }
  }
};
</script>

<style scoped>
.add-room {
  padding: 20px;
}
.form-group {
  margin-bottom: 15px;
}
</style>
