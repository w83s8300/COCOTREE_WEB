<template>
  <div class="line-settings-page">
    <!-- 頁頭標題 -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2 mb-4">
      <div>
        <h2 class="fw-bold mb-1 text-dark d-flex align-items-center">
          <i class="bi bi-line text-success me-2 fs-2"></i>LINE 整合設定
        </h2>
        <p class="text-muted small mb-0">
          管理 LINE Login 授權頻道、工作室官方 LINE 好友連結以及學員帳號關聯整合
        </p>
      </div>
      <div class="d-flex gap-2">
        <router-link to="/admin/students" class="btn btn-outline-secondary btn-sm d-flex align-items-center gap-1 shadow-sm">
          <i class="bi bi-people"></i>
          <span>檢視學員名單</span>
        </router-link>
        <button
          type="button"
          class="btn btn-success btn-sm d-flex align-items-center gap-1 shadow-sm px-3 fw-bold"
          :disabled="saving"
          @click="saveSettings"
        >
          <span v-if="saving" class="spinner-border spinner-border-sm"></span>
          <i v-else class="bi bi-floppy-fill"></i>
          <span>儲存所有設定</span>
        </button>
      </div>
    </div>

    <!-- 狀態摘要卡片列 -->
    <div class="row g-3 mb-4">
      <div class="col-sm-6 col-lg-3">
        <div class="card border-0 shadow-sm rounded-3 p-3 bg-white h-100">
          <div class="d-flex align-items-center">
            <div class="status-icon-circle me-3" :class="settings.line_login_enabled ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">
              <i class="bi" :class="settings.line_login_enabled ? 'bi-toggle-on fs-3' : 'bi-toggle-off fs-3'"></i>
            </div>
            <div>
              <div class="small text-muted">功能啟用狀態</div>
              <div class="fw-bold fs-6" :class="settings.line_login_enabled ? 'text-success' : 'text-secondary'">
                {{ settings.line_login_enabled ? '已啟用運作中' : '目前停用中' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card border-0 shadow-sm rounded-3 p-3 bg-white h-100">
          <div class="d-flex align-items-center">
            <div class="status-icon-circle me-3" :class="isChannelConfigured ? 'bg-success-subtle text-success' : 'bg-warning-subtle text-warning'">
              <i class="bi" :class="isChannelConfigured ? 'bi-check-circle-fill fs-4' : 'bi-exclamation-circle-fill fs-4'"></i>
            </div>
            <div>
              <div class="small text-muted">API 金鑰狀態</div>
              <div class="fw-bold fs-6" :class="isChannelConfigured ? 'text-dark' : 'text-warning'">
                {{ isChannelConfigured ? '已填寫 Channel ID' : '尚未完整設定' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card border-0 shadow-sm rounded-3 p-3 bg-white h-100">
          <div class="d-flex align-items-center">
            <div class="status-icon-circle bg-primary-subtle text-primary me-3">
              <i class="bi bi-person-check fs-4"></i>
            </div>
            <div>
              <div class="small text-muted">已綁定 LINE 學員</div>
              <div class="fw-bold fs-5 text-dark">
                {{ stats.linkedCount }} <span class="fs-6 text-muted fw-normal">/ {{ stats.totalCount }} 人</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3">
        <div class="card border-0 shadow-sm rounded-3 p-3 bg-white h-100">
          <div class="d-flex align-items-center">
            <div class="status-icon-circle bg-info-subtle text-info me-3">
              <i class="bi bi-pie-chart-fill fs-4"></i>
            </div>
            <div>
              <div class="small text-muted">學員 LINE 綁定率</div>
              <div class="fw-bold fs-5 text-dark">
                {{ stats.linkRate }}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入 LINE 系統設定...</p>
    </div>

    <!-- 主要設定表單 -->
    <div v-else class="row g-4">
      <!-- 左欄：參數設定 -->
      <div class="col-lg-7">
        <!-- 區塊 1：功能開關與 LINE Login 頻道憑證 -->
        <div class="card border-0 shadow-sm rounded-3 mb-4">
          <div class="card-header bg-white py-3 border-bottom d-flex align-items-center justify-content-between">
            <h5 class="fw-bold mb-0 text-dark d-flex align-items-center">
              <i class="bi bi-shield-lock-fill text-success me-2"></i>LINE Login 憑證設定
            </h5>
            <span class="badge" :class="settings.line_login_enabled ? 'bg-success' : 'bg-secondary'">
              {{ settings.line_login_enabled ? '開關: 開啟' : '開關: 關閉' }}
            </span>
          </div>

          <div class="card-body p-4">
            <!-- 總開關 -->
            <div class="form-check form-switch mb-4 p-3 bg-light rounded-3 border d-flex align-items-center justify-content-between ps-3">
              <label class="form-check-label fw-bold mb-0 text-dark" for="loginSwitch">
                <div>啟用 LINE 快速登入與帳號關聯</div>
                <small class="text-muted fw-normal">關閉後前台將暫時隱藏 LINE 登入與關聯按鈕</small>
              </label>
              <input
                id="loginSwitch"
                v-model="settings.line_login_enabled"
                class="form-check-input fs-5 ms-3 my-0"
                type="checkbox"
                role="switch"
              />
            </div>

            <!-- Channel ID -->
            <div class="mb-3">
              <label class="form-label fw-bold small text-dark mb-1">
                Channel ID (頻道識別碼) <span class="text-danger">*</span>
              </label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-hash"></i></span>
                <input
                  type="text"
                  v-model.trim="settings.line_channel_id"
                  class="form-control font-monospace"
                  placeholder="例如：2006789123"
                  :disabled="saving"
                />
              </div>
              <small class="text-muted">於 LINE Developers Console 的 LINE Login 頻道之「Basic settings」頁籤可取得。</small>
            </div>

            <!-- Channel Secret -->
            <div class="mb-3">
              <label class="form-label fw-bold small text-dark mb-1">
                Channel Secret (頻道金鑰) <span class="text-danger">*</span>
              </label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-key-fill"></i></span>
                <input
                  :type="showSecret ? 'text' : 'password'"
                  v-model.trim="settings.line_channel_secret"
                  class="form-control font-monospace"
                  placeholder="例如：4a89bc345d12ef67..."
                  :disabled="saving"
                />
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  @click="showSecret = !showSecret"
                >
                  <i :class="showSecret ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
              <small class="text-muted">用於伺服器端與 LINE 安全交換 Token，系統將嚴格保密。</small>
            </div>
          </div>
        </div>

        <!-- 區塊 2：工作室官方 LINE 帳號資訊 -->
        <div class="card border-0 shadow-sm rounded-3">
          <div class="card-header bg-white py-3 border-bottom">
            <h5 class="fw-bold mb-0 text-dark d-flex align-items-center">
              <i class="bi bi-chat-heart-fill text-success me-2"></i>官方 LINE 帳號好友引導
            </h5>
          </div>

          <div class="card-body p-4">
            <div class="mb-3">
              <label class="form-label fw-bold small text-dark mb-1">
                LINE 官方帳號 ID (選填)
              </label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-at"></i></span>
                <input
                  type="text"
                  v-model.trim="settings.line_official_id"
                  class="form-control"
                  placeholder="例如：@dancestudio"
                  :disabled="saving"
                />
              </div>
              <small class="text-muted">展示於前台聯絡我們與學員中心，方便學員搜尋加入官方好友。</small>
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold small text-dark mb-1">
                LINE 官方加好友連結 (選填)
              </label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-link-45deg"></i></span>
                <input
                  type="url"
                  v-model.trim="settings.line_official_url"
                  class="form-control"
                  placeholder="例如：https://line.me/R/ti/p/@dancestudio"
                  :disabled="saving"
                />
                <a
                  v-if="settings.line_official_url"
                  :href="settings.line_official_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-outline-success"
                  title="開新分頁測試連結"
                >
                  <i class="bi bi-box-arrow-up-right me-1"></i>測試
                </a>
              </div>
              <small class="text-muted">點擊後可自動呼叫手機 LINE App 開啟加好友頁面。</small>
            </div>
          </div>
        </div>
      </div>

      <!-- 右欄：LINE Developers 回呼網址與設定教學指引 -->
      <div class="col-lg-5">
        <!-- Card: 回呼網址設定 -->
        <div class="card border-0 shadow-sm rounded-3 mb-4 border-top border-4 border-success">
          <div class="card-body p-4">
            <div class="d-flex align-items-center gap-2 mb-2">
              <i class="bi bi-arrow-repeat text-success fs-4"></i>
              <h5 class="fw-bold mb-0 text-dark">Callback URL (回呼網址)</h5>
            </div>
            <p class="small text-muted mb-3">
              請務必將此網址加入至您的 LINE Developers 後台，否則用戶授權時會出現網址無效錯誤：
            </p>

            <div class="p-3 bg-light rounded-3 border mb-3">
              <div class="small fw-bold text-secondary mb-1">回呼網址 (Callback URL)：</div>
              <div class="input-group input-group-sm">
                <input
                  type="text"
                  class="form-control font-monospace bg-white"
                  :value="callbackUrl"
                  readonly
                />
                <button
                  type="button"
                  class="btn btn-outline-success"
                  @click="copyCallbackUrl"
                >
                  <i class="bi bi-clipboard me-1"></i>複製
                </button>
              </div>
            </div>

            <div class="alert alert-info py-2 px-3 small d-flex align-items-start mb-0">
              <i class="bi bi-info-circle-fill me-2 mt-1 flex-shrink-0 text-info"></i>
              <div>
                如果您的網站上線了自訂網域（例如 <code>https://yourdomain.com</code>），請記得在該網域環境下複製並於 LINE 後台同步更新。
              </div>
            </div>
          </div>
        </div>

        <!-- Card: Step-by-Step 串接指南 -->
        <div class="card border-0 shadow-sm rounded-3">
          <div class="card-body p-4">
            <h6 class="fw-bold text-dark mb-3 d-flex align-items-center justify-content-between">
              <span><i class="bi bi-compass-fill text-primary me-2"></i>5 分鐘快速串接教學</span>
              <a
                href="https://developers.line.biz/console/"
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn-sm btn-outline-primary"
              >
                前往 LINE Developers <i class="bi bi-box-arrow-up-right ms-1"></i>
              </a>
            </h6>

            <div class="timeline-steps small">
              <div class="step-item d-flex gap-3 mb-3">
                <div class="step-number bg-success text-white rounded-circle flex-shrink-0 d-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">1</div>
                <div>
                  <div class="fw-bold text-dark">註冊 Provider</div>
                  <div class="text-muted">以您的 LINE 帳號登入 LINE Developers Console 並建立 Provider。</div>
                </div>
              </div>

              <div class="step-item d-flex gap-3 mb-3">
                <div class="step-number bg-success text-white rounded-circle flex-shrink-0 d-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">2</div>
                <div>
                  <div class="fw-bold text-dark">建立「LINE Login」Channel</div>
                  <div class="text-muted">選擇建立 Channel 類型為 <strong>LINE Login</strong>，填寫應用程式名稱與說明。</div>
                </div>
              </div>

              <div class="step-item d-flex gap-3 mb-3">
                <div class="step-number bg-success text-white rounded-circle flex-shrink-0 d-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">3</div>
                <div>
                  <div class="fw-bold text-dark">設定 Callback URL</div>
                  <div class="text-muted">進入 <strong>LINE Login → Developing settings</strong>，將上方 Callback URL 填入。</div>
                </div>
              </div>

              <div class="step-item d-flex gap-3 mb-3">
                <div class="step-number bg-success text-white rounded-circle flex-shrink-0 d-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">4</div>
                <div>
                  <div class="fw-bold text-dark">複製金鑰填入本頁</div>
                  <div class="text-muted">至 <strong>Basic settings</strong> 複製 <code>Channel ID</code> 與 <code>Channel Secret</code> 儲存於本頁。</div>
                </div>
              </div>

              <div class="step-item d-flex gap-3">
                <div class="step-number bg-success text-white rounded-circle flex-shrink-0 d-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">5</div>
                <div>
                  <div class="fw-bold text-dark">完成！立即體驗快速登入</div>
                  <div class="text-muted">前往前台點選「使用 LINE 快速登入」，即可體驗一鍵登入與關聯綁定！</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api, { API_ENDPOINTS } from '@/utils/api'
import { showToast } from '@/utils/toast'

export default {
  name: 'LineSettings',
  data() {
    return {
      loading: true,
      saving: false,
      showSecret: false,
      settings: {
        line_login_enabled: true,
        line_channel_id: '',
        line_channel_secret: '',
        line_official_id: '',
        line_official_url: ''
      },
      stats: {
        totalCount: 0,
        linkedCount: 0,
        linkRate: 0
      }
    }
  },
  computed: {
    isChannelConfigured() {
      return !!(this.settings.line_channel_id && this.settings.line_channel_id.trim())
    },
    callbackUrl() {
      if (typeof window !== 'undefined') {
        return window.location.origin + '/line-callback'
      }
      return '/line-callback'
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        // 並行取得 LINE 設定與學員統計
        const [settingsRes, studentsRes] = await Promise.allSettled([
          api.get('/admin/settings/line'),
          api.get(API_ENDPOINTS.STUDENTS)
        ])

        if (settingsRes.status === 'fulfilled' && settingsRes.value.success) {
          const s = settingsRes.value.settings || {}
          this.settings = {
            line_login_enabled: s.line_login_enabled !== false,
            line_channel_id: s.line_channel_id || '',
            line_channel_secret: s.line_channel_secret || '',
            line_official_id: s.line_official_id || '',
            line_official_url: s.line_official_url || ''
          }
        }

        if (studentsRes.status === 'fulfilled' && studentsRes.value.success) {
          const students = studentsRes.value.students || []
          const total = students.length
          const linked = students.filter(item => !!item.line_user_id).length
          const rate = total > 0 ? Math.round((linked / total) * 100) : 0
          this.stats = {
            totalCount: total,
            linkedCount: linked,
            linkRate: rate
          }
        }
      } catch (err) {
        console.error('載入設定失敗:', err)
        showToast('載入 LINE 設定失敗，請稍後重試', 'error')
      } finally {
        this.loading = false
      }
    },
    async saveSettings() {
      this.saving = true
      try {
        const payload = {
          line_login_enabled: this.settings.line_login_enabled,
          line_channel_id: this.settings.line_channel_id.trim(),
          line_channel_secret: this.settings.line_channel_secret.trim(),
          line_official_id: this.settings.line_official_id.trim(),
          line_official_url: this.settings.line_official_url.trim()
        }

        const res = await api.post('/admin/settings/line', payload)
        if (res.success) {
          showToast(res.message || 'LINE 設定已成功儲存！', 'success')
        } else {
          showToast(res.error || res.message || '儲存失敗', 'error')
        }
      } catch (err) {
        showToast(err.message || '儲存設定失敗，請檢查伺服器連線', 'error')
      } finally {
        this.saving = false
      }
    },
    copyCallbackUrl() {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(this.callbackUrl)
          .then(() => showToast('已成功複製 Callback URL 至剪貼簿！', 'success'))
          .catch(() => showToast('複製失敗，請手動複製', 'warning'))
      } else {
        showToast('請手動選取並複製網址', 'info')
      }
    }
  }
}
</script>

<style scoped>
.line-settings-page {
  padding: 10px;
}
.status-icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.step-number {
  font-size: 0.75rem;
  font-weight: bold;
}
</style>

