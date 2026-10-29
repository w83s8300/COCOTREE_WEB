<template>
  <div v-if="auth.state.showLoginModal" class="modal-backdrop-custom" @click.self="close">
    <div class="modal-dialog-custom">
      <div class="modal-content-custom shadow-lg">
        <!-- Header -->
        <div class="modal-header-custom pb-2">
          <div class="d-flex align-items-center">
            <div class="icon-circle me-3" :class="{ 'bg-register': currentTab === 'register' }">
              <i :class="currentTab === 'register' ? 'bi bi-person-plus-fill' : 'bi bi-person-fill'"></i>
            </div>
            <div>
              <h5 class="modal-title mb-0 fw-bold">{{ currentTab === 'register' ? '會員註冊' : '學員登入' }}</h5>
              <small class="text-muted">Dance Studio 會員專區</small>
            </div>
          </div>
          <button type="button" class="btn-close-custom" @click="close" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <!-- 頁籤切換 (登入 / 註冊) -->
        <div class="px-4 pt-3 pb-1 border-bottom bg-light d-flex gap-2">
          <button
            type="button"
            class="tab-btn flex-fill py-2 btn btn-sm rounded-pill"
            :class="currentTab === 'login' ? 'btn-primary fw-bold shadow-sm' : 'btn-outline-secondary bg-white'"
            @click="switchTab('login')"
          >
            <i class="bi bi-box-arrow-in-right me-1"></i>學員登入
          </button>
          <button
            type="button"
            class="tab-btn flex-fill py-2 btn btn-sm rounded-pill"
            :class="currentTab === 'register' ? 'btn-success fw-bold shadow-sm' : 'btn-outline-secondary bg-white'"
            @click="switchTab('register')"
          >
            <i class="bi bi-person-plus-fill me-1"></i>會員註冊
          </button>
        </div>

        <!-- Body -->
        <div class="modal-body-custom">
          <!-- 錯誤訊息提示 -->
          <div v-if="errorMessage" class="alert alert-danger py-2 px-3 small mb-3 d-flex align-items-center">
            <i class="bi bi-exclamation-circle-fill me-2 flex-shrink-0"></i>
            <div>{{ errorMessage }}</div>
          </div>

          <!-- ============================== -->
          <!-- 模式一：學員登入                -->
          <!-- ============================== -->
          <div v-if="currentTab === 'login'">
            <!-- 一般登入表單（手機 + 密碼，一次輸入） -->
            <form v-if="step === 'login'" @submit.prevent="handleLogin">
              <!-- 手機號碼 -->
              <div class="mb-3">
                <label class="form-label fw-bold small mb-1">手機電話號碼 <span class="text-danger">*</span></label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-telephone-fill"></i></span>
                  <input
                    ref="phoneInput"
                    v-model.trim="phone"
                    type="tel"
                    class="form-control"
                    placeholder="例如：0912345678"
                    required
                    :disabled="loading"
                    autofocus
                  />
                </div>
              </div>

              <!-- 登入密碼 -->
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <label class="form-label fw-bold small mb-0">登入密碼 <span class="text-danger">*</span></label>
                  <button type="button" class="btn btn-link btn-sm p-0 text-decoration-none text-muted small" @click="goToFirstLoginCheck">
                    <i class="bi bi-key me-1"></i>首次登入未設密碼？
                  </button>
                </div>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
                  <input
                    ref="passwordInput"
                    v-model="password"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    placeholder="請輸入登入密碼"
                    required
                    :disabled="loading"
                  />
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="showPassword = !showPassword"
                    tabindex="-1"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
              </div>

              <div class="d-grid mt-4">
                <button type="submit" class="btn btn-primary py-2 fw-bold" :disabled="loading || !phone || !password">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  {{ loading ? '登入中...' : '學員登入' }}
                </button>
              </div>

              <!-- LINE 快速登入分隔線 -->
              <div class="d-flex align-items-center my-3">
                <hr class="flex-grow-1 my-0 text-muted" />
                <span class="px-2 text-muted small fw-bold">或使用第三方帳號</span>
                <hr class="flex-grow-1 my-0 text-muted" />
              </div>

              <!-- LINE 快速登入按鈕 -->
              <div class="d-grid mb-2">
                <button
                  type="button"
                  class="btn btn-line-login py-2 fw-bold d-flex align-items-center justify-content-center gap-2 shadow-sm"
                  :disabled="lineLoggingIn"
                  @click="handleLineQuickLogin"
                >
                  <span v-if="lineLoggingIn" class="spinner-border spinner-border-sm"></span>
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                    <path d="M12 2C6.48 2 2 5.92 2 10.76c0 3.08 1.83 5.79 4.67 7.31-.2.72-.73 2.61-.84 3.01-.13.49.18.48.38.35.16-.11 2.22-1.51 3.12-2.13.88.24 1.78.37 2.67.37 5.52 0 10-3.92 10-8.91S17.52 2 12 2zm5.72 11.59h-2.17c-.24 0-.43-.19-.43-.43V8.84c0-.24.19-.43.43-.43h2.17c.24 0 .43.19.43.43v.68c0 .24-.19.43-.43.43h-1.31v.96h1.31c.24 0 .43.19.43.43v.68c0 .24-.19.43-.43.43h-1.31v.97h1.31c.24 0 .43.19.43.43v.68c0 .23-.19.42-.43.42zm-3.52-.43c0 .24-.19.43-.43.43h-.68c-.24 0-.43-.19-.43-.43V8.84c0-.24.19-.43.43-.43h.68c.24 0 .43.19.43.43v4.32zm-2.22 0c0 .18-.11.34-.27.4-.05.02-.11.03-.16.03-.12 0-.23-.05-.31-.13l-1.92-2.61v2.31c0 .24-.19.43-.43.43h-.68c-.24 0-.43-.19-.43-.43V8.84c0-.18.11-.34.27-.4.16-.06.35-.03.47.1l1.92 2.61V8.84c0-.24.19-.43.43-.43h.68c.24 0 .43.19.43.43v4.32zm-4.71 0c0 .24-.19.43-.43.43H4.7c-.24 0-.43-.19-.43-.43V8.84c0-.24.19-.43.43-.43h.68c.24 0 .43.19.43.43v3.46h1.01c.24 0 .43.19.43.43v.43z"/>
                  </svg>
                  <span>使用 LINE 快速登入</span>
                </button>
              </div>

              <!-- 提示前往註冊 -->
              <div class="text-center mt-3 pt-2 border-top">
                <span class="text-muted small">還不是會員？</span>
                <button type="button" class="btn btn-link btn-sm p-0 ms-1 fw-bold text-success text-decoration-none" @click="goToRegisterWithPhone">
                  點此立即註冊新會員
                </button>
              </div>
            </form>

            <!-- 首次登入設定密碼表單 -->
            <form v-else-if="step === 'first_login'" @submit.prevent="handleFirstLogin">
              <div class="alert alert-success py-2 px-3 small mb-3">
                <i class="bi bi-stars me-1 text-warning"></i>
                <strong>歡迎首次登入，{{ studentName }}！</strong>
                <div class="mt-1">您為現場建立的會員，請直接設定您的登入密碼。</div>
              </div>

              <div class="mb-2 text-muted small">
                <strong>登入手機：</strong>{{ phone }}
                <a href="javascript:void(0)" class="ms-2 text-decoration-none" @click="backToLogin">更換</a>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">設定新密碼 <span class="text-danger">*</span></label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-lock-fill"></i></span>
                  <input
                    v-model="newPassword"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    placeholder="請輸入至少4碼新密碼"
                    required
                    minlength="4"
                    :disabled="loading"
                    autofocus
                  />
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="showPassword = !showPassword"
                    tabindex="-1"
                  >
                    <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  </button>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">再次確認密碼 <span class="text-danger">*</span></label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-shield-lock-fill"></i></span>
                  <input
                    v-model="confirmPassword"
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    placeholder="再次輸入相同密碼"
                    required
                    minlength="4"
                    :disabled="loading"
                  />
                </div>
              </div>

              <div class="d-grid gap-2 mt-4">
                <button type="submit" class="btn btn-success py-2 fw-bold" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  {{ loading ? '設定中...' : '設定密碼並登入' }}
                </button>
                <button type="button" class="btn btn-link text-muted btn-sm" @click="backToLogin" :disabled="loading">
                  返回帳號密碼登入
                </button>
              </div>
            </form>

            <!-- 首次登入檢查手機表單 -->
            <form v-else-if="step === 'first_login_phone'" @submit.prevent="handleCheckFirstLoginPhone">
              <div class="alert alert-info py-2 px-3 small mb-3">
                <i class="bi bi-info-circle me-1"></i>
                請輸入您在教室櫃檯留存的手機號碼，系統將引導您直接開通並設定密碼。
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">手機電話號碼 <span class="text-danger">*</span></label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-telephone-fill"></i></span>
                  <input
                    v-model.trim="phone"
                    type="tel"
                    class="form-control"
                    placeholder="例如：0912345678"
                    required
                    :disabled="loading"
                    autofocus
                  />
                </div>
              </div>

              <div class="d-grid gap-2 mt-4">
                <button type="submit" class="btn btn-primary py-2 fw-bold" :disabled="loading || !phone">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  {{ loading ? '查詢中...' : '下一步設定密碼' }}
                </button>
                <button type="button" class="btn btn-link text-muted btn-sm" @click="backToLogin" :disabled="loading">
                  返回帳號密碼登入
                </button>
              </div>
            </form>
          </div>

          <!-- ============================== -->
          <!-- 模式二：會員註冊                -->
          <!-- ============================== -->
          <div v-else-if="currentTab === 'register'">
            <form @submit.prevent="handleRegister">
              <div class="row g-2">
                <!-- 姓名 -->
                <div class="col-12 mb-2">
                  <label class="form-label fw-bold small mb-1">學員真實姓名 <span class="text-danger">*</span></label>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text"><i class="bi bi-person-badge"></i></span>
                    <input
                      ref="regNameInput"
                      v-model.trim="regForm.name"
                      type="text"
                      class="form-control"
                      placeholder="請輸入您的中文或英文姓名"
                      required
                      :disabled="loading"
                      autofocus
                    />
                  </div>
                </div>

                <!-- 手機號碼 -->
                <div class="col-12 mb-2">
                  <label class="form-label fw-bold small mb-1">手機號碼 (登入帳號) <span class="text-danger">*</span></label>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text"><i class="bi bi-telephone"></i></span>
                    <input
                      v-model.trim="regForm.phone"
                      type="tel"
                      class="form-control"
                      placeholder="例如：0912345678"
                      required
                      :disabled="loading"
                    />
                  </div>
                  <div class="form-text small text-muted" style="font-size: 0.75rem;">
                    手機號碼將作為您日後登入與預約的重要依據。
                  </div>
                </div>

                <!-- 設定密碼 -->
                <div class="col-6 mb-2">
                  <label class="form-label fw-bold small mb-1">設定登入密碼 <span class="text-danger">*</span></label>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input
                      v-model="regForm.password"
                      :type="showRegPassword ? 'text' : 'password'"
                      class="form-control"
                      placeholder="至少4碼"
                      required
                      minlength="4"
                      :disabled="loading"
                    />
                    <button
                      type="button"
                      class="btn btn-outline-secondary px-2"
                      @click="showRegPassword = !showRegPassword"
                      tabindex="-1"
                    >
                      <i :class="showRegPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                  </div>
                </div>

                <!-- 確認密碼 -->
                <div class="col-6 mb-2">
                  <label class="form-label fw-bold small mb-1">再次確認密碼 <span class="text-danger">*</span></label>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text"><i class="bi bi-shield-lock"></i></span>
                    <input
                      v-model="regForm.confirmPassword"
                      :type="showRegPassword ? 'text' : 'password'"
                      class="form-control"
                      placeholder="再次輸入"
                      required
                      minlength="4"
                      :disabled="loading"
                    />
                  </div>
                </div>

                <!-- 電子信箱 -->
                <div class="col-12 mb-2">
                  <label class="form-label fw-bold small mb-1">電子信箱 (選填)</label>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                    <input
                      v-model.trim="regForm.email"
                      type="email"
                      class="form-control"
                      placeholder="例如：user@example.com"
                      :disabled="loading"
                    />
                  </div>
                </div>

                <!-- 出生年月日 -->
                <div class="col-12 mb-2">
                  <label class="form-label fw-bold small mb-1">出生年月日 (選填)</label>
                  <div class="input-group input-group-sm">
                    <span class="input-group-text"><i class="bi bi-calendar3"></i></span>
                    <input
                      v-model="regForm.date_of_birth"
                      type="date"
                      class="form-control"
                      :disabled="loading"
                    />
                  </div>
                </div>

                <!-- 展開更多選填 (緊急聯絡人) -->
                <div class="col-12 mt-1">
                  <a
                    href="javascript:void(0)"
                    class="small text-decoration-none text-secondary d-inline-flex align-items-center"
                    @click="showMoreFields = !showMoreFields"
                  >
                    <i :class="showMoreFields ? 'bi bi-chevron-up' : 'bi bi-chevron-down'" class="me-1"></i>
                    {{ showMoreFields ? '收合緊急聯絡人資訊' : '填寫緊急聯絡人 (選填)' }}
                  </a>
                </div>

                <template v-if="showMoreFields">
                  <div class="col-6 mb-2">
                    <label class="form-label small mb-1">緊急聯絡人</label>
                    <input
                      v-model.trim="regForm.emergency_contact"
                      type="text"
                      class="form-control form-control-sm"
                      placeholder="姓名或稱謂"
                      :disabled="loading"
                    />
                  </div>
                  <div class="col-6 mb-2">
                    <label class="form-label small mb-1">緊急電話</label>
                    <input
                      v-model.trim="regForm.emergency_phone"
                      type="tel"
                      class="form-control form-control-sm"
                      placeholder="聯絡人電話"
                      :disabled="loading"
                    />
                  </div>
                </template>
              </div>

              <!-- 提交註冊按鈕 -->
              <div class="d-grid mt-4">
                <button type="submit" class="btn btn-success py-2 fw-bold" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  {{ loading ? '註冊中...' : '立即註冊會員並登入' }}
                </button>
              </div>

              <div class="text-center mt-3 pt-2 border-top">
                <span class="text-muted small">已經是會員？</span>
                <button type="button" class="btn btn-link btn-sm p-0 ms-1 fw-bold text-primary text-decoration-none" @click="switchTab('login')">
                  返回學員登入
                </button>
              </div>
            </form>
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
  name: 'StudentLoginModal',
  data() {
    return {
      auth: useStudentAuth(),
      currentTab: 'login', // 'login' | 'register'
      step: 'login', // 'login' | 'first_login' | 'first_login_phone'
      phone: '',
      studentName: '',
      password: '',
      newPassword: '',
      confirmPassword: '',
      showPassword: false,
      loading: false,
      errorMessage: '',

      // 註冊表單資料
      regForm: {
        name: '',
        phone: '',
        password: '',
        confirmPassword: '',
        email: '',
        date_of_birth: '',
        emergency_contact: '',
        emergency_phone: ''
      },
      showRegPassword: false,
      showMoreFields: false,
      lineLoggingIn: false
    }
  },
  watch: {
    'auth.state.showLoginModal'(isOpen) {
      if (isOpen) {
        this.currentTab = this.auth.state.authTab || 'login'
        this.resetForm()
        this.$nextTick(() => {
          if (this.currentTab === 'login' && this.$refs.phoneInput) {
            this.$refs.phoneInput.focus()
          } else if (this.currentTab === 'register' && this.$refs.regNameInput) {
            this.$refs.regNameInput.focus()
          }
        })
      }
    },
    'auth.state.authTab'(newTab) {
      if (newTab) {
        this.currentTab = newTab
      }
    }
  },
  methods: {
    switchTab(tab) {
      this.currentTab = tab
      this.errorMessage = ''
      this.step = 'login'
      this.$nextTick(() => {
        if (tab === 'login' && this.$refs.phoneInput) {
          this.$refs.phoneInput.focus()
        } else if (tab === 'register' && this.$refs.regNameInput) {
          this.$refs.regNameInput.focus()
        }
      })
    },
    goToRegisterWithPhone() {
      const curPhone = this.phone.trim()
      this.switchTab('register')
      if (curPhone) {
        this.regForm.phone = curPhone
      }
    },
    goToFirstLoginCheck() {
      this.step = 'first_login_phone'
      this.errorMessage = ''
    },
    resetForm() {
      this.step = 'login'
      this.phone = ''
      this.studentName = ''
      this.password = ''
      this.newPassword = ''
      this.confirmPassword = ''
      this.showPassword = false
      this.loading = false
      this.errorMessage = ''

      this.regForm = {
        name: '',
        phone: '',
        password: '',
        confirmPassword: '',
        email: '',
        date_of_birth: '',
        emergency_contact: '',
        emergency_phone: ''
      }
      this.showRegPassword = false
      this.showMoreFields = false
    },
    close() {
      this.auth.closeLoginModal()
      this.resetForm()
    },
    backToLogin() {
      this.step = 'login'
      this.newPassword = ''
      this.confirmPassword = ''
      this.errorMessage = ''
      this.$nextTick(() => {
        if (this.$refs.passwordInput) {
          this.$refs.passwordInput.focus()
        } else if (this.$refs.phoneInput) {
          this.$refs.phoneInput.focus()
        }
      })
    },
    async handleLogin() {
      const cleanPhone = this.phone.trim()
      if (!cleanPhone) {
        this.errorMessage = '請輸入手機號碼'
        return
      }
      if (!this.password) {
        this.errorMessage = '請輸入登入密碼'
        return
      }

      this.loading = true
      this.errorMessage = ''

      try {
        const res = await api.post('/student/login', {
          phone: cleanPhone,
          password: this.password
        })

        if (res.success && res.student) {
          this.auth.setStudent(res.student)
          showToast(`歡迎回來，${res.student.name}！`, 'success')
          this.close()
        } else if (res.require_set_password) {
          // 首次登入流程（尚未設定密碼）
          this.studentName = res.name || ''
          this.step = 'first_login'
          this.newPassword = ''
          this.confirmPassword = ''
        } else {
          this.errorMessage = res.message || '登入失敗，請檢查手機號碼或密碼'
        }
      } catch (err) {
        this.errorMessage = err.message || '登入失敗，請檢查手機號碼與密碼是否正確'
      } finally {
        this.loading = false
      }
    },
    async handleLineQuickLogin() {
      this.lineLoggingIn = true
      try {
        const redirectUri = window.location.origin + '/line-callback'
        const state = `login:${Date.now()}`
        const res = await api.get(`/line/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}&state=${encodeURIComponent(state)}`)

        if (res.success && res.configured && res.auth_url) {
          window.location.href = res.auth_url
        } else {
          showToast(res.message || '尚未設定 LINE Login Channel ID，請至管理後台設定！', 'warning')
        }
      } catch (err) {
        showToast(err.message || '啟動 LINE 登入失敗', 'error')
      } finally {
        this.lineLoggingIn = false
      }
    },
    async handleCheckFirstLoginPhone() {
      const cleanPhone = this.phone.trim()
      if (!cleanPhone) {
        this.errorMessage = '請輸入手機電話號碼'
        return
      }

      this.loading = true
      this.errorMessage = ''

      try {
        const res = await api.post('/student/check-phone', { phone: cleanPhone })
        if (!res.exists) {
          this.errorMessage = '查無此電話對應的學員資料。若您尚未註冊，請點選上方「會員註冊」。'
          return
        }

        this.studentName = res.name || ''
        if (res.is_first_login) {
          this.step = 'first_login'
        } else {
          showToast('您已經設定過密碼，請直接輸入密碼登入！', 'info')
          this.step = 'login'
          this.$nextTick(() => {
            if (this.$refs.passwordInput) {
              this.$refs.passwordInput.focus()
            }
          })
        }
      } catch (err) {
        this.errorMessage = err.message || '查詢失敗，請稍後再試'
      } finally {
        this.loading = false
      }
    },
    async handleLineQuickLogin() {
      this.lineLoggingIn = true
      try {
        const redirectUri = window.location.origin + '/line-callback'
        const state = `login:${Date.now()}`
        const res = await api.get(`/line/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}&state=${encodeURIComponent(state)}`)

        if (res.success && res.configured && res.auth_url) {
          window.location.href = res.auth_url
        } else {
          showToast(res.message || '尚未設定 LINE Login Channel ID，請至管理後台設定！', 'warning')
        }
      } catch (err) {
        showToast(err.message || '啟動 LINE 登入失敗', 'error')
      } finally {
        this.lineLoggingIn = false
      }
    },
    async handleFirstLogin() {
      if (!this.newPassword || this.newPassword.length < 4) {
        this.errorMessage = '密碼長度至少需要 4 碼'
        return
      }
      if (this.newPassword !== this.confirmPassword) {
        this.errorMessage = '兩次輸入的密碼不一致，請重新確認'
        return
      }

      this.loading = true
      this.errorMessage = ''

      try {
        const res = await api.post('/student/login', {
          phone: this.phone.trim(),
          new_password: this.newPassword
        })

        if (res.success && res.student) {
          this.auth.setStudent(res.student)
          showToast(`密碼設定成功！歡迎您，${res.student.name}`, 'success')
          this.close()
        } else {
          this.errorMessage = res.message || '設定失敗，請重試'
        }
      } catch (err) {
        this.errorMessage = err.message || '設定密碼失敗，請稍後再試'
      } finally {
        this.loading = false
      }
    },
    async handleLineQuickLogin() {
      this.lineLoggingIn = true
      try {
        const redirectUri = window.location.origin + '/line-callback'
        const state = `login:${Date.now()}`
        const res = await api.get(`/line/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}&state=${encodeURIComponent(state)}`)

        if (res.success && res.configured && res.auth_url) {
          window.location.href = res.auth_url
        } else {
          showToast(res.message || '尚未設定 LINE Login Channel ID，請至管理後台設定！', 'warning')
        }
      } catch (err) {
        showToast(err.message || '啟動 LINE 登入失敗', 'error')
      } finally {
        this.lineLoggingIn = false
      }
    },
    async handleRegister() {
      if (!this.regForm.name.trim()) {
        this.errorMessage = '請填寫真實姓名'
        return
      }
      if (!this.regForm.phone.trim()) {
        this.errorMessage = '請填寫手機電話號碼'
        return
      }
      if (!this.regForm.password || this.regForm.password.length < 4) {
        this.errorMessage = '密碼長度至少需要 4 碼'
        return
      }
      if (this.regForm.password !== this.regForm.confirmPassword) {
        this.errorMessage = '兩次輸入的密碼不一致，請重新確認'
        return
      }

      this.loading = true
      this.errorMessage = ''

      try {
        const payload = {
          name: this.regForm.name.trim(),
          phone: this.regForm.phone.trim(),
          password: this.regForm.password,
          email: this.regForm.email.trim() || null,
          date_of_birth: this.regForm.date_of_birth || null,
          emergency_contact: this.regForm.emergency_contact.trim() || null,
          emergency_phone: this.regForm.emergency_phone.trim() || null
        }

        const res = await api.post('/student/register', payload)

        if (res.success && res.student) {
          this.auth.setStudent(res.student)
          showToast(res.message || `註冊成功！歡迎加入，${res.student.name}`, 'success')
          this.close()
        } else {
          this.errorMessage = res.error || res.message || '註冊失敗，請重試'
        }
      } catch (err) {
        this.errorMessage = err.message || '註冊失敗，請稍後再試'
      } finally {
        this.loading = false
      }
    },
    async handleLineQuickLogin() {
      this.lineLoggingIn = true
      try {
        const redirectUri = window.location.origin + '/line-callback'
        const state = `login:${Date.now()}`
        const res = await api.get(`/line/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}&state=${encodeURIComponent(state)}`)

        if (res.success && res.configured && res.auth_url) {
          window.location.href = res.auth_url
        } else {
          showToast(res.message || '尚未設定 LINE Login Channel ID，請至管理後台設定！', 'warning')
        }
      } catch (err) {
        showToast(err.message || '啟動 LINE 登入失敗', 'error')
      } finally {
        this.lineLoggingIn = false
      }
    }
  }
}
</script>

<style scoped>
.btn-line-login {
  background-color: #06C755;
  color: #fff;
  border: none;
  transition: all 0.2s ease;
}
.btn-line-login:hover {
  background-color: #05a847;
  color: #fff;
}

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
  max-width: 460px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: slideDown 0.25s ease-out;
}

.modal-content-custom {
  background: #ffffff;
  border-radius: 1rem;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-header-custom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem 0.75rem 1.5rem;
}

.icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0d6efd, #0b5ed7);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: 0 4px 10px rgba(13, 110, 253, 0.3);
  transition: all 0.3s;
}

.icon-circle.bg-register {
  background: linear-gradient(135deg, #198754, #157347);
  box-shadow: 0 4px 10px rgba(25, 135, 84, 0.3);
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

.modal-body-custom {
  padding: 1.25rem 1.5rem;
  overflow-y: auto;
}

.tab-btn {
  font-size: 0.85rem;
  letter-spacing: 0.5px;
  transition: all 0.2s ease;
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
