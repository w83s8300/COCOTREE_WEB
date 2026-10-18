<template>
  <div class="schedules">
    <!-- 標題和新增按鈕 -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>課程時間表管理</h2>
      <button @click="addNewSchedule" class="btn btn-success">
        <i class="bi bi-plus-lg me-1"></i>新增課程時間表
      </button>
    </div>

    <!-- 月份選擇器 -->
    <div class="container my-4">
      <div class="d-flex justify-content-center align-items-center mb-4 flex-wrap gap-2">
        <input 
          type="month" 
          v-model="selectedMonth" 
          class="form-control w-auto" 
          @change="onMonthChange"
        />
        <span class="fw-bold text-secondary">
          {{ formatMonthRange(monthStartDate, monthEndDate) }}
        </span>
      </div>

      <!-- 舞蹈類型篩選器 -->
      <div class="d-flex justify-content-center flex-wrap mb-4 filter-buttons">
        <button
          v-for="type in danceTypes"
          :key="type"
          @click="selectedDanceType = type"
          :class="{ 'active': selectedDanceType === type }"
          class="btn btn-outline-primary m-1"
        >
          {{ type }}
        </button>
      </div>

      <!-- 載入中狀態 -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
        <p class="mt-2 text-muted">正在載入課程時間表...</p>
      </div>

      <!-- 桌面版表格 (O(1) 矩陣快速查詢) -->
      <div v-else class="table-responsive d-none d-lg-block">
        <table class="table table-bordered table-striped text-center schedule-table">
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
                  v-for="schedule in (scheduleMatrix[`${timeSlot}|${day}`] || [])"
                  :key="schedule.id"
                  :class="getLessonClass(schedule.style_name)"
                  class="schedule-cell"
                  @click="viewEnrollments(schedule)"
                  style="cursor: pointer"
                >
                  <p class="schedule-name">{{ schedule.course_name }}</p>
                  <p class="schedule-date">{{ formatScheduleDate(schedule.schedule_date) }}</p>
                  <p class="schedule-teacher">{{ schedule.teacher_name }}</p>
                  <p class="schedule-level">{{ schedule.level }}</p>
                  <div class="enrollment-info mb-2">
                    <small>報名人數：{{ schedule.enrollment_count || 0 }}/{{ schedule.course_capacity || 15 }}人</small>
                  </div>
                  <div class="enrollment-status mb-2">
                    <span v-if="!!schedule.allow_enrollment && (schedule.enrollment_count || 0) < (schedule.course_capacity || 15)" class="badge bg-success">可報名</span>
                    <span v-else-if="(schedule.enrollment_count || 0) >= (schedule.course_capacity || 15)" class="badge bg-warning text-dark">已滿額</span>
                    <span v-else class="badge bg-secondary">未開放</span>
                  </div>
                  <div class="schedule-actions">
                    <div class="d-flex flex-wrap gap-1 justify-content-center">
                      <button @click.stop="editSchedule(schedule.id)" class="btn btn-sm btn-light">編輯</button>
                      <button 
                        @click.stop="toggleEnrollment(schedule.id, schedule.allow_enrollment)" 
                        :class="!!schedule.allow_enrollment ? 'btn btn-sm btn-warning' : 'btn btn-sm btn-success'"
                      >
                        {{ !!schedule.allow_enrollment ? '關閉' : '開放' }}
                      </button>
                      <button @click.stop="deleteSchedule(schedule.id)" class="btn btn-sm btn-danger">刪除</button>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 手機版卡片 -->
      <div v-if="!loading" class="d-lg-none">
        <template v-for="(day, dayIndex) in daysOfWeek" :key="dayIndex">
          <div v-if="getSchedulesForDay(day).length > 0" class="mb-4">
            <h4 class="text-center py-2 bg-light border rounded">{{ day }} ({{ getDateForDay(dayIndex) }})</h4>
            <div 
              v-for="schedule in getSchedulesForDay(day)" 
              :key="schedule.id" 
              :class="getLessonClass(schedule.style_name)" 
              class="schedule-card-mobile p-3 mb-2 rounded text-white"
              @click="viewEnrollments(schedule)"
              style="cursor: pointer"
            >
              <div class="schedule-card-mobile-time fw-bold">{{ formatTime(schedule.start_time) }} - {{ formatTime(schedule.end_time) }}</div>
              <div class="schedule-card-mobile-details">
                <p class="schedule-name fs-5 fw-bold mb-1">{{ schedule.course_name }}</p>
                <p class="schedule-date mb-1">{{ formatScheduleDate(schedule.schedule_date) }}</p>
                <p class="schedule-teacher mb-1">授課：{{ schedule.teacher_name }} | {{ schedule.level }}</p>
                <div class="enrollment-info mb-2">
                  <small>報名人數：{{ schedule.enrollment_count || 0 }}/{{ schedule.course_capacity || 15 }}人</small>
                </div>
                <div class="enrollment-status mb-2">
                  <span v-if="!!schedule.allow_enrollment && (schedule.enrollment_count || 0) < (schedule.course_capacity || 15)" class="badge bg-success">可報名</span>
                  <span v-else-if="(schedule.enrollment_count || 0) >= (schedule.course_capacity || 15)" class="badge bg-warning text-dark">已滿額</span>
                  <span v-else class="badge bg-secondary">未開放</span>
                </div>
                <div class="schedule-actions mt-2">
                  <div class="d-flex flex-wrap gap-2">
                    <button @click.stop="editSchedule(schedule.id)" class="btn btn-sm btn-light">編輯</button>
                    <button 
                      @click.stop="toggleEnrollment(schedule.id, schedule.allow_enrollment)" 
                      :class="!!schedule.allow_enrollment ? 'btn btn-sm btn-warning' : 'btn btn-sm btn-success'"
                    >
                      {{ !!schedule.allow_enrollment ? '關閉報名' : '開放報名' }}
                    </button>
                    <button @click.stop="deleteSchedule(schedule.id)" class="btn btn-sm btn-danger">刪除</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Bootstrap Modal for adding/editing schedule -->
    <div class="modal fade" id="editScheduleModal" tabindex="-1" aria-labelledby="editScheduleModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editScheduleModalLabel">{{ editingScheduleId ? '編輯課程時間表' : '新增課程時間表' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddSchedule 
              v-if="showEditModal" 
              :scheduleId="editingScheduleId" 
              :initialDate="selectedDateForAdd" 
              @schedule-updated="handleScheduleUpdated" 
              @close-modal="closeEditModal" 
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Bootstrap Modal for viewing enrollments -->
    <div class="modal fade" id="enrollmentModal" tabindex="-1" aria-labelledby="enrollmentModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="enrollmentModalLabel">課程報名人員</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedSchedule">
              <!-- 課程資訊 -->
              <div class="course-info mb-4 p-3 bg-light rounded">
                <h6 class="fw-bold mb-3">課程資訊</h6>
                <div class="row">
                  <div class="col-md-6">
                    <p class="mb-1"><strong>課程名稱：</strong>{{ selectedSchedule.course_name }}</p>
                    <p class="mb-1"><strong>上課日期：</strong>{{ formatDate(selectedSchedule.schedule_date) }}</p>
                    <p class="mb-1"><strong>上課時間：</strong>{{ formatTime(selectedSchedule.start_time) }} - {{ formatTime(selectedSchedule.end_time) }}</p>
                  </div>
                  <div class="col-md-6">
                    <p class="mb-1"><strong>授課老師：</strong>{{ selectedSchedule.teacher_name || '未指定' }}</p>
                    <p class="mb-1"><strong>教室：</strong>{{ selectedSchedule.room_name || '未指定' }}</p>
                    <p class="mb-1"><strong>容量人數：</strong>{{ enrollmentList.length }}/{{ selectedSchedule.course_capacity || 15 }}人</p>
                  </div>
                </div>
              </div>

              <!-- 報名人員列表 -->
              <div class="enrollment-list">
                <h6 class="fw-bold mb-3">報名人員名冊</h6>
                <div v-if="enrollmentList.length === 0" class="alert alert-info">
                  目前此時段尚無學員報名。
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover align-middle">
                    <thead>
                      <tr>
                        <th>學員姓名</th>
                        <th>報名時間</th>
                        <th>狀態</th>
                        <th>操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="enrollment in enrollmentList" :key="enrollment.enrollment_id">
                        <td class="fw-bold">{{ enrollment.student_name }}</td>
                        <td>{{ formatDateTime(enrollment.enrollment_time) }}</td>
                        <td>
                          <span class="badge bg-success" v-if="enrollment.status === 'confirmed'">已確認</span>
                          <span class="badge bg-warning text-dark" v-else-if="enrollment.status === 'pending'">待確認</span>
                          <span class="badge bg-danger" v-else-if="enrollment.status === 'cancelled'">已取消</span>
                          <span class="badge bg-secondary" v-else>{{ enrollment.status }}</span>
                        </td>
                        <td>
                          <button 
                            @click="cancelEnrollment(enrollment.enrollment_id)" 
                            class="btn btn-sm btn-outline-danger"
                            v-if="enrollment.status !== 'cancelled'"
                          >
                            取消報名
                          </button>
                          <span v-else class="text-muted small">已取消</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">關閉</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api, { API_ENDPOINTS, buildApiUrl } from '@/utils/api';
import AddSchedule from '../forms/AddSchedule.vue';
import { Modal } from 'bootstrap';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';

export default {
  name: 'Schedules',
  components: {
    AddSchedule
  },
  data() {
    return {
      schedules: [],
      loading: false,
      showEditModal: false,
      editingScheduleId: null,
      editModal: null,
      selectedDateForAdd: null,
      
      // 報名名冊查看
      enrollmentModal: null,
      selectedSchedule: null,
      enrollmentList: [],
      
      // 表格篩選與時段
      danceTypes: ['全部'],
      selectedDanceType: '全部',
      timeSlots: [
        '09:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00',
        '14:00 - 15:00', '15:00 - 16:00', '18:00 - 19:00',
        '19:00 - 20:00', '20:00 - 21:00', '21:00 - 22:00'
      ],
      daysOfWeek: ['週一', '週二', '週三', '週四', '週五', '週六', '週日'],
      selectedMonth: '',
      monthStartDate: null,
      monthEndDate: null,
      monthDates: []
    };
  },
  computed: {
    // 篩選後排程
    filteredSchedules() {
      return this.schedules
        .filter(schedule => {
          return this.selectedDanceType === '全部' || schedule.style_name === this.selectedDanceType;
        })
        .sort((a, b) => {
          const dateCompare = new Date(a.schedule_date) - new Date(b.schedule_date);
          if (dateCompare !== 0) return dateCompare;
          return (a.start_time || '').localeCompare(b.start_time || '');
        });
    },
    // 預計算二維矩陣 O(1) 查詢，消除了原本 63 格重複線性掃描與正則比對
    scheduleMatrix() {
      const matrix = {};
      this.filteredSchedules.forEach(schedule => {
        const start = this.formatTime(schedule.start_time);
        const end = this.formatTime(schedule.end_time);
        const timeSlot = `${start} - ${end}`;
        const day = this.getDayText(schedule.day_of_week);
        const key = `${timeSlot}|${day}`;

        if (!matrix[key]) {
          matrix[key] = [];
        }
        matrix[key].push(schedule);
      });
      return matrix;
    }
  },
  mounted() {
    const editModalEl = document.getElementById('editScheduleModal');
    if (editModalEl) {
      this.editModal = new Modal(editModalEl);
      editModalEl.addEventListener('hidden.bs.modal', () => {
        this.showEditModal = false;
        this.editingScheduleId = null;
        this.selectedDateForAdd = null;
      });
    }

    const enrollModalEl = document.getElementById('enrollmentModal');
    if (enrollModalEl) {
      this.enrollmentModal = new Modal(enrollModalEl);
      enrollModalEl.addEventListener('hidden.bs.modal', () => {
        this.selectedSchedule = null;
        this.enrollmentList = [];
      });
    }

    this.initializeCurrentMonth();
    this.fetchDanceTypes();
  },
  beforeUnmount() {
    if (this.editModal) this.editModal.dispose();
    if (this.enrollmentModal) this.enrollmentModal.dispose();
  },
  created() {
    this.fetchSchedules();
  },
  methods: {
    async fetchDanceTypes() {
      try {
        const data = await api.get(API_ENDPOINTS.STYLES);
        if (data.success && data.styles) {
          this.danceTypes = ['全部', ...data.styles.map(s => s.name)];
        }
      } catch (error) {
        console.error('獲取舞蹈類型失敗:', error);
      }
    },
    async fetchSchedules() {
      this.loading = true;
      try {
        let url = API_ENDPOINTS.SCHEDULES;
        if (this.monthStartDate && this.monthEndDate) {
          const start_date = this.formatDateForAPI(this.monthStartDate);
          const end_date = this.formatDateForAPI(this.monthEndDate);
          url += `?start_date=${start_date}&end_date=${end_date}`;
        }
        const data = await api.get(url);
        if (data.success) {
          this.schedules = data.schedules || [];
          this.generateTimeSlots(this.schedules);
        } else {
          this.schedules = [];
        }
      } catch (error) {
        console.error('獲取課程時間表失敗:', error);
        this.schedules = [];
      } finally {
        this.loading = false;
      }
    },
    initializeCurrentMonth() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      this.selectedMonth = `${year}-${month}`;
      this.calculateMonthDates();
    },
    calculateMonthDates() {
      if (!this.selectedMonth) return;
      const [year, month] = this.selectedMonth.split('-');
      this.monthStartDate = new Date(parseInt(year), parseInt(month) - 1, 1);
      this.monthEndDate = new Date(parseInt(year), parseInt(month), 0);
      this.monthDates = [];
      for (let d = new Date(this.monthStartDate); d <= this.monthEndDate; d.setDate(d.getDate() + 1)) {
        this.monthDates.push(new Date(d));
      }
    },
    onMonthChange() {
      this.calculateMonthDates();
      this.fetchSchedules();
    },
    formatMonthRange(startDate, endDate) {
      if (!startDate || !endDate) return '';
      return `${startDate.getFullYear()}年${startDate.getMonth() + 1}月`;
    },
    getDateForDay(dayIndex) {
      if (!this.monthDates.length) return '';
      const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      const chineseDays = ['週日', '週一', '週二', '週三', '週四', '週五', '週六'];
      const targetDay = chineseDays[dayIndex];

      const datesForDay = this.monthDates.filter(date => {
        const dayName = dayNames[date.getDay()];
        return this.getDayText(dayName) === targetDay;
      });

      if (datesForDay.length === 0) return '';
      return datesForDay.map(date => date.getDate()).join(',');
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
    getDayText(dayOfWeek) {
      const map = {
        'Monday': '週一', 'Tuesday': '週二', 'Wednesday': '週三', 'Thursday': '週四', 
        'Friday': '週五', 'Saturday': '週六', 'Sunday': '週日'
      };
      return map[dayOfWeek] || dayOfWeek;
    },
    formatScheduleDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    },
    getSchedulesForDay(day) {
      return this.schedules
        .filter(schedule => {
          const matchesDay = this.getDayText(schedule.day_of_week) === day;
          const matchesType = this.selectedDanceType === '全部' || schedule.style_name === this.selectedDanceType;
          return matchesDay && matchesType;
        })
        .sort((a, b) => (a.start_time || '').localeCompare(b.start_time || ''));
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
    addNewSchedule() {
      this.editingScheduleId = null;
      this.selectedDateForAdd = null;
      this.showEditModal = true;
      this.$nextTick(() => this.editModal?.show());
    },
    editSchedule(id) {
      this.editingScheduleId = id;
      this.selectedDateForAdd = null;
      this.showEditModal = true;
      this.$nextTick(() => this.editModal?.show());
    },
    async toggleEnrollment(scheduleId, allowEnrollment) {
      const newStatus = !allowEnrollment;
      const action = newStatus ? '開放' : '關閉';
      const confirmed = await showConfirm(`確定要${action}此課程時段的報名功能嗎？`);
      if (!confirmed) return;

      try {
        await api.put(`${API_ENDPOINTS.SCHEDULES}/${scheduleId}`, {
          allow_enrollment: newStatus
        });
        showToast(`已${action}課程報名功能！`, 'success');
        this.fetchSchedules();
      } catch (error) {
        console.error('更新報名狀態失敗:', error);
        showToast('更新報名狀態失敗！', 'error');
      }
    },
    async deleteSchedule(id) {
      const confirmed = await showConfirm('確定要刪除這個課程時間表嗎？');
      if (!confirmed) return;

      try {
        await api.delete(`${API_ENDPOINTS.SCHEDULES}/${id}`);
        showToast('課程時間表已刪除！', 'success');
        this.fetchSchedules();
      } catch (error) {
        console.error('刪除課程時間表失敗:', error);
        showToast('刪除課程時間表失敗！', 'error');
      }
    },
    handleScheduleUpdated() {
      this.fetchSchedules();
      this.editModal?.hide();
    },
    closeEditModal() {
      this.editModal?.hide();
    },
    async viewEnrollments(schedule) {
      if (!schedule || !schedule.id) {
        showToast('無效的課程資料', 'error');
        return;
      }

      try {
        const data = await api.get(`${API_ENDPOINTS.SCHEDULES}/${schedule.id}/enrollments`);
        if (data.success) {
          this.selectedSchedule = data.schedule;
          this.enrollmentList = data.enrollments || [];
          this.enrollmentModal?.show();
        } else {
          showToast('無法獲取報名人員資料', 'error');
        }
      } catch (error) {
        console.error('獲取報名人員失敗:', error);
        showToast('獲取報名人員失敗，請稍後再試', 'error');
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月${String(date.getDate()).padStart(2, '0')}日`;
    },
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return '';
      const date = new Date(dateTimeString);
      return `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    },
    async cancelEnrollment(enrollmentId) {
      const confirmed = await showConfirm('確定要取消這位學員的報名嗎？');
      if (!confirmed) return;

      try {
        const data = await api.put(buildApiUrl(`/enrollments/${enrollmentId}`), {
          status: 'cancelled'
        });

        if (data.success) {
          showToast('取消報名成功！', 'success');
          if (this.selectedSchedule?.schedule_id) {
            const enrollData = await api.get(`${API_ENDPOINTS.SCHEDULES}/${this.selectedSchedule.schedule_id}/enrollments`);
            if (enrollData.success) {
              this.selectedSchedule = enrollData.schedule;
              this.enrollmentList = enrollData.enrollments || [];
            }
          }
          this.fetchSchedules();
        } else {
          showToast(`取消報名失敗：${data.error || '未知錯誤'}`, 'error');
        }
      } catch (error) {
        console.error('取消報名失敗:', error);
        showToast('取消報名失敗，請稍後再試', 'error');
      }
    }
  }
};
</script>

<style scoped>
.schedules {
  padding: 10px;
}

.schedule-table {
  background-color: #ffffff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  overflow: hidden;
}

.schedule-table th {
  background-color: #212529;
  color: white;
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

.schedule-name {
  font-weight: bold;
  margin-bottom: 2px;
  font-size: 0.9rem;
}

.schedule-date {
  font-size: 0.75rem;
  margin-bottom: 2px;
  opacity: 0.85;
}

.schedule-teacher {
  font-size: 0.8rem;
  margin-bottom: 2px;
}

.schedule-level {
  font-size: 0.7rem;
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 1px 6px;
  border-radius: 4px;
  margin-bottom: 4px;
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
