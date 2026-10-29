<template>
  <div class="line-callback-page container py-5">
    <div class="row justify-content-center">
      <div class="col-md-7 col-lg-5">
        <div class="card shadow-lg border-0 rounded-4 overflow-hidden">
          <!-- Card Header with LINE Brand Color -->
          <div class="line-header text-white p-4 text-center">
            <div class="line-icon-badge mb-2 mx-auto">
              <svg viewBox="0 0 24 24" width="38" height="38" fill="currentColor">
                <path d="M12 2C6.48 2 2 5.92 2 10.76c0 3.08 1.83 5.79 4.67 7.31-.2.72-.73 2.61-.84 3.01-.13.49.18.48.38.35.16-.11 2.22-1.51 3.12-2.13.88.24 1.78.37 2.67.37 5.52 0 10-3.92 10-8.91S17.52 2 12 2zm5.72 11.59h-2.17c-.24 0-.43-.19-.43-.43V8.84c0-.24.19-.43.43-.43h2.17c.24 0 .43.19.43.43v.68c0 .24-.19.43-.43.43h-1.31v.96h1.31c.24 0 .43.19.43.43v.68c0 .24-.19.43-.43.43h-1.31v.97h1.31c.24 0 .43.19.43.43v.68c0 .23-.19.42-.43.42zm-3.52-.43c0 .24-.19.43-.43.43h-.68c-.24 0-.43-.19-.43-.43V8.84c0-.24.19-.43.43-.43h.68c.24 0 .43.19.43.43v4.32zm-2.22 0c0 .18-.11.34-.27.4-.05.02-.11.03-.16.03-.12 0-.23-.05-.31-.13l-1.92-2.61v2.31c0 .24-.19.43-.43.43h-.68c-.24 0-.43-.19-.43-.43V8.84c0-.18.11-.34.27-.4.16-.06.35-.03.47.1l1.92 2.61V8.84c0-.24.19-.43.43-.43h.68c.24 0 .43.19.43.43v4.32zm-4.71 0c0 .24-.19.43-.43.43H4.7c-.24 0-.43-.19-.43-.43V8.84c0-.24.19-.43.43-.43h.68c.24 0 .43.19.43.43v3.46h1.01c.24 0 .43.19.43.43v.43z"/>
              </svg>
            </div>
            <h4 class="fw-bold mb-1">LINE 帳號驗證</h4>
            <p class="small text-white-50 mb-0">Dance Studio 舞蹈工作室</p>
          </div>

          <div class="card-body p-4 text-center">
            <!-- 狀態 1：處理驗證中 -->
            <div v-if="loading" class="py-4">
              <div class="spinner-border text-success mb-3" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <h5 class="fw-bold text-dark">正在與 LINE 伺服器同步資訊...</h5>
              <p class="text-muted small">請稍候，系統正在為您安全驗證會員身份。</p>
            </div>

            <!-- 狀態 2：驗證成功 -->
            <div v-else-if="successMessage" class="py-4">
              <div class="text-success mb-3">
                <i class="bi bi-check-circle-fill display-3"></i>
              </div>
              <h5 class="fw-bold text-dark mb-2">{{ successMessage }}</h5>
              <p class="text-muted small">系統將在幾秒後自動轉導，請稍候...</p>
              <button class="btn btn-primary btn-sm rounded-pill px-4 mt-2" @click="goToTarget">
                立即前往首頁
              </button>
            </div>

            <!-- 狀態 3：需要關聯會員帳號 (未曾綁定之 LINE) -->
            <div v-else-if="needLink" class="text-start">
              <div class="alert alert-info py-2 px-3 small d-flex align-items-center mb-3">
                <i class="bi bi-info-circle-fill fs-5 me-2 flex-shrink-0 text-info"></i>
                <div>
                  您好，LINE 用戶<strong>「{{ lineDisplayName }}」</strong>！此 LINE 帳號尚未關聯任何 Dance Studio 學員帳號。
                </div>
              </div>

              <!-- LINE 個人資訊預覽卡 -->
              <div class="d-flex align-items-center bg-light p-3 rounded-3 mb-3 border">
                <img
                  v-if="linePictureUrl"
                  :src="linePictureUrl"
                  alt="LINE Avatar"
                  class="rounded-circle me-3 border"
                  width="48"
                  height="48"
                  style="object-fit: cover;"
                />
                <div v-else class="rounded-circle bg-success text-white d-flex align-items-center justify-content-center me-3" style="width: 48px; height: 48px;">
                  <i class="bi bi-line fs-4"></i>
                </div>
                <div>
                  <div class="fw-bold text-dark">{{ lineDisplayName }}</div>
                  <div class="small text-muted font-monospace">LINE ID: {{ formatLineId(lineUserId) }}</div>
                </div>
              </div>

              <!-- 頁籤選擇：關聯既有手機帳號 / 註冊新會員 -->
              <ul class="nav nav-pills nav-fill mb-3 bg-light p-1 rounded-pill border">
                <li class="nav-item">
                  <button
                    class="nav-link btn-sm rounded-pill fw-bold"
                    :class="{ active: linkTab === 'existing' }"
                    @click="linkTab = 'existing'"
                  >
                    <i class="bi bi-link-45deg me-1"></i>關聯既有會員
                  </button>
                </li>
                <li class="nav-item">
                  <button
                    class="nav-link btn-sm rounded-pill fw-bold"
                    :class="{ active: linkTab === 'new' }"
                    @click="linkTab = 'new'"
                  >
                    <i class="bi bi-person-plus-fill me-1"></i>註冊新會員並綁定
                  </button>
                </li>
              </ul>

              <!-- 錯誤訊息提示 -->
              <div v-if="formError" class="alert alert-danger py-2 px-3 small mb-3">
                <i class="bi bi-exclamation-triangle-fill me-1"></i>{{ formError }}
              </div>

              <!-- 模式 A：關聯既有手機會員 -->
              <form v-if="linkTab === 'existing'" @submit.prevent="handleLinkExisting">
                <div class="mb-3">
                  <label class="form-label small fw-bold mb-1">手機號碼 <span class="text-danger">*</span></label>
                  <input
                    type="tel"
                    v-model.trim="formPhone"
                    class="form-control form-control-sm"
                    placeholder="請輸入註冊時的手機號碼 (例如 0912345678)"
                    required
                    :disabled="submitting"
                  />
                </div>
                <div class="mb-3">
                  <div class="d-flex justify-content-between align-items-center mb-1">
                    <label class="form-label small fw-bold mb-0">會員密碼 <span class="text-danger">*</span></label>
                    <small class="text-muted">首次登入請設定新密碼</small>
                  </div>
                  <input
                    type="password"
                    v-model="formPassword"
                    class="form-control form-control-sm"
                    placeholder="請輸入密碼 (至少 4 位)"
                    required
                    :disabled="submitting"
                  />
                </div>
                <button type="submit" class="btn btn-success w-100 fw-bold shadow-sm" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi bi-check2-circle me-1"></i>完成關聯並登入
                </button>
              </form>

              <!-- 模式 B：註冊新會員並綁定 -->
              <form v-else @submit.prevent="handleRegisterNew">
                <div class="mb-2">
                  <label class="form-label small fw-bold mb-1">姓名 <span class="text-danger">*</span></label>
                  <input
                    type="text"
                    v-model.trim="formName"
                    class="form-control form-control-sm"
                    placeholder="您的真實姓名"
                    required
                    :disabled="submitting"
                  />
                </div>
                <div class="mb-2">
                  <label class="form-label small fw-bold mb-1">手機電話 <span class="text-danger">*</span></label>
                  <input
                    type="tel"
                    v-model.trim="formPhone"
                    class="form-control form-control-sm"
                    placeholder="例如 0912345678"
                    required
                    :disabled="submitting"
                  />
                </div>
                <div class="mb-2">
                  <label class="form-label small fw-bold mb-1">設定登入密碼 <span class="text-danger">*</span></label>
                  <input
                    type="password"
                    v-model="formPassword"
                    class="form-control form-control-sm"
                    placeholder="至少 4 個字元"
                    required
                    :disabled="submitting"
                  />
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold mb-1">電子信箱 (選填)</label>
                  <input
                    type="email"
                    v-model.trim="formEmail"
                    class="form-control form-control-sm"
                    placeholder="example@mail.com"
                    :disabled="submitting"
                  />
                </div>
                <button type="submit" class="btn btn-success w-100 fw-bold shadow-sm" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi bi-person-check-fill me-1"></i>建立新會員並綁定 LINE
                </button>
              </form>
            </div>

            <!-- 狀態 4：錯誤提示 -->
            <div v-else-if="errorMessage" class="py-3">
              <div class="text-danger mb-3">
                <i class="bi bi-x-circle-fill display-3"></i>
              </div>
              <h5 class="fw-bold text-dark mb-2">LINE 驗證失敗</h5>
              <div class="alert alert-danger py-2 px-3 small text-start mb-3">
                {{ errorMessage }}
              </div>
              <div class="d-flex justify-content-center gap-2">
                <button class="btn btn-outline-secondary btn-sm rounded-pill px-3" @click="goToLogin">
                  返回學員登入
                </button>
                <button class="btn btn-primary btn-sm rounded-pill px-3" @click="retryAuth">
                  重新嘗試
                </button>
              </div>
            </div>
          </div>
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
  name: 'LineCallback',
  data() {
    return {
      auth: useStudentAuth(),
      loading: true,
      errorMessage: null,
      successMessage: null,
      needLink: false,
      lineUserId: '',
      lineDisplayName: '',
      linePictureUrl: '',
      linkTab: 'existing',
      formPhone: '',
      formPassword: '',
      formName: '',
      formEmail: '',
      formError: '',
      submitting: false
    }
  },
  mounted() {
    this.processCallback()
  },
  methods: {
    formatLineId(id) {
      if (!id) return ''
      if (id.length <= 10) return id
      return id.substring(0, 6) + '...' + id.substring(id.length - 4)
    },
    async processCallback() {
      const code = this.$route.query.code
      const state = this.$route.query.state || ''
      const error = this.$route.query.error
      const errorDescription = this.$route.query.error_description

      if (error) {
        this.loading = false
        this.errorMessage = errorDescription || error || '您已取消 LINE 登入授權。'
        return
      }

      if (!code) {
        this.loading = false
        this.errorMessage = '未收到 LINE 授權代碼 (code)，請重新嘗試。'
        return
      }

      const redirectUri = window.location.origin + '/line-callback'
      const studentId = this.auth.isLoggedIn ? this.auth.currentStudent.id : null

      try {
        const res = await api.post('/line/callback', {
          code,
          redirect_uri: redirectUri,
          state,
          student_id: studentId
        })

        this.loading = false

        if (res.action === 'bound') {
          // 綁定成功
          this.successMessage = res.message || 'LINE 帳號關聯成功！'
          this.auth.setStudent(res.student)
          showToast(this.successMessage, 'success')
          setTimeout(() => {
            this.goToProfile()
          }, 1500)
        } else if (res.action === 'login') {
          // 登入成功
          this.successMessage = res.message || 'LINE 快速登入成功！'
          this.auth.setStudent(res.student)
          showToast(this.successMessage, 'success')
          setTimeout(() => {
            this.goToTarget()
          }, 1200)
        } else if (res.action === 'need_link') {
          // 需要關聯
          this.needLink = true
          this.lineUserId = res.line_user_id
          this.lineDisplayName = res.line_display_name || 'LINE 會員'
          this.linePictureUrl = res.line_picture_url || ''
          this.formName = this.lineDisplayName
        } else {
          this.errorMessage = res.message || '處理失敗，請重試'
        }
      } catch (err) {
        this.loading = false
        this.errorMessage = err.message || '連線至伺服器處理 LINE 驗證失敗'
      }
    },
    async handleLinkExisting() {
      this.formError = ''
      if (!this.formPhone) {
        this.formError = '請輸入手機電話號碼'
        return
      }
      if (!this.formPassword) {
        this.formError = '請輸入會員密碼'
        return
      }

      this.submitting = true
      try {
        const res = await api.post('/student/line/link-with-phone', {
          mode: 'link',
          phone: this.formPhone,
          password: this.formPassword,
          line_user_id: this.lineUserId,
          line_display_name: this.lineDisplayName,
          line_picture_url: this.linePictureUrl
        })

        if (res.success && res.student) {
          this.auth.setStudent(res.student)
          showToast(res.message || '關聯成功！歡迎回來。', 'success')
          this.goToTarget()
        } else {
          this.formError = res.error || res.message || '關聯失敗'
        }
      } catch (err) {
        this.formError = err.message || '關聯處理失敗，請確認手機與密碼'
      } finally {
        this.submitting = false
      }
    },
    async handleRegisterNew() {
      this.formError = ''
      if (!this.formName) {
        this.formError = '請輸入姓名'
        return
      }
      if (!this.formPhone) {
        this.formError = '請輸入手機電話號碼'
        return
      }
      if (!this.formPassword || this.formPassword.length < 4) {
        this.formError = '密碼長度至少需 4 個字元'
        return
      }

      this.submitting = true
      try {
        const res = await api.post('/student/line/link-with-phone', {
          mode: 'register',
          name: this.formName,
          phone: this.formPhone,
          password: this.formPassword,
          email: this.formEmail || null,
          line_user_id: this.lineUserId,
          line_display_name: this.lineDisplayName,
          line_picture_url: this.linePictureUrl
        })

        if (res.success && res.student) {
          this.auth.setStudent(res.student)
          showToast(res.message || '註冊成功並已綁定 LINE！', 'success')
          this.goToTarget()
        } else {
          this.formError = res.error || res.message || '註冊失敗'
        }
      } catch (err) {
        this.formError = err.message || '註冊失敗，該電話號碼可能已註冊'
      } finally {
        this.submitting = false
      }
    },
    goToTarget() {
      this.$router.push('/')
    },
    goToProfile() {
      this.$router.push('/').then(() => {
        this.auth.openProfileModal()
      })
    },
    goToLogin() {
      this.$router.push('/').then(() => {
        this.auth.openLoginModal()
      })
    },
    retryAuth() {
      window.location.reload()
    }
  }
}
</script>

<style scoped>
.line-callback-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
}
.line-header {
  background: linear-gradient(135deg, #06C755 0%, #05a847 100%);
}
.line-icon-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  backdrop-filter: blur(4px);
}
.nav-pills .nav-link.active {
  background-color: #06C755;
  color: #fff;
}
</style>

