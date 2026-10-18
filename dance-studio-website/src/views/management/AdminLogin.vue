<template>
  <div class="admin-login-page py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-lg border-0 rounded-4 overflow-hidden">
            <div class="card-header bg-dark text-white p-4 text-center">
              <div class="fs-1 mb-2">🎭</div>
              <h4 class="fw-bold mb-1">後台管理系統</h4>
              <p class="small text-light-50 mb-0">請選擇身分並登入管理選單</p>
            </div>

            <div class="card-body p-4">
              <!-- 權限身分快速登入按鈕 -->
              <div class="mb-4">
                <label class="form-label small fw-bold text-secondary mb-2">
                  <i class="bi bi-lightning-charge-fill text-warning me-1"></i>快速切換權限試用：
                </label>
                <div class="d-grid gap-2">
                  <button 
                    type="button" 
                    class="btn btn-outline-danger btn-sm text-start d-flex justify-content-between align-items-center"
                    @click="fillCredentials('admin', 'admin123')"
                  >
                    <span><strong>👑 管理員 (Administrator)</strong> - 全站管理</span>
                    <span class="badge bg-danger">admin</span>
                  </button>
                  <button 
                    type="button" 
                    class="btn btn-outline-success btn-sm text-start d-flex justify-content-between align-items-center"
                    @click="fillCredentials('counter', 'desk123')"
                  >
                    <span><strong>🛎️ 櫃檯客服 (Front Desk)</strong> - 學生/報名/課表 (不顯示鐘點費)</span>
                    <span class="badge bg-success">counter</span>
                  </button>
                  <button 
                    type="button" 
                    class="btn btn-outline-primary btn-sm text-start d-flex justify-content-between align-items-center"
                    @click="fillCredentials('teacher', 'teacher123')"
                  >
                    <span><strong>💃 授課老師 (Teacher)</strong> - 課表/老師列表/鐘點試算</span>
                    <span class="badge bg-primary">teacher</span>
                  </button>
                </div>
              </div>

              <div class="position-relative text-center my-3">
                <hr class="text-muted" />
                <span class="position-absolute top-50 start-50 translate-middle bg-white px-2 small text-muted">
                  或輸入帳號密碼
                </span>
              </div>

              <!-- 登入表單 -->
              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="adminUsername" class="form-label fw-semibold">管理員 / 員工帳號：</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-person"></i></span>
                    <input 
                      type="text" 
                      id="adminUsername" 
                      class="form-control" 
                      v-model="username" 
                      placeholder="請輸入帳號" 
                      required 
                    />
                  </div>
                </div>

                <div class="mb-4">
                  <label for="adminPassword" class="form-label fw-semibold">登入密碼：</label>
                  <div class="input-group">
                    <span class="input-group-text"><i class="bi bi-lock"></i></span>
                    <input 
                      :type="showPassword ? 'text' : 'password'" 
                      id="adminPassword" 
                      class="form-control" 
                      v-model="password" 
                      placeholder="請輸入密碼" 
                      required 
                    />
                    <button 
                      class="btn btn-outline-secondary" 
                      type="button" 
                      @click="showPassword = !showPassword"
                    >
                      <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                  </div>
                </div>

                <button 
                  type="submit" 
                  class="btn btn-dark w-100 py-2 fw-bold" 
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  <i v-else class="bi bi-box-arrow-in-right me-1"></i>登入管理後台
                </button>
              </form>
            </div>

            <!-- 權限說明 Card Footer -->
            <div class="card-footer bg-light p-3 small text-muted">
              <div class="fw-bold text-dark mb-1"><i class="bi bi-shield-lock me-1"></i>三種權限說明：</div>
              <ul class="mb-0 ps-3">
                <li><strong>管理員</strong>：全功能開放，包含老師、課程、費用拆帳規則及系統設定。</li>
                <li><strong>櫃檯</strong>：負責學生名冊、課表排定、現場為學員加課與扣堂（不顯示師資授課鐘點費）。</li>
                <li><strong>老師</strong>：專屬查看授課時間表（含課堂點名名冊）、老師列表（本人帳號/密碼修改/銀行帳號）及鐘點薪資試算（不顯示全體學生列表）。</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAdminAuth } from '@/utils/adminAuth';
import { showToast } from '@/utils/toast';

export default {
  name: 'AdminLogin',
  data() {
    return {
      adminAuth: useAdminAuth(),
      username: '',
      password: '',
      showPassword: false,
      loading: false
    };
  },
  methods: {
    fillCredentials(u, p) {
      this.username = u;
      this.password = p;
    },
    async handleLogin() {
      if (!this.username || !this.password) {
        showToast('請輸入帳號與密碼', 'error');
        return;
      }
      this.loading = true;
      try {
        const user = await this.adminAuth.login(this.username, this.password);
        showToast(`登入成功！歡迎 ${user.name} (${this.adminAuth.roleLabel})`, 'success');
        
        // 依權限轉導至該身分可進入的首頁
        const redirectPath = this.adminAuth.getFirstAllowedRoute();
        this.$router.push(redirectPath);
      } catch (err) {
        showToast(err.message || '登入失敗，請確認帳號密碼', 'error');
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.admin-login-page {
  min-height: calc(100vh - 140px);
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  display: flex;
  align-items: center;
}
</style>

