<template>
  <div class="add-course">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="name">課程名稱:</label>
        <input type="text" id="name" v-model="course.name" required>
      </div>
      <div class="form-group">
        <label for="description">課程描述:</label>
        <textarea id="description" v-model="course.description"></textarea>
      </div>
      <div class="form-group">
        <label for="level">難度級別:</label>
        <input type="text" id="level" v-model="course.level" required>
      </div>
      <div class="form-group">
        <label for="style_id">風格:</label>
        <select id="style_id" v-model="course.style_id">
          <option :value="null">無</option>
          <option v-for="style in styles" :key="style.id" :value="style.id">
            {{ style.name }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="duration_minutes">課程時長 (分鐘):</label>
        <input type="number" id="duration_minutes" v-model="course.duration_minutes">
      </div>
      <div class="form-group">
        <label for="max_students">人數上限:</label>
        <input type="number" id="max_students" v-model="course.max_students">
      </div>
      <div class="form-group">
        <label for="price">扣堂數:</label>
        <input type="number" id="price" v-model="course.price" min="1" step="1">
      </div>
      <div class="form-group">
        <label for="teacher_id">授課老師:</label>
        <select id="teacher_id" v-model="course.teacher_id">
          <option :value="null">無</option>
          <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
            {{ teacher.name }}
          </option>
        </select>
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
    courseId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      course: {
        name: '',
        description: '',
        level: '',
        style_id: null,
        duration_minutes: 60,
        max_students: 15,
        price: null,
        teacher_id: null
      },
      teachers: [],
      styles: [],
      isEditMode: false
    };
  },
  created() {
    this.fetchTeachers();
    this.fetchStyles();
    if (this.courseId) {
      this.isEditMode = true;
      this.fetchCourse(this.courseId);
    }
  },
  methods: {
    fetchTeachers() {
      axios.get(API_ENDPOINTS.TEACHERS)
        .then(response => {
          this.teachers = response.data.teachers;
        })
        .catch(error => {
          console.error('獲取老師列表失敗:', error);
        });
    },
    fetchStyles() {
      axios.get(API_ENDPOINTS.STYLES)
        .then(response => {
          this.styles = response.data.styles;
        })
        .catch(error => {
          console.error('獲取風格列表失敗:', error);
        });
    },
    fetchCourse(id) {
      axios.get(`${API_ENDPOINTS.COURSES}/${id}`)
        .then(response => {
          this.course = response.data.course;
        })
        .catch(error => {
          console.error('獲取課程資料失敗:', error);
        });
    },
    submitForm() {
      if (this.isEditMode) {
        this.updateCourse();
      } else {
        this.addCourse();
      }
    },
    addCourse() {
      axios.post(API_ENDPOINTS.COURSES, this.course)
        .then(() => {
          alert('課程新增成功！');
          this.$emit('course-updated');
        })
        .catch(error => {
          console.error(error);
          alert('新增課程失敗！');
        });
    },
    updateCourse() {
      axios.put(`${API_ENDPOINTS.COURSES}/${this.course.id}`, this.course)
        .then(() => {
          alert('課程更新成功！');
          this.$emit('course-updated');
        })
        .catch(error => {
          console.error(error);
          alert('更新課程失敗！');
        });
    },
    closeModal() {
      this.$emit('close-modal');
    }
  }
};
</script>

<style scoped>
.add-course {
  padding: 20px;
}
.form-group {
  margin-bottom: 15px;
}
label {
  display: block;
  margin-bottom: 5px;
}
input, textarea, select {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
button {
  margin-right: 10px;
}
</style>
