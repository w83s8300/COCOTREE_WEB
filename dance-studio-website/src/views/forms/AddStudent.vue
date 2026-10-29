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
        <label for="bank_last_5" class="form-label">約定轉帳銀行帳號後 5 碼 (購課對帳):</label>
        <input type="text" id="bank_last_5" class="form-control" v-model="student.bank_last_5" maxlength="10" placeholder="例如：12345">
      </div>
      <div class="form-group">
        <label for="medical_notes" class="form-label">醫療備註:</label>
        <textarea id="medical_notes" class="form-control" v-model="student.medical_notes"></textarea>
      </div>
      <div class="form-group">
        <label for="remaining_classes" class="form-label">剩餘堂數:</label>
        <input type="number" id="remaining_classes" class="form-control" v-model="student.remaining_classes" min="0" placeholder="0">
      </div>
      <div class="row">
        <div class="col-md-6 form-group mb-3">
          <label for="membership_expiry" class="form-label fw-bold">會員年費到期日:</label>
          <input type="date" id="membership_expiry" class="form-control" v-model="student.membership_expiry">
          <small class="text-muted d-block mt-1">年度會員專屬資格有效期限</small>
        </div>
        <div class="col-md-6 form-group mb-3">
          <label for="monthly_pass_expiry" class="form-label fw-bold text-primary">月費暢跳到期日:</label>
          <input type="date" id="monthly_pass_expiry" class="form-control" v-model="student.monthly_pass_expiry">
          <small class="text-muted d-block mt-1">月費期間預約特定課程免扣堂數</small>
        </div>
      </div>
      <!-- LINE 帳號關聯區塊 -->
      <div class="card p-3 my-3 bg-light border">
        <h6 class="fw-bold mb-2 text-success">
          <i class="bi bi-line me-1"></i>LINE 帳號關聯資訊
        </h6>
        <div class="row g-2">
          <div class="col-md-6 form-group">
            <label for="line_display_name" class="form-label small mb-1">LINE 暱稱:</label>
            <input type="text" id="line_display_name" class="form-control form-control-sm" v-model="student.line_display_name" placeholder="例如：Alex">
          </div>
          <div class="col-md-6 form-group">
            <label for="line_user_id" class="form-label small mb-1">LINE User ID:</label>
            <input type="text" id="line_user_id" class="form-control form-control-sm font-monospace" v-model="student.line_user_id" placeholder="例如：U1234...">
          </div>
        </div>
        <div v-if="student.line_user_id || student.line_linked_at" class="small text-muted mt-2 d-flex justify-content-between align-items-center">
          <span>關聯時間：{{ student.line_linked_at || '未設定' }}</span>
          <button type="button" class="btn btn-outline-danger btn-sm py-0 px-2" @click="clearLineBinding">
            清除此關聯
          </button>
        </div>
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
        bank_last_5: '',
        medical_notes: '',
        remaining_classes: 0,
        membership_expiry: '',
        monthly_pass_expiry: '',
        line_user_id: '',
        line_display_name: '',
        line_picture_url: '',
        line_linked_at: ''
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
        bank_last_5: '',
        medical_notes: '',
        remaining_classes: 0,
        membership_expiry: '',
        monthly_pass_expiry: '',
        line_user_id: '',
        line_display_name: '',
        line_picture_url: '',
        line_linked_at: ''
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
          
          if (this.student.monthly_pass_expiry === '1911-01-01') {
            this.student.monthly_pass_expiry = '';
          } else if (this.student.monthly_pass_expiry) {
            this.student.monthly_pass_expiry = this.student.monthly_pass_expiry.split('T')[0];
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
      if (!studentData.monthly_pass_expiry || studentData.monthly_pass_expiry === '') {
        studentData.monthly_pass_expiry = null;
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
    },
    clearLineBinding() {
      this.student.line_user_id = null;
      this.student.line_display_name = null;
      this.student.line_picture_url = null;
      this.student.line_linked_at = null;
      showToast('已清除 LINE 關聯資訊，請點擊更新以儲存！', 'info');
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
