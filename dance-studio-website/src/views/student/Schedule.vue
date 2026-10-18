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
                  class="schedule-cell cursor-pointer d-flex p-0 overflow-hidden text-start"
                  @click="openModal(lesson)"
                >
                  <!-- 1/3 圖片區塊 (佔 3 分之一) -->
                  <div class="card-img-col flex-shrink-0" style="width: 33.333%;">
                    <img 
                      v-if="lesson.teacher_avatar" 
                      :src="lesson.teacher_avatar" 
                      :alt="lesson.teacher" 
                      class="w-100 h-100 object-fit-cover d-block" 
                      :title="lesson.teacher"
                    />
                    <div v-else class="w-100 h-100 d-flex flex-column align-items-center justify-content-center bg-light text-secondary">
                      <i class="bi bi-person-fill text-muted" style="font-size: 1.25rem;"></i>
                    </div>
                  </div>

                  <!-- 2/3 內容區塊 (佔 3 分之二) -->
                  <div class="card-content-col p-2 d-flex flex-column justify-content-between flex-grow-1" style="width: 66.667%; min-width: 0;">
                    <div>
                      <p class="lesson-name fw-bold mb-0 text-dark text-truncate" :title="lesson.name" style="font-size: 0.85rem;">{{ lesson.name }}</p>
                      <p class="lesson-teacher text-muted mb-1 text-truncate" :title="lesson.teacher" style="font-size: 0.72rem;">
                        <i class="bi bi-person me-1"></i>{{ lesson.teacher || '未指定' }}
                      </p>
                    </div>
                    <div>
                      <div class="enrollment-status mb-1">
                        <span v-if="myEnrolledScheduleIds.includes(lesson.schedule_id)" class="badge bg-info text-dark" style="font-size: 0.65rem;">已預約</span>
                        <span v-else-if="lesson.is_past" class="badge bg-secondary" style="font-size: 0.65rem;">已結束</span>
                        <span v-else-if="lesson.allow_enrollment && !lesson.is_full" class="badge bg-success" style="font-size: 0.65rem;">可報名</span>
                        <span v-else-if="lesson.is_full" class="badge bg-warning text-dark" style="font-size: 0.65rem;">已滿額</span>
                        <span v-else class="badge bg-secondary" style="font-size: 0.65rem;">不開放</span>
                      </div>
                      <small class="text-muted d-block" style="font-size: 0.68rem;">
                        {{ lesson.enrollment_count }}/{{ lesson.course_capacity }} 人
                      </small>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile View (手機版顯示：支援單日(天) / 全週切換，預設依天顯示) -->
      <div v-if="!loading" class="d-lg-none">
        <!-- 顯示模式切換按鈕 (天 / 週) -->
        <div class="d-flex justify-content-between align-items-center mb-3">
          <span class="fw-bold small text-secondary">
            <i class="bi bi-phone me-1 text-primary"></i>課表檢視方式
          </span>
          <div class="btn-group btn-group-sm shadow-sm" role="group">
            <button
              type="button"
              class="btn"
              :class="mobileViewMode === 'day' ? 'btn-primary fw-bold' : 'btn-outline-secondary bg-white'"
              @click="mobileViewMode = 'day'"
            >
              <i class="bi bi-calendar-day me-1"></i>依單日 (天)
            </button>
            <button
              type="button"
              class="btn"
              :class="mobileViewMode === 'week' ? 'btn-primary fw-bold' : 'btn-outline-secondary bg-white'"
              @click="mobileViewMode = 'week'"
            >
              <i class="bi bi-calendar-week me-1"></i>整週
            </button>
          </div>
        </div>

        <!-- 模式一：單日 (天) 顯示 -->
        <div v-if="mobileViewMode === 'day'" class="mobile-day-view">
          <!-- 星期滑動選單 (可左右滑動點選) -->
          <div class="day-selector-wrapper mb-3">
            <div class="day-pills-scroll d-flex gap-2 pb-2">
              <button
                v-for="(day, dayIndex) in daysOfWeek"
                :key="dayIndex"
                type="button"
                class="btn day-pill flex-shrink-0 text-center"
                :class="selectedDayIndex === dayIndex ? 'btn-primary active-day' : 'btn-outline-secondary bg-white'"
                @click="selectedDayIndex = dayIndex"
              >
                <div class="small fw-bold">{{ day }}</div>
                <div class="day-date small opacity-75">{{ getDateForDay(dayIndex) }}</div>
                <span
                  class="badge rounded-pill mt-1"
                  :class="selectedDayIndex === dayIndex ? 'bg-light text-primary' : (getLessonsForDay(day).length > 0 ? 'bg-primary text-white' : 'bg-light text-muted border')"
                >
                  {{ getLessonsForDay(day).length > 0 ? `${getLessonsForDay(day).length} 堂` : '0' }}
                </span>
              </button>
            </div>
          </div>

          <!-- 前一天 / 當前天 / 後一天快速切換 -->
          <div class="d-flex justify-content-between align-items-center bg-white p-2 rounded-3 mb-3 border shadow-sm">
            <button
              class="btn btn-sm btn-outline-secondary px-2"
              :disabled="selectedDayIndex <= 0"
              @click="selectedDayIndex--"
            >
              <i class="bi bi-chevron-left me-1"></i>前一天
            </button>
            <div class="text-center">
              <strong class="d-block text-dark fs-6">
                {{ currentSelectedDayText }} ({{ getDateForDay(selectedDayIndex) }})
              </strong>
              <small class="text-primary fw-medium">
                {{ currentDayLessons.length > 0 ? `共 ${currentDayLessons.length} 門課程` : '本日尚無排課' }}
              </small>
            </div>
            <button
              class="btn btn-sm btn-outline-secondary px-2"
              :disabled="selectedDayIndex >= 6"
              @click="selectedDayIndex++"
            >
              後一天<i class="bi bi-chevron-right ms-1"></i>
            </button>
          </div>

          <!-- 當天課程卡片清單 -->
          <div v-if="currentDayLessons.length > 0" class="mobile-lessons-list">
            <div
              v-for="lesson in currentDayLessons"
              :key="lesson.schedule_id"
              class="schedule-card-mobile p-0 mb-3 rounded-3 cursor-pointer shadow-sm border overflow-hidden bg-white d-flex text-start"
              @click="openModal(lesson)"
            >
              <!-- 1/3 圖片區塊 (佔 3 分之一) -->
              <div class="card-img-col flex-shrink-0 position-relative" style="width: 33.333%; min-height: 115px;">
                <img 
                  v-if="lesson.teacher_avatar" 
                  :src="lesson.teacher_avatar" 
                  :alt="lesson.teacher" 
                  class="w-100 h-100 object-fit-cover d-block"
                />
                <div v-else class="w-100 h-100 d-flex flex-column align-items-center justify-content-center bg-light text-secondary">
                  <i class="bi bi-person-fill fs-1 text-muted"></i>
                </div>
              </div>

              <!-- 2/3 內容區塊 (佔 3 分之二) -->
              <div class="card-content-col p-3 d-flex flex-column justify-content-between flex-grow-1" style="width: 66.667%; min-width: 0;">
                <div>
                  <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="badge bg-light text-dark border px-2 py-1 small">
                      <i class="bi bi-clock me-1 text-primary"></i>{{ lesson.time }}
                    </span>
                    <span v-if="myEnrolledScheduleIds.includes(lesson.schedule_id)" class="badge bg-info text-dark">已預約</span>
                    <span v-else-if="lesson.is_past" class="badge bg-secondary">已結束</span>
                    <span v-else-if="lesson.allow_enrollment && !lesson.is_full" class="badge bg-success">可報名</span>
                    <span v-else-if="lesson.is_full" class="badge bg-warning text-dark">已滿額</span>
                    <span v-else class="badge bg-secondary">不開放</span>
                  </div>

                  <h5 class="fw-bold mb-1 text-dark">{{ lesson.name }}</h5>
                  <p class="mb-2 small text-muted">
                    <span class="fw-semibold text-dark"><i class="bi bi-person-fill me-1 text-primary"></i>{{ lesson.teacher || '未指定' }}</span>
                    <span class="mx-1">·</span>
                    <span>{{ lesson.level }}</span>
                    <span class="mx-1">·</span>
                    <span class="badge bg-secondary-subtle text-dark border py-0 px-1">{{ lesson.type }}</span>
                  </p>
                </div>

                <div class="d-flex justify-content-between align-items-center pt-2 border-top small text-muted">
                  <span>扣除：<strong class="text-primary">{{ lesson.course_price }}</strong> 堂</span>
                  <span><i class="bi bi-people me-1"></i><strong>{{ lesson.enrollment_count }}/{{ lesson.course_capacity }}</strong> 人</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 本日無排課友善提示 -->
          <div v-else class="text-center py-5 bg-white rounded-3 border text-muted shadow-sm">
            <i class="bi bi-calendar-x fs-1 d-block mb-2 text-secondary"></i>
            <h6 class="fw-bold text-dark mb-1">本日暫無排定課程</h6>
            <p class="small text-muted mb-3">您可以點選下方按鈕直接切換到有課程的日期：</p>
            <div class="d-flex flex-wrap justify-content-center gap-2 px-2">
              <button
                v-for="(day, idx) in daysOfWeek"
                :key="idx"
                v-show="getLessonsForDay(day).length > 0"
                class="btn btn-outline-primary btn-sm"
                @click="selectedDayIndex = idx"
              >
                {{ day }} ({{ getLessonsForDay(day).length }} 堂)
              </button>
            </div>
          </div>
        </div>

        <!-- 模式二：整週列表顯示 -->
        <div v-else class="mobile-week-view">
          <template v-for="(day, dayIndex) in daysOfWeek" :key="dayIndex">
            <div v-if="getLessonsForDay(day).length > 0" class="mb-4">
              <h5 class="text-center py-2 bg-light border rounded fw-bold text-dark">
                {{ day }} ({{ getDateForDay(dayIndex) }})
              </h5>
              <div
                v-for="lesson in getLessonsForDay(day)"
                :key="lesson.schedule_id"
                class="schedule-card-mobile p-0 mb-2 rounded-3 cursor-pointer shadow-sm border overflow-hidden bg-white d-flex text-start"
                @click="openModal(lesson)"
              >
                <!-- 1/3 圖片區塊 (佔 3 分之一) -->
                <div class="card-img-col flex-shrink-0 position-relative" style="width: 33.333%; min-height: 105px;">
                  <img 
                    v-if="lesson.teacher_avatar" 
                    :src="lesson.teacher_avatar" 
                    :alt="lesson.teacher" 
                    class="w-100 h-100 object-fit-cover d-block"
                  />
                  <div v-else class="w-100 h-100 d-flex flex-column align-items-center justify-content-center bg-light text-secondary">
                    <i class="bi bi-person-fill fs-2 text-muted"></i>
                  </div>
                </div>

                <!-- 2/3 內容區塊 (佔 3 分之二) -->
                <div class="card-content-col p-2 p-sm-3 d-flex flex-column justify-content-between flex-grow-1" style="width: 66.667%; min-width: 0;">
                  <div>
                    <div class="d-flex justify-content-between align-items-center mb-1">
                      <span class="badge bg-light text-dark border small fw-bold">{{ lesson.time }}</span>
                      <span v-if="myEnrolledScheduleIds.includes(lesson.schedule_id)" class="badge bg-info text-dark">已預約</span>
                      <span v-else-if="lesson.is_past" class="badge bg-secondary">已結束</span>
                      <span v-else-if="lesson.allow_enrollment && !lesson.is_full" class="badge bg-success">可報名</span>
                      <span v-else-if="lesson.is_full" class="badge bg-warning text-dark">已滿額</span>
                      <span v-else class="badge bg-secondary">不開放</span>
                    </div>
                    <h6 class="fw-bold mb-1 text-dark">{{ lesson.name }}</h6>
                    <p class="mb-1 small text-muted">
                      授課：<strong class="text-dark">{{ lesson.teacher || '未指定' }}</strong> | {{ lesson.level }} | {{ lesson.type }}
                    </p>
                  </div>
                  <div class="d-flex justify-content-between align-items-center pt-1 border-top small text-muted" style="font-size: 0.75rem;">
                    <span>扣除：{{ lesson.course_price }} 堂</span>
                    <span>{{ lesson.enrollment_count }}/{{ lesson.course_capacity }} 人</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
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
              <!-- 老師大頭貼與課程標題橫幅 -->
              <div class="d-flex align-items-center gap-3 p-3 bg-light rounded-3 mb-3 border">
                <img 
                  v-if="selectedLesson.teacher_avatar" 
                  :src="selectedLesson.teacher_avatar" 
                  :alt="selectedLesson.teacher" 
                  class="rounded-circle object-fit-cover border shadow-sm"
                  style="width: 58px; height: 58px;"
                />
                <div v-else class="rounded-circle bg-white text-secondary border d-flex align-items-center justify-content-center shadow-sm" style="width: 58px; height: 58px;">
                  <i class="bi bi-person-fill fs-2 text-muted"></i>
                </div>
                <div>
                  <h6 class="fw-bold mb-1 text-dark fs-5">{{ selectedLesson.name }}</h6>
                  <div class="text-primary fw-semibold small">
                    <i class="bi bi-person-badge me-1"></i>授課老師：{{ selectedLesson.teacher || '未指定' }}
                  </div>
                  <div class="text-muted small">
                    舞風：{{ selectedLesson.type }} · 難度：{{ selectedLesson.level }}
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <p class="mb-1" v-if="selectedLesson.schedule_date"><strong>上課日期：</strong>{{ selectedLesson.schedule_date }} ({{ selectedLesson.day }})</p>
                <p class="mb-1"><strong>上課時間：</strong>{{ selectedLesson.time }} <span v-if="!selectedLesson.schedule_date">({{ selectedLesson.day }})</span></p>
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
                <!-- 已重複報名提示 -->
                <div v-if="isAlreadyEnrolled" class="alert alert-info py-3 mb-0 border shadow-sm rounded-3">
                  <div class="d-flex align-items-center">
                    <i class="bi bi-check-circle-fill fs-3 me-3 text-primary"></i>
                    <div>
                      <h6 class="fw-bold mb-1 text-primary">您已成功預約此堂課程</h6>
                      <p class="small mb-0 text-muted">本時段課程已在您的預約清單中，無法重複預約。</p>
                    </div>
                  </div>
                </div>

                <!-- 過去課程提示 (昨天與昨天以前) -->
                <div v-else-if="selectedLesson.is_past" class="alert alert-secondary py-3 mb-0 border shadow-sm rounded-3">
                  <div class="d-flex align-items-center">
                    <i class="bi bi-clock-history fs-3 me-3 text-secondary"></i>
                    <div>
                      <h6 class="fw-bold mb-1 text-secondary">課程時段已結束</h6>
                      <p class="small mb-0 text-muted">此為過去的課程時段（昨天與昨天以前），目前已截止預約。</p>
                    </div>
                  </div>
                </div>

                <div v-else-if="selectedLesson.allow_enrollment && !selectedLesson.is_full">
                  <!-- 已登入學員狀態 -->
                  <div v-if="isLoggedIn && currentStudent" class="card border-primary mb-3 bg-light">
                    <div class="card-body p-3">
                      <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="text-muted small">登入學員：</span>
                        <strong class="text-dark">{{ currentStudent.name }}</strong>
                      </div>
                      <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="text-muted small">目前剩餘堂數：</span>
                        <span class="badge bg-primary fs-6">{{ currentStudent.remaining_classes ?? 0 }} 堂</span>
                      </div>
                      <div class="d-flex justify-content-between align-items-center text-muted small">
                        <span>預約扣除：</span>
                        <span class="text-danger fw-bold">-{{ selectedLesson.course_price || 1 }} 堂</span>
                      </div>
                    </div>
                  </div>

                  <!-- 未登入狀態 -->
                  <div v-else class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                      <label for="studentName" class="form-label small mb-0 fw-bold">學員姓名：</label>
                      <div class="small">
                        <button type="button" class="btn btn-link btn-sm p-0 text-decoration-none me-2" @click="handlePromptLogin">
                          <i class="bi bi-box-arrow-in-right me-1"></i>學員登入
                        </button>
                        <button type="button" class="btn btn-link btn-sm p-0 text-decoration-none text-success fw-bold" @click="handlePromptRegister">
                          <i class="bi bi-person-plus-fill me-1"></i>會員註冊
                        </button>
                      </div>
                    </div>
                    <input 
                      type="text" 
                      id="studentName" 
                      v-model="studentName" 
                      class="form-control" 
                      placeholder="請輸入您的姓名"
                      @keyup.enter="enrollLesson(selectedLesson)"
                      :disabled="enrolling"
                    />
                    <div class="form-text small text-muted">
                      若已有會員，建議先登入以同步堂數及預約紀錄。
                    </div>
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
                v-if="isAlreadyEnrolled"
                type="button" 
                class="btn btn-outline-primary" 
                disabled
              >
                <i class="bi bi-check-circle-fill me-1"></i>已預約此課程
              </button>
              <button
                v-else-if="selectedLesson?.is_past"
                type="button"
                class="btn btn-secondary"
                disabled
              >
                <i class="bi bi-clock-history me-1"></i>課程已結束
              </button>
              <button 
                v-else-if="selectedLesson?.allow_enrollment && !selectedLesson?.is_full"
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
import { useStudentAuth } from '@/utils/auth';

export default {
  name: 'Schedule',
  components: {
    PageBanner
  },
  data() {
    return {
      auth: useStudentAuth(),
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
      daysOfWeek: ['週日', '週一', '週二', '週三', '週四', '週五', '週六'],
      classes: [],
      selectedWeekStart: '',
      weekStartDate: null,
      weekEndDate: null,
      weekDates: [],
      mobileViewMode: 'day',
      selectedDayIndex: 0,
      myEnrolledScheduleIds: []
    };
  },
  watch: {
    currentStudent: {
      immediate: true,
      handler() {
        this.fetchMyEnrollments();
      }
    }
  },
  computed: {
    isLoggedIn() {
      return !!this.auth.state.student && !!this.auth.state.student.id;
    },
    currentStudent() {
      return this.auth.state.student;
    },
    isAlreadyEnrolled() {
      if (!this.selectedLesson || !this.isLoggedIn) return false;
      return this.myEnrolledScheduleIds.includes(this.selectedLesson.schedule_id);
    },
    currentSelectedDayText() {
      return this.daysOfWeek[this.selectedDayIndex] || '週日';
    },
    currentDayLessons() {
      return this.getLessonsForDay(this.currentSelectedDayText);
    },
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
    this.fetchMyEnrollments();
  },
  methods: {
    async fetchMyEnrollments() {
      if (this.isLoggedIn && this.currentStudent?.id) {
        try {
          const res = await api.get(`/student/${this.currentStudent.id}/enrollments`);
          if (res.success && Array.isArray(res.enrollments)) {
            this.myEnrolledScheduleIds = res.enrollments
              .filter(e => e.status === 'confirmed')
              .map(e => e.schedule_id);
          } else {
            this.myEnrolledScheduleIds = [];
          }
        } catch (e) {
          this.myEnrolledScheduleIds = [];
        }
      } else {
        this.myEnrolledScheduleIds = [];
      }
    },
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
          const todayStr = this.formatDateForAPI(new Date());
          this.classes = result.schedules.map(s => {
            const isPast = s.is_past !== undefined
              ? !!s.is_past
              : (s.schedule_date ? (s.schedule_date < todayStr) : false);
            return {
              time: this.findMatchingTimeSlot(s.start_time, s.end_time),
              originalStartTime: s.start_time,
              originalEndTime: s.end_time,
              day: this.getDayText(s.day_of_week),
              name: s.course_name,
              teacher: s.teacher_name || '',
              teacher_avatar: s.teacher_avatar_url || '',
              level: s.level,
              type: s.style_name || '未知舞風',
              allow_enrollment: !isPast && !!s.dynamic_allow_enrollment,
              is_past: isPast,
              schedule_date: s.schedule_date,
              schedule_id: s.id,
              course_price: s.course_price || 1,
              enrollment_count: s.enrollment_count || 0,
              course_capacity: s.course_capacity || 15,
              is_full: (s.enrollment_count || 0) >= (s.course_capacity || 15)
            };
          });
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
      const currentDay = today.getDay(); // 0 是週日, 1 是週一... 6 是週六
      const sundayOffset = -currentDay;
      const sunday = new Date(today);
      sunday.setDate(today.getDate() + sundayOffset);

      this.selectedWeekStart = this.formatDateForInput(sunday);
      this.selectedDayIndex = currentDay;
      this.calculateWeekDates();
    },
    calculateWeekDates() {
      if (!this.selectedWeekStart) return;
      const selectedDate = new Date(this.selectedWeekStart);
      const currentDay = selectedDate.getDay();
      const sundayOffset = -currentDay;
      const sunday = new Date(selectedDate);
      sunday.setDate(selectedDate.getDate() + sundayOffset);

      this.weekStartDate = new Date(sunday);
      this.weekEndDate = new Date(sunday);
      this.weekEndDate.setDate(sunday.getDate() + 6);

      this.weekDates = [];
      for (let i = 0; i < 7; i++) {
        const date = new Date(sunday);
        date.setDate(sunday.getDate() + i);
        this.weekDates.push(date);
      }
      this.selectedWeekStart = this.formatDateForInput(sunday);
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
      if (this.isLoggedIn && this.currentStudent) {
        this.studentName = this.currentStudent.name || '';
      } else {
        this.studentName = '';
      }
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.selectedLesson = null;
      this.studentName = '';
    },
    handlePromptLogin() {
      this.closeModal();
      this.auth.openLoginModal();
    },
    handlePromptRegister() {
      this.closeModal();
      this.auth.openRegisterModal();
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
      if (lesson.is_past) {
        showToast('無法預約過去的課程時段（昨天與昨天以前不開放預約）！', 'warning');
        return;
      }
      if (this.isAlreadyEnrolled) {
        showToast('您已經預約過此時段課程，無法重複報名！', 'warning');
        return;
      }
      if (!lesson.allow_enrollment) {
        showToast('很抱歉，此課程目前不開放線上預約！', 'warning');
        return;
      }
      if (lesson.is_full) {
        showToast('很抱歉，此課程報名人數已額滿！', 'warning');
        return;
      }

      const bookingName = (this.isLoggedIn && this.currentStudent)
        ? this.currentStudent.name
        : this.studentName.trim();

      if (!bookingName) {
        showToast('請輸入您的姓名！', 'warning');
        return;
      }

      this.enrolling = true;
      try {
        const payload = {
          studentName: bookingName,
          student_name: bookingName,
          schedule_id: lesson.schedule_id,
          lesson: {
            name: lesson.name,
            time: lesson.time,
            day: lesson.day,
            teacher: lesson.teacher,
            level: lesson.level,
            type: lesson.type
          }
        };
        const result = await api.post(API_ENDPOINTS.ENROLLMENTS, payload);
        if (result.success) {
          showToast('預約報名成功！期待在課堂上遇見您。', 'success');
          // If logged in, refresh profile to update remaining classes and enrollments
          if (this.isLoggedIn) {
            await this.auth.refreshProfile();
            await this.fetchMyEnrollments();
          }
          this.closeModal();
          this.fetchSchedule();
        } else {
          showToast(`報名失敗：${result.error || '請稍後重試'}`, 'error');
        }
      } catch (error) {
        console.error('報名失敗:', error);
        showToast(error.message || '預約報名失敗，請稍後重試！', 'error');
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
  background: #ffffff;
  color: #212529;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  margin-bottom: 6px;
  min-height: 90px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.schedule-cell:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
  border-color: #adb5bd;
}

.schedule-card-mobile {
  background: #ffffff !important;
  color: #212529 !important;
  border: 1px solid #dee2e6;
  transition: all 0.2s ease;
}

.schedule-card-mobile:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
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

/* 行動版單日切換選單樣式 */
.day-selector-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.day-pills-scroll {
  display: flex;
  overflow-x: auto;
  scroll-behavior: smooth;
  padding-bottom: 4px;
}
.day-pills-scroll::-webkit-scrollbar {
  height: 4px;
}
.day-pills-scroll::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}
.day-pill {
  min-width: 78px;
  padding: 0.5rem 0.35rem;
  border-radius: 0.75rem;
  transition: all 0.2s ease;
  line-height: 1.2;
}
.day-pill.active-day {
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.35) !important;
  transform: translateY(-2px);
}

.schedule-cell-avatar {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}

.schedule-mobile-avatar {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}
</style>
