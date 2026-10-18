<template>
  <div v-if="show" class="modal-backdrop fade show"></div>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" role="dialog" @click.self="close">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content rounded-4 shadow border-0 overflow-hidden">
        <!-- 標頭 -->
        <div class="modal-header bg-gradient-primary text-white py-3 px-4">
          <div class="d-flex align-items-center">
            <div class="bg-white text-primary rounded-circle p-2 me-3 shadow-sm d-flex align-items-center justify-content-center" style="width: 42px; height: 42px;">
              <i class="bi bi-shield-check fs-4"></i>
            </div>
            <div>
              <h5 class="modal-title fw-bold mb-0">打卡 IP 白名單防護設定</h5>
              <div class="small opacity-75">限制櫃檯與老師打卡網路來源，防止遠端代打卡</div>
            </div>
          </div>
          <button type="button" class="btn-close btn-close-white" @click="close" aria-label="Close"></button>
        </div>

        <!-- 內容 -->
        <div class="modal-body p-4 text-start">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">載入中...</span>
            </div>
            <div class="text-muted small mt-2">載入 IP 防護設定中...</div>
          </div>

          <div v-else>
            <!-- 1. 開啟/關閉 IP 限制總開關 -->
            <div class="card border-0 bg-light rounded-3 p-3 mb-4 shadow-sm">
              <div class="d-flex flex-wrap justify-content-between align-items-center">
                <div class="me-3 mb-2 mb-sm-0">
                  <div class="d-flex align-items-center mb-1">
                    <h6 class="fw-bold mb-0 text-dark me-2">打卡 IP 白名單限制開關</h6>
                    <span 
                      class="badge" 
                      :class="enabled ? 'bg-success' : 'bg-secondary'"
                    >
                      {{ enabled ? '已開啟限制 (需在白名單內)' : '已關閉限制 (允許任意網路)' }}
                    </span>
                  </div>
                  <div class="text-muted small">
                    <i class="bi bi-info-circle me-1"></i>
                    如遇教室停電、Wi-Fi 斷網、外勤活動或應急打卡時，可隨時「關閉」限制，避免打卡受阻。
                  </div>
                </div>

                <div class="form-check form-switch fs-4 mb-0">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    role="switch" 
                    id="ipRestrictionSwitch" 
                    v-model="enabled"
                  />
                  <label class="form-check-label visually-hidden" for="ipRestrictionSwitch">切換開關</label>
                </div>
              </div>
            </div>

            <!-- 2. 自動偵測目前連線 IP 區塊 -->
            <div class="card border border-primary-subtle bg-primary-subtle bg-opacity-10 rounded-3 p-3 mb-4">
              <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
                <div class="d-flex align-items-center">
                  <i class="bi bi-broadcast text-primary fs-4 me-2"></i>
                  <div>
                    <div class="small text-muted fw-semibold">您目前的網路 IP 來源：</div>
                    <div class="fs-5 fw-bold font-monospace text-primary">
                      {{ clientIp || '偵測中...' }}
                    </div>
                  </div>
                </div>

                <div>
                  <button 
                    type="button" 
                    class="btn btn-outline-primary btn-sm rounded-pill px-3 shadow-sm"
                    @click="addCurrentIp"
                    :disabled="!clientIp"
                  >
                    <i class="bi bi-plus-circle-fill me-1"></i>
                    自動偵測並加入目前 IP
                  </button>
                </div>
              </div>
            </div>

            <!-- 3. 白名單 IP 清單編輯區 -->
            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <label for="allowedIpsInput" class="form-label fw-bold text-dark mb-0">
                  <i class="bi bi-list-check me-1 text-primary"></i>
                  允許打卡的 IP 白名單清單：
                </label>
                <span class="small text-muted">
                  已填寫 <strong>{{ parsedIpCount }}</strong> 組 IP / 網段
                </span>
              </div>

              <textarea 
                id="allowedIpsInput"
                class="form-control font-monospace" 
                rows="5"
                v-model="allowedIps"
                placeholder="例如：
203.0.113.195 (總館 Wi-Fi 對外 IP)
198.51.100.22 (分館固定 IP)
192.168.1.0/24 (教室區網網段)
127.0.0.1"
              ></textarea>
              <div class="form-text small text-muted mt-2">
                <i class="bi bi-lightbulb me-1 text-warning"></i>
                支援輸入一組或多組 IP（每行一筆或以逗號、分號隔開）。亦支援 CIDR 子網段（如 <code>192.168.1.0/24</code>）。
              </div>
            </div>

            <!-- 4. 防護規則說明提示 -->
            <div class="alert alert-secondary py-2 px-3 rounded-3 small mb-0">
              <div class="fw-semibold mb-1 text-dark">
                <i class="bi bi-shield-lock me-1 text-primary"></i>
                打卡檢驗防護規則說明：
              </div>
              <ul class="mb-0 ps-3 text-muted">
                <li><strong>櫃檯客服</strong>：「上班 / 下班打卡」皆會即時核對 IP。</li>
                <li><strong>授課老師</strong>：「上課 / 下課打卡」皆會即時核對 IP。</li>
                <li><strong>來源追蹤</strong>：所有打卡歷史均自動記錄當下 IP（<code>clock_in_ip</code> 與 <code>clock_out_ip</code>），方便管理員查核稽核。</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 頁尾 -->
        <div class="modal-footer bg-light py-2 px-4">
          <button type="button" class="btn btn-secondary px-4 rounded-3" @click="close" :disabled="saving">
            取消
          </button>
          <button type="button" class="btn btn-primary px-4 rounded-3 fw-bold shadow-sm" @click="saveSettings" :disabled="saving || loading">
            <span v-if="saving" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
            <i v-else class="bi bi-check-lg me-1"></i>
            儲存 IP 設定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { showToast } from '@/utils/toast';

export default {
  name: 'AttendanceIpModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:show', 'saved'],
  data() {
    return {
      loading: false,
      saving: false,
      enabled: false,
      allowedIps: '',
      clientIp: ''
    };
  },
  computed: {
    parsedIpCount() {
      if (!this.allowedIps) return 0;
      const items = this.allowedIps.split(/[\r\n,;]+/).map(s => s.trim()).filter(Boolean);
      return items.length;
    }
  },
  watch: {
    show(val) {
      if (val) {
        this.fetchSettings();
      }
    }
  },
  methods: {
    close() {
      this.$emit('update:show', false);
    },
    async fetchSettings() {
      this.loading = true;
      try {
        const res = await axios.get('/api/admin/settings/attendance-ip');
        if (res.data && res.data.success) {
          this.enabled = !!res.data.enabled;
          this.allowedIps = res.data.allowed_ips || '';
          this.clientIp = res.data.client_ip || '';
        }
      } catch (err) {
        console.error('取得 IP 設定失敗:', err);
        showToast('無法取得 IP 設定，請確認網路或稍後重試', 'danger');
      } finally {
        this.loading = false;
      }
    },
    addCurrentIp() {
      if (!this.clientIp) return;
      const cleanIp = this.clientIp.trim();
      const existing = this.allowedIps.split(/[\r\n,;]+/).map(s => s.trim()).filter(Boolean);

      if (existing.includes(cleanIp)) {
        showToast(`目前 IP [${cleanIp}] 已在白名單清單中！`, 'info');
        return;
      }

      if (this.allowedIps.trim().length > 0) {
        this.allowedIps = this.allowedIps.trim() + '\n' + cleanIp;
      } else {
        this.allowedIps = cleanIp;
      }

      showToast(`已將目前 IP [${cleanIp}] 自動加入白名單清單！記得點擊「儲存 IP 設定」`, 'success');
    },
    async saveSettings() {
      this.saving = true;
      try {
        const payload = {
          enabled: this.enabled,
          allowed_ips: this.allowedIps
        };
        const res = await axios.post('/api/admin/settings/attendance-ip', payload);
        if (res.data && res.data.success) {
          showToast(res.data.message || '打卡 IP 白名單設定已成功更新！', 'success');
          this.$emit('saved', {
            enabled: this.enabled,
            allowed_ips: this.allowedIps,
            client_ip: this.clientIp
          });
          this.close();
        } else {
          showToast(res.data?.error || '儲存設定失敗', 'danger');
        }
      } catch (err) {
        console.error('儲存 IP 設定失敗:', err);
        const msg = err.response?.data?.error || '儲存失敗，請重試';
        showToast(msg, 'danger');
      } finally {
        this.saving = false;
      }
    }
  }
};
</script>

<style scoped>
.bg-gradient-primary {
  background: linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%);
}
</style>

