<template>
  <div v-if="auth.state.showProfileModal && student" class="modal-backdrop-custom" @click.self="close">
    <div class="modal-dialog-custom">
      <div class="modal-content-custom shadow-lg">
        <!-- Header -->
        <div class="modal-header-custom">
          <div class="d-flex align-items-center">
            <div class="avatar-circle me-3">
              {{ studentInitials }}
            </div>
            <div>
              <h5 class="modal-title mb-0 fw-bold">{{ student.name }}</h5>
              <small class="text-muted"><i class="bi bi-telephone me-1"></i>{{ student.phone }}</small>
            </div>
          </div>
          <button type="button" class="btn-close-custom" @click="close" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <!-- 堂數亮點卡片 -->
        <div class="px-4 pt-3 pb-0">
          <div class="remaining-card p-3 rounded-3 d-flex justify-content-between align-items-center">
            <div>
              <div class="small text-white-50">目前剩餘堂數</div>
              <div class="remaining-count fw-bold text-white">
                {{ student.remaining_classes !== undefined ? student.remaining_classes : '--' }}
                <span class="fs-6 fw-normal">堂</span>
              </div>
              <div v-if="student.membership_expiry || student.expiry_date" class="small text-white-50 mt-1">
                會員年費：{{ formatDate(student.membership_expiry || student.expiry_date) }} |
                <span v-if="hasActiveMonthlyPass" class="text-warning fw-bold">月費 (至 {{ formatDate(student.monthly_pass_expiry) }})</span>
                <span v-else-if="student.monthly_pass_expiry" class="text-white-50">月費已過期</span>
                <span v-else class="text-white-50">月費未開通</span>
              </div>
            </div>
            <button
              class="btn btn-sm btn-outline-light d-flex align-items-center"
              @click="handleRefresh"
              :disabled="refreshing"
              title="重新整理堂數"
            >
              <i class="bi bi-arrow-clockwise me-1" :class="{ 'spin-icon': refreshing }"></i>
              {{ refreshing ? '更新中' : '重新整理' }}
            </button>
          </div>
        </div>

        <!-- 標籤切換 -->
        <div class="px-4 pt-3">
          <ul class="nav nav-tabs profile-tabs">
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'bookings' }"
                @click="switchTab('bookings')"
              >
                <i class="bi bi-calendar-check me-1"></i>我的預約紀錄
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'orders' }"
                @click="switchTab('orders')"
              >
                <i class="bi bi-receipt me-1"></i>購課紀錄
                <span v-if="orders && orders.length > 0" class="badge bg-secondary-subtle text-secondary ms-1" style="font-size: 0.65rem;">{{ orders.length }}</span>
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'info' }"
                @click="switchTab('info')"
              >
                <i class="bi bi-person-lines-fill me-1"></i>基本資料
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'password' }"
                @click="switchTab('password')"
              >
                <i class="bi bi-key-fill me-1"></i>修改密碼
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'line' }"
                @click="switchTab('line')"
              >
                <i class="bi bi-line text-success me-1"></i>LINE 關聯
                <span v-if="student.line_user_id" class="badge bg-success ms-1" style="font-size: 0.65rem;">已綁定</span>
              </button>
            </li>
          </ul>
        </div>

        <!-- Body -->
        <div class="modal-body-custom">
          <!-- 標籤 1：預約紀錄 -->
          <div v-if="activeTab === 'bookings'">
            <div v-if="loadingEnrollments" class="text-center py-4">
              <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
              <div class="small text-muted mt-2">載入預約紀錄中...</div>
            </div>

            <div v-else-if="enrollments.length === 0" class="text-center py-4 text-muted">
              <i class="bi bi-calendar-x fs-1 d-block mb-2 text-secondary"></i>
              目前尚無任何預約課程紀錄
              <div class="mt-2">
                <router-link to="/schedule" class="btn btn-outline-primary btn-sm" @click="close">
                  前往瀏覽課表
                </router-link>
              </div>
            </div>

            <div v-else class="enrollment-list">
              <div
                v-for="item in enrollments"
                :key="item.id"
                class="card mb-2 border-0 shadow-sm enrollment-card"
              >
                <div class="card-body p-3">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <h6 class="fw-bold mb-0 text-primary fs-6">{{ item.course_name || item.lesson_name || '舞蹈課程' }}</h6>
                      <div class="small text-muted mt-1" v-if="item.dance_type || item.lesson_type">
                        <span class="badge bg-light text-dark border me-1">{{ item.dance_type || item.lesson_type }}</span>
                        <span class="badge bg-light text-secondary border" v-if="item.lesson_level || item.level">{{ item.lesson_level || item.level }}</span>
                      </div>
                    </div>
                    <span class="badge px-2 py-1" :class="getStatusBadgeClass(item.status)">
                      {{ formatStatus(item.status) }}
                    </span>
                  </div>

                  <div class="small text-dark mb-1">
                    <i class="bi bi-calendar3 me-1 text-primary"></i>
                    <strong>{{ item.schedule_date || item.lesson_day || '' }}</strong>
                    <span v-if="item.day_of_week" class="ms-1">({{ item.day_of_week }})</span>
                    <span class="ms-2 text-secondary">
                      <i class="bi bi-clock me-1 text-primary"></i>{{ item.schedule_time || item.lesson_time || '時間依課表' }}
                    </span>
                  </div>

                  <div class="small text-muted d-flex justify-content-between pt-2 border-top mt-2">
                    <span>
                      <i class="bi bi-person-badge me-1"></i>授課老師：<strong class="text-dark">{{ item.teacher_name || item.lesson_teacher || '未指定' }}</strong>
                    </span>
                    <span>
                      <i class="bi bi-geo-alt me-1"></i>教室：<strong class="text-dark">{{ item.classroom_name || item.room_name || 'Dance Studio' }}</strong>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

                    <!-- 標籤 2：購課紀錄 -->
          <div v-else-if="activeTab === 'orders'">
            <div v-if="loadingOrders" class="text-center py-4">
              <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
              <div class="small text-muted mt-2">載入購課紀錄中...</div>
            </div>

            <div v-else-if="orders.length === 0" class="text-center py-4 text-muted">
              <i class="bi bi-receipt fs-1 d-block mb-2 text-secondary opacity-50"></i>
              <p class="mb-2">目前尚無購課紀錄</p>
              <a href="/pricing" @click="close" class="btn btn-outline-primary btn-sm">
                <i class="bi bi-tag me-1"></i>前往查看課程價目表買課
              </a>
            </div>

            <div v-else class="orders-list">
              <div
                v-for="order in orders"
                :key="order.id"
                class="order-card p-3 mb-3 bg-light rounded-3 border text-start"
              >
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <div>
                    <span class="fw-bold fs-6 text-dark me-2">{{ order.plan_title }}</span>
                    <span class="badge bg-primary-subtle text-primary border border-primary-subtle font-monospace">
                      {{ order.price }}
                    </span>
                    <span v-if="order.plan_type === 'membership_fee'" class="badge border ms-1" style="background-color: #fef3c7; color: #b45309; border-color: #fcd34d !important;">
                      會員年費 ({{ order.validity_days || 365 }} 天)
                    </span>
                    <span v-else-if="order.plan_type === 'monthly_pass'" class="badge border ms-1" style="background-color: #f3e8ff; color: #7e22ce; border-color: #d8b4fe !important;">
                      月票 ({{ order.validity_days || 30 }} 天)
                    </span>
                    <span v-if="order.classes_count && (order.plan_type === 'classes' || order.classes_count > 0)" class="badge bg-success-subtle text-success ms-1">
                      +{{ order.classes_count }} 堂
                    </span>
                  </div>
                  <span class="badge" :class="getOrderStatusBadgeClass(order.status)">
                    {{ formatOrderStatus(order.status) }}
                  </span>
                </div>

                <div class="small text-muted mb-2">
                  <span class="me-3"><i class="bi bi-hash me-1"></i>單號：<span class="font-monospace text-dark">{{ order.order_no }}</span></span>
                  <span><i class="bi bi-clock me-1"></i>{{ formatDateTime(order.created_at) }}</span>
                </div>

                <div class="p-2 bg-white rounded border small mb-2 d-flex justify-content-between align-items-center">
                  <div>
                    <span class="text-muted">轉帳銀行後5碼：</span>
                    <strong class="font-monospace text-dark fs-6">{{ order.bank_last_5 }}</strong>
                  </div>
                  <div v-if="order.status === 'pending'" class="text-warning-emphasis small">
                    <i class="bi bi-hourglass-split me-1"></i>工作人員核對中
                  </div>
                  <div v-else-if="order.status === 'confirmed'" class="text-success small fw-bold">
                    <i class="bi bi-check-circle-fill me-1"></i>已確認入帳加堂
                  </div>
                  <div v-else-if="order.status === 'rejected'" class="text-danger small fw-bold">
                    <i class="bi bi-x-circle-fill me-1"></i>已駁回
                  </div>
                </div>

                <div v-if="order.notes" class="small text-muted mb-1">
                  <span class="text-secondary">學員備註：</span>{{ order.notes }}
                </div>
                <div v-if="order.admin_notes" class="small p-2 bg-warning-subtle text-dark rounded border border-warning-subtle mt-1">
                  <strong>後台回覆備註：</strong>{{ order.admin_notes }}
                </div>
              </div>
            </div>
          </div>

          <!-- 標籤 2：基本資料 -->
          <div v-else-if="activeTab === 'info'" class="info-list">
            <div class="row g-3">
              <div class="col-sm-6">
                <label class="text-muted small">學員姓名</label>
                <div class="fw-bold">{{ student.name }}</div>
              </div>
              <div class="col-sm-6">
                <label class="text-muted small">手機號碼</label>
                <div class="fw-bold">{{ student.phone }}</div>
              </div>
              <div class="col-sm-6">
                <label class="text-muted small">電子信箱</label>
                <div>{{ student.email || '未填寫' }}</div>
              </div>
              <div class="col-sm-6">
                <label class="text-muted small">會員年費到期日</label>
                <div class="fw-bold text-dark"><i class="bi bi-award text-warning me-1"></i>{{ formatDate(student.membership_expiry || student.expiry_date) || '無效期限制' }}</div>
              </div>
              <div class="col-sm-6">
                <label class="text-muted small">月費暢跳到期日</label>
                <div class="fw-bold" :class="hasActiveMonthlyPass ? 'text-primary' : 'text-muted'">
                  <i class="bi bi-calendar-check me-1"></i>
                  <span v-if="student.monthly_pass_expiry">{{ formatDate(student.monthly_pass_expiry) }}</span>
                  <span v-else>未開通</span>
                  <span v-if="hasActiveMonthlyPass" class="badge bg-success-subtle text-success ms-2 small">暢跳中（免扣堂）</span>
                </div>
              </div>
              <div class="col-sm-6">
                <label class="text-muted small">約定轉帳銀行後 5 碼</label>
                <div class="input-group input-group-sm mt-1">
                  <input
                    type="text"
                    v-model.trim="bankLast5Input"
                    class="form-control font-monospace"
                    placeholder="例如：12345"
                    maxlength="10"
                    :disabled="savingBankLast5"
                  />
                  <button
                    class="btn btn-outline-primary"
                    type="button"
                    @click="handleSaveBankLast5"
                    :disabled="savingBankLast5"
                  >
                    <span v-if="savingBankLast5" class="spinner-border spinner-border-sm me-1"></span>
                    儲存
                  </button>
                </div>
                <small class="text-muted d-block mt-1">買課時會自動帶入此後5碼，方便快速對帳</small>
              </div>
              <div class="col-12" v-if="student.address">
                <label class="text-muted small">通訊地址</label>
                <div>{{ student.address }}</div>
              </div>
            </div>
            <div class="alert alert-light border small mt-4 mb-0">
              <i class="bi bi-info-circle me-1 text-primary"></i>
              如需變更手機號碼或基本資料，請聯繫現場櫃檯服務人員協助。
            </div>
          </div>

          <!-- 標籤 3：修改密碼 -->
          <div v-else-if="activeTab === 'password'">
            <div v-if="pwdSuccess" class="alert alert-success py-2 px-3 small mb-3">
              <i class="bi bi-check-circle-fill me-1"></i>{{ pwdSuccess }}
            </div>
            <div v-if="pwdError" class="alert alert-danger py-2 px-3 small mb-3">
              <i class="bi bi-exclamation-circle-fill me-1"></i>{{ pwdError }}
            </div>

            <form @submit.prevent="handleChangePassword">
              <div class="mb-3">
                <label class="form-label small fw-bold">舊密碼</label>
                <input
                  v-model="oldPassword"
                  type="password"
                  class="form-control form-control-sm"
                  placeholder="請輸入目前密碼"
                  required
                  :disabled="pwdLoading"
                />
              </div>

              <div class="mb-3">
                <label class="form-label small fw-bold">新密碼</label>
                <input
                  v-model="newPassword"
                  type="password"
                  class="form-control form-control-sm"
                  placeholder="請輸入新密碼 (至少4碼)"
                  required
                  minlength="4"
                  :disabled="pwdLoading"
                />
              </div>

              <div class="mb-3">
                <label class="form-label small fw-bold">確認新密碼</label>
                <input
                  v-model="confirmPassword"
                  type="password"
                  class="form-control form-control-sm"
                  placeholder="再次輸入新密碼"
                  required
                  minlength="4"
                  :disabled="pwdLoading"
                />
              </div>

              <div class="d-grid">
                <button type="submit" class="btn btn-primary btn-sm py-2 fw-bold" :disabled="pwdLoading">
                  <span v-if="pwdLoading" class="spinner-border spinner-border-sm me-1" role="status"></span>
                  {{ pwdLoading ? '更新中...' : '確認變更密碼' }}
                </button>
              </div>
            </form>
          </div>

          <!-- 標籤 4：LINE 帳號關聯 -->
          <div v-if="activeTab === 'line'" class="p-2">
            <!-- 已綁定狀態 -->
            <div v-if="student.line_user_id" class="line-status-box p-3 rounded-3 bg-light border">
              <div class="d-flex align-items-center mb-3">
                <img
                  v-if="student.line_picture_url"
                  :src="student.line_picture_url"
                  alt="LINE Avatar"
                  class="rounded-circle me-3 border border-2 border-success"
                  width="56"
                  height="56"
                  style="object-fit: cover;"
                />
                <div v-else class="rounded-circle bg-success text-white d-flex align-items-center justify-content-center me-3" style="width: 56px; height: 56px;">
                  <i class="bi bi-line fs-2"></i>
                </div>
                <div class="flex-grow-1">
                  <div class="d-flex align-items-center gap-2 mb-1">
                    <h6 class="fw-bold mb-0 text-dark">{{ student.line_display_name || '已綁定 LINE 用戶' }}</h6>
                    <span class="badge bg-success small"><i class="bi bi-check-circle-fill me-1"></i>已關聯</span>
                  </div>
                  <div class="small text-muted font-monospace mb-1">
                    <i class="bi bi-shield-check text-success me-1"></i>LINE ID: {{ formatLineId(student.line_user_id) }}
                  </div>
                  <div v-if="student.line_linked_at" class="text-muted" style="font-size: 0.75rem;">
                    關聯時間：{{ formatDateTime(student.line_linked_at) }}
                  </div>
                </div>
              </div>

              <div class="alert alert-success py-2 px-3 small mb-3">
                <i class="bi bi-info-circle-fill me-1"></i>
                您的帳號已成功與 LINE 綁定，未來可於首頁登入點選<strong>「LINE 快速登入」</strong>一鍵登入會員！
              </div>

              <div class="d-flex justify-content-end">
                <button
                  type="button"
                  class="btn btn-outline-danger btn-sm"
                  :disabled="lineUnbinding"
                  @click="handleUnbindLine"
                >
                  <span v-if="lineUnbinding" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi bi-link-45deg me-1"></i>解除 LINE 帳號關聯
                </button>
              </div>
            </div>

            <!-- 未綁定狀態 -->
            <div v-else class="text-center py-4">
              <div class="line-logo-circle mb-3 mx-auto">
                <svg viewBox="0 0 24 24" width="44" height="44" fill="#06C755">
                  <path d="M12 2C6.48 2 2 5.92 2 10.76c0 3.08 1.83 5.79 4.67 7.31-.2.72-.73 2.61-.84 3.01-.13.49.18.48.38.35.16-.11 2.22-1.51 3.12-2.13.88.24 1.78.37 2.67.37 5.52 0 10-3.92 10-8.91S17.52 2 12 2zm5.72 11.59h-2.17c-.24 0-.43-.19-.43-.43V8.84c0-.24.19-.43.43-.43h2.17c.24 0 .43.19.43.43v.68c0 .24-.19.43-.43.43h-1.31v.96h1.31c.24 0 .43.19.43.43v.68c0 .24-.19.43-.43.43h-1.31v.97h1.31c.24 0 .43.19.43.43v.68c0 .23-.19.42-.43.42zm-3.52-.43c0 .24-.19.43-.43.43h-.68c-.24 0-.43-.19-.43-.43V8.84c0-.24.19-.43.43-.43h.68c.24 0 .43.19.43.43v4.32zm-2.22 0c0 .18-.11.34-.27.4-.05.02-.11.03-.16.03-.12 0-.23-.05-.31-.13l-1.92-2.61v2.31c0 .24-.19.43-.43.43h-.68c-.24 0-.43-.19-.43-.43V8.84c0-.18.11-.34.27-.4.16-.06.35-.03.47.1l1.92 2.61V8.84c0-.24.19-.43.43-.43h.68c.24 0 .43.19.43.43v4.32zm-4.71 0c0 .24-.19.43-.43.43H4.7c-.24 0-.43-.19-.43-.43V8.84c0-.24.19-.43.43-.43h.68c.24 0 .43.19.43.43v3.46h1.01c.24 0 .43.19.43.43v.43z"/>
                </svg>
              </div>
              <h5 class="fw-bold text-dark mb-1">尚未關聯 LINE 帳號</h5>
              <p class="text-muted small px-3 mb-4">
                關聯官方 LINE 帳號後，您將可享受<strong>LINE 一鍵快速登入</strong>，報名管理更方便！
              </p>

              <div class="d-flex flex-column gap-2 col-md-8 mx-auto">
                <button
                  type="button"
                  class="btn btn-success fw-bold py-2 shadow-sm d-flex align-items-center justify-content-center gap-2"
                  :disabled="lineConnecting"
                  @click="handleStartLineAuth"
                >
                  <span v-if="lineConnecting" class="spinner-border spinner-border-sm"></span>
                  <i v-else class="bi bi-line fs-5"></i>
                  <span>立即授權綁定 LINE 帳號</span>
                </button>

                <button
                  type="button"
                  class="btn btn-outline-secondary btn-sm"
                  @click="showManualBindModal = !showManualBindModal"
                >
                  <i class="bi bi-pencil-square me-1"></i>手動輸入 / 模擬測試關聯
                </button>
              </div>

              <!-- 手動輸入/測試關聯卡 -->
              <div v-if="showManualBindModal" class="mt-3 p-3 bg-light rounded-3 text-start border col-md-10 mx-auto">
                <div class="fw-bold small mb-2 text-dark">
                  <i class="bi bi-tools me-1 text-primary"></i>手動設定或測試關聯：
                </div>
                <div class="mb-2">
                  <label class="form-label small mb-1">LINE 暱稱：</label>
                  <input
                    type="text"
                    v-model.trim="manualDisplayName"
                    class="form-control form-control-sm"
                    placeholder="例如：Alex / 小舞"
                  />
                </div>
                <div class="mb-3">
                  <label class="form-label small mb-1">LINE User ID：</label>
                  <input
                    type="text"
                    v-model.trim="manualUserId"
                    class="form-control form-control-sm font-monospace"
                    placeholder="以 U 開頭之 33 碼 (留空自動產生測試 ID)"
                  />
                </div>
                <button
                  type="button"
                  class="btn btn-primary btn-sm w-100"
                  :disabled="lineConnecting"
                  @click="handleManualBind"
                >
                  確認關聯此 LINE 帳號
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer-custom d-flex justify-content-between align-items-center">
          <button type="button" class="btn btn-outline-danger btn-sm" @click="handleLogout">
            <i class="bi bi-box-arrow-right me-1"></i>登出帳號
          </button>
          <button type="button" class="btn btn-secondary btn-sm" @click="close">關閉</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/utils/api'
import { useStudentAuth } from '@/utils/auth'
import { showToast } from '@/utils/toast'
import { showConfirm } from '@/utils/dialog'

export default {
  name: 'StudentProfileModal',
  data() {
    return {
      auth: useStudentAuth(),
      activeTab: 'bookings', // 'bookings' | 'info' | 'password'
      refreshing: false,
      loadingEnrollments: false,
      enrollments: [],
      orders: [],
      loadingOrders: false,
      bankLast5Input: '',
      savingBankLast5: false,
      // Password change form
      oldPassword: '',
      newPassword: '',
      confirmPassword: '',
      pwdLoading: false,
      pwdError: '',
      pwdSuccess: '',
      // LINE 關聯狀態
      lineConnecting: false,
      lineUnbinding: false,
      showManualBindModal: false,
      manualDisplayName: '',
      manualUserId: ''
    }
  },
  computed: {
    student() {
      return this.auth.state.student
    },
    studentInitials() {
      if (!this.student || !this.student.name) return '學'
      return this.student.name.charAt(0)
    },
    hasActiveMonthlyPass() {
      const exp = this.student?.monthly_pass_expiry
      if (!exp) return false
      try {
        const d = new Date(exp)
        if (isNaN(d.getTime())) return false
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        return d >= today
      } catch (e) {
        return false
      }
    }
  },
  watch: {
    'auth.state.showProfileModal'(isOpen) {
      if (isOpen && this.student) {
        this.bankLast5Input = this.student.bank_last_5 || ''
        if (this.activeTab === 'orders') {
          this.fetchOrders()
        } else {
          this.fetchEnrollments()
        }
        this.handleRefresh()
      }
    }
  },
  methods: {
    close() {
      this.auth.closeProfileModal()
      this.pwdError = ''
      this.pwdSuccess = ''
      this.oldPassword = ''
      this.newPassword = ''
      this.confirmPassword = ''
    },
    switchTab(tab) {
      this.activeTab = tab
      this.pwdError = ''
      this.pwdSuccess = ''
      if (tab === 'bookings') {
        this.fetchEnrollments()
      } else if (tab === 'orders') {
        this.fetchOrders()
      } else if (tab === 'info') {
        this.bankLast5Input = this.student?.bank_last_5 || ''
      }
    },
    async fetchOrders() {
      if (!this.student || !this.student.id) return
      this.loadingOrders = true
      try {
        const res = await api.get('/pricing/orders', { params: { student_id: this.student.id } })
        if (res.success) {
          this.orders = res.orders || []
        }
      } catch (err) {
        console.error('查詢購課紀錄失敗:', err)
      } finally {
        this.loadingOrders = false
      }
    },
    async handleSaveBankLast5() {
      const val = (this.bankLast5Input || '').trim()
      if (!val) {
        showToast('請輸入銀行後 5 碼', 'warning')
        return
      }
      this.savingBankLast5 = true
      try {
        const res = await api.put(`/student/${this.student.id}/bank-info`, { bank_last_5: val })
        if (res.success) {
          this.auth.setStudent({ ...this.student, bank_last_5: res.bank_last_5 })
          showToast(res.message || '銀行後 5 碼設定成功！', 'success')
        } else {
          showToast(res.error || '設定失敗', 'error')
        }
      } catch (err) {
        showToast(err.message || '設定失敗', 'error')
      } finally {
        this.savingBankLast5 = false
      }
    },
    getOrderStatusBadgeClass(status) {
      switch (status) {
        case 'confirmed':
          return 'bg-success'
        case 'pending':
          return 'bg-warning text-dark'
        case 'rejected':
          return 'bg-danger'
        default:
          return 'bg-secondary'
      }
    },
    formatOrderStatus(status) {
      switch (status) {
        case 'confirmed':
          return '已入帳加堂'
        case 'pending':
          return '待後台確認'
        case 'rejected':
          return '已駁回'
        case 'cancelled':
          return '已取消'
        default:
          return status || '待處理'
      }
    },
    formatDateTime(val) {
      if (!val) return ''
      try {
        const d = new Date(val)
        if (isNaN(d.getTime())) return val
        return d.toLocaleString('zh-TW', { hour12: false })
      } catch (e) {
        return val
      }
    },
    formatDate(val) {
      if (!val) return ''
      try {
        const d = new Date(val)
        if (isNaN(d.getTime())) return val
        return d.toLocaleDateString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit' })
      } catch (e) {
        return val
      }
    },
    getStatusBadgeClass(status) {
      switch (status) {
        case '已預約':
        case 'confirmed':
          return 'bg-success'
        case '已完成':
        case 'completed':
          return 'bg-secondary'
        case '已取消':
        case 'cancelled':
          return 'bg-danger'
        default:
          return 'bg-primary'
      }
    },
    formatStatus(status) {
      switch (status) {
        case 'confirmed':
        case '已預約':
          return '已預約'
        case 'completed':
        case '已完成':
          return '已完成'
        case 'cancelled':
        case '已取消':
          return '已取消'
        default:
          return status || '已預約'
      }
    },
    async handleRefresh() {
      this.refreshing = true
      try {
        await this.auth.refreshProfile()
      } catch (e) {
        // silent
      } finally {
        setTimeout(() => {
          this.refreshing = false
        }, 400)
      }
    },
    async fetchEnrollments() {
      if (!this.student || !this.student.id) return
      this.loadingEnrollments = true
      try {
        const res = await api.get(`/student/${this.student.id}/enrollments`)
        if (res.success && Array.isArray(res.enrollments)) {
          this.enrollments = res.enrollments
        } else {
          this.enrollments = []
        }
      } catch (e) {
        console.error('獲取預約失敗:', e)
        this.enrollments = []
      } finally {
        this.loadingEnrollments = false
      }
    },
    async handleChangePassword() {
      this.pwdError = ''
      this.pwdSuccess = ''

      if (!this.oldPassword) {
        this.pwdError = '請輸入舊密碼'
        return
      }
      if (!this.newPassword || this.newPassword.length < 4) {
        this.pwdError = '新密碼長度至少需要 4 碼'
        return
      }
      if (this.newPassword !== this.confirmPassword) {
        this.pwdError = '兩次輸入的新密碼不一致'
        return
      }

      this.pwdLoading = true
      try {
        const res = await api.post('/student/change-password', {
          student_id: this.student.id,
          old_password: this.oldPassword,
          new_password: this.newPassword
        })

        if (res.success) {
          this.pwdSuccess = '密碼修改成功！'
          this.oldPassword = ''
          this.newPassword = ''
          this.confirmPassword = ''
          showToast('密碼已成功修改', 'success')
        } else {
          this.pwdError = res.message || '修改失敗，請確認舊密碼是否正確'
        }
      } catch (err) {
        this.pwdError = err.message || '修改失敗，請確認舊密碼'
      } finally {
        this.pwdLoading = false
      }
    },
    handleLogout() {
      this.auth.logout()
      showToast('已安全登出', 'info')
      this.close()
    },
    formatLineId(id) {
      if (!id) return ''
      if (id.length <= 10) return id
      return id.substring(0, 6) + '...' + id.substring(id.length - 4)
    },
    formatDateTime(val) {
      if (!val) return ''
      try {
        const d = new Date(val)
        if (isNaN(d.getTime())) return val
        return d.toLocaleString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
      } catch (e) {
        return val
      }
    },
    async handleStartLineAuth() {
      this.lineConnecting = true
      try {
        const redirectUri = window.location.origin + '/line-callback'
        const state = `bind:${this.student.id}:${Date.now()}`
        const res = await api.get(`/line/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}&state=${encodeURIComponent(state)}`)

        if (res.success && res.configured && res.auth_url) {
          window.location.href = res.auth_url
        } else {
          showToast(res.message || '尚未設定 LINE Login Channel ID，您可先使用手動/模擬關聯測試！', 'warning')
          this.showManualBindModal = true
          this.manualDisplayName = this.student.name || '測試學員'
        }
      } catch (err) {
        showToast(err.message || '取得 LINE 授權網址失敗', 'error')
        this.showManualBindModal = true
      } finally {
        this.lineConnecting = false
      }
    },
    async handleManualBind() {
      if (!this.student || !this.student.id) return
      const displayName = this.manualDisplayName.trim() || this.student.name || 'LINE 用戶'
      const userId = this.manualUserId.trim() || ('Utest' + Math.random().toString(36).substring(2, 12) + Date.now().toString(36))

      this.lineConnecting = true
      try {
        const res = await api.post('/student/line/bind', {
          student_id: this.student.id,
          line_user_id: userId,
          line_display_name: displayName,
          line_picture_url: `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(displayName)}`
        })

        if (res.success && res.student) {
          this.auth.setStudent(res.student)
          showToast(res.message || 'LINE 帳號關聯成功！', 'success')
          this.showManualBindModal = false
          this.manualUserId = ''
          this.manualDisplayName = ''
        } else {
          showToast(res.error || res.message || '綁定失敗', 'error')
        }
      } catch (err) {
        showToast(err.message || '綁定失敗', 'error')
      } finally {
        this.lineConnecting = false
      }
    },
    async handleUnbindLine() {
      if (!this.student || !this.student.id) return
      const confirmed = await showConfirm(
        '確定要解除此會員的 LINE 帳號關聯嗎？解除後將無法使用 LINE 一鍵快速登入。',
        '解除 LINE 關聯'
      )
      if (!confirmed) return

      this.lineUnbinding = true
      try {
        const res = await api.post('/student/line/unbind', {
          student_id: this.student.id
        })

        if (res.success && res.student) {
          this.auth.setStudent(res.student)
          showToast('已成功解除 LINE 帳號關聯！', 'success')
        } else {
          showToast(res.error || res.message || '解除失敗', 'error')
        }
      } catch (err) {
        showToast(err.message || '解除失敗', 'error')
      } finally {
        this.lineUnbinding = false
      }
    }
  }
}
</script>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.65);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1060;
  padding: 1rem;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease-out;
}

.modal-dialog-custom {
  width: 100%;
  max-width: 520px;
  animation: slideDown 0.25s ease-out;
}

.modal-content-custom {
  background: #ffffff;
  border-radius: 1rem;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.modal-header-custom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.avatar-circle {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: linear-gradient(135deg, #20c997, #0d6efd);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  font-weight: bold;
  box-shadow: 0 4px 10px rgba(13, 110, 253, 0.25);
}

.btn-close-custom {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  color: #888;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.btn-close-custom:hover {
  color: #000;
  background-color: #f0f0f0;
}

.remaining-card {
  background: linear-gradient(135deg, #1f2937, #111827);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.remaining-count {
  font-size: 2.2rem;
  line-height: 1.1;
}

.profile-tabs .nav-link {
  color: #6c757d;
  font-weight: 500;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 0.5rem 0.85rem;
  font-size: 0.9rem;
}

.profile-tabs .nav-link.active {
  color: #0d6efd;
  border-bottom: 2px solid #0d6efd;
  background: transparent;
}

.modal-body-custom {
  padding: 1.25rem 1.5rem;
  max-height: 380px;
  overflow-y: auto;
}

.modal-footer-custom {
  padding: 1rem 1.5rem;
  background-color: #f8f9fa;
  border-top: 1px solid #f0f0f0;
}

.enrollment-card {
  background: #fdfdfd;
  border: 1px solid #edf0f2 !important;
  transition: transform 0.15s, box-shadow 0.15s;
}

.enrollment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

.spin-icon {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideDown {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>

