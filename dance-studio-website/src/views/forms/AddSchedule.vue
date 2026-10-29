<template>
  <div class="add-schedule">
    <div v-if="loadingData" class="text-center py-4">
      <div class="spinner-border text-primary spinner-border-sm me-2" role="status"></div>
      <span class="text-muted">正在載入課程時間表資料...</span>
    </div>

    <form v-else @submit.prevent="submitForm">
      <div class="form-group">
        <label for="course_id" class="form-label fw-semibold">課程:</label>
        <select id="course_id" class="form-select" v-model="schedule.course_id" required>
          <option :value="null" disabled>-- 請選擇課程 --</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }} {{ course.teacher_name ? `(${course.teacher_name} 老師)` : '' }}
          </option>
        </select>
      </div>

      <!-- 授課師資 / 代課老師設定 -->
      <div class="form-group">
        <label for="teacher_id" class="form-label fw-semibold d-flex justify-content-between align-items-center">
          <span>
            <i class="bi bi-person-badge me-1 text-primary"></i>授課老師 / 代課設定:
          </span>
          <span v-if="isSubstituteSelected" class="badge bg-warning text-dark">
            <i class="bi bi-arrow-repeat me-1"></i>代課中
          </span>
        </label>
        <select id="teacher_id" class="form-select" v-model="schedule.teacher_id" @change="onTeacherChange">
          <option :value="null">
            依課程預設師資 {{ defaultTeacherName ? `(${defaultTeacherName})` : '' }}
          </option>
          <option v-for="t in teachers" :key="t.id" :value="t.id">
            {{ t.name }} {{ defaultTeacherId && t.id === defaultTeacherId ? '(原課程老師)' : '(指定代課)' }}
          </option>
        </select>
        <div class="form-text small text-muted" v-if="defaultTeacherName">
          此課程預設師資為：<strong>{{ defaultTeacherName }}</strong>。若有預先代課需求，請選擇代課老師。
        </div>
      </div>

      <!-- 代課備註 (僅在選擇代課老師時出現) -->
      <div class="form-group bg-warning-subtle p-2 rounded border border-warning-subtle" v-if="isSubstituteSelected">
        <label for="substitute_notes" class="form-label fw-semibold text-warning-emphasis small mb-1">
          <i class="bi bi-chat-left-dots me-1"></i>代課原因 / 備註 (選填):
        </label>
        <input 
          type="text" 
          id="substitute_notes" 
          class="form-control form-control-sm" 
          v-model="schedule.substitute_notes" 
          placeholder="例如: 原老師請假，由李老師代課"
        >
      </div>

      <div class="form-group">
        <label for="room_id" class="form-label fw-semibold">教室:</label>
        <select id="room_id" class="form-select" v-model="schedule.room_id">
          <option :value="null">無</option>
          <option v-for="room in rooms" :key="room.id" :value="room.id">
            {{ room.name }}
          </option>
        </select>
      </div>

      <!-- 單日或區間模式切換（僅新增模式顯示） -->
      <div class="form-group" v-if="!isEditMode">
        <label class="form-label d-block mb-1 fw-semibold">建立模式:</label>
        <div class="btn-group" role="group">
          <button type="button" class="btn btn-sm" :class="mode==='single' ? 'btn-primary' : 'btn-outline-primary'" @click="mode='single'">單日</button>
          <button type="button" class="btn btn-sm" :class="mode==='range' ? 'btn-primary' : 'btn-outline-primary'" @click="mode='range'">日期區間 + 每週</button>
        </div>
      </div>

      <!-- 單日日期 -->
      <div class="form-group" v-if="mode==='single' || isEditMode">
        <label for="schedule_date" class="form-label fw-semibold">日期:</label>
        <input type="date" id="schedule_date" class="form-control" v-model="schedule.schedule_date" required>
      </div>

      <!-- 區間日期與星期選擇 -->
      <div v-else class="border rounded p-2 mb-3 bg-light">
        <div class="form-group">
          <label for="start_date" class="form-label fw-semibold">開始日期:</label>
          <input type="date" id="start_date" class="form-control" v-model="range.start_date" required>
        </div>
        <div class="form-group">
          <label for="end_date" class="form-label fw-semibold">結束日期:</label>
          <input type="date" id="end_date" class="form-control" v-model="range.end_date" required>
        </div>
        <div class="form-group">
          <label class="form-label fw-semibold">選擇星期 (可多選):</label>
          <div class="weekdays">
            <label v-for="d in weekdays" :key="d.value" class="weekday-item">
              <input type="checkbox" :value="d.value" v-model="range.weekdays"> {{ d.label }}
            </label>
          </div>
        </div>
        <small class="text-muted" v-if="generatedDates.length">將建立 {{ generatedDates.length }} 筆排程</small>
      </div>

      <div class="row">
        <div class="col-md-6">
          <div class="form-group">
            <label for="start_time" class="form-label fw-semibold">開始時間:</label>
            <input type="time" id="start_time" class="form-control" v-model="schedule.start_time" required>
          </div>
        </div>
        <div class="col-md-6">
          <div class="form-group">
            <label for="end_time" class="form-label fw-semibold">結束時間:</label>
            <input type="time" id="end_time" class="form-control" v-model="schedule.end_time" required>
          </div>
        </div>
      </div>

      <div class="form-group">
        <div class="d-flex align-items-center p-3 border rounded" :class="schedule.allow_enrollment ? 'bg-light-success' : 'bg-light-warning'">
          <input type="checkbox" v-model="schedule.allow_enrollment" class="form-check-input me-3" id="allow_enrollment">
          <div>
            <label for="allow_enrollment" class="form-check-label fw-bold mb-1 cursor-pointer">
              {{ schedule.allow_enrollment ? '✅ 開放報名' : '❌ 關閉報名' }}
            </label>
            <small class="text-muted d-block">
              {{ schedule.allow_enrollment ? '學生可以報名此課程時段' : '學生無法報名此課程時段' }}
            </small>
          </div>
        </div>
      </div>

      <div class="d-flex justify-content-end gap-2 mt-4 pt-2 border-top">
        <button type="button" class="btn btn-secondary px-3" @click="closeModal">取消</button>
        <button type="submit" class="btn btn-primary px-4 fw-bold" :disabled="submitting">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
          {{ isEditMode ? '更新時間表' : (mode==='single' ? '新增時間表' : '批次新增時間表') }}
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
    scheduleId: {
      type: [Number, String],
      default: null
    },
    initialData: {
      type: Object,
      default: null
    },
    initialDate: {
      type: String,
      default: null
    }
  },
  emits: ['schedule-updated', 'close-modal'],
  data() {
    return {
      schedule: {
        course_id: null,
        room_id: null,
        teacher_id: null,
        is_substitute: false,
        substitute_notes: '',
        schedule_date: '',
        start_time: '',
        end_time: '',
        allow_enrollment: true
      },
      mode: 'single', // single | range
      range: {
        start_date: '',
        end_date: '',
        weekdays: [] // Monday ... Sunday
      },
      weekdays: [
        { value: 'Monday', label: '週一' },
        { value: 'Tuesday', label: '週二' },
        { value: 'Wednesday', label: '週三' },
        { value: 'Thursday', label: '週四' },
        { value: 'Friday', label: '週五' },
        { value: 'Saturday', label: '週六' },
        { value: 'Sunday', label: '週日' }
      ],
      courses: [],
      rooms: [],
      teachers: [],
      isEditMode: false,
      submitting: false,
      loadingData: false
    };
  },
  computed: {
    selectedCourse() {
      if (!this.schedule.course_id) return null;
      return this.courses.find(c => Number(c.id) === Number(this.schedule.course_id)) || null;
    },
    defaultTeacherId() {
      return this.selectedCourse?.teacher_id ? Number(this.selectedCourse.teacher_id) : null;
    },
    defaultTeacherName() {
      return this.selectedCourse?.teacher_name || '';
    },
    isSubstituteSelected() {
      if (this.schedule.teacher_id && this.defaultTeacherId && Number(this.schedule.teacher_id) !== Number(this.defaultTeacherId)) {
        return true;
      }
      return !!this.schedule.is_substitute;
    },
    generatedDates() {
      if (this.mode !== 'range' || !this.range.start_date || !this.range.end_date || this.range.weekdays.length===0) return [];
      const start = new Date(this.range.start_date);
      const end = new Date(this.range.end_date);
      if (end < start) return [];
      const result = [];
      const selected = new Set(this.range.weekdays);
      for (let d = new Date(start); d <= end; d.setDate(d.getDate()+1)) {
        const dayName = d.toLocaleDateString('en-US', { weekday: 'long' });
        if (selected.has(dayName)) {
          result.push(d.toISOString().slice(0,10));
        }
      }
      return result;
    }
  },
  watch: {
    scheduleId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.isEditMode = true;
          this.mode = 'single';
          if (this.initialData) {
            this.applyScheduleData(this.initialData);
          }
          this.fetchSchedule(newId);
        } else {
          this.isEditMode = false;
          if (this.initialDate) {
            this.schedule.schedule_date = this.normalizeDate(this.initialDate);
          }
        }
      }
    },
    initialData: {
      immediate: true,
      handler(newData) {
        if (newData && this.scheduleId) {
          this.applyScheduleData(newData);
        }
      }
    }
  },
  created() {
    this.fetchCourses();
    this.fetchRooms();
    this.fetchTeachers();
  },
  methods: {
    normalizeTime(timeStr) {
      if (!timeStr) return '';
      const parts = String(timeStr).trim().split(':');
      if (parts.length >= 2) {
        const hh = parts[0].padStart(2, '0');
        const mm = parts[1].padStart(2, '0');
        return `${hh}:${mm}`;
      }
      return String(timeStr).trim();
    },
    normalizeDate(dateStr) {
      if (!dateStr) return '';
      const str = String(dateStr).trim();
      return str.split('T')[0];
    },
    onTeacherChange() {
      if (this.schedule.teacher_id && this.defaultTeacherId && Number(this.schedule.teacher_id) !== Number(this.defaultTeacherId)) {
        this.schedule.is_substitute = true;
      } else if (!this.schedule.teacher_id || Number(this.schedule.teacher_id) === Number(this.defaultTeacherId)) {
        this.schedule.is_substitute = false;
        this.schedule.substitute_notes = '';
      }
    },
    applyScheduleData(data) {
      if (!data) return;
      this.schedule = {
        course_id: data.course_id ? Number(data.course_id) : null,
        room_id: data.room_id ? Number(data.room_id) : null,
        teacher_id: data.teacher_id ? Number(data.teacher_id) : null,
        is_substitute: Boolean(data.is_substitute),
        substitute_notes: data.substitute_notes || '',
        schedule_date: this.normalizeDate(data.schedule_date),
        start_time: this.normalizeTime(data.start_time),
        end_time: this.normalizeTime(data.end_time),
        allow_enrollment: data.allow_enrollment !== undefined ? !!data.allow_enrollment : true
      };
    },
    async fetchCourses() {
      try {
        const data = await api.get(API_ENDPOINTS.COURSES);
        this.courses = data.courses || [];
      } catch (error) {
        console.error('獲取課程列表失敗:', error);
      }
    },
    async fetchRooms() {
      try {
        const data = await api.get(API_ENDPOINTS.ROOMS);
        this.rooms = data.rooms || [];
      } catch (error) {
        console.error('獲取教室列表失敗:', error);
      }
    },
    async fetchTeachers() {
      try {
        const data = await api.get(API_ENDPOINTS.TEACHERS);
        this.teachers = data.teachers || [];
      } catch (error) {
        console.error('獲取老師列表失敗:', error);
      }
    },
    async fetchSchedule(id) {
      this.loadingData = true;
      try {
        const data = await api.get(`${API_ENDPOINTS.SCHEDULES}/${id}`);
        if (data && data.schedule) {
          this.applyScheduleData(data.schedule);
        }
      } catch (error) {
        console.error('獲取課程時間表資料失敗:', error);
        // 若 API 發生錯誤但有 initialData，保留使用 initialData
        if (!this.schedule.course_id && this.initialData) {
          this.applyScheduleData(this.initialData);
        }
      } finally {
        this.loadingData = false;
      }
    },
    submitForm() {
      if (this.isEditMode) {
        this.updateSchedule();
      } else {
        this.addSchedule();
      }
    },
    async addSchedule() {
      const basePayload = {
        course_id: this.schedule.course_id,
        room_id: this.schedule.room_id,
        schedule_date: this.schedule.schedule_date,
        start_time: this.schedule.start_time,
        end_time: this.schedule.end_time,
        allow_enrollment: this.schedule.allow_enrollment,
        teacher_id: this.schedule.teacher_id || null,
        is_substitute: this.isSubstituteSelected,
        substitute_notes: this.isSubstituteSelected ? (this.schedule.substitute_notes || '') : null
      };

      if (this.mode === 'single') {
        this.submitting = true;
        try {
          await api.post(API_ENDPOINTS.SCHEDULES, basePayload);
          showToast('課程時間表新增成功！', 'success');
          this.$emit('schedule-updated');
        } catch (error) {
          console.error(error);
          showToast('新增課程時間表失敗！', 'error');
        } finally {
          this.submitting = false;
        }
        return;
      }

      // range mode
      const dates = this.generatedDates;
      if (dates.length === 0) {
        showToast('請確認日期區間與星期選擇正確。', 'error');
        return;
      }
      if (!this.schedule.course_id || !this.schedule.start_time || !this.schedule.end_time) {
        showToast('請填寫課程、開始與結束時間。', 'error');
        return;
      }
      this.submitting = true;
      const failures = [];
      for (const dateStr of dates) {
        const payload = {
          ...basePayload,
          schedule_date: dateStr
        };
        try {
          await api.post(API_ENDPOINTS.SCHEDULES, payload);
        } catch (e) {
          failures.push(dateStr);
        }
      }
      if (failures.length === 0) {
        showToast(`批次建立成功，共建立 ${dates.length} 筆。`, 'success');
      } else {
        showToast(`部分建立失敗。成功 ${dates.length - failures.length} 筆，失敗 ${failures.length} 筆: ${failures.join(', ')}`, 'error');
      }
      this.$emit('schedule-updated');
      this.submitting = false;
    },
    async updateSchedule() {
      this.submitting = true;
      try {
        const payload = {
          course_id: this.schedule.course_id,
          room_id: this.schedule.room_id,
          schedule_date: this.schedule.schedule_date,
          start_time: this.schedule.start_time,
          end_time: this.schedule.end_time,
          allow_enrollment: this.schedule.allow_enrollment,
          teacher_id: this.schedule.teacher_id || null,
          is_substitute: this.isSubstituteSelected,
          substitute_notes: this.isSubstituteSelected ? (this.schedule.substitute_notes || '') : null
        };
        await api.put(`${API_ENDPOINTS.SCHEDULES}/${this.scheduleId}`, payload);
        showToast('課程時間表更新成功！', 'success');
        this.$emit('schedule-updated');
      } catch (error) {
        console.error(error);
        showToast('更新課程時間表失敗！', 'error');
      } finally {
        this.submitting = false;
      }
    },
    closeModal() {
      this.$emit('close-modal');
    }
  }
};
</script>

<style scoped>
.add-schedule {
  padding: 20px;
}
.form-group {
  margin-bottom: 15px;
}
.weekdays {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.weekday-item {
  font-size: 0.85rem;
  background: #fff;
  border: 1px solid #ccc;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
}
.weekday-item input {
  margin-right: 4px;
}

/* 報名狀態樣式 */
.bg-light-success {
  background: #d1edff !important;
  border-color: #28a745 !important;
}
.bg-light-warning {
  background: #fff3cd !important;
  border-color: #ffc107 !important;
}
.cursor-pointer {
  cursor: pointer;
}
.add-schedule .form-check-input {
  width: 1.2em;
  height: 1.2em;
}
</style>
