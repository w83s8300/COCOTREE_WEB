<template>
  <div class="students">
    <!-- 頂部標題與工具列 -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2 mb-3">
      <div>
        <h2 class="fw-bold mb-0">學生列表</h2>
        <small class="text-muted">共 {{ filteredStudents.length }} 位學員資料</small>
      </div>
      <div class="d-flex flex-wrap align-items-center gap-2">
        <!-- LINE 綁定狀態篩選 -->
        <select v-model="lineFilter" class="form-select form-select-sm" style="width: 140px;">
          <option value="all">LINE: 全部</option>
          <option value="linked">🟢 已關聯 LINE</option>
          <option value="unlinked">⚪ 未關聯 LINE</option>
        </select>

        <!-- 搜尋姓名 -->
        <div class="input-group input-group-sm" style="width: 200px;">
          <input
            type="text"
            v-model="searchQuery"
            @keyup.enter="fetchStudents"
            placeholder="搜尋學生姓名"
            class="form-control"
          />
          <button @click="fetchStudents" class="btn btn-outline-secondary">
            <i class="bi bi-search"></i>
          </button>
        </div>

        <!-- LINE 整合設定按鈕 -->
        <button @click="openLineSettingsModal" class="btn btn-outline-success btn-sm text-nowrap">
          <i class="bi bi-line me-1"></i>LINE 設定
        </button>

        <!-- 新增學生按鈕 -->
        <button @click="openCreate" class="btn btn-success btn-sm text-nowrap">
          <i class="bi bi-plus-lg me-1"></i>新增學生
        </button>
      </div>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入學生資料...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button @click="fetchStudents" class="btn btn-outline-danger btn-sm">重新嘗試</button>
    </div>

    <!-- 空資料狀態 -->
    <div v-else-if="filteredStudents.length === 0" class="text-center py-5 text-muted">
      <i class="bi bi-people fs-1 d-block mb-2 text-secondary opacity-50"></i>
      <p>找不到符合條件的學生資料。</p>
    </div>

    <!-- 表格內容 -->
    <div v-else class="table-responsive">
      <table class="table table-hover table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col">姓名</th>
            <th scope="col">電子郵件</th>
            <th scope="col">電話</th>
            <th scope="col">LINE 關聯</th>
            <th scope="col">出生年月日</th>
            <th scope="col">剩餘堂數</th>
            <th scope="col">會員年費到期日</th>
            <th scope="col">月費暢跳到期日</th>
            <th scope="col">銀行後5碼</th>
            <th scope="col">緊急聯絡人</th>
            <th scope="col">緊急聯絡電話</th>
            <th scope="col">醫療備註</th>
            <th scope="col" class="text-center" style="width: 140px;">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in filteredStudents" :key="student.id">
            <td class="fw-bold">{{ student.name }}</td>
            <td>{{ student.email || '-' }}</td>
            <td>{{ student.phone || '-' }}</td>
            <!-- LINE 關聯狀態欄位 -->
            <td>
              <div v-if="student.line_user_id" class="d-flex align-items-center gap-1">
                <span
                  class="badge bg-success-subtle text-success border border-success d-inline-flex align-items-center py-1 px-2"
                  :title="`LINE ID: ${student.line_user_id}\n關聯時間: ${formatDateTime(student.line_linked_at)}`"
                  style="cursor: help;"
                >
                  <i class="bi bi-line me-1 fs-6"></i>
                  <span>{{ student.line_display_name || '已關聯' }}</span>
                </span>
                <button
                  type="button"
                  class="btn btn-link btn-sm text-danger p-0 ms-1"
                  title="解除此學員的 LINE 綁定"
                  @click="handleUnbindLine(student)"
                >
                  <i class="bi bi-x-circle"></i>
                </button>
              </div>
              <div v-else class="d-flex align-items-center gap-1">
                <span class="badge bg-light text-muted border">未關聯</span>
                <button
                  type="button"
                  class="btn btn-link btn-sm text-primary p-0 ms-1"
                  title="快速為此學員關聯 LINE"
                  @click="openQuickBind(student)"
                >
                  <i class="bi bi-link-45deg"></i>綁定
                </button>
              </div>
            </td>
            <td>{{ formatDate(student.date_of_birth) }}</td>
            <td>
              <span class="badge" :class="student.remaining_classes > 0 ? 'bg-success' : 'bg-warning text-dark'">
                {{ student.remaining_classes || 0 }} 堂
              </span>
            </td>
            <td>
              <span v-if="student.membership_expiry" :class="isExpired(student.membership_expiry) ? 'text-danger' : 'text-dark'">
                {{ formatDate(student.membership_expiry) }}
              </span>
              <span v-else class="text-muted small">未開通</span>
            </td>
            <td>
              <div v-if="student.monthly_pass_expiry">
                <span class="badge" :class="isExpired(student.monthly_pass_expiry) ? 'bg-secondary' : 'bg-info text-dark'">
                  {{ isExpired(student.monthly_pass_expiry) ? '已過期' : '暢跳中' }}
                </span>
                <div class="small mt-1" :class="isExpired(student.monthly_pass_expiry) ? 'text-muted' : 'text-primary fw-bold'">
                  {{ formatDate(student.monthly_pass_expiry) }}
                </div>
              </div>
              <span v-else class="text-muted small">未開通</span>
            </td>
            <td>
              <span v-if="student.bank_last_5" class="badge bg-light text-dark border font-monospace">
                {{ student.bank_last_5 }}
              </span>
              <span v-else class="text-muted small">-</span>
            </td>
            <td>{{ student.emergency_contact || '-' }}</td>
            <td>{{ student.emergency_phone || '-' }}</td>
            <td>{{ student.medical_notes || '無' }}</td>
            <td class="text-center">
              <button @click="openEdit(student.id)" class="btn btn-primary btn-sm me-1">編輯</button>
              <button @click="deleteStudent(student.id)" class="btn btn-danger btn-sm">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bootstrap Modal for adding/editing student -->
    <div class="modal fade" id="editStudentModal" tabindex="-1" aria-labelledby="editStudentModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editStudentModalLabel">{{ editingId ? '編輯學生' : '新增學生' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddStudent
              v-if="showForm"
              :studentId="editingId"
              @student-updated="handleStudentUpdated"
              @close-modal="closeModal"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 櫃檯快速為學員綁定 LINE Modal -->
    <div v-if="showQuickBindModal" class="modal-backdrop-custom" @click.self="showQuickBindModal = false">
      <div class="modal-dialog-custom">
        <div class="modal-content-custom shadow-lg">
          <div class="modal-header p-3 border-bottom d-flex justify-content-between align-items-center">
            <h5 class="modal-title fw-bold mb-0 text-success">
              <i class="bi bi-line me-2"></i>為【{{ targetStudent?.name }}】綁定 LINE
            </h5>
            <button type="button" class="btn-close" @click="showQuickBindModal = false"></button>
          </div>
          <div class="modal-body p-3">
            <div class="mb-3">
              <label class="form-label small fw-bold mb-1">LINE 用戶暱稱：</label>
              <input
                type="text"
                v-model.trim="quickBindDisplayName"
                class="form-control form-control-sm"
                placeholder="例如：Alex / 小舞"
              />
            </div>
            <div class="mb-3">
              <label class="form-label small fw-bold mb-1">LINE User ID：</label>
              <input
                type="text"
                v-model.trim="quickBindUserId"
                class="form-control form-control-sm font-monospace"
                placeholder="以 U 開頭之 33 碼 (留空自動產生測試 ID)"
              />
            </div>
            <div class="small text-muted mb-3 bg-light p-2 rounded border">
              <i class="bi bi-info-circle me-1 text-primary"></i>
              綁定後該學員即可於首頁使用此 LINE 帳號一鍵登入會員系統。
            </div>
            <div class="d-flex justify-content-end gap-2">
              <button type="button" class="btn btn-secondary btn-sm" @click="showQuickBindModal = false">取消</button>
              <button
                type="button"
                class="btn btn-success btn-sm fw-bold"
                :disabled="quickBindLoading"
                @click="submitQuickBind"
              >
                <span v-if="quickBindLoading" class="spinner-border spinner-border-sm me-1"></span>
                確認關聯 LINE
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- LINE 系統整合設定 Modal -->
    <div v-if="showLineSettingsModal" class="modal-backdrop-custom" @click.self="showLineSettingsModal = false">
      <div class="modal-dialog-custom" style="max-width: 580px;">
        <div class="modal-content-custom shadow-lg">
          <div class="modal-header p-3 border-bottom d-flex justify-content-between align-items-center bg-light">
            <h5 class="modal-title fw-bold mb-0 text-success">
              <i class="bi bi-line me-2"></i>LINE 官方串接設定
            </h5>
            <button type="button" class="btn-close" @click="showLineSettingsModal = false"></button>
          </div>
          <div class="modal-body p-3">
            <div class="mb-3 form-check form-switch">
              <input
                class="form-check-input"
                type="checkbox"
                id="lineLoginEnabled"
                v-model="lineConfig.line_login_enabled"
              />
              <label class="form-check-label fw-bold" for="lineLoginEnabled">
                啟用 LINE 快速登入與會員關聯功能
              </label>
            </div>

            <div class="mb-3">
              <label class="form-label small fw-bold mb-1">
                LINE Login Channel ID (頻道識別碼)：
              </label>
              <input
                type="text"
                v-model.trim="lineConfig.line_channel_id"
                class="form-control form-control-sm font-monospace"
                placeholder="例如：2006789123"
              />
              <small class="text-muted">請至 LINE Developers 建立「LINE Login」Channel 後取得</small>
            </div>

            <div class="mb-3">
              <label class="form-label small fw-bold mb-1">
                LINE Login Channel Secret (頻道金鑰)：
              </label>
              <input
                type="password"
                v-model.trim="lineConfig.line_channel_secret"
                class="form-control form-control-sm font-monospace"
                placeholder="請輸入 Channel Secret"
              />
            </div>

            <div class="mb-3">
              <label class="form-label small fw-bold mb-1">
                LINE 官方帳號 ID (選填)：
              </label>
              <input
                type="text"
                v-model.trim="lineConfig.line_official_id"
                class="form-control form-control-sm"
                placeholder="例如：@dancestudio"
              />
            </div>

            <div class="mb-3">
              <label class="form-label small fw-bold mb-1">
                LINE 官方加好友連結 (選填)：
              </label>
              <input
                type="url"
                v-model.trim="lineConfig.line_official_url"
                class="form-control form-control-sm"
                placeholder="例如：https://line.me/R/ti/p/@dancestudio"
              />
            </div>

            <!-- LINE Developers 回呼網址教學提示 -->
            <div class="p-3 bg-light rounded-3 border mb-3">
              <div class="fw-bold small mb-1 text-dark">
                <i class="bi bi-gear-fill me-1 text-primary"></i>LINE Developers 後台 Callback URL 設定：
              </div>
              <p class="small text-muted mb-2">
                請在 LINE Developers 控制台的 <strong>LINE Login → Developing settings → Callback URL</strong> 填入以下網址：
              </p>
              <div class="input-group input-group-sm">
                <input
                  type="text"
                  class="form-control font-monospace bg-white"
                  :value="callbackUrl"
                  readonly
                />
                <button class="btn btn-outline-secondary" type="button" @click="copyCallbackUrl">
                  <i class="bi bi-clipboard me-1"></i>複製
                </button>
              </div>
            </div>

            <div class="d-flex justify-content-end gap-2">
              <button type="button" class="btn btn-secondary btn-sm" @click="showLineSettingsModal = false">取消</button>
              <button
                type="button"
                class="btn btn-success btn-sm fw-bold px-3"
                :disabled="savingLineConfig"
                @click="saveLineConfig"
              >
                <span v-if="savingLineConfig" class="spinner-border spinner-border-sm me-1"></span>
                儲存設定
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api, { API_ENDPOINTS } from '@/utils/api';
import AddStudent from '../forms/AddStudent.vue';
import { useCrudModal } from '@/composables/useCrudModal';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';

export default {
  name: 'Students',
  components: {
    AddStudent
  },
  setup() {
    const { showForm, editingId, initModal, openCreate, openEdit, closeModal } = useCrudModal('editStudentModal');
    return { showForm, editingId, initModal, openCreate, openEdit, closeModal };
  },
  data() {
    return {
      students: [],
      searchQuery: '',
      lineFilter: 'all', // 'all' | 'linked' | 'unlinked'
      loading: false,
      error: null,

      // 櫃檯快速綁定 LINE
      showQuickBindModal: false,
      targetStudent: null,
      quickBindDisplayName: '',
      quickBindUserId: '',
      quickBindLoading: false,

      // LINE 系統設定
      showLineSettingsModal: false,
      savingLineConfig: false,
      lineConfig: {
        line_login_enabled: true,
        line_channel_id: '',
        line_channel_secret: '',
        line_official_id: '',
        line_official_url: ''
      }
    };
  },
  computed: {
    filteredStudents() {
      return this.students.filter(s => {
        // 姓名搜尋過濾
        if (this.searchQuery.trim()) {
          const q = this.searchQuery.trim().toLowerCase();
          const matchName = s.name && s.name.toLowerCase().includes(q);
          const matchPhone = s.phone && s.phone.includes(q);
          const matchLine = s.line_display_name && s.line_display_name.toLowerCase().includes(q);
          if (!matchName && !matchPhone && !matchLine) return false;
        }
        // LINE 狀態過濾
        if (this.lineFilter === 'linked') {
          return !!s.line_user_id;
        } else if (this.lineFilter === 'unlinked') {
          return !s.line_user_id;
        }
        return true;
      });
    },
    callbackUrl() {
      if (typeof window !== 'undefined') {
        return window.location.origin + '/line-callback';
      }
      return '/line-callback';
    }
  },
  mounted() {
    this.initModal();
  },
  created() {
    this.fetchStudents();
  },
  methods: {
    async fetchStudents() {
      this.loading = true;
      this.error = null;
      try {
        let endpoint = API_ENDPOINTS.STUDENTS;
        if (this.searchQuery.trim()) {
          endpoint += `?name=${encodeURIComponent(this.searchQuery.trim())}`;
        }
        const data = await api.get(endpoint);
        this.students = data.students || [];
      } catch (err) {
        console.error('獲取學生列表失敗:', err);
        this.error = '獲取學生列表失敗，請稍後再試。';
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString || dateString === '1911-01-01' || dateString === '0000-00-00') return '未設定';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '未設定';
      return date.toLocaleDateString('zh-TW');
    },
    isExpired(dateString) {
      if (!dateString) return true;
      const d = new Date(dateString);
      if (isNaN(d.getTime())) return true;
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return d < today;
    },
    formatDateTime(dtStr) {
      if (!dtStr) return '未設定';
      try {
        const d = new Date(dtStr);
        if (isNaN(d.getTime())) return dtStr;
        return d.toLocaleString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
      } catch (e) {
        return dtStr;
      }
    },
    async deleteStudent(id) {
      const confirmed = await showConfirm('確定要刪除這位學生嗎？此動作將移除該學生的所有修課紀錄。');
      if (!confirmed) return;

      try {
        await api.delete(`${API_ENDPOINTS.STUDENTS}/${id}`);
        showToast('學生已成功刪除！', 'success');
        this.fetchStudents();
      } catch (err) {
        console.error('刪除學生失敗:', err);
        showToast('刪除學生失敗，請重試。', 'error');
      }
    },
    handleStudentUpdated() {
      this.fetchStudents();
      this.closeModal();
    },
    // 櫃檯快速解除學生 LINE 綁定
    async handleUnbindLine(student) {
      const confirmed = await showConfirm(
        `確定要解除學員【${student.name}】與 LINE 帳號「${student.line_display_name || ''}」的關聯嗎？`,
        '解除 LINE 關聯'
      );
      if (!confirmed) return;

      try {
        const res = await api.post('/student/line/unbind', {
          student_id: student.id
        });
        if (res.success) {
          showToast(`已解除【${student.name}】的 LINE 關聯`, 'success');
          this.fetchStudents();
        } else {
          showToast(res.message || '解除失敗', 'error');
        }
      } catch (err) {
        showToast(err.message || '解除失敗', 'error');
      }
    },
    // 開啟快速綁定 Modal
    openQuickBind(student) {
      this.targetStudent = student;
      this.quickBindDisplayName = student.name || '學員';
      this.quickBindUserId = '';
      this.showQuickBindModal = true;
    },
    async submitQuickBind() {
      if (!this.targetStudent) return;
      const displayName = this.quickBindDisplayName.trim() || this.targetStudent.name || 'LINE 用戶';
      const userId = this.quickBindUserId.trim() || ('Utest' + Math.random().toString(36).substring(2, 12) + Date.now().toString(36));

      this.quickBindLoading = true;
      try {
        const res = await api.post('/student/line/bind', {
          student_id: this.targetStudent.id,
          line_user_id: userId,
          line_display_name: displayName,
          line_picture_url: `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(displayName)}`
        });

        if (res.success) {
          showToast(res.message || 'LINE 關聯成功！', 'success');
          this.showQuickBindModal = false;
          this.fetchStudents();
        } else {
          showToast(res.error || res.message || '關聯失敗', 'error');
        }
      } catch (err) {
        showToast(err.message || '關聯失敗', 'error');
      } finally {
        this.quickBindLoading = false;
      }
    },
    // 開啟 LINE 整合設定 Modal
    async openLineSettingsModal() {
      this.showLineSettingsModal = true;
      try {
        const res = await api.get('/admin/settings/line');
        if (res.success && res.settings) {
          this.lineConfig = {
            line_login_enabled: res.settings.line_login_enabled,
            line_channel_id: res.settings.line_channel_id || '',
            line_channel_secret: res.settings.line_channel_secret || '',
            line_official_id: res.settings.line_official_id || '',
            line_official_url: res.settings.line_official_url || ''
          };
        }
      } catch (err) {
        console.error('取得 LINE 設定失敗:', err);
      }
    },
    async saveLineConfig() {
      this.savingLineConfig = true;
      try {
        const res = await api.post('/admin/settings/line', this.lineConfig);
        if (res.success) {
          showToast('LINE 串接設定已成功更新！', 'success');
          this.showLineSettingsModal = false;
        } else {
          showToast(res.message || '儲存設定失敗', 'error');
        }
      } catch (err) {
        showToast(err.message || '儲存設定失敗', 'error');
      } finally {
        this.savingLineConfig = false;
      }
    },
    copyCallbackUrl() {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(this.callbackUrl)
          .then(() => showToast('已複製 Callback URL 至剪貼簿！', 'success'))
          .catch(() => showToast('複製失敗，請手動複製', 'warning'));
      } else {
        showToast('請手動選取並複製網址', 'info');
      }
    }
  }
};
</script>

<style scoped>
.students {
  padding: 10px;
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
}
.modal-dialog-custom {
  width: 100%;
  max-width: 480px;
}
.modal-content-custom {
  background: #ffffff;
  border-radius: 0.75rem;
  overflow: hidden;
}
</style>
