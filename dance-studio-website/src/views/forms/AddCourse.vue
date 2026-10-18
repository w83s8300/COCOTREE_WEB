<template>
  <div class="add-course">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="name" class="form-label">課程名稱:</label>
        <input type="text" id="name" class="form-control" v-model="course.name" required>
      </div>
      <div class="form-group">
        <label for="description" class="form-label">課程描述:</label>
        <textarea id="description" class="form-control" v-model="course.description"></textarea>
      </div>
      <div class="form-group">
        <label for="level" class="form-label">難度級別:</label>
        <input type="text" id="level" class="form-control" v-model="course.level" required>
      </div>
      <div class="form-group">
        <label for="style_id" class="form-label">風格:</label>
        <select id="style_id" class="form-select" v-model="course.style_id">
          <option :value="null">無</option>
          <option v-for="style in styles" :key="style.id" :value="style.id">
            {{ style.name }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="duration_minutes" class="form-label">課程時長 (分鐘):</label>
        <input type="number" id="duration_minutes" class="form-control" v-model="course.duration_minutes">
      </div>
      <div class="form-group">
        <label for="max_students" class="form-label">人數上限:</label>
        <input type="number" id="max_students" class="form-control" v-model="course.max_students">
      </div>
      <div class="form-group">
        <label for="price" class="form-label">扣堂數:</label>
        <input type="number" id="price" class="form-control" v-model="course.price" min="1" step="1">
      </div>
      <div class="form-group">
        <label for="teacher_id" class="form-label">授課老師:</label>
        <select id="teacher_id" class="form-select" v-model="course.teacher_id">
          <option :value="null">無</option>
          <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
            {{ teacher.name }}
          </option>
        </select>
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
    courseId: {
      type: Number,
      default: null
    }
  },
  emits: ['course-updated', 'close-modal'],
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
      isEditMode: false,
      submitting: false
    };
  },
  watch: {
    courseId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.isEditMode = true;
          this.fetchCourse(newId);
        } else {
          this.isEditMode = false;
          this.resetForm();
        }
      }
    }
  },
  created() {
    this.fetchTeachers();
    this.fetchStyles();
  },
  methods: {
    resetForm() {
      this.course = {
        name: '',
        description: '',
        level: '',
        style_id: null,
        duration_minutes: 60,
        max_students: 15,
        price: null,
        teacher_id: null
      };
    },
    fetchTeachers() {
      api.get(API_ENDPOINTS.TEACHERS)
        .then(data => {
          this.teachers = data.teachers;
        })
        .catch(error => {
          console.error('獲取老師列表失敗:', error);
        });
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
    fetchCourse(id) {
      api.get(`${API_ENDPOINTS.COURSES}/${id}`)
        .then(data => {
          this.course = data.course;
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
      this.submitting = true;
      api.post(API_ENDPOINTS.COURSES, this.course)
        .then(() => {
          showToast('課程新增成功！', 'success');
          this.$emit('course-updated');
        })
        .catch(error => {
          console.error(error);
          showToast('新增課程失敗！', 'error');
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    updateCourse() {
      this.submitting = true;
      api.put(`${API_ENDPOINTS.COURSES}/${this.course.id}`, this.course)
        .then(() => {
          showToast('課程更新成功！', 'success');
          this.$emit('course-updated');
        })
        .catch(error => {
          console.error(error);
          showToast('更新課程失敗！', 'error');
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
.add-course {
  padding: 20px;
}
.form-group {
  margin-bottom: 15px;
}
.add-course .btn {
  margin-right: 10px;
}
</style>
