<template>
  <div class="add-teacher">
    <form @submit.prevent="submitForm">
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
      <div class="form-group">
        <label for="bio" class="form-label">簡介:</label>
        <textarea id="bio" class="form-control" v-model="teacher.bio"></textarea>
      </div>
      <div class="form-group">
        <label for="hourly_rate" class="form-label">時薪:</label>
        <input type="number" id="hourly_rate" class="form-control" v-model="teacher.hourly_rate">
      </div>
      <div class="form-group">
        <label for="styles" class="form-label">專長風格:</label>
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
        style_ids: []
      },
      styles: [],
      isEditMode: false,
      submitting: false
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
          this.teacher = data.teacher;
          this.teacher.style_ids = data.teacher.styles.map(s => s.id);
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
      
      if (this.teacher.hourly_rate && this.teacher.hourly_rate < 0) {
        showToast('時薪不能為負數！', 'error');
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
