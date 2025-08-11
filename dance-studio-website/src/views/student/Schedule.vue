<template>
  <div class="schedule-page">
    <!-- 1. Banner -->
    <div class="banner">
      <img src="https://picsum.photos/1920/500?random=36" alt="Schedule Banner" class="banner-img">
      <div class="banner-text">
        <h1>課程時間表 / SCHEDULE</h1>
      </div>
    </div>

    <!-- 2. Class Schedule with Filters -->
    <div class="container my-5">
      <h2 class="text-center mb-4">完整課程時間表</h2>

      <!-- 週選擇器 -->
      <div class="d-flex flex-wrap align-items-center justify-content-center mb-4">
        <!-- label + input 包在一起 -->
        <div class="d-flex align-items-center mb-2 mb-md-0">
          <label class="form-label me-2 mb-0">選擇日期：</label>
          <input 
            type="date" 
            v-model="selectedWeekStart" 
            class="form-control w-auto mx-2"
            @change="onWeekChange"
            title="選擇任意日期，系統會顯示該日期所在週的課程表"
          />
        </div>

        <!-- span 分開一列 -->
        <span class="mx-2 text-muted text-center">
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
          class="btn btn-outline-light m-2"
        >
          {{ type }}
        </button>
      </div>

      <!-- Desktop Table View -->
      <div class="table-responsive d-none d-lg-block">
        <table class="table table-bordered table-Secondary table-striped text-center schedule-table">
          <thead>
            <tr>
              <th>時間</th>
              <th v-for="(day, index) in daysOfWeek" :key="index">
                {{ day }}<br/>
                <small>{{ getDateForDay(index) }}</small>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(timeSlot, timeIndex) in timeSlots" :key="timeIndex">
              <td>{{ timeSlot }}</td>
              <td v-for="(day, dayIndex) in daysOfWeek" :key="dayIndex">
                <div
                  v-for="(lesson, lessonIndex) in getFilteredLessons(timeSlot, day)"
                  :key="lessonIndex"
                  :class="getLessonClass(lesson.type)"
                  class="lesson-cell"
                  @click="openModal(lesson)"
                  style="cursor: pointer"
                >
                  <p class="lesson-name">{{ lesson.name }}</p>
                  <p class="lesson-teacher">{{ lesson.teacher }}</p>
                  <p class="lesson-level">{{ lesson.level }}</p>
                  <div class="enrollment-info">
                    <small class="text-muted">{{ lesson.enrollment_count }}/{{ lesson.course_capacity }}人</small>
                  </div>
                  <div class="enrollment-status">
                    <span v-if="lesson.allow_enrollment && !lesson.is_full" class="badge bg-success">可報名</span>
                    <span v-else-if="lesson.is_full" class="badge bg-warning">已滿額</span>
                    <span v-else class="badge bg-secondary">不開放報名</span>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Card View -->
      <div class="d-lg-none">
        <template v-for="(day, dayIndex) in daysOfWeek" :key="dayIndex">
          <div v-if="getLessonsForDay(day).length > 0" class="mb-4">
            <h3 class="text-center">{{ day }} {{ getDateForDay(dayIndex) }}</h3>
            <div 
              v-for="(lesson, lessonIndex) in getLessonsForDay(day)" 
              :key="lessonIndex" 
              :class="getLessonClass(lesson.type)" 
              class="lesson-card-mobile"
              @click="openModal(lesson)"
              style="cursor: pointer"
            >
              <div class="lesson-card-mobile-time">{{ lesson.time }}</div>
              <div class="lesson-card-mobile-details">
                <p class="lesson-name">{{ lesson.name }}</p>
                <p class="lesson-teacher">{{ lesson.teacher }}</p>
                <p class="lesson-level">{{ lesson.level }}</p>
                <div class="enrollment-info">
                  <small class="text-muted">報名人數：{{ lesson.enrollment_count }}/{{ lesson.course_capacity }}人</small>
                </div>
                <div class="enrollment-status">
                  <span v-if="lesson.allow_enrollment && !lesson.is_full" class="badge bg-success">可報名</span>
                  <span v-else-if="lesson.is_full" class="badge bg-warning">已滿額</span>
                  <span v-else class="badge bg-secondary">不開放報名</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Lesson Details Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h4 class="modal-title">課程詳情</h4>
          <button type="button" class="btn-close" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body" v-if="selectedLesson">
          <div class="lesson-detail-card" >
            <h5 class="lesson-name-large">{{ selectedLesson.name }}</h5>
            <div class="lesson-info">
              <div class="info-item">
                <strong>時間：</strong>{{ selectedLesson.time }}
              </div>
              <div class="info-item">
                <strong>星期：</strong>{{ selectedLesson.day }}
              </div>
              <div class="info-item">
                <strong>教師：</strong>{{ selectedLesson.teacher }}
              </div>
              <div class="info-item">
                <strong>程度：</strong>{{ selectedLesson.level }}
              </div>
              <div class="info-item">
                <strong>舞蹈類型：</strong>{{ selectedLesson.type }}
              </div>
              <div class="info-item">
                <strong>報名人數：</strong>{{ selectedLesson.enrollment_count }}/{{ selectedLesson.course_capacity }}人
              </div>
              <div class="info-item">
                <strong>報名狀態：</strong>
                <span v-if="selectedLesson.allow_enrollment && !selectedLesson.is_full" class="badge bg-success">可報名</span>
                <span v-else-if="selectedLesson.is_full" class="badge bg-warning">已滿額</span>
                <span v-else class="badge bg-secondary">不開放報名</span>
              </div>
            </div>
            <!-- <div class="lesson-description">
              <h6>課程介紹</h6>
              <p>{{ getLessonDescription(selectedLesson.type) }}</p>
            </div> -->
            <div class="enrollment-form">
              <h6>報名資訊</h6>
              <div v-if="selectedLesson.allow_enrollment && !selectedLesson.is_full">
                <div class="form-group row">
                  <label for="studentName" class="col-2 col-form-label">姓名：</label>
                  <div class="col-10">
                    <input 
                      type="text" 
                      id="studentName" 
                      v-model="studentName" 
                      class="form-control" 
                      placeholder="請輸入您的姓名"
                      @keyup.enter="enrollLesson(selectedLesson)"
                    />
                  </div>
                </div>
              </div>
              <div v-else-if="selectedLesson.is_full" class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                此課程報名人數已滿，無法報名。
              </div>
              <div v-else class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                此課程目前不開放報名。
              </div>
            </div>
            <div class="lesson-actions">
              <button 
                v-if="selectedLesson.allow_enrollment && !selectedLesson.is_full"
                class="btn btn-primary me-2" 
                @click="enrollLesson(selectedLesson)">
                立即報名
              </button>
              <button 
                v-else-if="selectedLesson.is_full"
                class="btn btn-warning me-2" 
                disabled>
                已滿額
              </button>
              <button 
                v-else
                class="btn btn-secondary me-2" 
                disabled>
                不開放報名
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL, API_ENDPOINTS } from '@/utils/api.js';

export default {
  name: 'Schedule',
  data() {
    return {
      showModal: false,
      selectedLesson: null,
      studentName: '',
      danceTypes: [], // 從後端取得
      selectedDanceType: '全部',
      timeSlots: [
        '09:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00',
        '14:00 - 15:00', '15:00 - 16:00', '18:00 - 19:00',
        '19:00 - 20:00', '20:00 - 21:00', '21:00 - 22:00'
      ],
      daysOfWeek: ['週一', '週二', '週三', '週四', '週五', '週六', '週日'],
      classes: [], // 從後端取得
      selectedWeekStart: '',
      weekStartDate: null,
      weekEndDate: null,
      weekDates: [] // 儲存該週的七天日期
    };
  },
  mounted() {
    this.initializeCurrentWeek();
    this.fetchDanceTypes();
    this.fetchSchedule();
  },
  methods: {
    async fetchDanceTypes() {
      try {
        const response = await fetch(API_ENDPOINTS.STYLES);
        const result = await response.json();
        if (response.ok && result.success) {
          this.danceTypes = ['全部', ...result.styles.map(s => s.name)];
        } else {
          this.danceTypes = ['全部'];
        }
      } catch (error) {
        this.danceTypes = ['全部'];
      }
    },
    async fetchSchedule() {
      if (!this.weekStartDate || !this.weekEndDate) {
        return;
      }
      
      // 格式化日期為 YYYY-MM-DD
      const start_date = this.formatDateForAPI(this.weekStartDate);
      const end_date = this.formatDateForAPI(this.weekEndDate);
      
      try {
        const response = await fetch(`${API_ENDPOINTS.SCHEDULES}?start_date=${start_date}&end_date=${end_date}`);
        const result = await response.json();
        if (response.ok && result.success) {
          // 動態生成時間段並轉換後端資料格式
          this.generateTimeSlots(result.schedules);
          this.classes = result.schedules.map(s => ({
            time: this.findMatchingTimeSlot(s.start_time, s.end_time),
            originalStartTime: s.start_time,
            originalEndTime: s.end_time,
            day: this.getDayText(s.day_of_week),
            name: s.course_name,
            teacher: s.teacher_name || '',
            level: s.level,
            type: s.style_name || '未知類型', // 使用正確的欄位名稱 style_name
            allow_enrollment: !!s.dynamic_allow_enrollment, // 使用動態報名狀態
            schedule_id: s.id, // 新增課程時間表 ID
            course_price: s.course_price || 1, // 新增課程扣堂數，預設為1
            enrollment_count: s.enrollment_count || 0, // 新增報名人數
            course_capacity: s.course_capacity || 15, // 使用課程容量
            is_full: s.enrollment_count >= s.course_capacity // 使用課程容量判斷是否已滿
          }));
          
        } else {
          this.classes = [];
        }
      } catch (error) {
        this.classes = [];
      }
    },
    getDayText(dayOfWeek) {
      // 英文轉中文
      const map = {
        'Monday': '週一', 'Tuesday': '週二', 'Wednesday': '週三', 'Thursday': '週四', 'Friday': '週五', 'Saturday': '週六', 'Sunday': '週日'
      };
      return map[dayOfWeek] || dayOfWeek;
    },
    initializeCurrentWeek() {
      // 設定為當前週的週一
      const today = new Date();
      const currentDay = today.getDay(); // 0是週日，1是週一
      const mondayOffset = currentDay === 0 ? -6 : 1 - currentDay; // 計算到週一的偏移
      const monday = new Date(today);
      monday.setDate(today.getDate() + mondayOffset);
      
      this.selectedWeekStart = this.formatDateForInput(monday);
      this.calculateWeekDates();
    },
    calculateWeekDates() {
      if (!this.selectedWeekStart) return;
      
      const selectedDate = new Date(this.selectedWeekStart);
      
      // 計算該日期所在週的週一
      const currentDay = selectedDate.getDay(); // 0是週日，1是週一，2是週二...
      const mondayOffset = currentDay === 0 ? -6 : 1 - currentDay; // 計算到週一的偏移
      const monday = new Date(selectedDate);
      monday.setDate(selectedDate.getDate() + mondayOffset);
      
      // 設定週一為週開始日期
      this.weekStartDate = new Date(monday);
      
      // 計算週日（週一 + 6天）
      this.weekEndDate = new Date(monday);
      this.weekEndDate.setDate(monday.getDate() + 6);
      
      // 計算該週的七天日期（從週一開始）
      this.weekDates = [];
      for (let i = 0; i < 7; i++) {
        const date = new Date(monday);
        date.setDate(monday.getDate() + i);
        this.weekDates.push(date);
      }
      
      // 更新日期選擇器顯示週一的日期
      this.selectedWeekStart = this.formatDateForInput(monday);
    },
    onWeekChange() {
      // 當週日期改變時，先計算週日期，然後自動獲取課程表
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
    generateTimeSlots(schedules) {
      // 從API資料中收集所有不重複的時間段
      const timeSlotSet = new Set();
      
      schedules.forEach(schedule => {
        const startTime = this.formatTime(schedule.start_time);
        const endTime = this.formatTime(schedule.end_time);
        const timeSlot = `${startTime} - ${endTime}`;
        timeSlotSet.add(timeSlot);
      });
      
      // 將時間段轉換為陣列並排序
      const newTimeSlots = Array.from(timeSlotSet).sort((a, b) => {
        const timeA = a.split(' - ')[0];
        const timeB = b.split(' - ')[0];
        return timeA.localeCompare(timeB);
      });
      
      // 如果有新的時間段，更新 timeSlots
      if (newTimeSlots.length > 0) {
        this.timeSlots = newTimeSlots;
      }
    },
    formatTime(timeString) {
      // 將 "14:50:00" 格式轉換為 "14:50"
      if (timeString && timeString.includes(':')) {
        const parts = timeString.split(':');
        return `${parts[0]}:${parts[1]}`;
      }
      return timeString;
    },
    findMatchingTimeSlot(startTime, endTime) {
      // 格式化時間
      const formattedStart = this.formatTime(startTime);
      const formattedEnd = this.formatTime(endTime);
      const targetTimeSlot = `${formattedStart} - ${formattedEnd}`;
      
      // 在現有的 timeSlots 中尋找匹配的時間段
      const matchingSlot = this.timeSlots.find(slot => slot === targetTimeSlot);
      
      if (matchingSlot) {
        return matchingSlot;
      }
      
      // 如果找不到完全匹配的，返回格式化後的時間段
      return targetTimeSlot;
    },
    getFilteredLessons(time, day) {
      return this.classes.filter(lesson => {
        const matchesTime = lesson.time === time;
        const matchesDay = lesson.day === day;
        const matchesType = this.selectedDanceType === '全部' || lesson.type === this.selectedDanceType;
        return matchesTime && matchesDay && matchesType;
      });
    },
    getLessonsForDay(day) {
      return this.classes
        .filter(lesson => lesson.day === day && (this.selectedDanceType === '全部' || lesson.type === this.selectedDanceType))
        .sort((a, b) => a.time.localeCompare(b.time));
    },
    getLessonClass(type) {
      // Map dance types to CSS classes for background colors
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
        'Street Jazz': 'bg-jazz' // Street Jazz uses Jazz color
      };
      return classMap[type] || '';
    },
    openModal(lesson) {
      this.selectedLesson = lesson;
      this.showModal = true;
      // 防止背景滾動
      document.body.style.overflow = 'hidden';
    },
    closeModal() {
      this.showModal = false;
      this.selectedLesson = null;
      this.studentName = ''; // 清空輸入的名字
      // 恢復背景滾動
      document.body.style.overflow = 'auto';
    },
    getLessonDescription(type) {
      const descriptions = {
        'Hip Hop': 'Hip Hop是一種源自美國的街舞文化，強調個人風格和自由表達，結合了力量、節奏感和創意。',
        'Jazz': 'Jazz舞蹈充滿活力和表現力，結合了古典技巧與現代元素，強調身體的延展性和音樂性。',
        'K-POP': 'K-POP舞蹈融合了多種舞蹈風格，動作精準、整齊劃一，充滿活力和時尚感。',
        'Locking': 'Locking是一種節奏感強烈的街舞，以突然的停頓和鎖定動作為特色，充滿幽默感。',
        'Waacking': 'Waacking強調手臂的快速揮舞和優雅的身體線條，展現個人魅力和表演性。',
        'Breaking': 'Breaking包含了power moves、toprock、downrock等元素，是街舞文化的重要組成部分。',
        'Popping': 'Popping通過肌肉的收縮和放鬆創造機械式的動作效果，強調身體的控制力。',
        'Heels': 'Heels舞蹈穿著高跟鞋表演，強調女性魅力、優雅和自信的表達。',
        'Contemporary': 'Contemporary現代舞結合了芭蕾、現代舞和爵士舞的技巧，注重情感表達和創意。',
        'Vogue': 'Vogue起源於紐約舞廳文化，以時尚雜誌的pose和優雅的手部動作為特色。'
      };
      return descriptions[type] || '這是一個精彩的舞蹈課程，歡迎您來體驗！';
    },
    async enrollLesson(lesson) {
      // 檢查是否允許報名
      if (!lesson.allow_enrollment) {
        alert('很抱歉，此課程目前不開放報名！');
        return;
      }

      // 檢查是否已滿額
      if (lesson.is_full) {
        alert('很抱歉，此課程報名人數已滿！');
        return;
      }

      // 檢查是否有輸入名字
      if (!this.studentName.trim()) {
        alert('請輸入您的姓名！');
        return;
      }

      try {
        // 準備要發送的資料
        const enrollmentData = {
          studentName: this.studentName,
          lesson: lesson,
          schedule_id: lesson.schedule_id // 新增課程時間表 ID
        };

        console.log('=== 發送報名資料到後端 ===');
        console.log('報名資料:', enrollmentData);

        // 發送 POST 請求到後端 (使用動態 API 配置)
        const response = await fetch(`${API_BASE_URL}/enrollment`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(enrollmentData)
        });

        const result = await response.json();

        if (response.ok && result.success) {
          console.log('=== 後端回應成功 ===');
          console.log('報名編號:', result.enrollment.id);
          console.log('剩餘堂數:', result.enrollment.remainingClasses);
          console.log('完整回應:', result);
          console.log('==================');
          
          // 顯示報名成功訊息（包含剩餘堂數）
          const remainingClasses = result.enrollment.remainingClasses;
          const coursePrice = lesson.course_price || 1; // 課程扣堂數
          alert(`${this.studentName} 您好！\n您已成功報名 ${lesson.name} 課程！\n\n報名詳情：\n• 報名編號：${result.enrollment.id}\n• 時間：${lesson.day} ${lesson.time}\n• 老師：${lesson.teacher}\n• 扣除堂數：${coursePrice}堂\n• 剩餘堂數：${remainingClasses}堂\n\n報名資料已儲存至資料庫！`);
          
          // 報名成功後關閉 Modal
          this.closeModal();
          
          // 自動獲取課程表
          this.fetchSchedule();
        } else {
          console.error('報名失敗:', result);
          // 顯示後端回傳的具體錯誤訊息
          alert(`報名失敗：${result.error || result.message || '未知錯誤'}`);
        }

      } catch (error) {
        console.error('=== 報名請求錯誤 ===');
        console.error('錯誤詳情:', error);
        console.log('==================');
        alert('網路錯誤，請檢查後端服務是否正常運行，或稍後再試！\n\n提示：請確保 Docker 容器正在運行。');
      }
    }
  }
};
</script>

<style src="../../assets/css/Schedule.css"></style>
