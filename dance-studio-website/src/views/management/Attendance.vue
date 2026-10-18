<template>
  <div class="attendance-page container-fluid px-0">
    <!-- 頁面標題與即時時鐘 -->
    <div class="d-flex flex-wrap justify-content-between align-items-center mb-4 pb-2 border-bottom">
      <div>
        <h2 class="fw-bold mb-1">
          <i class="bi bi-clock-history text-primary me-2"></i>
          {{ isDesk ? '櫃檯客服上下班打卡' : '員工上下班打卡管理' }}
        </h2>
        <div class="text-muted small">
          紀錄每日出勤工時與時薪薪資結算
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

    <div class="row g-4 mb-4">
      <!-- 左側：打卡操作核心主卡片 -->
      <div class="col-lg-5">
        <div class="card border-0 shadow-sm rounded-4 h-100 overflow-hidden">
          <div 
            class="card-header py-3 px-4 text-white d-flex justify-content-between align-items-center"
            :class="isClockedIn ? 'bg-gradient-success' : 'bg-gradient-primary'"
          >
            <div class="d-flex align-items-center">
              <div class="status-indicator me-2" :class="isClockedIn ? 'pulsing-dot' : ''"></div>
              <strong class="fs-6">{{ isClockedIn ? '目前工作中 (已打卡)' : '目前尚未上班' }}</strong>
            </div>
            <span class="badge bg-white text-dark shadow-sm">
              {{ adminAuth.roleLabel }}
            </span>
          </div>

          <div class="card-body p-4 text-center d-flex flex-column justify-content-between">
            <!-- 員工身分資訊 -->
            <div class="mb-3">
              <div class="avatar-circle mx-auto mb-2 shadow-sm bg-light text-primary fs-3 d-flex align-items-center justify-content-center">
                {{ isDesk ? '🛎️' : '👤' }}
              </div>
              <h5 class="fw-bold text-dark mb-1">{{ adminAuth.currentUser?.name }}</h5>
              <div class="small text-muted font-monospace mb-2">@{{ adminAuth.currentUser?.username }}</div>

              <div class="d-inline-flex flex-wrap gap-2 justify-content-center">
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle px-2 py-1">
                  <i class="bi bi-cash me-1"></i>時薪: NT$ {{ userHourlyRate }} /小時
                </span>
                <span v-if="adminAuth.currentUser?.bank_account" class="badge bg-light text-secondary border px-2 py-1" :title="adminAuth.currentUser.bank_account">
                  <i class="bi bi-bank me-1"></i>{{ adminAuth.currentUser.bank_account }}
                </span>
                <span v-if="currentClientIp" class="badge bg-light text-secondary border px-2 py-1 font-monospace" :title="`打卡連線來源 IP: ${currentClientIp}`">
                  <i class="bi bi-wifi me-1 text-primary"></i>IP: {{ currentClientIp }}
                </span>
              </div>
            </div>

            <!-- 打卡計時動態看板 -->
            <div v-if="isClockedIn" class="working-panel p-3 my-3 bg-success-subtle rounded-3 border border-success-subtle text-start">
              <div class="d-flex justify-content-between align-items-center mb-1 small text-muted">
                <span><i class="bi bi-box-arrow-in-right me-1 text-success"></i>上班打卡時間：</span>
                <span class="text-dark font-monospace fw-semibold">{{ formatTimeOnly(activeShift?.clock_in) }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-1 small text-muted">
                <span><i class="bi bi-clock-history me-1 text-primary"></i>計薪起算時間：</span>
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle font-monospace">
                  {{ formatTimeHm(activeEffectiveClockIn) }} (30分進位)
                </span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-1 small text-muted">
                <span><i class="bi bi-hourglass-split me-1 text-secondary"></i>目前退位截止：</span>
                <span class="badge bg-secondary-subtle text-secondary border font-monospace">
                  {{ formatTimeHm(currentEffectiveClockOut) }} (30分退位)
                </span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-1 small text-muted">
                <span><i class="bi bi-stopwatch me-1 text-primary"></i>有效計薪工時：</span>
                <strong class="text-primary font-monospace fs-6">
                  {{ liveEffectiveWorkHours }} 小時
                  <span class="small text-muted fw-normal">({{ liveWorkDuration }})</span>
                </strong>
              </div>
              <div class="d-flex justify-content-between align-items-center small text-muted pt-2 border-top border-success-subtle">
                <span><i class="bi bi-coin me-1 text-warning"></i>目前結算薪資：</span>
                <div>
                  <strong class="text-success fs-5">NT$ {{ liveEstimatedPay.toLocaleString() }}</strong>
                  <span class="small text-muted ms-1">(不到1元捨去)</span>
                </div>
              </div>

              <!-- 快捷立即下班打卡按鈕 -->
              <div class="mt-3 pt-2 border-top border-success-subtle">
                <button 
                  @click="handleClockOut" 
                  class="btn btn-danger w-100 py-2 rounded-3 fw-bold shadow pulse-anim"
                  :disabled="punching"
                >
                  <span v-if="punching" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-box-arrow-right me-2 fs-5"></i>
                  立即下班打卡 (完成工作並結算)
                </button>
              </div>
            </div>

            <div v-else class="not-working-panel p-3 my-3 bg-light rounded-3 text-muted small text-start">
              <div class="fw-semibold text-dark mb-1">
                <i class="bi bi-info-circle text-primary me-1"></i>出勤計薪規範說明：
              </div>
              <ul class="mb-0 ps-3">
                <li><strong>30分鐘進退位</strong>：上班時間往後進位至下一個半小時整點（例：8:40 算 9:00 起算）；下班時間往前退位至上一個半小時整點（例：9:45 算 9:30 截止）。</li>
                <li><strong>不到1元不算1元</strong>：時薪 NT$ {{ userHourlyRate }}，薪資計算無條件捨去小數點保留整數元。</li>
              </ul>
            </div>

            <!-- 備註輸入 -->
            <div class="mb-3 text-start">
              <label class="form-label small fw-semibold text-secondary">
                <i class="bi bi-pencil-square me-1"></i>{{ isClockedIn ? '下班交接備註 (選填)' : '上班備註 (選填)' }}：
              </label>
              <input 
                type="text" 
                class="form-control form-control-sm" 
                v-model="punchNotes" 
                :placeholder="isClockedIn ? '例如: 今日交接款項無誤、教室門窗已鎖' : '例如: 早班、代班、晚班'" 
              />
            </div>

            <!-- 雙打卡按鈕區：上班打卡與下班打卡同時清楚可見 -->
            <div class="mt-2">
              <div class="row g-2">
                <div class="col-6">
                  <button 
                    @click="handleClockIn" 
                    class="btn btn-lg w-100 py-3 rounded-4 fw-bold punch-btn transition-all shadow-sm"
                    :class="!isClockedIn ? 'btn-success text-white' : 'btn-light text-muted border opacity-50'"
                    :disabled="isClockedIn || punching"
                  >
                    <span v-if="punching && !isClockedIn" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-box-arrow-in-right me-1 fs-5"></i>
                    上班打卡
                    <div class="small fw-normal mt-1" style="font-size: 0.75rem;">
                      {{ !isClockedIn ? '點擊開始工作' : '工作中' }}
                    </div>
                  </button>
                </div>

                <div class="col-6">
                  <button 
                    @click="handleClockOut" 
                    class="btn btn-lg w-100 py-3 rounded-4 fw-bold punch-btn transition-all shadow-sm"
                    :class="isClockedIn ? 'btn-danger text-white pulse-anim' : 'btn-light text-muted border opacity-50'"
                    :disabled="!isClockedIn || punching"
                  >
                    <span v-if="punching && isClockedIn" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-box-arrow-right me-1 fs-5"></i>
                    下班打卡
                    <div class="small fw-normal mt-1" style="font-size: 0.75rem;">
                      {{ isClockedIn ? '點擊結束下班' : '尚未開始工作' }}
                    </div>
                  </button>
                </div>
              </div>

              <!-- 狀態提示文字 -->
              <div class="text-center small mt-2">
                <span v-if="!isClockedIn" class="text-muted">
                  <i class="bi bi-info-circle me-1"></i>開始工作時點擊綠色「上班打卡」；工作結束時點擊紅色「下班打卡」。
                </span>
                <span v-else class="text-danger fw-bold">
                  <i class="bi bi-broadcast me-1"></i>出勤工作中！工作完成後，請點擊右方紅色「下班打卡」結算薪資。
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右側：今日出勤明細 -->
      <div class="col-lg-7">
        <div class="card border-0 shadow-sm rounded-4 h-100">
          <div class="card-header bg-white py-3 px-4 border-bottom d-flex justify-content-between align-items-center">
            <h6 class="fw-bold mb-0 text-dark">
              <i class="bi bi-calendar-check me-2 text-primary"></i>今日打卡紀錄 ({{ todayRecords.length }})
            </h6>
            <button class="btn btn-sm btn-outline-secondary" @click="fetchStatus" title="重新整理">
              <i class="bi bi-arrow-clockwise me-1"></i>重新整理
            </button>
          </div>
          <div class="card-body p-0">
            <div v-if="todayRecords.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-inbox fs-1 d-block mb-2 text-secondary opacity-50"></i>
              今日尚無打卡記錄，請在左側點擊「上班打卡」
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light small">
                  <tr>
                    <th>上班打卡</th>
                    <th>下班打卡</th>
                    <th>有效工時</th>
                    <th>時薪</th>
                    <th>當班薪資</th>
                    <th>打卡 IP</th>
                    <th>狀態</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in todayRecords" :key="r.id">
                    <td class="small">
                      <div class="font-monospace fw-semibold text-success">
                        <i class="bi bi-box-arrow-in-right me-1"></i>{{ formatTimeOnly(r.clock_in) }}
                      </div>
                      <div class="text-muted small" style="font-size: 0.75rem;">
                        起算: {{ formatTimeHm(r.effective_clock_in || getEffectiveIn(r.clock_in)) }}
                      </div>
                    </td>
                    <td class="small">
                      <template v-if="r.clock_out">
                        <div class="font-monospace fw-semibold text-danger">
                          <i class="bi bi-box-arrow-right me-1"></i>{{ formatTimeOnly(r.clock_out) }}
                        </div>
                        <div class="text-muted small" style="font-size: 0.75rem;">
                          截止: {{ formatTimeHm(r.effective_clock_out || getEffectiveOut(r.clock_out)) }}
                        </div>
                      </template>
                      <span v-else class="badge bg-success-subtle text-success">進行中...</span>
                    </td>
                    <td class="fw-bold">
                      {{ r.clock_out ? `${r.work_hours} 小時` : '-' }}
                    </td>
                    <td class="small text-muted">NT$ {{ r.hourly_rate }}</td>
                    <td class="fw-bold text-success">
                      {{ r.clock_out ? `NT$ ${Math.floor(r.total_pay).toLocaleString()}` : '計算中...' }}
                    </td>
                    <td class="small font-monospace">
                      <div v-if="r.clock_in_ip" class="text-success text-truncate" style="max-width: 130px;" :title="`上班 IP: ${r.clock_in_ip}`">
                        <i class="bi bi-box-arrow-in-right me-1"></i>{{ r.clock_in_ip }}
                      </div>
                      <div v-if="r.clock_out_ip" class="text-danger text-truncate" style="max-width: 130px;" :title="`下班 IP: ${r.clock_out_ip}`">
                        <i class="bi bi-box-arrow-right me-1"></i>{{ r.clock_out_ip }}
                      </div>
                      <span v-if="!r.clock_in_ip && !r.clock_out_ip" class="text-muted">-</span>
                    </td>
                    <td>
                      <span v-if="r.clock_out" class="badge bg-secondary">已下班</span>
                      <span v-else class="badge bg-success">工作中</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 歷史紀錄與月度統計 -->
    <div class="card border-0 shadow-sm rounded-4 mt-4">
      <div class="card-header bg-white py-3 px-4 border-bottom">
        <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
          <h5 class="fw-bold mb-0 text-dark">
            <i class="bi bi-journal-text me-2 text-primary"></i>打卡出勤歷史明細與結算
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
            <!-- 管理員專用：可篩選員工 -->
            <div v-if="isAdmin" class="d-flex align-items-center">
              <span class="small text-muted me-2">員工：</span>
              <select class="form-select form-select-sm" v-model="filterUserId" @change="fetchHistory">
                <option value="">全部員工</option>
                <option v-for="u in staffUsers" :key="u.id" :value="u.id">
                  {{ u.name }} ({{ u.role === 'desk' ? '櫃檯' : u.role }})
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
                <i class="bi bi-calendar-range me-1 text-primary"></i>當月累計出勤班次
              </div>
              <div class="fs-4 fw-bold text-dark">{{ summary.total_shifts }} <span class="fs-6 fw-normal text-muted">次</span></div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="bg-white p-3 rounded-3 shadow-sm border">
              <div class="text-muted small mb-1">
                <i class="bi bi-hourglass-split me-1 text-primary"></i>當月累計總工時
              </div>
              <div class="fs-4 fw-bold text-primary">{{ summary.total_hours }} <span class="fs-6 fw-normal text-muted">小時</span></div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="bg-white p-3 rounded-3 shadow-sm border">
              <div class="text-muted small mb-1">
                <i class="bi bi-cash-coin me-1 text-success"></i>當月預計結算薪資
              </div>
              <div class="fs-4 fw-bold text-success">NT$ {{ Math.floor(summary.total_pay).toLocaleString() }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 計薪規則說明提示條 -->
      <div class="alert alert-info py-2 px-3 mx-4 my-3 d-flex align-items-center small">
        <i class="bi bi-info-circle-fill fs-5 me-2 text-info"></i>
        <div>
          <strong>出勤計薪規範：</strong>
          有效工時以 <strong>30 分鐘</strong> 為單位（例：8:40 上班算 9:00 起算、9:45 下班算 9:30 截止）；薪資結算 <strong>不到 1 元不算 1 元</strong>（無條件捨去小數點角分，保留整數元）。
        </div>
      </div>

      <!-- 歷史明細表格 -->
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light small">
            <tr>
              <th scope="col">ID</th>
              <th scope="col" v-if="isAdmin">員工姓名</th>
              <th scope="col">出勤日期</th>
              <th scope="col">上班打卡</th>
              <th scope="col">下班打卡</th>
              <th scope="col">有效工時</th>
              <th scope="col">時薪</th>
              <th scope="col">薪資小計</th>
              <th scope="col">打卡 IP</th>
              <th scope="col">備註</th>
              <th scope="col" v-if="isAdmin" class="text-center" style="width: 140px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="historyRecords.length === 0">
              <td :colspan="isAdmin ? 11 : 9" class="text-center py-4 text-muted">
                該月份查無出勤打卡紀錄
              </td>
            </tr>
            <tr v-for="h in historyRecords" :key="h.id">
              <td>#{{ h.id }}</td>
              <td v-if="isAdmin" class="fw-bold">
                {{ h.user_name }}
                <span class="badge bg-secondary-subtle text-secondary small ms-1">{{ h.role }}</span>
              </td>
              <td>{{ formatDate(h.clock_in) }}</td>
              <td class="small">
                <div class="font-monospace fw-semibold text-success">
                  <i class="bi bi-box-arrow-in-right me-1"></i>{{ formatTimeOnly(h.clock_in) }}
                </div>
                <div class="text-muted small" style="font-size: 0.75rem;">
                  起算: {{ formatTimeHm(h.effective_clock_in || getEffectiveIn(h.clock_in)) }}
                </div>
              </td>
              <td class="small">
                <template v-if="h.clock_out">
                  <div class="font-monospace fw-semibold text-danger">
                    <i class="bi bi-box-arrow-right me-1"></i>{{ formatTimeOnly(h.clock_out) }}
                  </div>
                  <div class="text-muted small" style="font-size: 0.75rem;">
                    截止: {{ formatTimeHm(h.effective_clock_out || getEffectiveOut(h.clock_out)) }}
                  </div>
                </template>
                <span v-else class="badge bg-warning text-dark">未打卡下班</span>
              </td>
              <td class="fw-bold">
                {{ h.clock_out ? `${h.work_hours} 小時` : '-' }}
              </td>
              <td class="small text-muted">NT$ {{ h.hourly_rate }}</td>
              <td class="fw-bold text-success">
                {{ h.clock_out ? `NT$ ${Math.floor(h.total_pay).toLocaleString()}` : '計算中...' }}
              </td>
              <td class="small font-monospace">
                <div v-if="h.clock_in_ip" class="text-success text-truncate" style="max-width: 140px;" :title="`上班打卡 IP: ${h.clock_in_ip}`">
                  <i class="bi bi-box-arrow-in-right me-1"></i>{{ h.clock_in_ip }}
                </div>
                <div v-if="h.clock_out_ip" class="text-danger text-truncate" style="max-width: 140px;" :title="`下班打卡 IP: ${h.clock_out_ip}`">
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
                  title="編輯打卡時間與薪資"
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

    <!-- 編輯出勤打卡紀錄 Modal -->
    <div v-if="showEditModal" class="modal-backdrop fade show"></div>
    <div v-if="showEditModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rounded-4 shadow border-0 overflow-hidden">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title fw-bold">
              <i class="bi bi-pencil-square me-2"></i>編輯出勤打卡時間與薪資
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="closeEditModal"></button>
          </div>
          <form @submit.prevent="submitEditRecord">
            <div class="modal-body p-4 text-start">
              <!-- 員工基本資訊卡 -->
              <div class="bg-light p-3 rounded-3 mb-3 border d-flex justify-content-between align-items-center">
                <div>
                  <div class="fw-bold text-dark fs-6">{{ editingRecord?.user_name }}</div>
                  <div class="small text-muted font-monospace">紀錄編號: #{{ editForm.id }}</div>
                </div>
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle">
                  {{ editingRecord?.role || '員工' }}
                </span>
              </div>

              <!-- 上班打卡時間 -->
              <div class="mb-3">
                <label class="form-label fw-semibold text-dark">
                  <i class="bi bi-box-arrow-in-right text-success me-1"></i>上班打卡時間：
                </label>
                <input 
                  type="datetime-local" 
                  class="form-control font-monospace" 
                  v-model="editForm.clock_in" 
                  required 
                  step="1" 
                />
                <div class="form-text small text-muted">
                  計薪起算時間：
                  <strong class="text-primary font-monospace">
                    {{ formatTimeHm(computedEditEffectiveIn) }}
                  </strong>
                  （30分鐘往後進位）
                </div>
              </div>

              <!-- 下班打卡時間 -->
              <div class="mb-3">
                <label class="form-label fw-semibold text-dark">
                  <i class="bi bi-box-arrow-right text-danger me-1"></i>下班打卡時間：
                </label>
                <input 
                  type="datetime-local" 
                  class="form-control font-monospace" 
                  v-model="editForm.clock_out" 
                  step="1" 
                />
                <div class="form-text small text-muted">
                  <template v-if="editForm.clock_out">
                    計薪截止時間：
                    <strong class="text-danger font-monospace">
                      {{ formatTimeHm(computedEditEffectiveOut) }}
                    </strong>
                    （30分鐘往前退位）
                  </template>
                  <span v-else class="text-warning">留空表示該班次仍在上班中</span>
                </div>
              </div>

              <!-- 時薪調整 -->
              <div class="mb-3">
                <label class="form-label fw-semibold text-dark">
                  <i class="bi bi-cash me-1 text-primary"></i>時薪 (元/小時)：
                </label>
                <div class="input-group">
                  <span class="input-group-text">$</span>
                  <input 
                    type="number" 
                    class="form-control font-monospace" 
                    v-model.number="editForm.hourly_rate" 
                    min="0" 
                    step="1" 
                    required 
                  />
                  <span class="input-group-text">/小時</span>
                </div>
              </div>

              <!-- 即時重算工時與薪資預覽 -->
              <div class="p-3 bg-primary-subtle rounded-3 mb-3 border border-primary-subtle">
                <div class="d-flex justify-content-between align-items-center mb-1 small">
                  <span class="text-muted"><i class="bi bi-clock me-1 text-primary"></i>重新計算有效工時：</span>
                  <strong class="text-primary font-monospace fs-6">{{ computedEditWorkHours }} 小時</strong>
                </div>
                <div class="d-flex justify-content-between align-items-center small">
                  <span class="text-muted"><i class="bi bi-cash-coin me-1 text-success"></i>重新計算結算薪資：</span>
                  <div>
                    <strong class="text-success fs-5">NT$ {{ computedEditTotalPay.toLocaleString() }}</strong>
                    <span class="small text-muted ms-1">(不到1元捨去)</span>
                  </div>
                </div>
              </div>

              <!-- 備註說明 -->
              <div class="mb-2">
                <label class="form-label fw-semibold text-dark">
                  <i class="bi bi-pencil-square me-1 text-secondary"></i>紀錄備註：
                </label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="editForm.notes" 
                  placeholder="例如：管理員修正下班時間、補登出勤" 
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
  name: 'Attendance',
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
      isClockedIn: false,
      activeShift: null,
      todayRecords: [],
      historyRecords: [],
      summary: {
        total_shifts: 0,
        total_hours: 0,
        total_pay: 0
      },
      staffUsers: [],
      selectedMonth: currentMonth,
      filterUserId: '',
      punchNotes: '',
      punching: false,
      currentTime: new Date(),
      timer: null,
      showEditModal: false,
      editingRecord: null,
      editForm: {
        id: null,
        clock_in: '',
        clock_out: '',
        hourly_rate: 0,
        notes: ''
      },
      savingEdit: false
    };
  },
  computed: {
    isAdmin() {
      return this.adminAuth.currentRole === 'admin';
    },
    isDesk() {
      return this.adminAuth.currentRole === 'desk';
    },
    userHourlyRate() {
      if (this.activeShift?.hourly_rate) {
        return this.activeShift.hourly_rate;
      }
      return this.adminAuth.currentUser?.hourly_rate || 0;
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
    // 上班計薪起算時間 (30分鐘往後進位)
    activeEffectiveClockIn() {
      if (!this.activeShift?.clock_in) return null;
      if (this.activeShift.effective_clock_in) {
        return new Date(this.activeShift.effective_clock_in);
      }
      return this.roundClockIn(this.activeShift.clock_in);
    },
    // 若當前時間下班，計薪截止時間 (30分鐘往前退位)
    currentEffectiveClockOut() {
      return this.roundClockOut(this.currentTime);
    },
    // 即時打卡實際經過時間
    liveWorkDuration() {
      if (!this.activeShift?.clock_in) return '0 小時 0 分 0 秒';
      const start = new Date(this.activeShift.clock_in).getTime();
      const now = this.currentTime.getTime();
      const diffSeconds = Math.max(0, Math.floor((now - start) / 1000));
      const hours = Math.floor(diffSeconds / 3600);
      const minutes = Math.floor((diffSeconds % 3600) / 60);
      const seconds = diffSeconds % 60;
      return `${hours} 小時 ${minutes} 分 ${seconds} 秒`;
    },
    // 即時有效計薪工時 (以30分鐘為單位，0.5小時倍數)
    liveEffectiveWorkHours() {
      if (!this.activeEffectiveClockIn) return 0;
      const effInTime = this.activeEffectiveClockIn.getTime();
      const effOutTime = this.currentEffectiveClockOut.getTime();
      const diffMs = effOutTime - effInTime;
      if (diffMs <= 0) return 0;
      return Math.round((diffMs / (3600 * 1000)) * 10) / 10;
    },
    // 即時預估薪資 (不到1元不算1元，無條件捨去小數點角分)
    liveEstimatedPay() {
      if (!this.activeEffectiveClockIn) return 0;
      const hours = this.liveEffectiveWorkHours;
      const rate = this.userHourlyRate;
      return Math.floor(hours * rate);
    },
    // 編輯 Modal 即時計算起算時間
    computedEditEffectiveIn() {
      if (!this.editForm.clock_in) return null;
      return this.roundClockIn(this.editForm.clock_in);
    },
    // 編輯 Modal 即時計算截止時間
    computedEditEffectiveOut() {
      if (!this.editForm.clock_out) return null;
      return this.roundClockOut(this.editForm.clock_out);
    },
    // 編輯 Modal 即時重算工時
    computedEditWorkHours() {
      if (!this.editForm.clock_in || !this.editForm.clock_out) return 0;
      const effIn = this.computedEditEffectiveIn;
      const effOut = this.computedEditEffectiveOut;
      if (!effIn || !effOut) return 0;
      const diffMs = effOut.getTime() - effIn.getTime();
      if (diffMs <= 0) return 0;
      return Math.round((diffMs / (3600 * 1000)) * 10) / 10;
    },
    // 編輯 Modal 即時重算薪資 (不到1元不算1元)
    computedEditTotalPay() {
      const hours = this.computedEditWorkHours;
      const rate = Number(this.editForm.hourly_rate) || 0;
      return Math.floor(hours * rate);
    }
  },
  created() {
    this.fetchStatus();
    this.fetchHistory();
    if (this.isAdmin) {
      this.fetchStaffUsers();
    }
  },
  mounted() {
    // 啟動即時時鐘
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
    roundClockIn(dateObj) {
      if (!dateObj) return null;
      const d = new Date(dateObj);
      const m = d.getMinutes();
      const s = d.getSeconds();
      const ms = d.getMilliseconds();
      if (m === 0 && s === 0 && ms === 0) return d;
      if (m < 30 || (m === 30 && s === 0 && ms === 0)) {
        d.setMinutes(30, 0, 0);
        return d;
      } else {
        d.setHours(d.getHours() + 1, 0, 0, 0);
        return d;
      }
    },
    roundClockOut(dateObj) {
      if (!dateObj) return null;
      const d = new Date(dateObj);
      const m = d.getMinutes();
      if (m < 30) {
        d.setMinutes(0, 0, 0);
        return d;
      } else {
        d.setMinutes(30, 0, 0);
        return d;
      }
    },
    getEffectiveIn(dateStr) {
      if (!dateStr) return null;
      return this.roundClockIn(dateStr);
    },
    getEffectiveOut(dateStr) {
      if (!dateStr) return null;
      return this.roundClockOut(dateStr);
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
    formatTimeHm(dateStrOrObj) {
      if (!dateStrOrObj) return '-';
      const d = (dateStrOrObj instanceof Date) ? dateStrOrObj : new Date(dateStrOrObj);
      if (isNaN(d.getTime())) return '-';
      return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    },
    formatDateTime(dateStr) {
      if (!dateStr) return '-';
      const d = new Date(dateStr);
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    },
    async fetchStatus() {
      const uid = this.adminAuth.currentUser?.id;
      if (!uid) return;
      try {
        const res = await api.get(`/admin/attendance/status?user_id=${uid}`);
        if (res.success) {
          this.isClockedIn = res.is_clocked_in;
          this.activeShift = res.active_shift;
          this.todayRecords = res.today_records || [];
          if (res.client_ip) {
            this.currentClientIp = res.client_ip;
          }
        }
      } catch (err) {
        console.error('查詢打卡狀態失敗:', err);
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
      let url = `/admin/attendance?month=${this.selectedMonth}`;
      if (uid) {
        url += `&user_id=${uid}`;
      }
      try {
        const res = await api.get(url);
        if (res.success) {
          this.historyRecords = res.records || [];
          this.summary = res.summary || { total_shifts: 0, total_hours: 0, total_pay: 0 };
        }
      } catch (err) {
        console.error('獲取出勤歷史失敗:', err);
      }
    },
    async fetchStaffUsers() {
      try {
        const res = await api.get('/admin/users');
        if (res.success) {
          this.staffUsers = res.users || [];
        }
      } catch (err) {
        console.error('獲取員工清單失敗:', err);
      }
    },
    async handleClockIn() {
      const uid = this.adminAuth.currentUser?.id;
      if (!uid) {
        showToast('請先登入後台！', 'error');
        return;
      }
      this.punching = true;
      try {
        const res = await api.post('/admin/attendance/clock-in', {
          user_id: uid,
          notes: this.punchNotes
        });
        if (res.success) {
          showToast(res.message || '上班打卡成功！祝您工作愉快！', 'success');
          this.punchNotes = '';
          await this.fetchStatus();
          await this.fetchHistory();
        }
      } catch (err) {
        showToast(err.message || '上班打卡失敗，請稍後再試', 'error');
      } finally {
        this.punching = false;
      }
    },
    async handleClockOut() {
      const uid = this.adminAuth.currentUser?.id;
      if (!uid) return;

      const ok = await showConfirm('確定現在要進行【下班打卡】嗎？系統將自動計算本次出勤工時與薪資。');
      if (!ok) return;

      this.punching = true;
      try {
        const res = await api.post('/admin/attendance/clock-out', {
          user_id: uid,
          notes: this.punchNotes
        });
        if (res.success) {
          showToast(res.message || '下班打卡成功！辛苦了！', 'success');
          this.punchNotes = '';
          await this.fetchStatus();
          await this.fetchHistory();
        }
      } catch (err) {
        showToast(err.message || '下班打卡失敗，請稍後再試', 'error');
      } finally {
        this.punching = false;
      }
    },
    async deleteRecord(id) {
      const ok = await showConfirm('確定要刪除這筆打卡記錄嗎？');
      if (!ok) return;
      try {
        const res = await api.delete(`/admin/attendance/${id}`);
        if (res.success) {
          showToast('打卡記錄已刪除', 'success');
          this.fetchHistory();
          this.fetchStatus();
        }
      } catch (err) {
        showToast(err.message || '刪除失敗', 'error');
      }
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
    openEditModal(record) {
      this.editingRecord = record;
      this.editForm = {
        id: record.id,
        clock_in: this.toDatetimeLocal(record.clock_in),
        clock_out: this.toDatetimeLocal(record.clock_out),
        hourly_rate: record.hourly_rate,
        notes: record.notes || ''
      };
      this.showEditModal = true;
    },
    closeEditModal() {
      this.showEditModal = false;
      this.editingRecord = null;
    },
    async submitEditRecord() {
      if (!this.editForm.clock_in) {
        showToast('上班打卡時間不可為空', 'error');
        return;
      }
      if (this.editForm.clock_out && new Date(this.editForm.clock_out) < new Date(this.editForm.clock_in)) {
        showToast('下班打卡時間不可早於上班打卡時間', 'error');
        return;
      }

      this.savingEdit = true;
      try {
        const res = await api.put(`/admin/attendance/${this.editForm.id}`, {
          clock_in: this.editForm.clock_in,
          clock_out: this.editForm.clock_out || null,
          hourly_rate: this.editForm.hourly_rate,
          notes: this.editForm.notes
        });
        if (res.success) {
          showToast(res.message || '出勤紀錄已成功更新！', 'success');
          this.closeEditModal();
          await this.fetchStatus();
          await this.fetchHistory();
        }
      } catch (err) {
        showToast(err.message || '更新失敗，請檢查輸入內容', 'error');
      } finally {
        this.savingEdit = false;
      }
    }
  }
};
</script>

<style scoped>
.attendance-page {
  padding: 10px;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
}

.bg-gradient-success {
  background: linear-gradient(135deg, #198754 0%, #157347 100%);
}

.avatar-circle {
  width: 70px;
  height: 70px;
  border-radius: 50%;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #ffc107;
  display: inline-block;
}

.pulsing-dot {
  background-color: #20c997;
  box-shadow: 0 0 0 0 rgba(32, 201, 151, 0.7);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(32, 201, 151, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 10px rgba(32, 201, 151, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(32, 201, 151, 0);
  }
}

.punch-btn {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.punch-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15) !important;
}

.punch-btn:active:not(:disabled) {
  transform: translateY(1px);
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

