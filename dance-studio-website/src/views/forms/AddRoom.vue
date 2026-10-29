<template>
  <div class="add-room">
    <form @submit.prevent="submitForm">
      <!-- 教室環境照片 -->
      <div class="form-group mb-4 text-center">
        <label class="form-label fw-semibold d-block">教室環境照片:</label>
        <div class="d-flex flex-column align-items-center">
          <div 
            class="room-photo-preview position-relative rounded-3 shadow-sm border mb-2 overflow-hidden bg-light"
            style="width: 240px; height: 140px; cursor: pointer;"
            @click="$refs.roomFileInput.click()"
            title="點擊選擇圖片"
          >
            <img 
              v-if="room.image_url" 
              :src="room.image_url" 
              alt="教室環境照片" 
              class="w-100 h-100 object-fit-cover"
            />
            <div v-else class="w-100 h-100 d-flex flex-column align-items-center justify-content-center text-secondary">
              <i class="bi bi-camera fs-1 text-muted"></i>
              <span class="small text-muted mt-1">點擊上傳環境照片</span>
            </div>
          </div>
          <input 
            type="file" 
            ref="roomFileInput" 
            class="d-none" 
            accept="image/png, image/jpeg, image/jpg, image/webp, image/gif" 
            @change="handleImageFileSelected" 
          />
          <div class="d-flex gap-2">
            <button 
              type="button" 
              class="btn btn-outline-primary btn-sm" 
              @click="$refs.roomFileInput.click()" 
              :disabled="uploadingImage"
            >
              <span v-if="uploadingImage" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-upload me-1"></i>{{ room.image_url ? '更換照片' : '選擇照片' }}
            </button>
            <button 
              type="button" 
              v-if="room.image_url" 
              class="btn btn-outline-danger btn-sm" 
              @click="room.image_url = ''"
              :disabled="uploadingImage"
            >
              <i class="bi bi-trash3 me-1"></i>移除照片
            </button>
          </div>
          <div class="form-text small mt-1">支援 JPG, PNG, WEBP 等圖片格式，將同步展示於官網「關於我們」環境介紹</div>
        </div>
      </div>

      <div class="form-group mb-3">
        <label for="name" class="form-label fw-bold">教室名稱 <span class="text-danger">*</span>:</label>
        <input type="text" id="name" class="form-control" v-model="room.name" placeholder="例如：Studio A、A 教室" required>
      </div>
      <div class="form-group mb-3">
        <label for="capacity" class="form-label">容納人數 (人):</label>
        <input type="number" id="capacity" class="form-control" v-model="room.capacity" min="1" placeholder="例如：20">
      </div>
      <div class="form-group mb-3">
        <label for="equipment" class="form-label">設備規格 (多項可用逗號或換行分隔):</label>
        <textarea id="equipment" class="form-control" v-model="room.equipment" rows="2" placeholder="例如：專業音響, 落地大鏡, 芭蕾把杆, 獨立冷暖空調"></textarea>
      </div>
      <div class="form-group mb-3">
        <label for="description" class="form-label">描述介紹:</label>
        <textarea id="description" class="form-control" v-model="room.description" rows="3" placeholder="例如：寬敞明亮的空間，適合大型團體課程與排練。"></textarea>
      </div>
      <div class="form-group mb-3">
        <label for="hourly_rate" class="form-label">時租費率 (NT$/小時):</label>
        <input type="number" id="hourly_rate" class="form-control" v-model="room.hourly_rate" placeholder="例如：500">
      </div>
      <div class="form-group mb-4">
        <div class="form-check">
          <input type="checkbox" id="is_available" class="form-check-input" v-model="room.is_available">
          <label for="is_available" class="form-check-label fw-bold">是否開放可用</label>
        </div>
      </div>
      <div class="d-flex justify-content-end gap-2">
        <button type="button" class="btn btn-secondary" @click="closeModal">取消</button>
        <button type="submit" class="btn btn-primary px-4" :disabled="submitting || uploadingImage">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
          {{ isEditMode ? '更新教室' : '新增教室' }}
        </button>
      </div>
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
        image_url: '',
        hourly_rate: null,
        is_available: true
      },
      isEditMode: false,
      submitting: false,
      uploadingImage: false
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
        image_url: '',
        hourly_rate: null,
        is_available: true
      };
    },
    fetchRoom(id) {
      api.get(`${API_ENDPOINTS.ROOMS}/${id}`)
        .then(data => {
          this.room = {
            ...data.room,
            is_available: Boolean(data.room.is_available)
          };
        })
        .catch(error => {
          console.error('獲取教室資料失敗:', error);
          showToast('獲取教室資料失敗', 'error');
        });
    },
    async handleImageFileSelected(e) {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!file.type.startsWith('image/')) {
        showToast('請選取有效的圖片檔案 (JPG, PNG, WEBP, GIF)！', 'error');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        showToast('圖片大小不得超過 10MB！', 'error');
        return;
      }
      this.uploadingImage = true;
      try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await api.post('/upload/room-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        if (res.image_url) {
          this.room.image_url = res.image_url;
          showToast('教室圖片上傳成功！', 'success');
        }
      } catch (err) {
        showToast(err.message || '圖片上傳失敗，請重試', 'error');
      } finally {
        this.uploadingImage = false;
        if (e.target) e.target.value = '';
      }
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
          showToast(error.message || '新增教室失敗！', 'error');
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
          showToast(error.message || '更新教室失敗！', 'error');
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
  padding: 10px;
}
.room-photo-preview {
  transition: opacity 0.2s;
}
.room-photo-preview:hover {
  opacity: 0.9;
}
</style>
