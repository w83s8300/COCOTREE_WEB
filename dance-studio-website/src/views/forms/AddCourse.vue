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

      <!-- 師資鐘點 / 拆帳規則 (櫃檯客服不顯示) -->
      <div v-if="canViewSalary" class="card bg-light border-0 mb-4 p-3 rounded-3">
        <h6 class="fw-bold mb-3 text-primary d-flex align-items-center">
          <i class="bi bi-cash-coin me-2"></i>師資鐘點費 / 拆帳規則
        </h6>
        <div class="row g-3">
          <div class="col-md-4">
            <label for="base_salary" class="form-label fw-semibold">授課標準底金 (元):</label>
            <div class="input-group">
              <span class="input-group-text">$</span>
              <input 
                type="number" 
                id="base_salary" 
                class="form-control" 
                v-model.number="course.base_salary" 
                min="0" 
                step="10" 
                placeholder="0"
              >
            </div>
            <div class="form-text">老師每堂課標準保底薪資</div>
          </div>
          <div class="col-md-4">
            <label for="low_student_threshold" class="form-label fw-semibold">幾人以下 (人):</label>
            <div class="input-group">
              <input 
                type="number" 
                id="low_student_threshold" 
                class="form-control" 
                v-model.number="course.low_student_threshold" 
                min="0" 
                step="1" 
                placeholder="0 為不啟用"
              >
              <span class="input-group-text">人(含)以下</span>
            </div>
            <div class="form-text">0 表示不限制低額門檻</div>
          </div>
          <div class="col-md-4">
            <label for="low_student_salary" class="form-label fw-semibold">只有多少元 (元):</label>
            <div class="input-group">
              <span class="input-group-text">$</span>
              <input 
                type="number" 
                id="low_student_salary" 
                class="form-control" 
                v-model.number="course.low_student_salary" 
                min="0" 
                step="10" 
                placeholder="0"
              >
            </div>
            <div class="form-text">符合幾人以下時的固定薪資</div>
          </div>

          <div class="col-md-4">
            <label for="extra_student_threshold" class="form-label fw-semibold">超過幾人開始加成 (人):</label>
            <div class="input-group">
              <input 
                type="number" 
                id="extra_student_threshold" 
                class="form-control" 
                v-model.number="course.extra_student_threshold" 
                min="0" 
                step="1" 
                placeholder="0"
              >
              <span class="input-group-text">人以後</span>
            </div>
            <div class="form-text">學生超過此人數後開始加給</div>
          </div>
          <div class="col-md-4">
            <label for="extra_student_fee" class="form-label fw-semibold">一人加多少 (元/人):</label>
            <div class="input-group">
              <span class="input-group-text">+$</span>
              <input 
                type="number" 
                id="extra_student_fee" 
                class="form-control" 
                v-model.number="course.extra_student_fee" 
                min="0" 
                step="10" 
                placeholder="0"
              >
              <span class="input-group-text">/人</span>
            </div>
            <div class="form-text">每超出 1 位學生增加的費用</div>
          </div>
          <div class="col-md-4">
            <label for="salary_cap" class="form-label fw-semibold">費用上限 (元，0為無上限):</label>
            <div class="input-group">
              <span class="input-group-text">$</span>
              <input 
                type="number" 
                id="salary_cap" 
                class="form-control" 
                v-model.number="course.salary_cap" 
                min="0" 
                step="50" 
                placeholder="0 表示無上限"
              >
            </div>
            <div class="form-text">上限設為 0 代表無金額上限</div>
          </div>
        </div>

        <div class="alert alert-info py-2 px-3 mt-3 mb-0 small border-0 bg-white shadow-sm">
          <i class="bi bi-info-circle-fill me-1 text-primary"></i>
          <strong>規則試算預覽：</strong> {{ salaryRuleSummary }}
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
import { useAdminAuth } from '@/utils/adminAuth';

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
      adminAuth: useAdminAuth(),
      course: {
        name: '',
        description: '',
        level: '',
        style_id: null,
        duration_minutes: 60,
        max_students: 15,
        price: null,
        teacher_id: null,
        base_salary: 0,
        low_student_threshold: 0,
        low_student_salary: 0,
        extra_student_threshold: 0,
        extra_student_fee: 0,
        salary_cap: 0
      },
      teachers: [],
      styles: [],
      isEditMode: false,
      submitting: false
    };
  },
  computed: {
    canViewSalary() {
      return this.adminAuth.canViewSalary;
    },
    salaryRuleSummary() {
      const base = Number(this.course.base_salary) || 0;
      const lowThresh = Number(this.course.low_student_threshold) || 0;
      const lowSalary = Number(this.course.low_student_salary) || 0;
      const threshold = Number(this.course.extra_student_threshold) || 0;
      const extraFee = Number(this.course.extra_student_fee) || 0;
      const cap = Number(this.course.salary_cap) || 0;

      let text = '';
      if (lowThresh > 0) {
        text += `1 ~ ${lowThresh} 人只有 NT$ ${lowSalary}；超過 ${lowThresh} 人底金 NT$ ${base}`;
      } else {
        text += `底金 NT$ ${base}`;
      }
      text += `（無人報名則為 $0）`;

      if (extraFee > 0) {
        text += `，超過 ${threshold} 人後每多 1 人加 NT$ ${extraFee}`;
      } else {
        text += `，無學生人數額外加成`;
      }

      if (cap > 0) {
        text += `，最高上限 NT$ ${cap}`;
      } else {
        text += `，無費用上限 (上限0)`;
      }
      return text;
    }
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
        teacher_id: null,
        base_salary: 0,
        low_student_threshold: 0,
        low_student_salary: 0,
        extra_student_threshold: 0,
        extra_student_fee: 0,
        salary_cap: 0
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
          this.course = {
            ...data.course,
            base_salary: data.course.base_salary ?? 0,
            low_student_threshold: data.course.low_student_threshold ?? 0,
            low_student_salary: data.course.low_student_salary ?? 0,
            extra_student_threshold: data.course.extra_student_threshold ?? 0,
            extra_student_fee: data.course.extra_student_fee ?? 0,
            salary_cap: data.course.salary_cap ?? 0
          };
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
