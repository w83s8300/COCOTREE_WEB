<template>
  <div class="add-schedule">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="course_id" class="form-label">課程:</label>
        <select id="course_id" class="form-select" v-model="schedule.course_id" required>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="room_id" class="form-label">教室:</label>
        <select id="room_id" class="form-select" v-model="schedule.room_id">
          <option :value="null">無</option>
          <option v-for="room in rooms" :key="room.id" :value="room.id">
            {{ room.name }}
          </option>
        </select>
      </div>
      <!-- 單日或區間模式切換 -->
      <div class="form-group">
        <label class="form-label d-block mb-1">建立模式:</label>
        <div class="btn-group" role="group">
          <button type="button" class="btn btn-sm" :class="mode==='single' ? 'btn-primary' : 'btn-outline-primary'" @click="mode='single'">單日</button>
          <button type="button" class="btn btn-sm" :class="mode==='range' ? 'btn-primary' : 'btn-outline-primary'" @click="mode='range'">日期區間 + 每週</button>
        </div>
      </div>

      <!-- 單日日期 -->
      <div class="form-group" v-if="mode==='single'">
        <label for="schedule_date" class="form-label">日期:</label>
        <input type="date" id="schedule_date" class="form-control" v-model="schedule.schedule_date" required>
      </div>

      <!-- 區間日期與星期選擇 -->
      <div v-else class="border rounded p-2 mb-3 bg-light">
        <div class="form-group">
          <label for="start_date" class="form-label">開始日期:</label>
          <input type="date" id="start_date" class="form-control" v-model="range.start_date" required>
        </div>
        <div class="form-group">
          <label for="end_date" class="form-label">結束日期:</label>
          <input type="date" id="end_date" class="form-control" v-model="range.end_date" required>
        </div>
        <div class="form-group">
          <label class="form-label">選擇星期 (可多選):</label>
          <div class="weekdays">
            <label v-for="d in weekdays" :key="d.value" class="weekday-item">
              <input type="checkbox" :value="d.value" v-model="range.weekdays"> {{ d.label }}
            </label>
          </div>
        </div>
        <small class="text-muted" v-if="generatedDates.length">將建立 {{ generatedDates.length }} 筆排程</small>
      </div>
      <div class="form-group">
        <label for="start_time" class="form-label">開始時間:</label>
        <input type="time" id="start_time" class="form-control" v-model="schedule.start_time" required>
      </div>
      <div class="form-group">
        <label for="end_time" class="form-label">結束時間:</label>
        <input type="time" id="end_time" class="form-control" v-model="schedule.end_time" required>
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
      <button type="submit" class="btn btn-primary" :disabled="submitting">
        <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
        {{ isEditMode ? '更新' : (mode==='single' ? '新增' : '批次新增') }}
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
    scheduleId: {
      type: Number,
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
      isEditMode: false,
      submitting: false
    };
  },
  computed: {
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
  created() {
    this.fetchCourses();
    this.fetchRooms();
    if (this.scheduleId) {
      this.isEditMode = true;
      this.fetchSchedule(this.scheduleId);
    } else if (this.initialDate) {
      this.schedule.schedule_date = this.initialDate;
    }
  },
  methods: {
    fetchCourses() {
      api.get(API_ENDPOINTS.COURSES)
        .then(data => {
          this.courses = data.courses;
        })
        .catch(error => {
          console.error('獲取課程列表失敗:', error);
        });
    },
    fetchRooms() {
      api.get(API_ENDPOINTS.ROOMS)
        .then(data => {
          this.rooms = data.rooms;
        })
        .catch(error => {
          console.error('獲取教室列表失敗:', error);
        });
    },
    fetchSchedule(id) {
      api.get(`${API_ENDPOINTS.SCHEDULES}/${id}`)
        .then(data => {
          this.schedule = data.schedule;
          // 確保日期格式正確，以便 input type="date" 顯示
          if (this.schedule.schedule_date) {
            this.schedule.schedule_date = this.schedule.schedule_date.split('T')[0];
          }
          // 確保 allow_enrollment 是布林值
          this.schedule.allow_enrollment = !!this.schedule.allow_enrollment;
        })
        .catch(error => {
          console.error('獲取課程時間表資料失敗:', error);
        });
    },
    submitForm() {
      if (this.isEditMode) {
        this.updateSchedule();
      } else {
        this.addSchedule();
      }
    },
    async addSchedule() {
      if (this.mode === 'single') {
        this.submitting = true;
        try {
          await api.post(API_ENDPOINTS.SCHEDULES, this.schedule);
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
          course_id: this.schedule.course_id,
          room_id: this.schedule.room_id,
          schedule_date: dateStr,
          start_time: this.schedule.start_time,
          end_time: this.schedule.end_time,
          allow_enrollment: this.schedule.allow_enrollment
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
    updateSchedule() {
      this.submitting = true;
      api.put(`${API_ENDPOINTS.SCHEDULES}/${this.scheduleId}`, this.schedule)
        .then(() => {
          showToast('課程時間表更新成功！', 'success');
          this.$emit('schedule-updated');
        })
        .catch(error => {
          console.error(error);
          showToast('更新課程時間表失敗！', 'error');
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
