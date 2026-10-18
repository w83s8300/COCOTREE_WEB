<template>
  <div class="schedules">
    <!-- 標題和新增按鈕 -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>課程時間表管理</h2>
      <button @click="addNewSchedule" class="btn btn-success">
        <i class="bi bi-plus-lg me-1"></i>新增課程時間表
      </button>
    </div>

    <div class="container my-3 px-0">
      <!-- 控制面板：檢視切換與日期導航 -->
      <div class="card p-3 mb-4 shadow-sm border-0 bg-light">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
          <!-- 檢視模式切換：月顯示 / 週顯示 -->
          <div class="btn-group shadow-sm" role="group" aria-label="檢視切換">
            <button
              type="button"
              class="btn"
              :class="viewMode === 'month' ? 'btn-primary' : 'btn-outline-primary'"
              @click="setViewMode('month')"
            >
              <i class="bi bi-calendar3 me-1"></i>月顯示
            </button>
            <button
              type="button"
              class="btn"
              :class="viewMode === 'week' ? 'btn-primary' : 'btn-outline-primary'"
              @click="setViewMode('week')"
            >
              <i class="bi bi-calendar-week me-1"></i>週顯示
            </button>
          </div>

          <!-- 月顯示控制項 -->
          <div v-if="viewMode === 'month'" class="d-flex align-items-center flex-wrap gap-2">
            <div class="btn-group" role="group">
              <button class="btn btn-outline-secondary btn-sm" @click="prevMonth" title="上個月">
                <i class="bi bi-chevron-left"></i> 上個月
              </button>
              <button class="btn btn-outline-secondary btn-sm" @click="thisMonth" title="回到本月">
                本月
              </button>
              <button class="btn btn-outline-secondary btn-sm" @click="nextMonth" title="下個月">
                下個月 <i class="bi bi-chevron-right"></i>
              </button>
            </div>
            <input 
              type="month" 
              v-model="selectedMonth" 
              class="form-control form-control-sm w-auto" 
              @change="onMonthChange"
              title="選擇月份"
            />
            <span class="fw-bold text-dark ms-1">
              {{ formatMonthDisplay(monthStartDate) }}
            </span>
          </div>

          <!-- 週顯示控制項 -->
          <div v-else class="d-flex align-items-center flex-wrap gap-2">
            <div class="btn-group" role="group">
              <button class="btn btn-outline-secondary btn-sm" @click="prevWeek" title="上一週">
                <i class="bi bi-chevron-left"></i> 上一週
              </button>
              <button class="btn btn-outline-secondary btn-sm" @click="thisWeek" title="回到本週">
                本週
              </button>
              <button class="btn btn-outline-secondary btn-sm" @click="nextWeek" title="下一週">
                下一週 <i class="bi bi-chevron-right"></i>
              </button>
            </div>
            <input 
              type="date" 
              v-model="selectedWeekDate" 
              class="form-control form-control-sm w-auto" 
              @change="onWeekDateChange"
              title="選擇任意日期跳轉至該週"
            />
            <span class="fw-bold text-dark ms-1">
              {{ formatWeekRange(weekStartDate, weekEndDate) }}
            </span>
          </div>
        </div>
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

      <!-- 無排程資料提示 -->
      <div v-else-if="filteredSchedules.length === 0" class="alert alert-info text-center my-4 py-4 shadow-sm border-0">
        <i class="bi bi-calendar-x fs-2 d-block mb-2 text-primary"></i>
        <h5 class="fw-bold">此時段尚無排程</h5>
        <p class="text-muted mb-3">此{{ viewMode === 'week' ? '週' : '月份' }}目前沒有安排任何課程時間表。</p>
        <button @click="addNewSchedule" class="btn btn-primary btn-sm">
          <i class="bi bi-plus-lg me-1"></i>立即新增排程
        </button>
      </div>

      <!-- 桌面版表格 (O(1) 矩陣快速查詢) -->
      <div v-else class="table-responsive d-none d-lg-block">
        <table class="table table-bordered table-striped text-center schedule-table align-middle">
          <thead class="table-dark">
            <tr>
              <th scope="col" style="width: 110px;">時間</th>
              <th 
                scope="col" 
                v-for="(day, index) in daysOfWeek" 
                :key="index"
                :class="{ 'bg-primary bg-gradient': isDayToday(index) }"
                style="min-width: 140px;"
              >
                <div class="d-flex flex-column align-items-center py-1">
                  <span class="fs-6">
                    {{ day }}
                    <span v-if="isDayToday(index)" class="badge bg-warning text-dark ms-1" style="font-size: 0.65rem;">今日</span>
                  </span>
                  <small :class="viewMode === 'week' ? 'text-warning fw-bold mt-1' : 'text-light-50 mt-1'">
                    <span v-if="viewMode === 'week'">{{ getDateForDay(index) }}</span>
                    <span v-else>{{ getDateForDay(index) }} 日</span>
                  </small>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(timeSlot, timeIndex) in timeSlots" :key="timeIndex">
              <td class="time-slot">{{ timeSlot }}</td>
              <td 
                v-for="(day, dayIndex) in daysOfWeek" 
                :key="dayIndex"
                :class="{ 'table-primary bg-opacity-10': isDayToday(dayIndex) }"
              >
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
                  <p class="schedule-teacher d-flex align-items-center justify-content-center gap-1">
                    <img 
                      v-if="schedule.teacher_avatar_url" 
                      :src="schedule.teacher_avatar_url" 
                      :alt="schedule.teacher_name" 
                      class="rounded-circle object-fit-cover border border-white border-opacity-75 shadow-sm" 
                      style="width: 20px; height: 20px;" 
                    />
                    <span>{{ schedule.teacher_name }}</span>
                  </p>
                  <p class="schedule-level">{{ schedule.level }}</p>
                  <div class="enrollment-info mb-1">
                    <small>報名人數：{{ schedule.enrollment_count || 0 }}/{{ schedule.course_capacity || 15 }}人</small>
                  </div>
                  <div class="salary-tag mb-2" v-if="canViewScheduleSalary(schedule)">
                    <span class="badge bg-light text-primary border border-primary-subtle shadow-sm py-1 px-2" style="font-size: 0.72rem;">
                      <i class="bi bi-cash-coin me-1"></i>目前費用: ${{ getScheduleSalary(schedule).total }}
                    </span>
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
      <div v-if="!loading && filteredSchedules.length > 0" class="d-lg-none">
        <template v-for="(day, dayIndex) in daysOfWeek" :key="dayIndex">
          <div v-if="getSchedulesForDay(day).length > 0" class="mb-4">
            <h4 class="text-center py-2 bg-light border rounded d-flex justify-content-center align-items-center gap-2">
              <span>{{ day }}</span>
              <span class="badge bg-secondary" v-if="viewMode === 'week'">{{ getDateForDay(dayIndex) }}</span>
              <span class="badge bg-secondary" v-else>{{ getDateForDay(dayIndex) }} 日</span>
              <span v-if="isDayToday(dayIndex)" class="badge bg-danger">今日</span>
            </h4>
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
                <p class="schedule-teacher mb-1 d-flex align-items-center gap-1">
                  <img 
                    v-if="schedule.teacher_avatar_url" 
                    :src="schedule.teacher_avatar_url" 
                    :alt="schedule.teacher_name" 
                    class="rounded-circle object-fit-cover border border-white border-opacity-75 shadow-sm" 
                    style="width: 24px; height: 24px;" 
                  />
                  <span>授課：{{ schedule.teacher_name }} | {{ schedule.level }}</span>
                </p>
                <div class="enrollment-info mb-1">
                  <small>報名人數：{{ schedule.enrollment_count || 0 }}/{{ schedule.course_capacity || 15 }}人</small>
                </div>
                <div class="salary-tag mb-2" v-if="canViewScheduleSalary(schedule)">
                  <span class="badge bg-light text-primary border border-primary-subtle shadow-sm py-1 px-2">
                    <i class="bi bi-cash-coin me-1"></i>目前費用: ${{ getScheduleSalary(schedule).total }}
                  </span>
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
            <h5 class="modal-title" id="enrollmentModalLabel">{{ canViewScheduleSalary(selectedSchedule) ? '課程報名人員與費用明細' : '課程報名人員名冊' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedSchedule">
              <!-- 目前費用 / 師資薪資大字牌 (僅管理員或該堂授課老師本人可見) -->
              <div v-if="canViewScheduleSalary(selectedSchedule)" class="card border-0 bg-primary bg-opacity-10 mb-4 p-3 rounded-3 shadow-sm">
                <div class="d-flex flex-wrap justify-content-between align-items-center pb-2 mb-2 border-bottom border-primary-subtle">
                  <div class="d-flex align-items-center">
                    <span class="badge bg-primary me-2 fs-6"><i class="bi bi-cash-coin me-1"></i>目前費用</span>
                    <strong class="fs-5 text-dark">師資授課鐘點費</strong>
                  </div>
                  <div class="text-end">
                    <span class="text-muted small me-2">目前累計：</span>
                    <span class="fs-2 fw-bold text-primary">NT$ {{ teacherSalary.total.toLocaleString() }}</span>
                  </div>
                </div>

                <div class="row g-2 small text-secondary">
                  <div :class="teacherSalary.lowStudentThreshold > 0 ? 'col-6 col-md-2' : 'col-sm-6 col-md-3'">
                    <div class="p-2 bg-white rounded border">
                      <div class="text-muted">標準底金</div>
                      <div class="fw-bold text-dark fs-6">NT$ {{ teacherSalary.base }}</div>
                    </div>
                  </div>
                  <div v-if="teacherSalary.lowStudentThreshold > 0" class="col-6 col-md-3">
                    <div class="p-2 bg-white rounded border" :class="{'border-warning bg-warning bg-opacity-10': teacherSalary.isLowTier}">
                      <div class="text-muted">低額門檻規則</div>
                      <div class="fw-bold text-dark fs-6">
                        ≤ {{ teacherSalary.lowStudentThreshold }} 人: NT$ {{ teacherSalary.lowStudentSalary }}
                        <span v-if="teacherSalary.isLowTier" class="badge bg-warning text-dark ms-1">生效中</span>
                      </div>
                    </div>
                  </div>
                  <div :class="teacherSalary.lowStudentThreshold > 0 ? 'col-6 col-md-2' : 'col-sm-6 col-md-3'">
                    <div class="p-2 bg-white rounded border">
                      <div class="text-muted">已確認人數</div>
                      <div class="fw-bold text-dark fs-6">{{ teacherSalary.studentCount }} 人</div>
                    </div>
                  </div>
                  <div :class="teacherSalary.lowStudentThreshold > 0 ? 'col-6 col-md-3' : 'col-sm-6 col-md-3'">
                    <div class="p-2 bg-white rounded border">
                      <div class="text-muted">加成條件</div>
                      <div class="fw-bold text-dark fs-6">
                        <template v-if="teacherSalary.feePerStudent > 0">
                          > {{ teacherSalary.threshold }} 人 (+${{ teacherSalary.feePerStudent }}/人)
                        </template>
                        <template v-else>無人數加成</template>
                      </div>
                    </div>
                  </div>
                  <div :class="teacherSalary.lowStudentThreshold > 0 ? 'col-6 col-md-2' : 'col-sm-6 col-md-3'">
                    <div class="p-2 bg-white rounded border">
                      <div class="text-muted">超額加發金額</div>
                      <div class="fw-bold text-success fs-6">+ NT$ {{ teacherSalary.extraBonus }}</div>
                    </div>
                  </div>
                </div>

                <!-- 規則明細提示與上限說明 -->
                <div class="mt-2 pt-2 border-top border-primary-subtle d-flex flex-wrap justify-content-between align-items-center small">
                  <span class="text-muted">
                    <i class="bi bi-calculator me-1 text-primary"></i>
                    <strong>計算公式：</strong>
                    <template v-if="teacherSalary.studentCount === 0">
                      目前尚無人報名，鐘點費用為 NT$ 0（底金 NT${{ teacherSalary.base }} 於有學員報名後生效）
                    </template>
                    <template v-else-if="teacherSalary.isLowTier">
                      目前報名 {{ teacherSalary.studentCount }} 人（符合 {{ teacherSalary.lowStudentThreshold }} 人以下規則），鐘點費固定為 NT$ {{ teacherSalary.lowStudentSalary }}
                    </template>
                    <template v-else>
                      底金 NT${{ teacherSalary.base }}
                      <template v-if="teacherSalary.feePerStudent > 0">
                        + 超過 {{ teacherSalary.threshold }} 人（多 {{ teacherSalary.extraStudents }} 人 × NT${{ teacherSalary.feePerStudent }}）
                      </template>
                      = NT${{ teacherSalary.totalBeforeCap }}
                    </template>
                  </span>
                  <div class="mt-1 mt-md-0">
                    <span v-if="!teacherSalary.cap || teacherSalary.cap === 0" class="badge bg-success-subtle text-success border border-success-subtle">
                      無費用上限 (上限0)
                    </span>
                    <span v-else-if="teacherSalary.isCapped" class="badge bg-danger">
                      已達上限 NT$ {{ teacherSalary.cap }}
                    </span>
                    <span v-else class="badge bg-secondary-subtle text-dark border">
                      上限 NT$ {{ teacherSalary.cap }}
                    </span>
                  </div>
                </div>
              </div>

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
                    <p class="mb-1 d-flex align-items-center gap-2">
                      <strong>授課老師：</strong>
                      <img 
                        v-if="selectedSchedule.teacher_avatar_url" 
                        :src="selectedSchedule.teacher_avatar_url" 
                        :alt="selectedSchedule.teacher_name" 
                        class="rounded-circle object-fit-cover border shadow-sm" 
                        style="width: 24px; height: 24px;" 
                      />
                      <span>{{ selectedSchedule.teacher_name || '未指定' }}</span>
                    </p>
                    <p class="mb-1"><strong>教室：</strong>{{ selectedSchedule.room_name || '未指定' }}</p>
                    <p class="mb-1"><strong>已確認學員：</strong>{{ confirmedStudentCount }}/{{ selectedSchedule.course_capacity || 15 }}人</p>
                  </div>
                </div>
              </div>

              <!-- 報名人員列表 -->
              <div class="enrollment-list">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h6 class="fw-bold mb-0">
                    <i class="bi bi-people-fill me-1 text-primary"></i>報名人員名冊 (共 {{ enrollmentList.length }} 人)
                  </h6>
                  <button 
                    type="button" 
                    class="btn btn-sm"
                    :class="showAddStudentPanel ? 'btn-outline-secondary' : 'btn-primary'"
                    @click="openAddStudentPanel"
                  >
                    <i :class="showAddStudentPanel ? 'bi bi-x-lg me-1' : 'bi bi-person-plus-fill me-1'"></i>
                    {{ showAddStudentPanel ? '收起表單' : '直接加學生' }}
                  </button>
                </div>

                <!-- 直接加學生表單卡片 -->
                <div v-if="showAddStudentPanel" class="card border border-primary-subtle bg-light mb-3 shadow-sm rounded-3">
                  <div class="card-header bg-white d-flex justify-content-between align-items-center py-2">
                    <strong class="text-primary small"><i class="bi bi-person-plus-fill me-1"></i>為此課程時段新增學員</strong>
                    <button type="button" class="btn-close btn-sm" @click="showAddStudentPanel = false"></button>
                  </div>
                  <div class="card-body py-3">
                    <form @submit.prevent="submitAddStudent">
                      <div class="row g-3">
                        <!-- 選擇學員 -->
                        <div class="col-md-7">
                          <label class="form-label fw-semibold small">選擇現有學員：</label>
                          <select class="form-select form-select-sm" v-model="addStudentForm.student_id" @change="onStudentSelectChange" required>
                            <option value="" disabled>-- 請選擇學員 --</option>
                            <option v-for="stu in allStudents" :key="stu.id" :value="stu.id">
                              {{ stu.name }} (電話: {{ stu.phone || '未填' }} | 剩餘: {{ stu.remaining_classes ?? 0 }} 堂)
                            </option>
                            <option value="custom">＋ 非系統名單學員（手動輸入姓名）</option>
                          </select>

                          <!-- 若為手動自行輸入姓名 -->
                          <div v-if="addStudentForm.student_id === 'custom'" class="mt-2">
                            <input 
                              type="text" 
                              class="form-control form-control-sm" 
                              placeholder="請輸入學員姓名 (例如: 訪客/體驗學員)" 
                              v-model="addStudentForm.custom_name" 
                              required
                            />
                            <div class="form-text small text-muted">手動輸入之學員將不扣除系統帳號堂數。</div>
                          </div>
                          <div v-else-if="selectedStudentInfo" class="mt-1 small">
                            目前剩餘堂數：<strong :class="selectedStudentInfo.remaining_classes > 0 ? 'text-success' : 'text-danger'">
                              {{ selectedStudentInfo.remaining_classes ?? 0 }} 堂
                            </strong>
                          </div>
                        </div>

                        <!-- 是否扣堂數與扣幾堂 -->
                        <div class="col-md-5">
                          <label class="form-label fw-semibold small">堂數扣除設定：</label>
                          <div class="form-check form-switch mb-2">
                            <input 
                              class="form-check-input" 
                              type="checkbox" 
                              id="deductToggle" 
                              v-model="addStudentForm.deduct_classes"
                              :disabled="addStudentForm.student_id === 'custom'"
                            >
                            <label class="form-check-label small fw-semibold" for="deductToggle">
                              {{ addStudentForm.deduct_classes ? '扣除學員堂數' : '不扣除堂數 (0 堂)' }}
                            </label>
                          </div>
                          <div v-if="addStudentForm.deduct_classes" class="input-group input-group-sm">
                            <span class="input-group-text">扣除</span>
                            <input 
                              type="number" 
                              class="form-control" 
                              v-model.number="addStudentForm.deducted_classes" 
                              min="1" 
                              step="1"
                              required
                            >
                            <span class="input-group-text">堂</span>
                          </div>
                          <div v-else class="text-muted small">
                            <i class="bi bi-info-circle me-1"></i>本筆報名不扣堂數（0 堂，適用體驗/補課/免費招待）。
                          </div>
                        </div>
                      </div>

                      <div class="mt-3 text-end">
                        <button type="button" class="btn btn-secondary btn-sm me-2" @click="showAddStudentPanel = false">取消</button>
                        <button type="submit" class="btn btn-primary btn-sm" :disabled="submittingStudent">
                          <span v-if="submittingStudent" class="spinner-border spinner-border-sm me-1" role="status"></span>
                          <i v-else class="bi bi-check-lg me-1"></i>確認加入學員
                        </button>
                      </div>
                    </form>
                  </div>
                </div>

                <div v-if="enrollmentList.length === 0" class="alert alert-info">
                  目前此時段尚無學員報名。
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover align-middle">
                    <thead>
                      <tr>
                        <th>學員姓名</th>
                        <th>扣除堂數</th>
                        <th>報名時間</th>
                        <th>狀態</th>
                        <th>操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="enrollment in enrollmentList" :key="enrollment.enrollment_id">
                        <td class="fw-bold">{{ enrollment.student_name }}</td>
                        <td>
                          <span v-if="enrollment.deducted_classes > 0" class="badge bg-primary-subtle text-primary border border-primary-subtle">
                            扣 {{ enrollment.deducted_classes }} 堂
                          </span>
                          <span v-else class="badge bg-light text-secondary border">
                            不扣堂 (0堂)
                          </span>
                        </td>
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
import { useAdminAuth } from '@/utils/adminAuth';

export default {
  name: 'Schedules',
  components: {
    AddSchedule
  },
  data() {
    return {
      adminAuth: useAdminAuth(),
      // 檢視模式：'month' (月顯示) 或 'week' (週顯示)
      viewMode: localStorage.getItem('schedules_view_mode') || 'month',

      // 月顯示相關狀態
      selectedMonth: '',
      monthStartDate: null,
      monthEndDate: null,
      monthDates: [],

      // 週顯示相關狀態
      selectedWeekDate: '',
      weekStartDate: null,
      weekEndDate: null,
      activeWeekDates: [],

      schedules: [],
      loading: false,
      showEditModal: false,
      editingScheduleId: null,
      editModal: null,
      selectedDateForAdd: null,
      
      // 報名名冊查看與手動加學生
      enrollmentModal: null,
      selectedSchedule: null,
      enrollmentList: [],
      allStudents: [],
      showAddStudentPanel: false,
      submittingStudent: false,
      addStudentForm: {
        student_id: '',
        custom_name: '',
        deduct_classes: true,
        deducted_classes: 1
      },
      
      // 表格篩選與時段
      danceTypes: ['全部'],
      selectedDanceType: '全部',
      timeSlots: [
        '09:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00',
        '14:00 - 15:00', '15:00 - 16:00', '18:00 - 19:00',
        '19:00 - 20:00', '20:00 - 21:00', '21:00 - 22:00'
      ],
      daysOfWeek: ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
    };
  },
  computed: {
    canViewSalary() {
      return this.adminAuth.canViewSalary;
    },
    confirmedStudentCount() {
      return (this.enrollmentList || []).filter(e => e.status === 'confirmed').length;
    },
    selectedStudentInfo() {
      if (!this.addStudentForm.student_id || this.addStudentForm.student_id === 'custom') return null;
      return this.allStudents.find(s => s.id === this.addStudentForm.student_id) || null;
    },
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
    // 預計算二維矩陣 O(1) 查詢
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
    },
    // 當前選取課程時間表的師資鐘點費用計算
    teacherSalary() {
      if (!this.selectedSchedule) {
        return {
          total: 0,
          totalBeforeCap: 0,
          base: 0,
          lowStudentThreshold: 0,
          lowStudentSalary: 0,
          isLowTier: false,
          threshold: 0,
          feePerStudent: 0,
          extraStudents: 0,
          extraBonus: 0,
          cap: 0,
          isCapped: false,
          studentCount: 0
        };
      }
      // 計算已確認報名的學員人數
      const confirmedCount = this.enrollmentList.filter(e => e.status === 'confirmed').length;
      return this.calculateSalary(this.selectedSchedule, confirmedCount);
    }
  },
  created() {
    this.initializeDates();
    this.fetchDanceTypes();
    this.fetchSchedules();
    this.fetchStudents();
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
  },
  beforeUnmount() {
    if (this.editModal) this.editModal.dispose();
    if (this.enrollmentModal) this.enrollmentModal.dispose();
  },
  methods: {
    // 切換月/週檢視模式
    setViewMode(mode) {
      if (this.viewMode === mode) return;
      this.viewMode = mode;
      try {
        localStorage.setItem('schedules_view_mode', mode);
      } catch (e) {
        // 忽略 localStorage 不可用情況
      }

      if (mode === 'week') {
        // 從月轉週：若該月份包含今天則跳到本週，否則跳到該月第 1 週
        const today = new Date();
        const [y, m] = this.selectedMonth.split('-').map(Number);
        if (today.getFullYear() === y && today.getMonth() + 1 === m) {
          this.calculateWeekDates(today);
        } else {
          this.calculateWeekDates(new Date(y, m - 1, 1));
        }
      } else {
        // 從週轉月：以當週週一所屬月份為基準
        const ref = this.weekStartDate || new Date();
        const y = ref.getFullYear();
        const m = String(ref.getMonth() + 1).padStart(2, '0');
        this.selectedMonth = `${y}-${m}`;
        this.calculateMonthDates();
      }
      this.fetchSchedules();
    },

    // 日期初始化
    initializeDates() {
      const today = new Date();

      // 初始化月
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      this.selectedMonth = `${year}-${month}`;
      this.calculateMonthDates();

      // 初始化週 (週一至週日)
      this.calculateWeekDates(today);
    },

    // 計算指定日期所在週的日期清單 (週日至週六)
    calculateWeekDates(referenceDate) {
      const ref = referenceDate ? new Date(referenceDate) : new Date();
      const day = ref.getDay(); // 0 是週日, 1 是週一...
      const sundayOffset = -day;
      const sunday = new Date(ref);
      sunday.setDate(ref.getDate() + sundayOffset);
      sunday.setHours(0, 0, 0, 0);

      this.activeWeekDates = [];
      for (let i = 0; i < 7; i++) {
        const d = new Date(sunday);
        d.setDate(sunday.getDate() + i);
        this.activeWeekDates.push(d);
      }

      this.weekStartDate = this.activeWeekDates[0];
      this.weekEndDate = this.activeWeekDates[6];
      this.selectedWeekDate = this.formatDateForInput(ref);
    },

    // 計算當前月份的所有日期
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

    onWeekDateChange() {
      if (!this.selectedWeekDate) return;
      this.calculateWeekDates(this.selectedWeekDate);
      this.fetchSchedules();
    },

    // 月份快捷切換
    prevMonth() {
      const [year, month] = this.selectedMonth.split('-').map(Number);
      const d = new Date(year, month - 2, 1);
      this.selectedMonth = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      this.calculateMonthDates();
      this.fetchSchedules();
    },
    nextMonth() {
      const [year, month] = this.selectedMonth.split('-').map(Number);
      const d = new Date(year, month, 1);
      this.selectedMonth = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      this.calculateMonthDates();
      this.fetchSchedules();
    },
    thisMonth() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      this.selectedMonth = `${year}-${month}`;
      this.calculateMonthDates();
      this.fetchSchedules();
    },

    // 週快捷切換
    prevWeek() {
      const d = new Date(this.weekStartDate);
      d.setDate(d.getDate() - 7);
      this.calculateWeekDates(d);
      this.fetchSchedules();
    },
    nextWeek() {
      const d = new Date(this.weekStartDate);
      d.setDate(d.getDate() + 7);
      this.calculateWeekDates(d);
      this.fetchSchedules();
    },
    thisWeek() {
      this.calculateWeekDates(new Date());
      this.fetchSchedules();
    },

    // 格式化顯示文字
    formatMonthDisplay(date) {
      if (!date) return '';
      return `${date.getFullYear()}年${date.getMonth() + 1}月`;
    },
    formatWeekRange(startDate, endDate) {
      if (!startDate || !endDate) return '';
      const sY = startDate.getFullYear();
      const sM = String(startDate.getMonth() + 1).padStart(2, '0');
      const sD = String(startDate.getDate()).padStart(2, '0');
      const eY = endDate.getFullYear();
      const eM = String(endDate.getMonth() + 1).padStart(2, '0');
      const eD = String(endDate.getDate()).padStart(2, '0');
      if (sY === eY) {
        return `${sY}/${sM}/${sD} (週一) ～ ${eM}/${eD} (週日)`;
      }
      return `${sY}/${sM}/${sD} (週一) ～ ${eY}/${eM}/${eD} (週日)`;
    },

    // 判斷某一天是否為今天
    isSameDay(d1, d2) {
      if (!d1 || !d2) return false;
      return d1.getFullYear() === d2.getFullYear() &&
             d1.getMonth() === d2.getMonth() &&
             d1.getDate() === d2.getDate();
    },
    isDayToday(dayIndex) {
      const today = new Date();
      if (this.viewMode === 'week') {
        if (!this.activeWeekDates[dayIndex]) return false;
        return this.isSameDay(this.activeWeekDates[dayIndex], today);
      } else {
        if (!this.monthStartDate || !this.monthEndDate) return false;
        if (today < this.monthStartDate || today > this.monthEndDate) return false;
        return today.getDay() === dayIndex;
      }
    },

    // 取得指定星期在表頭中的日期文字
    getDateForDay(dayIndex) {
      if (this.viewMode === 'week') {
        if (!this.activeWeekDates[dayIndex]) return '';
        const d = this.activeWeekDates[dayIndex];
        return `${d.getMonth() + 1}/${d.getDate()}`;
      } else {
        if (!this.monthDates.length) return '';
        const dates = this.monthDates.filter(d => d.getDay() === dayIndex);
        if (!dates.length) return '';
        return dates.map(d => d.getDate()).join(',');
      }
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
        'Ballet': 'bg-contemporary',
        'Hip-Hop': 'bg-hiphop',
        'Hip Hop': 'bg-hiphop',
        'Jazz': 'bg-jazz',
        'K-POP': 'bg-kpop',
        'Locking': 'bg-locking',
        'Waacking': 'bg-waacking',
        'Breaking': 'bg-breaking',
        'Popping': 'bg-popping',
        'Heels': 'bg-heels',
        'Contemporary': 'bg-contemporary',
        'Modern': 'bg-locking',
        'Street Dance': 'bg-hiphop',
        'Vogue': 'bg-vogue',
        'Street Jazz': 'bg-jazz'
      };
      return classMap[type] || 'bg-secondary';
    },

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
        const startDate = this.viewMode === 'week' ? this.weekStartDate : this.monthStartDate;
        const endDate = this.viewMode === 'week' ? this.weekEndDate : this.monthEndDate;

        if (startDate && endDate) {
          const start_date = this.formatDateForAPI(startDate);
          const end_date = this.formatDateForAPI(endDate);
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

    addNewSchedule() {
      this.editingScheduleId = null;
      this.selectedDateForAdd = this.viewMode === 'week' ? this.formatDateForAPI(new Date()) : null;
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
          this.fetchStudents();
        } else {
          showToast(`取消報名失敗：${data.error || '未知錯誤'}`, 'error');
        }
      } catch (error) {
        console.error('取消報名失敗:', error);
        showToast('取消報名失敗，請稍後再試', 'error');
      }
    },
    async fetchStudents() {
      try {
        const data = await api.get(API_ENDPOINTS.STUDENTS);
        this.allStudents = data.students || [];
      } catch (error) {
        console.error('獲取學員列表失敗:', error);
      }
    },
    openAddStudentPanel() {
      if (!this.allStudents.length) {
        this.fetchStudents();
      }
      const defaultDeducted = Math.max(1, parseInt(this.selectedSchedule?.course_price) || 1);
      this.addStudentForm = {
        student_id: '',
        custom_name: '',
        deduct_classes: true,
        deducted_classes: defaultDeducted
      };
      this.showAddStudentPanel = !this.showAddStudentPanel;
    },
    onStudentSelectChange() {
      if (this.addStudentForm.student_id === 'custom') {
        this.addStudentForm.deduct_classes = false;
        this.addStudentForm.deducted_classes = 0;
      } else {
        const defaultDeducted = Math.max(1, parseInt(this.selectedSchedule?.course_price) || 1);
        this.addStudentForm.deduct_classes = true;
        this.addStudentForm.deducted_classes = defaultDeducted;
      }
    },
    async submitAddStudent() {
      if (!this.selectedSchedule?.schedule_id) return;

      let studentId = this.addStudentForm.student_id;
      let studentName = '';

      if (studentId === 'custom') {
        studentName = (this.addStudentForm.custom_name || '').trim();
        if (!studentName) {
          showToast('請輸入學員姓名', 'error');
          return;
        }
        studentId = null;
      } else {
        const student = this.selectedStudentInfo;
        if (!student) {
          showToast('請先選擇學員', 'error');
          return;
        }
        studentName = student.name;
      }

      const deductClasses = this.addStudentForm.deduct_classes;
      const deductedClasses = deductClasses ? Math.max(0, parseInt(this.addStudentForm.deducted_classes) || 0) : 0;

      // 檢查剩餘堂數是否充足
      if (deductClasses && deductedClasses > 0 && this.selectedStudentInfo) {
        const remaining = this.selectedStudentInfo.remaining_classes || 0;
        if (remaining < deductedClasses) {
          showToast(`學員【${studentName}】剩餘堂數不足！（目前剩餘 ${remaining} 堂，欲扣除 ${deductedClasses} 堂）`, 'error');
          return;
        }
      }

      this.submittingStudent = true;
      try {
        const res = await api.post(`${API_ENDPOINTS.SCHEDULES}/${this.selectedSchedule.schedule_id}/enrollments`, {
          student_id: studentId,
          student_name: studentName,
          deduct_classes: deductClasses,
          deducted_classes: deductedClasses
        });

        if (res.success) {
          showToast(res.message || '學員報名成功！', 'success');
          this.showAddStudentPanel = false;
          // 重新載入報名名單與試算
          const enrollData = await api.get(`${API_ENDPOINTS.SCHEDULES}/${this.selectedSchedule.schedule_id}/enrollments`);
          if (enrollData.success) {
            this.selectedSchedule = enrollData.schedule;
            this.enrollmentList = enrollData.enrollments || [];
          }
          this.fetchSchedules();
          this.fetchStudents();
        } else {
          showToast(res.error || '新增報名失敗', 'error');
        }
      } catch (err) {
        console.error('新增學員報名失敗:', err);
        showToast(err.message || '新增學員報名失敗，請稍後再試', 'error');
      } finally {
        this.submittingStudent = false;
      }
    },
    calculateSalary(schedule, count) {
      if (!schedule) {
        return {
          total: 0,
          totalBeforeCap: 0,
          base: 0,
          lowStudentThreshold: 0,
          lowStudentSalary: 0,
          isLowTier: false,
          threshold: 0,
          feePerStudent: 0,
          extraStudents: 0,
          extraBonus: 0,
          cap: 0,
          isCapped: false,
          studentCount: 0
        };
      }
      const base = Number(schedule.base_salary) || 0;
      const lowStudentThreshold = Number(schedule.low_student_threshold) || 0;
      const lowStudentSalary = Number(schedule.low_student_salary) || 0;
      const threshold = Number(schedule.extra_student_threshold) || 0;
      const feePerStudent = Number(schedule.extra_student_fee) || 0;
      const cap = Number(schedule.salary_cap) || 0;
      const studentCount = Number(count) || 0;

      // 1. 沒人報名就 0
      if (studentCount === 0) {
        return {
          total: 0,
          totalBeforeCap: 0,
          base,
          lowStudentThreshold,
          lowStudentSalary,
          isLowTier: false,
          threshold,
          feePerStudent,
          extraStudents: 0,
          extraBonus: 0,
          cap,
          isCapped: false,
          studentCount: 0
        };
      }

      // 2. 若啟用「幾人以下只有多少元」規則，且報名人數 <= 門檻人數
      if (lowStudentThreshold > 0 && studentCount <= lowStudentThreshold) {
        let total = lowStudentSalary;
        let isCapped = false;
        if (cap > 0 && total > cap) {
          total = cap;
          isCapped = true;
        }
        return {
          total,
          totalBeforeCap: lowStudentSalary,
          base,
          lowStudentThreshold,
          lowStudentSalary,
          isLowTier: true,
          threshold,
          feePerStudent,
          extraStudents: 0,
          extraBonus: 0,
          cap,
          isCapped,
          studentCount
        };
      }

      // 3. 超過低額門檻或未設定低額門檻：標準底金 + 超額加成
      const extraStudents = Math.max(0, studentCount - threshold);
      const extraBonus = extraStudents * feePerStudent;
      const totalBeforeCap = base + extraBonus;

      let total = totalBeforeCap;
      let isCapped = false;
      if (cap > 0 && totalBeforeCap > cap) {
        total = cap;
        isCapped = true;
      }

      return {
        total,
        totalBeforeCap,
        base,
        lowStudentThreshold,
        lowStudentSalary,
        isLowTier: false,
        threshold,
        feePerStudent,
        extraStudents,
        extraBonus,
        cap,
        isCapped,
        studentCount
      };
    },
    getScheduleSalary(schedule) {
      const count = schedule.enrollment_count || 0;
      return this.calculateSalary(schedule, count);
    },
    canViewScheduleSalary(schedule) {
      if (!schedule) return false;
      // 系統管理員 (admin) 擁有全部查看權限
      if (this.adminAuth.currentRole === 'admin') {
        return true;
      }
      // 授課老師 (teacher) 只能查看自己的授課鐘點費，不得看到其他老師的授課鐘點費
      if (this.adminAuth.currentRole === 'teacher') {
        const user = this.adminAuth.currentUser;
        if (!user) return false;

        const myTeacherId = user.teacher_id;
        const scheduleTeacherId = schedule.teacher_id;

        // 1. 若皆有設定 teacher_id，優先比對 ID
        if (myTeacherId && scheduleTeacherId && Number(myTeacherId) === Number(scheduleTeacherId)) {
          return true;
        }

        // 2. 比對老師名稱（考量張美麗 vs 張美麗老師等包含關係）
        const myName = (user.name || '').trim();
        const myTeacherName = (user.teacher_name || '').trim();
        const scheduleTeacherName = (schedule.teacher_name || '').trim();

        if (scheduleTeacherName) {
          if (myName && (scheduleTeacherName === myName || scheduleTeacherName.includes(myName) || myName.includes(scheduleTeacherName))) {
            return true;
          }
          if (myTeacherName && (scheduleTeacherName === myTeacherName || scheduleTeacherName.includes(myTeacherName) || myTeacherName.includes(scheduleTeacherName))) {
            return true;
          }
        }

        return false;
      }
      // 櫃檯客服與其他身分不可查看
      return false;
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
