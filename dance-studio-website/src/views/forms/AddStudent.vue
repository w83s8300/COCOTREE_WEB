<template>
  <div class="add-student">
    <h2>{{ isEditing ? '編輯學生' : '新增學生' }}</h2>
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="name" class="form-label">姓名:</label>
        <input type="text" id="name" class="form-control" v-model="student.name" required>
      </div>
      <div class="form-group">
        <label for="email" class="form-label">電子郵件:</label>
        <input type="email" id="email" class="form-control" v-model="student.email">
      </div>
      <div class="form-group">
        <label for="phone" class="form-label">電話:</label>
        <input type="tel" id="phone" class="form-control" v-model="student.phone">
      </div>
      <div class="form-group">
        <label for="date_of_birth" class="form-label">出生年月日:</label>
        <input type="date" id="date_of_birth" class="form-control" v-model="student.date_of_birth">
      </div>
      <div class="form-group">
        <label for="emergency_contact" class="form-label">緊急聯絡人:</label>
        <input type="text" id="emergency_contact" class="form-control" v-model="student.emergency_contact">
      </div>
      <div class="form-group">
        <label for="emergency_phone" class="form-label">緊急聯絡人電話:</label>
        <input type="tel" id="emergency_phone" class="form-control" v-model="student.emergency_phone">
      </div>
      <div class="form-group">
        <label for="medical_notes" class="form-label">醫療備註:</label>
        <textarea id="medical_notes" class="form-control" v-model="student.medical_notes"></textarea>
      </div>
      <div class="form-group">
        <label for="remaining_classes" class="form-label">剩餘堂數:</label>
        <input type="number" id="remaining_classes" class="form-control" v-model="student.remaining_classes" min="0" placeholder="0">
      </div>
      <div class="form-group">
        <label for="membership_expiry" class="form-label">會員到期日:</label>
        <input type="date" id="membership_expiry" class="form-control" v-model="student.membership_expiry">
      </div>
      <button type="submit" class="btn btn-primary" :disabled="submitting">
        <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
        {{ isEditing ? '更新' : '新增' }}
      </button>
      <button type="button" class="btn btn-secondary ms-2" @click="$emit('close-modal')">取消</button>
    </form>
  </div>
</template>

<script>
import api, { API_ENDPOINTS } from '@/utils/api';
import { showToast } from '@/utils/toast';

export default {
  props: {
    studentId: {
      type: Number,
      default: null
    }
  },
  emits: ['student-updated', 'close-modal'],
  data() {
    return {
      student: {
        name: '',
        email: '',
        phone: '',
        date_of_birth: null,
        emergency_contact: '',
        emergency_phone: '',
        medical_notes: '',
        remaining_classes: 0,
        membership_expiry: ''
      },
      isEditing: false,
      submitting: false
    };
  },
  watch: {
    studentId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.isEditing = true;
          this.fetchStudentData(newId);
        } else {
          this.isEditing = false;
          this.resetForm();
        }
      }
    }
  },
  methods: {
    resetForm() {
      this.student = {
        name: '',
        email: '',
        phone: '',
        date_of_birth: null,
        emergency_contact: '',
        emergency_phone: '',
        medical_notes: '',
        remaining_classes: 0,
        membership_expiry: ''
      };
    },
    fetchStudentData(id) {
      api.get(`${API_ENDPOINTS.STUDENTS}/${id}`)
        .then(data => {
          this.student = data.student;
          
          // 處理日期欄位，如果是 1911-01-01 則顯示為空
          if (this.student.date_of_birth === '1911-01-01') {
            this.student.date_of_birth = '';
          } else if (this.student.date_of_birth) {
            this.student.date_of_birth = this.student.date_of_birth.split('T')[0];
          }
          
          if (this.student.membership_expiry === '1911-01-01') {
            this.student.membership_expiry = '';
          } else if (this.student.membership_expiry) {
            this.student.membership_expiry = this.student.membership_expiry.split('T')[0];
          }
        })
        .catch(error => {
          console.error('獲取學生資料失敗:', error);
          showToast('獲取學生資料失敗！', 'error');
          this.$emit('close-modal'); // 獲取失敗時關閉 modal
        });
    },
    submitForm() {
      // 處理空的日期欄位
      const studentData = { ...this.student };
      if (!studentData.date_of_birth || studentData.date_of_birth === '') {
        studentData.date_of_birth = '1911-01-01';
      }
      if (!studentData.membership_expiry || studentData.membership_expiry === '') {
        studentData.membership_expiry = '1911-01-01';
      }
      
      if (this.isEditing) {
        this.updateStudent(studentData);
      } else {
        this.addStudent(studentData);
      }
    },
    addStudent(studentData) {
      this.submitting = true;
      api.post(API_ENDPOINTS.STUDENTS, studentData)
        .then(() => {
          showToast('學生新增成功！', 'success');
          this.$emit('student-updated');
        })
        .catch(error => {
          console.error(error);
          showToast('新增學生失敗！', 'error');
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    updateStudent(studentData) {
      this.submitting = true;
      api.put(`${API_ENDPOINTS.STUDENTS}/${this.studentId}`, studentData)
        .then(() => {
          showToast('學生更新成功！', 'success');
          this.$emit('student-updated');
        })
        .catch(error => {
          console.error(error);
          showToast('更新學生失敗！', 'error');
        })
        .finally(() => {
          this.submitting = false;
        });
    }
  }
};
</script>

<style scoped>
.add-student {
  padding: 20px;
}
.form-group {
  margin-bottom: 15px;
}
</style>
