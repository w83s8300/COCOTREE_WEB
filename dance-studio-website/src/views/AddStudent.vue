<template>
  <div class="add-student">
    <h2>{{ isEditing ? '編輯學生' : '新增學生' }}</h2>
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="name">姓名:</label>
        <input type="text" id="name" v-model="student.name" required>
      </div>
      <div class="form-group">
        <label for="email">電子郵件:</label>
        <input type="email" id="email" v-model="student.email" required>
      </div>
      <div class="form-group">
        <label for="phone">電話:</label>
        <input type="tel" id="phone" v-model="student.phone">
      </div>
      <div class="form-group">
        <label for="date_of_birth">出生年月日:</label>
        <input type="date" id="date_of_birth" v-model="student.date_of_birth">
      </div>
      <div class="form-group">
        <label for="emergency_contact">緊急聯絡人:</label>
        <input type="text" id="emergency_contact" v-model="student.emergency_contact">
      </div>
      <div class="form-group">
        <label for="emergency_phone">緊急聯絡人電話:</label>
        <input type="tel" id="emergency_phone" v-model="student.emergency_phone">
      </div>
      <div class="form-group">
        <label for="medical_notes">醫療備註:</label>
        <textarea id="medical_notes" v-model="student.medical_notes"></textarea>
      </div>
      <div class="form-group">
        <label for="remaining_classes">剩餘堂數:</label>
        <input type="number" id="remaining_classes" v-model="student.remaining_classes" min="0" placeholder="0">
      </div>
      <div class="form-group">
        <label for="membership_expiry">會員到期日:</label>
        <input type="date" id="membership_expiry" v-model="student.membership_expiry">
      </div>
      <button type="submit" class="btn btn-primary">{{ isEditing ? '更新' : '新增' }}</button>
      <button type="button" class="btn btn-secondary ms-2" @click="$emit('close-modal')">取消</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    studentId: {
      type: Number,
      default: null
    }
  },
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
      isEditing: false
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
      axios.get(`http://localhost:8001/api/students/${id}`)
        .then(response => {
          this.student = response.data.student;
          if (this.student.membership_expiry) {
            this.student.membership_expiry = this.student.membership_expiry.split('T')[0];
          }
        })
        .catch(error => {
          console.error('獲取學生資料失敗:', error);
          alert('獲取學生資料失敗！');
          this.$emit('close-modal'); // 獲取失敗時關閉 modal
        });
    },
    submitForm() {
      if (this.isEditing) {
        this.updateStudent();
      } else {
        this.addStudent();
      }
    },
    addStudent() {
      axios.post('http://localhost:8001/api/students', this.student)
        .then(() => {
          alert('學生新增成功！');
          this.$emit('student-updated');
        })
        .catch(error => {
          console.error(error);
          alert('新增學生失敗！');
        });
    },
    updateStudent() {
      axios.put(`http://localhost:8001/api/students/${this.studentId}`, this.student)
        .then(() => {
          alert('學生更新成功！');
          this.$emit('student-updated');
        })
        .catch(error => {
          console.error(error);
          alert('更新學生失敗！');
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
  padding: 10px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
