<template>
  <div class="schedule-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=36" title="課程時間表 / SCHEDULE" />

    <!-- 2. Class Schedule with Filters -->
    <div class="container my-5">
      <h2 class="text-center mb-4 fw-bold">完整課程時間表</h2>

      <!-- 週選擇器 -->
      <div class="d-flex flex-wrap align-items-center justify-content-center mb-4">
        <div class="d-flex align-items-center mb-2 mb-md-0">
          <label class="form-label me-2 mb-0 fw-bold">選擇日期：</label>
          <input 
            type="date" 
            v-model="selectedWeekStart" 
            class="form-control w-auto mx-2"
            @change="onWeekChange"
            title="選擇任意日期，系統會顯示該日期所在週的課程表"
          />
        </div>
        <span class="mx-2 text-muted text-center fw-medium">
          週期：{{ formatDateRange(weekStartDate, weekEndDate) }}
        </span>
      </div>

      <!-- Dance Type Filters -->
      <div class="d-flex justify-content-center flex-wrap mb-4 filter-buttons">
        <button
          v-for="type in danceTypes"
          :key="type"
          @click="selectedDanceType = type"
          :class="{ 'active': selectedDanceType === type }"
          class="btn btn-outline-dark m-1"
        >
          {{ type }}
        </button>
      </div>

      <!-- 載入中狀態 -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
        <p class="mt-2 text-muted">正在載入每週課表...</p>
      </div>

      <!-- Desktop Table View (O(1) 矩陣快速查詢) -->
      <div v-else class="table-responsive d-none d-lg-block">
        <table class="table table-bordered table-striped text-center schedule-table align-middle">
          <thead class="table-dark">
            <tr>
              <th scope="col" style="width: 120px;">時間</th>
              <th scope="col" v-for="(day, index) in daysOfWeek" :key="index">
                {{ day }}<br/>
                <small class="text-light-50">{{ getDateForDay(index) }}</small>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(timeSlot, timeIndex) in timeSlots" :key="timeIndex">
              <td class="time-slot">{{ timeSlot }}</td>
              <td v-for="(day, dayIndex) in daysOfWeek" :key="dayIndex">
                <div
                  v-for="lesson in (scheduleMatrix[`${timeSlot}|${day}`] || [])"
                  :key="lesson.schedule_id"
                  :class="getLessonClass(lesson.type)"
                  class="schedule-cell cursor-pointer"
                  @click="openModal(lesson)"
                >
                  <p class="lesson-name fw-bold mb-1">{{ lesson.name }}</p>
                  <p class="lesson-teacher small mb-1">{{ lesson.teacher }} | {{ lesson.level }}</p>
                  <div class="enrollment-status mb-1">
                    <span v-if="lesson.allow_enrollment && !lesson.is_full" class="badge bg-success">可報名</span>
                    <span v-else-if="lesson.is_full" class="badge bg-warning text-dark">已滿額</span>
                    <span v-else class="badge bg-secondary">不開放</span>
                  </div>
                  <small class="text-white-50 d-block">
                    {{ lesson.enrollment_count }}/{{ lesson.course_capacity }} 人
                  </small>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Card View -->
      <div v-if="!loading" class="d-lg-none">
        <template v-for="(day, dayIndex) in daysOfWeek" :key="dayIndex">
          <div v-if="getLessonsForDay(day).length > 0" class="mb-4">
            <h4 class="text-center py-2 bg-light border rounded">{{ day }} ({{ getDateForDay(dayIndex) }})</h4>
            <div
              v-for="lesson in getLessonsForDay(day)"
              :key="lesson.schedule_id"
              :class="getLessonClass(lesson.type)"
              class="schedule-card-mobile p-3 mb-2 rounded text-white cursor-pointer shadow-sm"
              @click="openModal(lesson)"
            >
              <div class="fw-bold mb-1">{{ lesson.time }}</div>
              <h5 class="fw-bold mb-1">{{ lesson.name }}</h5>
              <p class="mb-1 small">授課：{{ lesson.teacher }} | 程度：{{ lesson.level }}</p>
              <div class="d-flex justify-content-between align-items-center mt-2">
                <span v-if="lesson.allow_enrollment && !lesson.is_full" class="badge bg-success">可報名</span>
                <span v-else-if="lesson.is_full" class="badge bg-warning text-dark">已滿額</span>
                <span v-else class="badge bg-secondary">不開放</span>
                <small>{{ lesson.enrollment_count }}/{{ lesson.course_capacity }} 人</small>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Lesson Detail & Enrollment Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal d-block" tabindex="-1" role="dialog">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title fw-bold">{{ selectedLesson?.name }}</h5>
              <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
            </div>
            <div class="modal-body text-start" v-if="selectedLesson">
              <div class="mb-3">
                <p class="mb-1"><strong>上課時間：</strong>{{ selectedLesson.time }} ({{ selectedLesson.day }})</p>
                <p class="mb-1"><strong>授課老師：</strong>{{ selectedLesson.teacher || '未指定' }}</p>
                <p class="mb-1"><strong>課程難度：</strong>{{ selectedLesson.level }}</p>
                <p class="mb-1"><strong>舞風類型：</strong>{{ selectedLesson.type }}</p>
                <p class="mb-1"><strong>報名人數：</strong>{{ selectedLesson.enrollment_count }}/{{ selectedLesson.course_capacity }} 人</p>
                <p class="mb-0"><strong>扣除堂數：</strong>{{ selectedLesson.course_price }} 堂</p>
              </div>

              <div class="p-3 bg-light rounded mb-3">
                <h6 class="fw-bold mb-2">舞風介紹</h6>
                <p class="mb-0 small text-muted">{{ getLessonDescription(selectedLesson.type) }}</p>
              </div>

              <!-- 報名表單 -->
              <div class="enrollment-section">
                <h6 class="fw-bold mb-2">預約報名</h6>
                <div v-if="selectedLesson.allow_enrollment && !selectedLesson.is_full">
                  <div class="mb-3">
                    <label for="studentName" class="form-label small">學員姓名：</label>
                    <input 
                      type="text" 
                      id="studentName" 
                      v-model="studentName" 
                      class="form-control" 
                      placeholder="請輸入您的姓名"
                      @keyup.enter="enrollLesson(selectedLesson)"
                      :disabled="enrolling"
                    />
                  </div>
                </div>
                <div v-else-if="selectedLesson.is_full" class="alert alert-warning py-2 small mb-0">
                  <i class="bi bi-exclamation-triangle me-1"></i>此時段報名人數已額滿，無法預約。
                </div>
                <div v-else class="alert alert-secondary py-2 small mb-0">
                  <i class="bi bi-info-circle me-1"></i>此課程時段目前未開放線上預約。
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">關閉</button>
              <button 
                v-if="selectedLesson?.allow_enrollment && !selectedLesson?.is_full"
                type="button" 
                class="btn btn-primary" 
                @click="enrollLesson(selectedLesson)"
                :disabled="enrolling"
              >
                <span v-if="enrolling" class="spinner-border spinner-border-sm me-1" role="status"></span>
                {{ enrolling ? '報名中...' : '確認報名' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api, { API_ENDPOINTS } from '@/utils/api';
import PageBanner from '@/components/PageBanner.vue';
import { showToast } from '@/utils/toast';

export default {
  name: 'Schedule',
  components: {
    PageBanner
  },
  data() {
    return {
      showModal: false,
      selectedLesson: null,
      studentName: '',
      loading: false,
      enrolling: false,
      danceTypes: ['全部'],
      selectedDanceType: '全部',
      timeSlots: [
        '09:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00',
        '14:00 - 15:00', '15:00 - 16:00', '18:00 - 19:00',
        '19:00 - 20:00', '20:00 - 21:00', '21:00 - 22:00'
      ],
      daysOfWeek: ['週一', '週二', '週三', '週四', '週五', '週六', '週日'],
      classes: [],
      selectedWeekStart: '',
      weekStartDate: null,
      weekEndDate: null,
      weekDates: []
    };
  },
  computed: {
    scheduleMatrix() {
      const matrix = {};
      const filtered = this.classes.filter(lesson => {
        return this.selectedDanceType === '全部' || lesson.type === this.selectedDanceType;
      });

      filtered.forEach(lesson => {
        const key = `${lesson.time}|${lesson.day}`;
        if (!matrix[key]) matrix[key] = [];
        matrix[key].push(lesson);
      });
      return matrix;
    }
  },
  mounted() {
    this.initializeCurrentWeek();
    this.fetchDanceTypes();
    this.fetchSchedule();
  },
  methods: {
    async fetchDanceTypes() {
      try {
        const data = await api.get(API_ENDPOINTS.STYLES);
        if (data.success && data.styles) {
          this.danceTypes = ['全部', ...data.styles.map(s => s.name)];
        }
      } catch (error) {
        this.danceTypes = ['全部'];
      }
    },
    async fetchSchedule() {
      if (!this.weekStartDate || !this.weekEndDate) return;
      this.loading = true;

      const start_date = this.formatDateForAPI(this.weekStartDate);
      const end_date = this.formatDateForAPI(this.weekEndDate);

      try {
        const result = await api.get(`${API_ENDPOINTS.SCHEDULES}?start_date=${start_date}&end_date=${end_date}`);
        if (result.success && result.schedules) {
          this.generateTimeSlots(result.schedules);
          this.classes = result.schedules.map(s => ({
            time: this.findMatchingTimeSlot(s.start_time, s.end_time),
            originalStartTime: s.start_time,
            originalEndTime: s.end_time,
            day: this.getDayText(s.day_of_week),
            name: s.course_name,
            teacher: s.teacher_name || '',
            level: s.level,
            type: s.style_name || '未知舞風',
            allow_enrollment: !!s.dynamic_allow_enrollment,
            schedule_id: s.id,
            course_price: s.course_price || 1,
            enrollment_count: s.enrollment_count || 0,
            course_capacity: s.course_capacity || 15,
            is_full: (s.enrollment_count || 0) >= (s.course_capacity || 15)
          }));
        } else {
          this.classes = [];
        }
      } catch (error) {
        this.classes = [];
      } finally {
        this.loading = false;
      }
    },
    getDayText(dayOfWeek) {
      const map = {
        'Monday': '週一', 'Tuesday': '週二', 'Wednesday': '週三', 'Thursday': '週四',
        'Friday': '週五', 'Saturday': '週六', 'Sunday': '週日'
      };
      return map[dayOfWeek] || dayOfWeek;
    },
    initializeCurrentWeek() {
      const today = new Date();
      const currentDay = today.getDay();
      const mondayOffset = currentDay === 0 ? -6 : 1 - currentDay;
      const monday = new Date(today);
      monday.setDate(today.getDate() + mondayOffset);

      this.selectedWeekStart = this.formatDateForInput(monday);
      this.calculateWeekDates();
    },
    calculateWeekDates() {
      if (!this.selectedWeekStart) return;
      const selectedDate = new Date(this.selectedWeekStart);
      const currentDay = selectedDate.getDay();
      const mondayOffset = currentDay === 0 ? -6 : 1 - currentDay;
      const monday = new Date(selectedDate);
      monday.setDate(selectedDate.getDate() + mondayOffset);

      this.weekStartDate = new Date(monday);
      this.weekEndDate = new Date(monday);
      this.weekEndDate.setDate(monday.getDate() + 6);

      this.weekDates = [];
      for (let i = 0; i < 7; i++) {
        const date = new Date(monday);
        date.setDate(monday.getDate() + i);
        this.weekDates.push(date);
      }
      this.selectedWeekStart = this.formatDateForInput(monday);
    },
    onWeekChange() {
      this.calculateWeekDates();
      this.fetchSchedule();
    },
    getDateForDay(dayIndex) {
      if (!this.weekDates[dayIndex]) return '';
      const date = this.weekDates[dayIndex];
      return `${date.getMonth() + 1}/${date.getDate()}`;
    },
    formatDateRange(startDate, endDate) {
      if (!startDate || !endDate) return '';
      const start = `${startDate.getMonth() + 1}/${startDate.getDate()}`;
      const end = `${endDate.getMonth() + 1}/${endDate.getDate()}`;
      return `${start} ~ ${end}`;
    },
    formatDateForInput(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    formatDateForAPI(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    formatTime(timeString) {
      if (timeString && timeString.includes(':')) {
        const parts = timeString.split(':');
        return `${parts[0]}:${parts[1]}`;
      }
      return timeString || '';
    },
    generateTimeSlots(schedules) {
      const timeSlotSet = new Set(this.timeSlots);
      schedules.forEach(schedule => {
        const startTime = this.formatTime(schedule.start_time);
        const endTime = this.formatTime(schedule.end_time);
        if (startTime && endTime) {
          timeSlotSet.add(`${startTime} - ${endTime}`);
        }
      });
      this.timeSlots = Array.from(timeSlotSet).sort((a, b) => {
        return a.split(' - ')[0].localeCompare(b.split(' - ')[0]);
      });
    },
    findMatchingTimeSlot(startTime, endTime) {
      const formattedStart = this.formatTime(startTime);
      const formattedEnd = this.formatTime(endTime);
      const targetTimeSlot = `${formattedStart} - ${formattedEnd}`;
      return this.timeSlots.find(slot => slot === targetTimeSlot) || targetTimeSlot;
    },
    getLessonsForDay(day) {
      return this.classes
        .filter(lesson => lesson.day === day && (this.selectedDanceType === '全部' || lesson.type === this.selectedDanceType))
        .sort((a, b) => a.time.localeCompare(b.time));
    },
    getLessonClass(type) {
      const classMap = {
        'Hip Hop': 'bg-hiphop',
        'Jazz': 'bg-jazz',
        'K-POP': 'bg-kpop',
        'Locking': 'bg-locking',
        'Waacking': 'bg-waacking',
        'Breaking': 'bg-breaking',
        'Popping': 'bg-popping',
        'Heels': 'bg-heels',
        'Contemporary': 'bg-contemporary',
        'Vogue': 'bg-vogue',
        'Street Jazz': 'bg-jazz'
      };
      return classMap[type] || 'bg-secondary';
    },
    openModal(lesson) {
      this.selectedLesson = lesson;
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.selectedLesson = null;
      this.studentName = '';
    },
    getLessonDescription(type) {
      const descriptions = {
        'Hip Hop': 'Hip Hop 是一種源自美國的街舞文化，強調個人風格和自由律動表達，結合了節奏感與創意。',
        'Jazz': 'Jazz 充滿活力和舞台表現力，結合古典芭蕾技巧與現代律動元素，強調身體的延展性與音樂性。',
        'K-POP': 'K-POP 融合多種現代街舞風格，動作精準、整齊劃一，充滿流行時尚魅力。',
        'Locking': 'Locking 節奏感強烈，以急速的停頓與鎖定動作為特色，充滿幽默感與歡樂氛圍。',
        'Waacking': 'Waacking 強調手臂的快速揮舞和優雅的身體線條，展現個人魅力與強烈音樂性。',
        'Breaking': 'Breaking 包含大地板與各類力量技巧展示，是街舞文化最經典熱血的象徵。',
        'Popping': 'Popping 透過肌肉的收縮與放鬆創造出震撼的爆點節奏，強調身體極致的控制力。',
        'Heels': 'Heels 穿著高跟鞋練習，強調女性魅力、身型優雅曲線與極致自信展現。',
        'Contemporary': 'Contemporary 結合芭蕾、現代舞與爵士技巧，注重細膩情感傳遞與身體對話。',
        'Vogue': 'Vogue 起源於紐約舞廳文化，以時尚雜誌的經典 pose 與流暢手部幾何線條著稱。'
      };
      return descriptions[type] || '這是一個精彩的舞蹈課程，歡迎您前來體驗感受！';
    },
    async enrollLesson(lesson) {
      if (!lesson.allow_enrollment) {
        showToast('很抱歉，此課程目前不開放線上預約！', 'warning');
        return;
      }
      if (lesson.is_full) {
        showToast('很抱歉，此課程報名人數已額滿！', 'warning');
        return;
      }
      if (!this.studentName.trim()) {
        showToast('請輸入您的姓名！', 'warning');
        return;
      }

      this.enrolling = true;
      try {
        const payload = {
          student_name: this.studentName.trim(),
          schedule_id: lesson.schedule_id
        };
        const result = await api.post(API_ENDPOINTS.ENROLLMENTS, payload);
        if (result.success) {
          showToast('預約報名成功！期待在課堂上遇見您。', 'success');
          this.closeModal();
          this.fetchSchedule();
        } else {
          showToast(`報名失敗：${result.error || '請稍後重試'}`, 'error');
        }
      } catch (error) {
        console.error('報名失敗:', error);
        showToast('預約報名失敗，請稍後重試！', 'error');
      } finally {
        this.enrolling = false;
      }
    }
  }
};
</script>

<style scoped>
.schedule-table {
  background-color: #ffffff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  overflow: hidden;
}

.schedule-table th {
  padding: 12px 6px;
  font-weight: 600;
  vertical-align: middle;
}

.schedule-table td {
  vertical-align: top;
  padding: 4px;
  min-height: 80px;
}

.time-slot {
  background-color: #f8f9fa;
  font-weight: 600;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  min-width: 50px;
  vertical-align: middle !important;
}

.schedule-cell {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 4px;
  transition: all 0.2s ease;
}

.schedule-cell:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

.cursor-pointer {
  cursor: pointer;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1055;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 舞風色彩標籤 */
.bg-hiphop { background: linear-gradient(135deg, #ff6b6b 0%, #c0392b 100%) !important; }
.bg-jazz { background: linear-gradient(135deg, #f39c12 0%, #d35400 100%) !important; }
.bg-kpop { background: linear-gradient(135deg, #e84393 0%, #fd79a8 100%) !important; }
.bg-locking { background: linear-gradient(135deg, #00b894 0%, #00cec9 100%) !important; }
.bg-waacking { background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%) !important; }
.bg-breaking { background: linear-gradient(135deg, #2d3436 0%, #636e72 100%) !important; }
.bg-popping { background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%) !important; }
.bg-heels { background: linear-gradient(135deg, #d63031 0%, #e17055 100%) !important; }
.bg-contemporary { background: linear-gradient(135deg, #00cec9 0%, #81ecec 100%) !important; }
.bg-vogue { background: linear-gradient(135deg, #fd79a8 0%, #fab1a0 100%) !important; }
</style>
