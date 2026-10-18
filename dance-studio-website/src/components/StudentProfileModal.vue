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
                到期日：{{ formatDate(student.membership_expiry || student.expiry_date) }}
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
                <label class="text-muted small">會員到期日</label>
                <div class="fw-bold text-primary">{{ formatDate(student.membership_expiry || student.expiry_date) || '無效期限制' }}</div>
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

export default {
  name: 'StudentProfileModal',
  data() {
    return {
      auth: useStudentAuth(),
      activeTab: 'bookings', // 'bookings' | 'info' | 'password'
      refreshing: false,
      loadingEnrollments: false,
      enrollments: [],
      // Password change form
      oldPassword: '',
      newPassword: '',
      confirmPassword: '',
      pwdLoading: false,
      pwdError: '',
      pwdSuccess: ''
    }
  },
  computed: {
    student() {
      return this.auth.state.student
    },
    studentInitials() {
      if (!this.student || !this.student.name) return '學'
      return this.student.name.charAt(0)
    }
  },
  watch: {
    'auth.state.showProfileModal'(isOpen) {
      if (isOpen && this.student) {
        this.activeTab = 'bookings'
        this.fetchEnrollments()
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

