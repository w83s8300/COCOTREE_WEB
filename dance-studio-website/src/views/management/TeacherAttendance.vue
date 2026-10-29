<template>
  <div class="teacher-attendance-page container-fluid px-0">
    <!-- 頁面標題與即時時鐘 -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4 pb-2 border-bottom">
      <div>
        <h2 class="fw-bold mb-1">
          <i class="bi bi-person-video3 text-primary me-2"></i>
          {{ isTeacher ? '授課老師上課下課打卡' : '老師授課上課下課管理' }}
        </h2>
        <div class="text-muted small">
          老師課堂出勤打卡、即時授課計時與鐘點費用結算
        </div>
      </div>
      <!-- 右側：IP 白名單設定按鈕與即時電子時鐘 -->
      <div class="d-flex align-items-center gap-2 mt-2 mt-md-0">
        <button 
          v-if="isAdmin" 
          class="btn btn-outline-primary btn-sm rounded-pill px-3 shadow-sm d-flex align-items-center"
          @click="showIpModal = true"
          title="設定打卡允許之 IP 白名單"
        >
          <i class="bi bi-shield-check me-1 fs-6"></i>
          <span>IP 白名單設定</span>
        </button>

        <div class="bg-white border rounded-3 px-3 py-2 shadow-sm text-end">
          <div class="text-secondary small fw-semibold">
            <i class="bi bi-calendar-event me-1"></i>{{ currentDateText }}
          </div>
          <div class="fs-4 fw-bold text-dark font-monospace text-primary">
            {{ currentTimeText }}
          </div>
        </div>
      </div>
    </div>

    <!-- 主要操作區塊 -->
    <div class="row g-4 mb-4">
      <!-- 左側：上課下課核心主卡片 -->
      <div class="col-lg-5">
        <div class="card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
          <div 
            class="card-header py-3 px-4 text-white d-flex justify-content-between align-items-center"
            :class="isInClass ? 'bg-gradient-warning-active' : 'bg-gradient-primary'"
          >
            <div class="d-flex align-items-center">
              <div class="status-indicator me-2" :class="isInClass ? 'pulsing-dot' : ''"></div>
              <strong class="fs-6">{{ isInClass ? '目前授課中 (上課打卡中)' : '目前非授課狀態' }}</strong>
            </div>
            <span class="badge bg-white text-dark shadow-sm">
              {{ isTeacher ? '授課老師' : adminAuth.roleLabel }}
            </span>
          </div>

          <div class="card-body p-4 text-center d-flex flex-column justify-content-between">
            <!-- 老師基本身分資訊 -->
            <div class="mb-3">
              <div class="avatar-circle mx-auto mb-2 shadow-sm bg-light text-primary fs-3 d-flex align-items-center justify-content-center overflow-hidden border">
                <img v-if="teacherInfo.avatar_url" :src="teacherInfo.avatar_url" alt="大頭貼" class="w-100 h-100 object-fit-cover" />
                <span v-else>💃</span>
              </div>
              <h5 class="fw-bold text-dark mb-1">
                {{ teacherInfo.name || adminAuth.currentUser?.name }}
              </h5>
              <div class="small text-muted font-monospace mb-2">@{{ adminAuth.currentUser?.username }}</div>

              <div class="d-inline-flex flex-wrap gap-2 justify-content-center">
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle px-2 py-1">
                  <i class="bi bi-calculator me-1"></i>依課堂師資鐘點費 / 拆帳規則計費
                </span>
                <span v-if="teacherInfo.bank_account" class="badge bg-light text-secondary border px-2 py-1" :title="teacherInfo.bank_account">
                  <i class="bi bi-bank me-1"></i>匯款帳號: {{ teacherInfo.bank_account }}
                </span>
                <span v-if="currentClientIp" class="badge bg-light text-secondary border px-2 py-1 font-monospace" :title="`打卡連線來源 IP: ${currentClientIp}`">
                  <i class="bi bi-wifi me-1 text-primary"></i>IP: {{ currentClientIp }}
                </span>
              </div>
            </div>

            <!-- 上課中動態即時看板 -->
            <div v-if="isInClass" class="in-class-panel p-3 my-3 bg-warning-subtle rounded-3 border border-warning-subtle text-start">
              <div class="d-flex justify-content-between align-items-center mb-1 small text-muted">
                <span><i class="bi bi-bookmark-star-fill text-warning me-1"></i>正在授課課程：</span>
                <strong class="text-dark fs-6">{{ activeShift?.course_name }}</strong>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-1 small text-muted">
                <span><i class="bi bi-box-arrow-in-right text-success me-1"></i>上課打卡時間：</span>
                <span class="text-dark font-monospace fw-semibold">{{ formatDateTime(activeShift?.clock_in) }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-1 small text-muted">
                <span><i class="bi bi-stopwatch text-primary me-1"></i>已上課時長：</span>
                <strong class="text-primary font-monospace fs-6">{{ liveClassDuration }}</strong>
              </div>
              <div v-if="activeShift?.student_count !== undefined" class="d-flex justify-content-between align-items-center mb-1 small text-muted">
                <span><i class="bi bi-people text-info me-1"></i>報名學員人數：</span>
                <span class="text-dark fw-bold font-monospace">{{ activeShift?.student_count }} 人</span>
              </div>

              <!-- 課堂拆帳規則說明條 -->
              <div v-if="activeCourseSalaryRulesText" class="p-2 my-2 bg-white rounded border border-warning-subtle small">
                <div class="text-secondary fw-semibold mb-1">
                  <i class="bi bi-card-checklist text-primary me-1"></i>此課堂鐘點拆帳規則：
                </div>
                <div class="text-muted small">
                  {{ activeCourseSalaryRulesText }}
                </div>
              </div>

              <div class="d-flex justify-content-between align-items-center small text-muted pt-2 border-top border-warning-subtle">
                <span><i class="bi bi-cash-coin text-success me-1"></i>預估課堂鐘點費：</span>
                <div>
                  <strong class="text-success fs-5">NT$ {{ liveEstimatedSalary.toLocaleString() }}</strong>
                  <span class="small text-muted ms-1">元</span>
                </div>
              </div>

              <!-- 上課進行中：顯著快捷下課打卡按鈕 -->
              <div class="mt-3 pt-2 border-top border-warning-subtle">
                <button 
                  @click="handleClockOut" 
                  class="btn btn-danger w-100 py-2 rounded-3 fw-bold shadow pulse-anim"
                  :disabled="punching"
                >
                  <span v-if="punching" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-box-arrow-right me-2 fs-5"></i>
                  立即下課打卡 (結束授課並結算)
                </button>
              </div>
            </div>

            <!-- 非授課狀態：選擇今日排程課程 -->
            <div v-else class="not-class-panel p-3 my-3 bg-light rounded-3 text-start small">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <label class="form-label fw-bold text-dark mb-0">
                  <i class="bi bi-calendar3-event text-primary me-1"></i>選擇本次上課課程：
                </label>
                <!-- 現場代課模式提示標籤 -->
                <span v-if="isSubstituteMode" class="badge bg-warning text-dark border border-warning shadow-sm">
                  <i class="bi bi-arrow-repeat me-1"></i>代課打卡進行中
                </span>
              </div>

              <!-- 統一下拉選單：包含今日排程、代課排程、與開設課程 -->
              <div class="mb-2">
                <select class="form-select form-select-sm" v-model="selectedScheduleId" @change="onScheduleSelectChange">
                  <option value="" disabled>-- 請下拉選擇本次上課之課程 --</option>
                  
                  <!-- 今日我的排程課程 -->
                  <optgroup v-if="todaySchedules.length > 0" label="📅 今日授課排程">
                    <option 
                      v-for="s in todaySchedules" 
                      :key="'today-' + s.schedule_id" 
                      :value="s.schedule_id"
                    >
                      【{{ s.time_range }}】{{ s.course_name }} {{ s.teacher_name ? `(${s.teacher_name}老師)` : '' }} {{ s.is_substitute ? '[代課]' : '' }} - 報名 {{ s.student_count }} 人
                    </option>
                  </optgroup>

                  <!-- 今日其他老師課程 (代課支援) -->
                  <optgroup v-if="substituteSchedules.length > 0" label="🔀 今日其他老師排程 (代課支援)">
                    <option 
                      v-for="sub in substituteSchedules" 
                      :key="'sub-' + sub.schedule_id" 
                      :value="'sub_' + sub.schedule_id"
                    >
                      【{{ sub.time_range }}】{{ sub.course_name }} (原師資: {{ sub.original_teacher_name || '原老師' }}) - 報名 {{ sub.student_count }} 人 [代課]
                    </option>
                  </optgroup>

                  <!-- 老師開設課程 (無固定排程) -->
                  <optgroup v-if="teacherCourses.length > 0" label="📚 開設課程 (自由/加開授課)">
                    <option 
                      v-for="c in teacherCourses" 
                      :key="'course-' + c.id" 
                      :value="'course_' + c.id"
                    >
                      {{ c.name }} (底金 NT$ {{ c.base_salary }})
                    </option>
                  </optgroup>

                  <option value="custom">＋ 自訂手動輸入課程名稱</option>
                </select>
              </div>

              <!-- 若選擇自訂輸入 -->
              <div v-if="selectedScheduleId === 'custom'" class="mb-2">
                <input 
                  type="text" 
                  class="form-control form-control-sm" 
                  v-model="customCourseName" 
                  placeholder="請輸入本次授課課程名稱 (例如: K-Pop MV舞蹈進階班)" 
                  required
                />
              </div>

              <!-- 代課模式醒目提示條 -->
              <div v-if="isSubstituteMode" class="alert alert-warning py-2 px-3 small mb-2 border-warning shadow-sm">
                <i class="bi bi-info-circle-fill me-1"></i>
                <strong>您正在進行代課打卡：</strong>
                此堂課出勤與授課鐘點費將自動結算計入您的名下，課表亦會同步標記為代課！
              </div>

              <!-- 即時顯示當前選擇課程的師資鐘點拆帳規則 -->
              <div v-if="currentSelectedRulesText" class="mt-2 p-2 bg-white rounded border small text-muted">
                <span class="text-primary fw-semibold"><i class="bi bi-info-circle me-1"></i>課堂鐘點規則：</span>
                {{ currentSelectedRulesText }}
              </div>

              <div class="text-muted small mt-2">
                <i class="bi bi-shield-check me-1 text-success"></i>
                點擊下方「上課打卡」即可開始課堂計時，下課打卡將依課堂拆帳規則結算鐘點費用。
              </div>
            </div>

            <!-- 備註輸入 -->
            <div class="mb-3 text-start">
              <label class="form-label small fw-semibold text-secondary">
                <i class="bi bi-pencil-square me-1"></i>{{ isInClass ? '下課備註 (選填)' : '上課備註 (選填)' }}：
              </label>
              <input 
                type="text" 
                class="form-control form-control-sm" 
                v-model="punchNotes" 
                :placeholder="isInClass ? '例如: 今日教完第二段副歌、代課已交代完畢' : '例如: 今日補課、代課班級'" 
              />
            </div>

            <!-- 雙打卡按鈕區：上課打卡與下課打卡同時清楚可見 -->
            <div class="mt-2">
              <div class="row g-2">
                <div class="col-6">
                  <button 
                    @click="handleClockIn" 
                    class="btn btn-lg w-100 py-3 rounded-4 fw-bold punch-btn transition-all shadow-sm"
                    :class="!isInClass ? 'btn-success text-white' : 'btn-light text-muted border opacity-50'"
                    :disabled="isInClass || punching"
                  >
                    <span v-if="punching && !isInClass" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-box-arrow-in-right me-1 fs-5"></i>
                    上課打卡
                    <div class="small fw-normal mt-1" style="font-size: 0.75rem;">
                      {{ !isInClass ? '點擊開始上課' : '已在上課中' }}
                    </div>
                  </button>
                </div>

                <div class="col-6">
                  <button 
                    @click="handleClockOut" 
                    class="btn btn-lg w-100 py-3 rounded-4 fw-bold punch-btn transition-all shadow-sm"
                    :class="isInClass ? 'btn-danger text-white pulse-anim' : 'btn-light text-muted border opacity-50'"
                    :disabled="!isInClass || punching"
                  >
                    <span v-if="punching && isInClass" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-box-arrow-right me-1 fs-5"></i>
                    下課打卡
                    <div class="small fw-normal mt-1" style="font-size: 0.75rem;">
                      {{ isInClass ? '點擊結束並結算' : '尚未開始上課' }}
                    </div>
                  </button>
                </div>
              </div>

              <!-- 狀態提示文字 -->
              <div class="text-center small mt-2">
                <span v-if="!isInClass" class="text-muted">
                  <i class="bi bi-info-circle me-1"></i>請先選擇課程後，點擊綠色「上課打卡」；下課時再點擊紅色「下課打卡」。
                </span>
                <span v-else class="text-danger fw-bold">
                  <i class="bi bi-broadcast me-1"></i>正在授課中！教學結束後，請點擊紅色「下課打卡」結算鐘點費。
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右側：今日排程與出勤狀態 -->
      <div class="col-lg-7">
        <div class="card border-0 shadow-sm rounded-4 h-100 d-flex flex-column">
          <div class="card-header bg-white py-3 px-4 border-bottom d-flex justify-content-between align-items-center">
            <h6 class="fw-bold mb-0 text-dark">
              <i class="bi bi-calendar-check me-2 text-primary"></i>今日授課課表與進度 ({{ todaySchedules.length }} 堂)
            </h6>
            <button class="btn btn-sm btn-outline-secondary" @click="fetchStatus" title="重新整理">
              <i class="bi bi-arrow-clockwise me-1"></i>重新整理
            </button>
          </div>

          <div class="card-body p-3 flex-grow-1">
            <!-- 今日課表卡片清單 -->
            <div v-if="todaySchedules.length === 0" class="text-center py-4 text-muted">
              <i class="bi bi-calendar-x fs-1 d-block mb-2 text-secondary opacity-50"></i>
              今日無固定排程課程，老師仍可於左側直接點擊「上課打卡」進行課程授課
            </div>

            <div v-else class="row g-3 mb-3">
              <div v-for="s in todaySchedules" :key="s.schedule_id" class="col-md-6">
                <div 
                  class="p-3 rounded-3 border h-100 schedule-card transition-all"
                  :class="{
                    'border-success bg-success-subtle': s.attendance_status === 'in_progress',
                    'border-secondary-subtle bg-light': s.attendance_status === 'completed',
                    'border-primary-subtle bg-white shadow-sm': s.attendance_status === 'pending'
                  }"
                >
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <span class="badge" :class="{
                      'bg-success': s.attendance_status === 'in_progress',
                      'bg-secondary': s.attendance_status === 'completed',
                      'bg-primary': s.attendance_status === 'pending'
                    }">
                      {{ s.attendance_text }}
                    </span>
                    <span class="badge bg-light text-secondary border font-monospace">
                      {{ s.room_name || '主教室' }}
                    </span>
                  </div>

                  <div class="d-flex align-items-center gap-1 mb-1">
                    <h6 class="fw-bold text-dark mb-0">{{ s.course_name }}</h6>
                    <span v-if="s.is_substitute" class="badge bg-warning text-dark border border-warning shadow-sm" style="font-size: 0.65rem;">
                      代課
                    </span>
                  </div>
                  <div class="text-muted small mb-2">
                    <i class="bi bi-clock me-1"></i>{{ s.time_range }}
                  </div>

                  <div class="d-flex justify-content-between align-items-center small pt-2 border-top">
                    <div>
                      <i class="bi bi-people me-1 text-primary"></i>
                      已報名: <strong>{{ s.student_count }}</strong> 人
                    </div>
                    <div class="text-success fw-bold">
                      預估 NT$ {{ s.estimated_salary.toLocaleString() }}
                    </div>
                  </div>

                  <!-- 課堂師資鐘點費 / 拆帳規則標籤 -->
                  <div class="mt-2 pt-2 border-top small text-secondary">
                    <div class="d-flex flex-wrap gap-1 align-items-center">
                      <span class="badge bg-light text-dark border">
                        底金 ${{ s.base_salary || 0 }}
                      </span>
                      <span v-if="s.low_student_threshold > 0" class="badge bg-warning-subtle text-dark border">
                        ≤ {{ s.low_student_threshold }}人: ${{ s.low_student_salary }}
                      </span>
                      <span v-if="s.extra_student_fee > 0" class="badge bg-info-subtle text-dark border">
                        > {{ s.extra_student_threshold || 0 }}人: +${{ s.extra_student_fee }}/人
                      </span>
                      <span v-if="s.salary_cap > 0" class="badge bg-secondary-subtle text-dark border">
                        上限 ${{ s.salary_cap }}
                      </span>
                      <span v-else class="badge bg-success-subtle text-success border">
                        無上限
                      </span>
                    </div>
                  </div>

                  <!-- 快捷上課 / 下課按鈕 -->
                  <div v-if="s.attendance_status === 'pending' && !isInClass" class="mt-2 pt-2 border-top text-end">
                    <button 
                      class="btn btn-sm btn-outline-success py-1 px-3 rounded-pill fw-semibold"
                      @click="quickClockIn(s)"
                    >
                      <i class="bi bi-play-circle me-1"></i>開始此堂課 (上課打卡)
                    </button>
                  </div>
                  <div v-else-if="s.attendance_status === 'in_progress'" class="mt-2 pt-2 border-top text-end">
                    <button 
                      class="btn btn-sm btn-danger py-1 px-3 rounded-pill fw-semibold shadow-sm pulse-anim"
                      @click="handleClockOut"
                    >
                      <i class="bi bi-box-arrow-right me-1"></i>結束此堂課 (下課打卡)
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 今日打卡紀錄清單 -->
            <div class="mt-3 pt-3 border-top">
              <h6 class="fw-bold text-dark small mb-2">
                <i class="bi bi-clock-history me-1 text-secondary"></i>今日打卡完成明細 ({{ todayRecords.length }})
              </h6>
              <div v-if="todayRecords.length === 0" class="text-muted small py-2">
                今日尚未有已結算之課堂打卡紀錄。
              </div>
              <div v-else class="table-responsive">
                <table class="table table-sm table-hover align-middle mb-0 small">
                  <thead class="table-light">
                    <tr>
                      <th>課程名稱</th>
                      <th>上課時間</th>
                      <th>下課時間</th>
                      <th>時長</th>
                      <th>學員人數</th>
                      <th>結算鐘點費</th>
                      <th>打卡 IP</th>
                      <th>狀態</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="r in todayRecords" :key="r.id">
                      <td class="fw-semibold">{{ r.course_name }}</td>
                      <td class="font-monospace text-success">{{ formatTimeOnly(r.clock_in) }}</td>
                      <td class="font-monospace text-danger">
                        <template v-if="r.clock_out">{{ formatTimeOnly(r.clock_out) }}</template>
                        <span v-else class="badge bg-warning text-dark">授課中</span>
                      </td>
                      <td>{{ r.clock_out ? `${r.duration_minutes} 分鐘` : '-' }}</td>
                      <td>{{ r.student_count }} 人</td>
                      <td class="fw-bold text-success">
                        {{ r.clock_out ? `NT$ ${r.calculated_salary.toLocaleString()}` : '計算中...' }}
                      </td>
                      <td class="small font-monospace">
                        <div v-if="r.clock_in_ip" class="text-success text-truncate" style="max-width: 120px;" :title="`上課 IP: ${r.clock_in_ip}`">
                          <i class="bi bi-box-arrow-in-right me-1"></i>{{ r.clock_in_ip }}
                        </div>
                        <div v-if="r.clock_out_ip" class="text-danger text-truncate" style="max-width: 120px;" :title="`下課 IP: ${r.clock_out_ip}`">
                          <i class="bi bi-box-arrow-right me-1"></i>{{ r.clock_out_ip }}
                        </div>
                        <span v-if="!r.clock_in_ip && !r.clock_out_ip" class="text-muted">-</span>
                      </td>
                      <td>
                        <span v-if="r.clock_out" class="badge bg-secondary">已結算</span>
                        <span v-else class="badge bg-success">進行中</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 歷史紀錄與月度鐘點費統計 -->
    <div class="card border-0 shadow-sm rounded-4 mt-4">
      <div class="card-header bg-white py-3 px-4 border-bottom">
        <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
          <h5 class="fw-bold mb-0 text-dark">
            <i class="bi bi-journal-text me-2 text-primary"></i>授課出勤歷史明細與鐘點費結算
          </h5>
          <!-- 篩選列 -->
          <div class="d-flex flex-wrap gap-2 align-items-center">
            <div class="d-flex align-items-center">
              <span class="small text-muted me-2">月份：</span>
              <input 
                type="month" 
                class="form-control form-control-sm" 
                v-model="selectedMonth" 
                @change="fetchHistory" 
              />
            </div>
            <!-- 管理員篩選老師 -->
            <div v-if="isAdmin" class="d-flex align-items-center">
              <span class="small text-muted me-2">老師：</span>
              <select class="form-select form-select-sm" v-model="filterUserId" @change="fetchHistory">
                <option value="">全部老師</option>
                <option v-for="u in teacherUsers" :key="u.id" :value="u.id">
                  {{ u.name }} (@{{ u.username }})
                </option>
              </select>
            </div>
            <button class="btn btn-sm btn-primary" @click="fetchHistory">
              <i class="bi bi-search me-1"></i>查詢
            </button>
          </div>
        </div>
      </div>

      <!-- 月度統計 KPI 看板 -->
      <div class="card-body bg-light border-bottom py-3">
        <div class="row g-3 text-center">
          <div class="col-md-4">
            <div class="bg-white p-3 rounded-3 shadow-sm border">
              <div class="text-muted small mb-1">
                <i class="bi bi-calendar-range me-1 text-primary"></i>當月累計授課堂數
              </div>
              <div class="fs-4 fw-bold text-dark">{{ summary.total_classes }} <span class="fs-6 fw-normal text-muted">堂</span></div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="bg-white p-3 rounded-3 shadow-sm border">
              <div class="text-muted small mb-1">
                <i class="bi bi-hourglass-split me-1 text-primary"></i>當月累計授課總時數
              </div>
              <div class="fs-4 fw-bold text-primary">
                {{ summary.total_hours }} <span class="fs-6 fw-normal text-muted">小時 ({{ summary.total_minutes }} 分鐘)</span>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="bg-white p-3 rounded-3 shadow-sm border">
              <div class="text-muted small mb-1">
                <i class="bi bi-cash-coin me-1 text-success"></i>當月預計結算鐘點費
              </div>
              <div class="fs-4 fw-bold text-success">NT$ {{ summary.total_salary.toLocaleString() }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 計薪規則說明提示條 -->
      <div class="alert alert-info py-2 px-3 mx-4 my-3 d-flex align-items-center small">
        <i class="bi bi-info-circle-fill fs-5 me-2 text-info"></i>
        <div>
          <strong>授課鐘點費說明：</strong>
          排程課程依該課程之「底金 + 超額學員分潤」或「特定人數以下規則」自動核算；課堂鐘點費用結算一律 <strong>不到 1 元不算 1 元</strong>（保留整數元）。
        </div>
      </div>

      <!-- 歷史明細表格 -->
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light small">
            <tr>
              <th scope="col">ID</th>
              <th scope="col" v-if="isAdmin">授課老師</th>
              <th scope="col">授課日期</th>
              <th scope="col">課程名稱</th>
              <th scope="col">上課打卡</th>
              <th scope="col">下課打卡</th>
              <th scope="col">時長 (分鐘)</th>
              <th scope="col">學員人數</th>
              <th scope="col">鐘點費小計</th>
              <th scope="col">打卡 IP</th>
              <th scope="col">備註</th>
              <th scope="col" v-if="isAdmin" class="text-center" style="width: 140px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="historyRecords.length === 0">
              <td :colspan="isAdmin ? 12 : 10" class="text-center py-4 text-muted">
                該月份查無授課打卡紀錄
              </td>
            </tr>
            <tr v-for="h in historyRecords" :key="h.id">
              <td>#{{ h.id }}</td>
              <td v-if="isAdmin" class="fw-bold">
                {{ h.teacher_name || h.user_name }}
              </td>
              <td>{{ formatDate(h.clock_in) }}</td>
              <td class="fw-semibold text-dark">
                {{ h.course_name }}
                <span v-if="h.is_substitute" class="badge bg-warning text-dark border border-warning shadow-sm ms-1" style="font-size: 0.68rem;">
                  代課
                </span>
              </td>
              <td class="font-monospace small text-success">
                <i class="bi bi-box-arrow-in-right me-1"></i>{{ formatTimeOnly(h.clock_in) }}
              </td>
              <td class="font-monospace small text-danger">
                <template v-if="h.clock_out">
                  <i class="bi bi-box-arrow-right me-1"></i>{{ formatTimeOnly(h.clock_out) }}
                </template>
                <span v-else class="badge bg-warning text-dark">未打卡下課</span>
              </td>
              <td>{{ h.clock_out ? `${h.duration_minutes} 分鐘` : '-' }}</td>
              <td>{{ h.student_count }} 人</td>
              <td class="fw-bold text-success">
                {{ h.clock_out ? `NT$ ${h.calculated_salary.toLocaleString()}` : '計算中...' }}
              </td>
              <td class="small font-monospace">
                <div v-if="h.clock_in_ip" class="text-success text-truncate" style="max-width: 140px;" :title="`上課打卡 IP: ${h.clock_in_ip}`">
                  <i class="bi bi-box-arrow-in-right me-1"></i>{{ h.clock_in_ip }}
                </div>
                <div v-if="h.clock_out_ip" class="text-danger text-truncate" style="max-width: 140px;" :title="`下課打卡 IP: ${h.clock_out_ip}`">
                  <i class="bi bi-box-arrow-right me-1"></i>{{ h.clock_out_ip }}
                </div>
                <span v-if="!h.clock_in_ip && !h.clock_out_ip" class="text-muted">-</span>
              </td>
              <td class="small text-muted text-truncate" style="max-width: 150px;" :title="h.notes">
                {{ h.notes || '-' }}
              </td>
              <td v-if="isAdmin" class="text-center text-nowrap">
                <button 
                  @click="openEditModal(h)" 
                  class="btn btn-sm btn-outline-primary me-1 px-2 py-1" 
                  title="編輯授課時間與鐘點費"
                >
                  <i class="bi bi-pencil-square me-1"></i>編輯
                </button>
                <button 
                  @click="deleteRecord(h.id)" 
                  class="btn btn-sm btn-outline-danger px-2 py-1" 
                  title="刪除紀錄"
                >
                  <i class="bi bi-trash me-1"></i>刪除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 管理員編輯授課打卡紀錄 Modal -->
    <div v-if="showEditModal" class="modal-backdrop fade show"></div>
    <div v-if="showEditModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rounded-4 shadow border-0 overflow-hidden">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title fw-bold">
              <i class="bi bi-pencil-square me-2"></i>編輯授課打卡時間與鐘點費
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="closeEditModal"></button>
          </div>
          <form @submit.prevent="submitEditRecord">
            <div class="modal-body p-4 text-start">
              <div class="bg-light p-3 rounded-3 mb-3 border d-flex justify-content-between align-items-center">
                <div>
                  <div class="fw-bold text-dark fs-6">{{ editingRecord?.teacher_name || editingRecord?.user_name }}</div>
                  <div class="small text-muted font-monospace">紀錄編號: #{{ editForm.id }}</div>
                </div>
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle">
                  授課打卡
                </span>
              </div>

              <!-- 課程名稱 (下拉選單) -->
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <label class="form-label fw-semibold text-dark mb-0">
                    <i class="bi bi-bookmark-star-fill text-warning me-1"></i>課程名稱：
                  </label>
                  <button 
                    type="button" 
                    class="btn btn-link btn-sm text-decoration-none p-0 small" 
                    @click="toggleCustomEditCourse"
                  >
                    <i class="bi" :class="isCustomEditCourse ? 'bi-list-ul' : 'bi-pencil-square'"></i>
                    {{ isCustomEditCourse ? '改用下拉選單選擇' : '自訂手動輸入課程' }}
                  </button>
                </div>

                <!-- 下拉選擇課程 -->
                <select 
                  v-if="!isCustomEditCourse" 
                  class="form-select" 
                  v-model="editForm.course_name" 
                  required 
                  @change="onEditCourseSelect"
                >
                  <option value="" disabled>-- 請下拉選擇課程 --</option>
                  <!-- 若當前紀錄的課程名稱不在現有課程清單中，自動保留為選項 -->
                  <option 
                    v-if="editForm.course_name && !allCourses.some(c => c.name === editForm.course_name)" 
                    :value="editForm.course_name"
                  >
                    {{ editForm.course_name }} (原紀錄課程)
                  </option>
                  <option 
                    v-for="c in allCourses" 
                    :key="c.id" 
                    :value="c.name"
                  >
                    {{ c.name }} ({{ c.teacher_name ? c.teacher_name + ' 老師' : '未指定師資' }} · {{ c.style_name || c.level }})
                  </option>
                </select>

                <!-- 自訂手動輸入課程名稱 -->
                <div v-else class="input-group">
                  <span class="input-group-text"><i class="bi bi-pencil"></i></span>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="editForm.course_name" 
                    placeholder="請輸入自訂課程名稱，例如：代課特別班、私人一對一"
                    required 
                  />
                </div>
                <div class="form-text small">
                  {{ isCustomEditCourse ? '可直接輸入非系統常態開設的特殊課程名稱' : '從舞蹈教室開設之課程清單中選擇' }}
                </div>
              </div>

              <!-- 上課打卡時間 -->
              <div class="mb-3">
                <label class="form-label fw-semibold text-dark">
                  <i class="bi bi-box-arrow-in-right text-success me-1"></i>上課打卡時間：
                </label>
                <input 
                  type="datetime-local" 
                  class="form-control font-monospace" 
                  v-model="editForm.clock_in" 
                  required 
                  step="1" 
                />
              </div>

              <!-- 下課打卡時間 -->
              <div class="mb-3">
                <label class="form-label fw-semibold text-dark">
                  <i class="bi bi-box-arrow-right text-danger me-1"></i>下課打卡時間：
                </label>
                <input 
                  type="datetime-local" 
                  class="form-control font-monospace" 
                  v-model="editForm.clock_out" 
                  step="1" 
                />
              </div>

              <div class="row g-2 mb-3">
                <div class="col-6">
                  <label class="form-label fw-semibold text-dark">學員人數：</label>
                  <input type="number" class="form-control" v-model.number="editForm.student_count" min="0" />
                </div>
                <div class="col-6">
                  <label class="form-label fw-semibold text-dark">鐘點費 (NT$)：</label>
                  <input type="number" class="form-control" v-model.number="editForm.calculated_salary" min="0" />
                </div>
              </div>

              <!-- 備註說明 -->
              <div class="mb-2">
                <label class="form-label fw-semibold text-dark">紀錄備註：</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="editForm.notes" 
                  placeholder="例如：管理員修正下課時間、代課補發" 
                />
              </div>
            </div>

            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-outline-secondary" @click="closeEditModal" :disabled="savingEdit">
                取消
              </button>
              <button type="submit" class="btn btn-primary px-4 fw-bold" :disabled="savingEdit">
                <span v-if="savingEdit" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-check-lg me-1"></i>
                儲存修改
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 打卡 IP 白名單設定 Modal -->
    <AttendanceIpModal v-model:show="showIpModal" @saved="onIpSettingsSaved" />
  </div>
</template>

<script>
import api from '@/utils/api';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';
import { useAdminAuth } from '@/utils/adminAuth';
import AttendanceIpModal from '@/components/AttendanceIpModal.vue';

export default {
  name: 'TeacherAttendance',
  components: {
    AttendanceIpModal
  },
  data() {
    const now = new Date();
    const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;

    return {
      adminAuth: useAdminAuth(),
      showIpModal: false,
      currentClientIp: '',
      isInClass: false,
      activeShift: null,
      todaySchedules: [],
      teacherCourses: [],
      todayRecords: [],
      historyRecords: [],
      teacherInfo: {
        user_id: null,
        teacher_id: null,
        name: '',
        bank_account: ''
      },
      summary: {
        total_classes: 0,
        total_minutes: 0,
        total_hours: 0,
        total_salary: 0
      },
      teacherUsers: [],
      selectedMonth: currentMonth,
      filterUserId: '',
      selectedScheduleId: '',
      selectedCourseId: '',
      customCourseName: '',
      punchNotes: '',
      isSubstituteMode: false,
      selectedSubstituteScheduleId: '',
      substituteSchedules: [],
      punching: false,
      currentTime: new Date(),
      timer: null,

      // 管理員編輯 Modal
      showEditModal: false,
      editingRecord: null,
      allCourses: [],
      isCustomEditCourse: false,
      editForm: {
        id: null,
        course_id: null,
        course_name: '',
        clock_in: '',
        clock_out: '',
        student_count: 0,
        calculated_salary: 0,
        notes: ''
      },
      savingEdit: false
    };
  },
  computed: {
    isAdmin() {
      return this.adminAuth.currentRole === 'admin';
    },
    isTeacher() {
      return this.adminAuth.currentRole === 'teacher';
    },
    currentDateText() {
      const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
      const y = this.currentTime.getFullYear();
      const m = String(this.currentTime.getMonth() + 1).padStart(2, '0');
      const d = String(this.currentTime.getDate()).padStart(2, '0');
      const day = days[this.currentTime.getDay()];
      return `${y}年${m}月${d}日 ${day}`;
    },
    currentTimeText() {
      const h = String(this.currentTime.getHours()).padStart(2, '0');
      const m = String(this.currentTime.getMinutes()).padStart(2, '0');
      const s = String(this.currentTime.getSeconds()).padStart(2, '0');
      return `${h}:${m}:${s}`;
    },
    // 上課經過時長
    liveClassDuration() {
      if (!this.activeShift?.clock_in) return '0 分鐘 0 秒';
      const start = new Date(this.activeShift.clock_in).getTime();
      const now = this.currentTime.getTime();
      const diffSeconds = Math.max(0, Math.floor((now - start) / 1000));
      const hours = Math.floor(diffSeconds / 3600);
      const minutes = Math.floor((diffSeconds % 3600) / 60);
      const seconds = diffSeconds % 60;
      if (hours > 0) {
        return `${hours} 小時 ${minutes} 分 ${seconds} 秒`;
      }
      return `${minutes} 分鐘 ${seconds} 秒`;
    },
    // 即時預估鐘點費 (嚴格依該課堂師資鐘點費/拆帳規則計算)
    liveEstimatedSalary() {
      if (!this.activeShift) return 0;
      // 1. 若 activeShift 本身已有後端計算好的預估
      if (this.activeShift.estimated_salary !== undefined && this.activeShift.estimated_salary !== null) {
        return this.activeShift.estimated_salary;
      }
      // 2. 若有對應的今日排程預估值
      if (this.activeShift.schedule_id) {
        const sched = this.todaySchedules.find(s => s.schedule_id === this.activeShift.schedule_id);
        if (sched && sched.estimated_salary !== undefined) {
          return sched.estimated_salary;
        }
      }
      // 3. 依該課堂規則即時換算
      if (this.activeShift.base_salary !== undefined) {
        const base = Number(this.activeShift.base_salary) || 0;
        const count = Number(this.activeShift.student_count) || 0;
        const lowThresh = Number(this.activeShift.low_student_threshold) || 0;
        const lowSal = Number(this.activeShift.low_student_salary) || 0;
        const extraThresh = Number(this.activeShift.extra_student_threshold) || 0;
        const extraFee = Number(this.activeShift.extra_student_fee) || 0;
        const cap = Number(this.activeShift.salary_cap) || 0;

        let total = base;
        if (count > 0 && lowThresh > 0 && count <= lowThresh) {
          total = lowSal;
        } else if (count > 0 && extraThresh > 0 && count > extraThresh) {
          total = base + (count - extraThresh) * extraFee;
        }
        if (cap > 0 && total > cap) {
          total = cap;
        }
        return Math.floor(total);
      }
      return 0;
    },
    selectedSubstitute() {
      if (!this.selectedSubstituteScheduleId) return null;
      return this.substituteSchedules.find(s => s.schedule_id === this.selectedSubstituteScheduleId) || null;
    },
    // 上課中課程拆帳規則文字
    activeCourseSalaryRulesText() {
      if (!this.activeShift) return '';
      if (this.activeShift.base_salary === undefined && !this.activeShift.schedule_id) return '';
      return this.formatRulesString(this.activeShift);
    },
    // 當前選取課程之拆帳規則文字
    currentSelectedRulesText() {
      if (this.isSubstituteMode && this.selectedSubstitute) {
        return this.formatRulesString(this.selectedSubstitute);
      } else if (this.selectedScheduleId) {
        const sched = this.todaySchedules.find(s => s.schedule_id === this.selectedScheduleId);
        if (sched) return this.formatRulesString(sched);
      } else if (this.selectedCourseId) {
        const course = this.teacherCourses.find(c => c.id === this.selectedCourseId);
        if (course) return this.formatRulesString(course);
      }
      return '';
    }
  },
  created() {
    this.fetchStatus();
    this.fetchHistory();
    this.fetchAllCourses();
    if (this.isAdmin) {
      this.fetchTeacherUsers();
    }
  },
  mounted() {
    this.timer = setInterval(() => {
      this.currentTime = new Date();
    }, 1000);
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  },
  methods: {
    formatRulesString(item) {
      if (!item) return '';
      const parts = [];
      const base = Number(item.base_salary) || 0;
      parts.push(`底金 NT$ ${base.toLocaleString()}`);

      const lowThresh = Number(item.low_student_threshold) || 0;
      const lowSal = Number(item.low_student_salary) || 0;
      if (lowThresh > 0) {
        parts.push(`門檻：${lowThresh} 人以下固定 NT$ ${lowSal.toLocaleString()}`);
      }

      const extraThresh = Number(item.extra_student_threshold) || 0;
      const extraFee = Number(item.extra_student_fee) || 0;
      if (extraThresh > 0 && extraFee > 0) {
        parts.push(`超過 ${extraThresh} 人每人 +NT$ ${extraFee.toLocaleString()}`);
      }

      const cap = Number(item.salary_cap) || 0;
      if (cap > 0) {
        parts.push(`上限 NT$ ${cap.toLocaleString()}`);
      } else {
        parts.push('無上限');
      }

      return parts.join(' ｜ ');
    },
    formatDate(dateStr) {
      if (!dateStr) return '-';
      const d = new Date(dateStr);
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    },
    formatTimeOnly(dateStrOrObj) {
      if (!dateStrOrObj) return '-';
      const d = (dateStrOrObj instanceof Date) ? dateStrOrObj : new Date(dateStrOrObj);
      if (isNaN(d.getTime())) return '-';
      return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`;
    },
    formatDateTime(dateStr) {
      if (!dateStr) return '-';
      const d = new Date(dateStr);
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    },
    toDatetimeLocal(dateStr) {
      if (!dateStr) return '';
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return '';
      const pad = (n) => String(n).padStart(2, '0');
      const yyyy = d.getFullYear();
      const MM = pad(d.getMonth() + 1);
      const dd = pad(d.getDate());
      const hh = pad(d.getHours());
      const mm = pad(d.getMinutes());
      const ss = pad(d.getSeconds());
      return `${yyyy}-${MM}-${dd}T${hh}:${mm}:${ss}`;
    },
    onScheduleSelectChange() {
      if (!this.selectedScheduleId) return;

      if (String(this.selectedScheduleId).startsWith('course_')) {
        const cId = Number(String(this.selectedScheduleId).replace('course_', ''));
        const found = this.teacherCourses.find(c => c.id === cId);
        this.selectedCourseId = cId;
        this.customCourseName = found ? found.name : '';
        this.isSubstituteMode = false;
        return;
      }

      if (String(this.selectedScheduleId).startsWith('sub_')) {
        const subId = Number(String(this.selectedScheduleId).replace('sub_', ''));
        const found = this.substituteSchedules.find(s => Number(s.schedule_id) === subId);
        this.selectedSubstituteScheduleId = subId;
        this.isSubstituteMode = true;
        this.customCourseName = found ? found.course_name : '';
        this.selectedCourseId = found ? found.course_id : null;
        return;
      }

      if (this.selectedScheduleId === 'custom') {
        this.selectedCourseId = '';
        this.customCourseName = '';
        this.isSubstituteMode = false;
        return;
      }

      // Check in todaySchedules
      const sId = Number(this.selectedScheduleId);
      const foundInToday = this.todaySchedules.find(s => Number(s.schedule_id) === sId);
      if (foundInToday) {
        this.customCourseName = foundInToday.course_name;
        this.selectedCourseId = foundInToday.course_id;
        this.isSubstituteMode = Boolean(foundInToday.is_substitute);
        if (this.isSubstituteMode) {
          this.selectedSubstituteScheduleId = foundInToday.schedule_id;
        }
        return;
      }
    },
    onCourseSelectChange() {
      if (this.selectedCourseId) {
        const found = this.teacherCourses.find(c => c.id === this.selectedCourseId);
        if (found) {
          this.customCourseName = found.name;
        }
      }
    },
    toggleSubstituteMode() {
      this.isSubstituteMode = !this.isSubstituteMode;
      if (this.isSubstituteMode && !this.selectedSubstituteScheduleId && this.substituteSchedules.length > 0) {
        this.selectedSubstituteScheduleId = this.substituteSchedules[0].schedule_id;
      }
    },
    async fetchStatus() {
      const uid = this.adminAuth.currentUser?.id;
      if (!uid) return;
      try {
        const d = this.currentTime || new Date();
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const todayStr = `${y}-${m}-${day}`;
        let url = `/admin/teacher-attendance/status?user_id=${uid}&date=${todayStr}`;
        if (this.$route.query.schedule_id) {
          url += `&schedule_id=${this.$route.query.schedule_id}`;
        }
        const res = await api.get(url);
        if (res.success) {
          this.isInClass = res.is_in_class;
          this.activeShift = res.active_shift;
          this.todaySchedules = res.today_schedules || [];
          this.teacherCourses = res.teacher_courses || [];
          this.todayRecords = res.today_records || [];
          this.substituteSchedules = res.substitute_schedules || [];
          if (res.client_ip) {
            this.currentClientIp = res.client_ip;
          }
          if (res.teacher_info) {
            this.teacherInfo = res.teacher_info;
          }
          // 檢查網址是否有傳入指定 schedule_id
          const qId = this.$route.query.schedule_id ? Number(this.$route.query.schedule_id) : null;
          if (qId) {
            const foundInToday = this.todaySchedules.find(s => Number(s.schedule_id) === qId);
            if (foundInToday) {
              this.selectedScheduleId = foundInToday.schedule_id;
              this.customCourseName = foundInToday.course_name;
              this.isSubstituteMode = Boolean(foundInToday.is_substitute);
            } else {
              const foundInSub = this.substituteSchedules.find(s => Number(s.schedule_id) === qId);
              if (foundInSub) {
                this.isSubstituteMode = true;
                this.selectedScheduleId = 'sub_' + foundInSub.schedule_id;
                this.selectedSubstituteScheduleId = foundInSub.schedule_id;
                this.customCourseName = foundInSub.course_name;
              }
            }
          } else {
            // 預設選中今日第一個排程
            if (!this.selectedScheduleId && this.todaySchedules.length > 0) {
              const pending = this.todaySchedules.find(s => s.attendance_status === 'pending');
              const target = pending || this.todaySchedules[0];
              this.selectedScheduleId = target.schedule_id;
              this.customCourseName = target.course_name;
              this.isSubstituteMode = Boolean(target.is_substitute);
            } else if (!this.selectedScheduleId && this.substituteSchedules.length > 0) {
              const firstSub = this.substituteSchedules[0];
              this.selectedScheduleId = 'sub_' + firstSub.schedule_id;
              this.selectedSubstituteScheduleId = firstSub.schedule_id;
              this.customCourseName = firstSub.course_name;
              this.isSubstituteMode = true;
            } else if (!this.selectedScheduleId && this.teacherCourses.length > 0) {
              this.selectedScheduleId = 'course_' + this.teacherCourses[0].id;
              this.selectedCourseId = this.teacherCourses[0].id;
              this.customCourseName = this.teacherCourses[0].name;
            }
          }
          if (!this.selectedSubstituteScheduleId && this.substituteSchedules.length > 0) {
            this.selectedSubstituteScheduleId = this.substituteSchedules[0].schedule_id;
          }
        }
      } catch (err) {
        console.error('查詢老師打卡狀態失敗:', err);
      }
    },
    onIpSettingsSaved(data) {
      if (data && data.client_ip) {
        this.currentClientIp = data.client_ip;
      }
      this.fetchStatus();
      this.fetchHistory();
    },
    async fetchHistory() {
      const uid = this.isAdmin ? this.filterUserId : this.adminAuth.currentUser?.id;
      let url = `/admin/teacher-attendance?month=${this.selectedMonth}`;
      if (uid) {
        url += `&user_id=${uid}`;
      }
      try {
        const res = await api.get(url);
        if (res.success) {
          this.historyRecords = res.records || [];
          this.summary = res.summary || { total_classes: 0, total_minutes: 0, total_hours: 0, total_salary: 0 };
        }
      } catch (err) {
        console.error('獲取授課打卡歷史失敗:', err);
      }
    },
    async fetchTeacherUsers() {
      try {
        const res = await api.get('/admin/users');
        if (res.success) {
          this.teacherUsers = (res.users || []).filter(u => u.role === 'teacher');
        }
      } catch (err) {
        console.error('獲取老師帳號清單失敗:', err);
      }
    },
    quickClockIn(schedule) {
      this.selectedScheduleId = schedule.schedule_id;
      this.selectedCourseId = '';
      this.customCourseName = schedule.course_name;
      this.handleClockIn();
    },
    async handleClockIn() {
      const uid = this.adminAuth.currentUser?.id;
      if (!uid) {
        showToast('請先登入後台！', 'error');
        return;
      }

      let courseName = '';
      let courseId = null;
      let scheduleId = null;
      let isSubstitute = false;
      let originalTeacherId = null;
      let notesToSend = this.punchNotes.trim();

      if (this.isSubstituteMode) {
        let subId = this.selectedSubstituteScheduleId;
        if (!subId && String(this.selectedScheduleId).startsWith('sub_')) {
          subId = Number(String(this.selectedScheduleId).replace('sub_', ''));
        } else if (!subId) {
          subId = Number(this.selectedScheduleId);
        }
        const found = this.substituteSchedules.find(s => Number(s.schedule_id) === Number(subId)) ||
                      this.todaySchedules.find(s => Number(s.schedule_id) === Number(subId));
        if (found) {
          scheduleId = found.schedule_id;
          courseId = found.course_id;
          courseName = found.course_name;
          isSubstitute = true;
          originalTeacherId = found.original_teacher_id;
          const origNote = `【代課: 原師資 ${found.original_teacher_name || '原老師'}】`;
          notesToSend = notesToSend ? `${origNote} ${notesToSend}` : origNote;
        } else {
          showToast('請選擇欲代課的課程排程！', 'warning');
          return;
        }
      } else {
        courseName = this.customCourseName.trim();
        courseId = this.selectedCourseId || null;
        if (this.selectedScheduleId && !String(this.selectedScheduleId).startsWith('course_') && this.selectedScheduleId !== 'custom') {
          const sId = Number(this.selectedScheduleId);
          const found = this.todaySchedules.find(s => Number(s.schedule_id) === sId);
          if (found) {
            scheduleId = found.schedule_id;
            courseName = found.course_name;
            courseId = found.course_id;
            if (found.is_substitute) {
              isSubstitute = true;
              originalTeacherId = found.original_teacher_id;
            }
          }
        } else if (this.selectedCourseId) {
          const found = this.teacherCourses.find(c => c.id === this.selectedCourseId);
          if (found) {
            courseName = found.name;
          }
        }
      }

      if (!courseName) {
        courseName = '一般授課課程';
      }

      this.punching = true;
      try {
        const res = await api.post('/admin/teacher-attendance/clock-in', {
          user_id: uid,
          schedule_id: scheduleId || null,
          course_id: courseId,
          course_name: courseName,
          notes: notesToSend || null,
          is_substitute: isSubstitute,
          original_teacher_id: originalTeacherId
        });
        if (res.success) {
          showToast(res.message || '上課打卡成功！祝您授課愉快！', 'success');
          this.punchNotes = '';
          this.isSubstituteMode = false;
          await this.fetchStatus();
          await this.fetchHistory();
        }
      } catch (err) {
        showToast(err.message || '上課打卡失敗，請稍後再試', 'error');
      } finally {
        this.punching = false;
      }
    },
    async handleClockOut() {
      const uid = this.adminAuth.currentUser?.id;
      if (!uid) return;

      const ok = await showConfirm('確定要進行【下課打卡】嗎？系統將自動結算本堂授課鐘點費。');
      if (!ok) return;

      this.punching = true;
      try {
        const res = await api.post('/admin/teacher-attendance/clock-out', {
          user_id: uid,
          notes: this.punchNotes
        });
        if (res.success) {
          showToast(res.message || '下課打卡成功！老師辛苦了！', 'success');
          this.punchNotes = '';
          await this.fetchStatus();
          await this.fetchHistory();
        }
      } catch (err) {
        showToast(err.message || '下課打卡失敗，請稍後再試', 'error');
      } finally {
        this.punching = false;
      }
    },
    async fetchAllCourses() {
      try {
        const res = await api.get('/courses');
        if (res.courses) {
          this.allCourses = res.courses;
        }
      } catch (err) {
        console.error('獲取所有課程清單失敗:', err);
      }
    },
    toggleCustomEditCourse() {
      this.isCustomEditCourse = !this.isCustomEditCourse;
    },
    onEditCourseSelect() {
      const selectedName = this.editForm.course_name;
      const found = this.allCourses.find(c => c.name === selectedName);
      if (found) {
        this.editForm.course_id = found.id;
      }
    },
    openEditModal(record) {
      this.editingRecord = record;
      this.isCustomEditCourse = false;
      this.editForm = {
        id: record.id,
        course_id: record.course_id || null,
        course_name: record.course_name || '',
        clock_in: this.toDatetimeLocal(record.clock_in),
        clock_out: this.toDatetimeLocal(record.clock_out),
        student_count: record.student_count || 0,
        calculated_salary: record.calculated_salary || 0,
        notes: record.notes || ''
      };
      this.showEditModal = true;
    },
    closeEditModal() {
      this.showEditModal = false;
      this.editingRecord = null;
      this.isCustomEditCourse = false;
    },
    async submitEditRecord() {
      if (!this.editForm.clock_in) {
        showToast('上課時間不可為空', 'error');
        return;
      }
      if (this.editForm.clock_out && new Date(this.editForm.clock_out) < new Date(this.editForm.clock_in)) {
        showToast('下課時間不可早於上課時間', 'error');
        return;
      }

      this.savingEdit = true;
      try {
        const res = await api.put(`/admin/teacher-attendance/${this.editForm.id}`, this.editForm);
        if (res.success) {
          showToast(res.message || '授課紀錄已成功更新！', 'success');
          this.closeEditModal();
          await this.fetchStatus();
          await this.fetchHistory();
        }
      } catch (err) {
        showToast(err.message || '更新失敗，請檢查輸入內容', 'error');
      } finally {
        this.savingEdit = false;
      }
    },
    async deleteRecord(id) {
      const ok = await showConfirm('確定要刪除這筆授課打卡記錄嗎？');
      if (!ok) return;
      try {
        const res = await api.delete(`/admin/teacher-attendance/${id}`);
        if (res.success) {
          showToast('授課記錄已刪除', 'success');
          this.fetchHistory();
          this.fetchStatus();
        }
      } catch (err) {
        showToast(err.message || '刪除失敗', 'error');
      }
    }
  }
};
</script>

<style scoped>
.teacher-attendance-page {
  padding: 10px;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
}

.bg-gradient-warning-active {
  background: linear-gradient(135deg, #fd7e14 0%, #e8590c 100%);
}

.avatar-circle {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  border: 3px solid #e7f1ff;
}

.punch-btn {
  font-size: 1.15rem;
  letter-spacing: 1px;
  transition: all 0.25s ease;
}

.punch-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15) !important;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #ffc107;
  display: inline-block;
}

.pulsing-dot {
  background-color: #ffffff;
  box-shadow: 0 0 0 rgba(255, 255, 255, 0.7);
  animation: pulse-ring 1.5s infinite;
}

@keyframes pulse-ring {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(255, 255, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
}

.schedule-card {
  transition: all 0.2s ease;
}

.schedule-card:hover {
  transform: translateY(-2px);
}

.pulse-anim {
  animation: pulse-button 1.8s infinite;
}

@keyframes pulse-button {
  0% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(220, 53, 69, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
  }
}
</style>

