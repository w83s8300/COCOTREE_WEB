<template>
  <div class="add-teacher">
    <form @submit.prevent="submitForm">
      <!-- 大頭貼照片 -->
      <div class="form-group mb-4 text-center">
        <label class="form-label fw-semibold d-block">老師大頭貼照片:</label>
        <div class="d-flex flex-column align-items-center">
          <div 
            class="avatar-picker-preview position-relative rounded-circle shadow-sm border mb-2 overflow-hidden bg-light"
            style="width: 100px; height: 100px; cursor: pointer;"
            @click="$refs.teacherFileInput.click()"
            title="點擊選擇圖片"
          >
            <img 
              v-if="teacher.avatar_url" 
              :src="teacher.avatar_url" 
              alt="老師大頭貼" 
              class="w-100 h-100 object-fit-cover"
            />
            <div v-else class="w-100 h-100 d-flex flex-column align-items-center justify-content-center text-secondary">
              <i class="bi bi-camera fs-2 text-muted"></i>
              <span class="small text-muted" style="font-size: 11px;">上傳照片</span>
            </div>
          </div>
          <input 
            type="file" 
            ref="teacherFileInput" 
            class="d-none" 
            accept="image/png, image/jpeg, image/jpg, image/webp, image/gif" 
            @change="handleAvatarFileSelected" 
          />
          <div class="d-flex gap-2">
            <button 
              type="button" 
              class="btn btn-outline-primary btn-sm" 
              @click="$refs.teacherFileInput.click()" 
              :disabled="uploadingAvatar"
            >
              <span v-if="uploadingAvatar" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-upload me-1"></i>{{ teacher.avatar_url ? '更換照片' : '選擇照片' }}
            </button>
            <button 
              type="button" 
              v-if="teacher.avatar_url" 
              class="btn btn-outline-danger btn-sm" 
              @click="teacher.avatar_url = ''"
              :disabled="uploadingAvatar"
            >
              <i class="bi bi-trash3 me-1"></i>移除
            </button>
          </div>
          <div class="form-text small mt-1">支援 JPG, PNG, WEBP 圖片格式</div>
        </div>
      </div>

      <div class="form-group">
        <label for="name" class="form-label">姓名:</label>
        <input type="text" id="name" class="form-control" v-model="teacher.name" required>
      </div>
      <div class="form-group">
        <label for="email" class="form-label">電子郵件:</label>
        <input type="email" id="email" class="form-control" v-model="teacher.email">
      </div>
      <div class="form-group">
        <label for="phone" class="form-label">電話:</label>
        <input type="tel" id="phone" class="form-control" v-model="teacher.phone">
      </div>
      <div class="form-group mb-3">
        <label for="bank_account" class="form-label fw-semibold">銀行帳號 (匯款資訊):</label>
        <input 
          type="text" 
          id="bank_account" 
          class="form-control" 
          v-model="teacher.bank_account" 
          placeholder="例如: (822 中國信託) 123-540-123456"
        >
        <div class="form-text">用於師資授課鐘點費匯款之金融機構代號與帳號</div>
      </div>
      <div class="card bg-light border-0 p-3 mb-3 rounded-3">
        <h6 class="fw-bold mb-2 text-dark d-flex align-items-center">
          <i class="bi bi-shield-lock-fill me-2 text-primary"></i>後台登入權限設定
        </h6>
        <div class="row g-2">
          <div class="col-md-6">
            <label for="account_username" class="form-label small fw-semibold">登入帳號:</label>
            <input 
              type="text" 
              id="account_username" 
              class="form-control" 
              v-model="teacher.account_username" 
              placeholder="例如: teacher_mei"
            >
          </div>
          <div class="col-md-6">
            <label for="teacher_password" class="form-label small fw-semibold">
              {{ isEditMode ? '修改密碼 (不修改請留空):' : '登入密碼:' }}
            </label>
            <input 
              type="password" 
              id="teacher_password" 
              class="form-control" 
              v-model="teacher.password" 
              placeholder="請設定登入密碼"
            >
          </div>
        </div>
      </div>
      <div class="form-group mb-3">
        <label for="bio" class="form-label fw-semibold">簡介:</label>
        <textarea id="bio" class="form-control" v-model="teacher.bio"></textarea>
      </div>
      <div class="form-group mb-3">
        <label for="styles" class="form-label fw-semibold">專長風格:</label>
        <div class="checkbox-group">
          <div v-for="style in styles" :key="style.id" class="checkbox-item">
            <input type="checkbox" :id="'style-' + style.id" :value="style.id" v-model="teacher.style_ids" class="checkbox-input">
            <label :for="'style-' + style.id" class="checkbox-label">{{ style.name }}</label>
          </div>
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
    teacherId: {
      type: Number,
      default: null
    }
  },
  emits: ['teacher-updated', 'close-modal'],
  data() {
    return {
      teacher: {
        name: '',
        email: '',
        phone: '',
        experience_years: null,
        bio: '',
        hourly_rate: null,
        bank_account: '',
        avatar_url: '',
        account_username: '',
        password: '',
        style_ids: []
      },
      styles: [],
      isEditMode: false,
      submitting: false,
      uploadingAvatar: false
    };
  },
  watch: {
    teacherId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.isEditMode = true;
          this.fetchTeacher(newId);
        } else {
          this.isEditMode = false;
          this.resetForm();
        }
      }
    }
  },
  created() {
    this.fetchStyles();
  },
  methods: {
    resetForm() {
      this.teacher = {
        name: '',
        email: '',
        phone: '',
        experience_years: null,
        bio: '',
        hourly_rate: null,
        bank_account: '',
        avatar_url: '',
        account_username: '',
        password: '',
        style_ids: []
      };
    },
    fetchStyles() {
      api.get(API_ENDPOINTS.STYLES)
        .then(data => {
          this.styles = data.styles;
        })
        .catch(error => {
          console.error('獲取風格列表失敗:', error);
        });
    },
    fetchTeacher(id) {
      api.get(`${API_ENDPOINTS.TEACHERS}/${id}`)
        .then(data => {
          this.teacher = {
            ...data.teacher,
            bank_account: data.teacher.bank_account || '',
            avatar_url: data.teacher.avatar_url || '',
            account_username: data.teacher.account_username || '',
            password: '',
            style_ids: (data.teacher.styles || []).map(s => s.id)
          };
        })
        .catch(error => {
          console.error('獲取老師資料失敗:', error);
        });
    },
    submitForm() {
      // 基本驗證
      if (!this.teacher.name || this.teacher.name.trim() === '') {
        showToast('請填寫老師姓名！', 'error');
        return;
      }
      
      if (this.teacher.email && !this.isValidEmail(this.teacher.email)) {
        showToast('請輸入有效的電子郵件地址！', 'error');
        return;
      }
      
      if (this.isEditMode) {
        this.updateTeacher();
      } else {
        this.addTeacher();
      }
    },
    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    },
    addTeacher() {
      this.submitting = true;
      api.post(API_ENDPOINTS.TEACHERS, this.teacher)
        .then(() => {
          showToast('老師新增成功！', 'success');
          this.$emit('teacher-updated');
        })
        .catch(error => {
          console.error('新增老師失敗:', error);
          let errorMessage = '新增老師失敗！';
          
          if (error.message) {
            if (error.message.includes('foreign key constraint fails')) {
              errorMessage = '新增老師失敗：選擇的專長風格無效！';
            } else if (error.message.includes('缺少必要欄位')) {
              errorMessage = '新增老師失敗：請填寫老師姓名！';
            } else {
              errorMessage = `新增老師失敗：${error.message}`;
            }
          }
          
          showToast(errorMessage, 'error');
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    updateTeacher() {
      this.submitting = true;
      api.put(`${API_ENDPOINTS.TEACHERS}/${this.teacher.id}`, this.teacher)
        .then(() => {
          showToast('老師更新成功！', 'success');
          this.$emit('teacher-updated');
        })
        .catch(error => {
          console.error('更新老師失敗:', error);
          let errorMessage = '更新老師失敗！';
          
          if (error.message) {
            if (error.message.includes('foreign key constraint fails')) {
              errorMessage = '更新老師失敗：選擇的專長風格無效！';
            } else if (error.message.includes('缺少必要欄位')) {
              errorMessage = '更新老師失敗：請填寫老師姓名！';
            } else {
              errorMessage = `更新老師失敗：${error.message}`;
            }
          }
          
          showToast(errorMessage, 'error');
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    closeModal() {
      this.$emit('close-modal');
    },
    async handleAvatarFileSelected(e) {
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
      this.uploadingAvatar = true;
      try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await api.post('/upload/avatar', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        if (res.avatar_url) {
          this.teacher.avatar_url = res.avatar_url;
          showToast('大頭貼上傳成功！', 'success');
        }
      } catch (err) {
        showToast(err.message || '圖片上傳失敗，請重試', 'error');
      } finally {
        this.uploadingAvatar = false;
        if (e.target) e.target.value = '';
      }
    }
  }
};
</script>

<style scoped>
.add-teacher {
  padding: 20px;
}
.form-group {
  margin-bottom: 15px;
}
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
  max-height: 200px;
  overflow-y: auto;
}
.checkbox-item {
  display: flex;
  align-items: center;
  min-width: 120px;
  margin-bottom: 8px;
}
.checkbox-input {
  width: auto !important;
  margin-right: 8px;
  transform: scale(1.2);
}
.checkbox-label {
  margin-bottom: 0;
  cursor: pointer;
  font-size: 14px;
  line-height: 1.4;
}
.checkbox-label:hover {
  color: #007bff;
}
</style>
