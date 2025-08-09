<template>
  <div class="add-teacher">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="name">姓名:</label>
        <input type="text" id="name" v-model="teacher.name" required>
      </div>
      <div class="form-group">
        <label for="email">電子郵件:</label>
        <input type="email" id="email" v-model="teacher.email">
      </div>
      <div class="form-group">
        <label for="phone">電話:</label>
        <input type="tel" id="phone" v-model="teacher.phone">
      </div>
      <div class="form-group">
        <label for="bio">簡介:</label>
        <textarea id="bio" v-model="teacher.bio"></textarea>
      </div>
      <div class="form-group">
        <label for="hourly_rate">時薪:</label>
        <input type="number" id="hourly_rate" v-model="teacher.hourly_rate">
      </div>
      <div class="form-group">
        <label>專長風格:</label>
        <div v-for="style in styles" :key="style.id">
          <input type="checkbox" :id="'style-' + style.id" :value="style.id" v-model="teacher.style_ids">
          <label :for="'style-' + style.id">{{ style.name }}</label>
        </div>
      </div>
      <button type="submit" class="btn btn-primary">{{ isEditMode ? '更新' : '新增' }}</button>
      <button type="button" class="btn btn-secondary" @click="closeModal">取消</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';
import { API_ENDPOINTS, buildApiUrl } from '@/utils/api.js';

export default {
  props: {
    teacherId: {
      type: Number,
      default: null
    }
  },
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
      isEditMode: false
    };
  },
  created() {
    this.fetchStyles();
    if (this.teacherId) {
      this.isEditMode = true;
      this.fetchTeacher(this.teacherId);
    }
  },
  methods: {
    fetchStyles() {
      axios.get(API_ENDPOINTS.STYLES)
        .then(response => {
          this.styles = response.data.styles;
        })
        .catch(error => {
          console.error('獲取風格列表失敗:', error);
        });
    },
    fetchTeacher(id) {
      axios.get(`${API_ENDPOINTS.TEACHERS}/${id}`)
        .then(response => {
          this.teacher = response.data.teacher;
          this.teacher.style_ids = response.data.teacher.styles.map(s => s.id);
        })
        .catch(error => {
          console.error('獲取老師資料失敗:', error);
        });
    },
    submitForm() {
      // 基本驗證
      if (!this.teacher.name || this.teacher.name.trim() === '') {
        alert('請填寫老師姓名！');
        return;
      }
      
      if (this.teacher.email && !this.isValidEmail(this.teacher.email)) {
        alert('請輸入有效的電子郵件地址！');
        return;
      }
      
      if (this.teacher.hourly_rate && this.teacher.hourly_rate < 0) {
        alert('時薪不能為負數！');
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
      axios.post(API_ENDPOINTS.TEACHERS, this.teacher)
        .then(() => {
          alert('老師新增成功！');
          this.$emit('teacher-updated');
        })
        .catch(error => {
          console.error('新增老師失敗:', error);
          let errorMessage = '新增老師失敗！';
          
          if (error.response && error.response.data && error.response.data.error) {
            const errorDetail = error.response.data.error;
            
            if (errorDetail.includes('Duplicate entry') && errorDetail.includes('email')) {
              errorMessage = '新增老師失敗：此電子郵件已被使用！';
            } else if (errorDetail.includes('foreign key constraint fails')) {
              errorMessage = '新增老師失敗：選擇的專長風格無效！';
            } else if (errorDetail.includes('缺少必要欄位')) {
              errorMessage = '新增老師失敗：請填寫老師姓名！';
            } else {
              errorMessage = `新增老師失敗：${errorDetail}`;
            }
          }
          
          alert(errorMessage);
        });
    },
    updateTeacher() {
      axios.put(`${API_ENDPOINTS.TEACHERS}/${this.teacher.id}`, this.teacher)
        .then(() => {
          alert('老師更新成功！');
          this.$emit('teacher-updated');
        })
        .catch(error => {
          console.error('更新老師失敗:', error);
          let errorMessage = '更新老師失敗！';
          
          if (error.response && error.response.data && error.response.data.error) {
            const errorDetail = error.response.data.error;
            
            if (errorDetail.includes('Duplicate entry') && errorDetail.includes('email')) {
              errorMessage = '更新老師失敗：此電子郵件已被使用！';
            } else if (errorDetail.includes('foreign key constraint fails')) {
              errorMessage = '更新老師失敗：選擇的專長風格無效！';
            } else if (errorDetail.includes('缺少必要欄位')) {
              errorMessage = '更新老師失敗：請填寫老師姓名！';
            } else {
              errorMessage = `更新老師失敗：${errorDetail}`;
            }
          }
          
          alert(errorMessage);
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
label {
  display: block;
  margin-bottom: 5px;
}
input, textarea {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
button {
  margin-right: 10px;
}
</style>
