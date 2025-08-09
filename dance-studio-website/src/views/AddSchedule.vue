<template>
  <div class="add-schedule">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="course_id">課程:</label>
        <select id="course_id" v-model="schedule.course_id" required>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="room_id">教室:</label>
        <select id="room_id" v-model="schedule.room_id">
          <option :value="null">無</option>
          <option v-for="room in rooms" :key="room.id" :value="room.id">
            {{ room.name }}
          </option>
        </select>
      </div>
      <!-- 單日或區間模式切換 -->
      <div class="form-group">
        <label class="d-block mb-1">建立模式:</label>
        <div class="btn-group" role="group">
          <button type="button" class="btn btn-sm" :class="mode==='single' ? 'btn-primary' : 'btn-outline-primary'" @click="mode='single'">單日</button>
          <button type="button" class="btn btn-sm" :class="mode==='range' ? 'btn-primary' : 'btn-outline-primary'" @click="mode='range'">日期區間 + 每週</button>
        </div>
      </div>

      <!-- 單日日期 -->
      <div class="form-group" v-if="mode==='single'">
        <label for="schedule_date">日期:</label>
        <input type="date" id="schedule_date" v-model="schedule.schedule_date" required>
      </div>

      <!-- 區間日期與星期選擇 -->
      <div v-else class="border rounded p-2 mb-3 bg-light">
        <div class="form-group">
          <label for="start_date">開始日期:</label>
          <input type="date" id="start_date" v-model="range.start_date" required>
        </div>
        <div class="form-group">
          <label for="end_date">結束日期:</label>
          <input type="date" id="end_date" v-model="range.end_date" required>
        </div>
        <div class="form-group">
          <label>選擇星期 (可多選):</label>
          <div class="weekdays">
            <label v-for="d in weekdays" :key="d.value" class="weekday-item">
              <input type="checkbox" :value="d.value" v-model="range.weekdays"> {{ d.label }}
            </label>
          </div>
        </div>
        <small class="text-muted" v-if="generatedDates.length">將建立 {{ generatedDates.length }} 筆排程</small>
      </div>
      <div class="form-group">
        <label for="start_time">開始時間:</label>
        <input type="time" id="start_time" v-model="schedule.start_time" required>
      </div>
      <div class="form-group">
        <label for="end_time">結束時間:</label>
        <input type="time" id="end_time" v-model="schedule.end_time" required>
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
      <button type="submit" class="btn btn-primary">{{ isEditMode ? '更新' : (mode==='single' ? '新增' : '批次新增') }}</button>
      <button type="button" class="btn btn-secondary" @click="closeModal">取消</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';
import { API_ENDPOINTS, buildApiUrl } from '@/utils/api.js';

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
      isEditMode: false
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
      axios.get('http://localhost:8001/api/courses')
        .then(response => {
          this.courses = response.data.courses;
        })
        .catch(error => {
          console.error('獲取課程列表失敗:', error);
        });
    },
    fetchRooms() {
      axios.get('http://localhost:8001/api/rooms')
        .then(response => {
          this.rooms = response.data.rooms;
        })
        .catch(error => {
          console.error('獲取教室列表失敗:', error);
        });
    },
    fetchSchedule(id) {
      axios.get(`http://localhost:8001/api/schedules/${id}`)
        .then(response => {
          this.schedule = response.data.schedule;
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
        try {
          await axios.post('http://localhost:8001/api/schedules', this.schedule);
          alert('課程時間表新增成功！');
          this.$emit('schedule-updated');
        } catch (error) {
          console.error(error);
          alert('新增課程時間表失敗！');
        }
        return;
      }

      // range mode
      const dates = this.generatedDates;
      if (dates.length === 0) {
        alert('請確認日期區間與星期選擇正確。');
        return;
      }
      if (!this.schedule.course_id || !this.schedule.start_time || !this.schedule.end_time) {
        alert('請填寫課程、開始與結束時間。');
        return;
      }
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
          await axios.post('http://localhost:8001/api/schedules', payload);
        } catch (e) {
          failures.push(dateStr);
        }
      }
      if (failures.length === 0) {
        alert(`批次建立成功，共建立 ${dates.length} 筆。`);
      } else {
        alert(`部分建立失敗。成功 ${dates.length - failures.length} 筆，失敗 ${failures.length} 筆: \n${failures.join(', ')}`);
      }
      this.$emit('schedule-updated');
    },
    updateSchedule() {
      axios.put(`http://localhost:8001/api/schedules/${this.scheduleId}`, this.schedule)
        .then(() => {
          alert('課程時間表更新成功！');
          this.$emit('schedule-updated');
        })
        .catch(error => {
          console.error(error);
          alert('更新課程時間表失敗！');
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
label {
  display: block;
  margin-bottom: 5px;
}
input, select {
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
 .weekday-item input { margin-right: 4px; }
 .border { border: 1px solid #dee2e6 !important; }
 .bg-light { background: #f8f9fa !important; }
 
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
 .form-check-input {
   width: 1.2em;
   height: 1.2em;
 }
</style>
