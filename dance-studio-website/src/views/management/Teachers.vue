<template>
  <div class="teachers">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>{{ isTeacher ? '老師列表 (我的資料)' : '老師列表' }}</h2>
      <div class="d-flex" v-if="!isTeacher">
        <input
          type="text"
          v-model="searchQuery"
          @keyup.enter="fetchTeachers"
          placeholder="搜尋老師姓名"
          class="form-control me-2"
        />
        <button @click="fetchTeachers" class="btn btn-outline-secondary text-nowrap">
          <i class="bi bi-search me-1"></i>搜尋
        </button>
        <button v-if="isAdmin" @click="openCreate" class="btn btn-success ms-2 text-nowrap">
          <i class="bi bi-plus-lg me-1"></i>新增老師
        </button>
      </div>
    </div>

    <!-- 老師身分提示橫幅 -->
    <div v-if="isTeacher" class="alert alert-info py-2 small mb-3">
      <i class="bi bi-person-check-fill me-1"></i>
      您好，<strong>{{ adminAuth.currentUser?.name }}</strong>！您在此可查看與修改您本人的<strong>後台登入帳號、密碼及匯款銀行帳號</strong>。
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入老師資料...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button @click="fetchTeachers" class="btn btn-outline-danger btn-sm">重新嘗試</button>
    </div>

    <!-- 空資料狀態 -->
    <div v-else-if="teachers.length === 0" class="text-center py-5 text-muted">
      <p>找不到符合條件的老師資料。</p>
    </div>

    <!-- 表格內容 -->
    <div v-else class="table-responsive">
      <table class="table table-hover table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col" class="text-center" style="width: 75px;">大頭貼</th>
            <th scope="col">姓名</th>
            <th scope="col">後台帳號</th>
            <th scope="col" class="text-center" style="width: 130px;">密碼修改</th>
            <th scope="col">銀行帳號</th>
            <th scope="col">電話</th>
            <th scope="col">電子郵件</th>
            <th scope="col">專長舞風</th>
            <th scope="col" class="text-center" style="width: 110px;">本月主打星</th>
            <th scope="col" class="text-center" style="width: 140px;">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="teacher in teachers" :key="teacher.id">
            <td class="text-center">
              <div 
                class="teacher-avatar-btn position-relative d-inline-block" 
                @click="openAvatarModal(teacher)"
                title="點擊更換大頭貼"
                role="button"
              >
                <img 
                  v-if="teacher.avatar_url" 
                  :src="teacher.avatar_url" 
                  :alt="teacher.name" 
                  class="rounded-circle object-fit-cover shadow-sm teacher-avatar-img border"
                />
                <div v-else class="rounded-circle bg-light text-secondary d-flex align-items-center justify-content-center border shadow-sm teacher-avatar-placeholder">
                  <i class="bi bi-person-fill fs-5"></i>
                </div>
                <span class="avatar-badge bg-primary text-white position-absolute bottom-0 end-0 rounded-circle d-flex align-items-center justify-content-center shadow-sm">
                  <i class="bi bi-camera-fill" style="font-size: 10px;"></i>
                </span>
              </div>
            </td>
            <td class="fw-bold">
              {{ teacher.name }}
              <span v-if="adminAuth.currentUser?.teacher_id === teacher.id" class="badge bg-primary ms-1">本人</span>
            </td>
            <td>
              <span v-if="teacher.account_username" class="badge bg-dark-subtle text-dark border font-monospace">
                <i class="bi bi-person-badge me-1"></i>@{{ teacher.account_username }}
              </span>
              <span v-else class="badge bg-secondary-subtle text-muted border">
                <i class="bi bi-dash-circle me-1"></i>未設定帳號
              </span>
            </td>
            <td class="text-center">
              <button 
                class="btn btn-sm btn-outline-warning text-dark text-nowrap" 
                @click="openAccountModal(teacher)"
                title="修改或設定登入密碼"
              >
                <i class="bi bi-key-fill text-warning me-1"></i>修改密碼
              </button>
            </td>
            <td>
              <div class="d-flex align-items-center justify-content-between">
                <span v-if="teacher.bank_account" class="fw-semibold text-secondary small">
                  <i class="bi bi-bank me-1 text-primary"></i>{{ teacher.bank_account }}
                </span>
                <span v-else class="text-muted small fst-italic">未填寫</span>
                <button 
                  class="btn btn-sm btn-link text-primary p-0 ms-2 text-decoration-none" 
                  @click="openAccountModal(teacher)" 
                  title="修改銀行帳號與密碼"
                >
                  <i class="bi bi-pencil-square"></i>
                </button>
              </div>
            </td>
            <td>{{ teacher.phone || '-' }}</td>
            <td>{{ teacher.email || '-' }}</td>
            <td>
              <div v-if="teacher.styles && teacher.styles.length > 0" class="d-flex flex-wrap gap-1">
                <span v-for="style in teacher.styles" :key="style.id" class="badge bg-info text-dark">
                  {{ style.name }}
                </span>
              </div>
              <span v-else class="text-muted small">無專長舞風</span>
            </td>
            <td class="text-center">
              <button
                v-if="isAdmin"
                type="button"
                class="btn btn-sm rounded-pill px-2 py-1 fw-bold shadow-sm"
                :class="teacher.is_featured ? 'btn-warning text-dark border-warning' : 'btn-outline-secondary'"
                @click="toggleFeatured(teacher)"
                :title="teacher.is_featured ? '點擊取消主打星' : '點擊設為本月主打星'"
              >
                <i :class="teacher.is_featured ? 'bi bi-star-fill text-dark' : 'bi bi-star'"></i>
                <span class="ms-1 small">{{ teacher.is_featured ? '主打星' : '設為' }}</span>
              </button>
              <span v-else class="badge" :class="teacher.is_featured ? 'bg-warning text-dark' : 'bg-light text-muted border'">
                {{ teacher.is_featured ? '⭐ 主打星' : '-' }}
              </span>
            </td>
            <td class="text-center">
              <button @click="openEdit(teacher.id)" class="btn btn-primary btn-sm me-1">編輯</button>
              <button v-if="isAdmin" @click="deleteTeacher(teacher.id)" class="btn btn-danger btn-sm">刪除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 老師帳號、密碼與銀行帳號修改 Modal -->
    <div v-if="showAccountModal" class="modal-backdrop fade show"></div>
    <div v-if="showAccountModal" class="modal fade show d-block" tabindex="-1" role="dialog">
      <div class="modal-dialog">
        <div class="modal-content shadow-lg border-0 rounded-4">
          <div class="modal-header bg-dark text-white">
            <h5 class="modal-title fw-bold">
              <i class="bi bi-shield-lock-fill text-warning me-2"></i>帳號、密碼與銀行帳號修改
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="closeAccountModal"></button>
          </div>
          <form @submit.prevent="submitAccountForm">
            <div class="modal-body p-4">
              <div class="alert alert-light border small mb-3">
                正在設定 <strong>{{ selectedTeacher?.name }}</strong> 的後台登入帳號、密碼及匯款銀行帳號。
              </div>

              <!-- 登入帳號 -->
              <div class="mb-3">
                <label class="form-label fw-semibold">後台登入帳號：</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-person-badge"></i></span>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="accountForm.username" 
                    required 
                    placeholder="請輸入後台登入帳號，例如 teacher" 
                  />
                </div>
              </div>

              <!-- 密碼 -->
              <div class="mb-3">
                <label class="form-label fw-semibold">設定新密碼：</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-key"></i></span>
                  <input 
                    :type="showPassword ? 'text' : 'password'" 
                    class="form-control" 
                    v-model="accountForm.password" 
                    placeholder="請輸入新密碼 (不修改請留空)" 
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

              <!-- 確認密碼 -->
              <div class="mb-3" v-if="accountForm.password">
                <label class="form-label fw-semibold">再次確認新密碼：</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-check2-circle"></i></span>
                  <input 
                    :type="showPassword ? 'text' : 'password'" 
                    class="form-control" 
                    v-model="accountForm.confirmPassword" 
                    placeholder="請再次輸入新密碼" 
                  />
                </div>
              </div>

              <!-- 銀行帳號 -->
              <div class="mb-3">
                <label class="form-label fw-semibold">銀行帳號 (匯款資訊)：</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-bank"></i></span>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="accountForm.bank_account" 
                    placeholder="例如: (822 中國信託) 123-540-123456" 
                  />
                </div>
                <div class="form-text small">供師資鐘點費結算匯款使用</div>
              </div>
            </div>

            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary" @click="closeAccountModal">取消</button>
              <button type="submit" class="btn btn-primary fw-bold" :disabled="submittingAccount">
                <span v-if="submittingAccount" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-check-lg me-1"></i>儲存更新
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 老師大頭貼上傳 Modal -->
    <div v-if="showAvatarModal" class="modal-backdrop fade show"></div>
    <div v-if="showAvatarModal" class="modal fade show d-block" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content shadow-lg border-0 rounded-4">
          <div class="modal-header bg-dark text-white">
            <h5 class="modal-title fw-bold">
              <i class="bi bi-image text-warning me-2"></i>更換老師大頭貼
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="closeAvatarModal"></button>
          </div>
          <div class="modal-body p-4 text-center">
            <h5 class="fw-bold mb-3">{{ avatarTeacher?.name }} 老師</h5>

            <!-- 大頭貼預覽 -->
            <div class="avatar-preview-box mx-auto mb-3 position-relative rounded-circle shadow border overflow-hidden">
              <img 
                v-if="avatarPreviewUrl" 
                :src="avatarPreviewUrl" 
                alt="預覽大頭貼" 
                class="w-100 h-100 object-fit-cover"
              />
              <div v-else class="w-100 h-100 bg-light text-secondary d-flex flex-column align-items-center justify-content-center">
                <i class="bi bi-person-bounding-box fs-1 mb-1 text-muted"></i>
                <span class="small text-muted">尚未設定大頭貼</span>
              </div>
            </div>

            <!-- 上傳方式切換與按鈕 -->
            <div class="d-flex flex-column gap-2 mb-3">
              <input 
                type="file" 
                ref="avatarFileInput" 
                class="d-none" 
                accept="image/png, image/jpeg, image/jpg, image/webp, image/gif" 
                @change="onAvatarFileChanged" 
              />
              <button 
                type="button" 
                class="btn btn-outline-primary fw-semibold" 
                @click="$refs.avatarFileInput.click()"
                :disabled="uploadingAvatar"
              >
                <i class="bi bi-cloud-arrow-up-fill me-1"></i>從電腦選擇圖片上傳
              </button>

              <div class="text-muted small my-1">─ 或直接輸入外部圖片網址 ─</div>
              
              <div class="input-group input-group-sm">
                <span class="input-group-text"><i class="bi bi-link-45deg"></i></span>
                <input 
                  type="url" 
                  class="form-control" 
                  v-model="avatarInputUrl" 
                  placeholder="https://example.com/photo.jpg" 
                  @input="onAvatarUrlInput"
                />
              </div>
            </div>

            <div v-if="avatarSelectedFile" class="alert alert-info py-2 small mb-0 text-start">
              <i class="bi bi-file-earmark-image me-1"></i>已選取檔案：<strong>{{ avatarSelectedFile.name }}</strong> ({{ (avatarSelectedFile.size / 1024).toFixed(1) }} KB)
            </div>
          </div>

          <div class="modal-footer bg-light d-flex justify-content-between">
            <button 
              type="button" 
              class="btn btn-outline-danger btn-sm" 
              v-if="avatarTeacher?.avatar_url || avatarPreviewUrl"
              @click="handleRemoveAvatar"
              :disabled="uploadingAvatar"
            >
              <i class="bi bi-trash3 me-1"></i>移除大頭貼
            </button>
            <div v-else></div>

            <div class="d-flex gap-2">
              <button type="button" class="btn btn-secondary" @click="closeAvatarModal" :disabled="uploadingAvatar">取消</button>
              <button 
                type="button" 
                class="btn btn-primary fw-bold" 
                @click="handleSaveAvatar" 
                :disabled="uploadingAvatar || (!avatarSelectedFile && avatarInputUrl === (avatarTeacher?.avatar_url || ''))"
              >
                <span v-if="uploadingAvatar" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-check-lg me-1"></i>儲存變更
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bootstrap Modal for adding/editing teacher -->
    <div class="modal fade" id="editTeacherModal" tabindex="-1" aria-labelledby="editTeacherModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editTeacherModalLabel">{{ editingId ? '編輯老師' : '新增老師' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <AddTeacher
              v-if="showForm"
              :teacherId="editingId"
              @teacher-updated="handleTeacherUpdated"
              @close-modal="closeModal"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api, { API_ENDPOINTS } from '@/utils/api';
import AddTeacher from '../forms/AddTeacher.vue';
import { useCrudModal } from '@/composables/useCrudModal';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';
import { useAdminAuth } from '@/utils/adminAuth';

export default {
  name: 'Teachers',
  components: {
    AddTeacher
  },
  setup() {
    const { showForm, editingId, initModal, openCreate, openEdit, closeModal } = useCrudModal('editTeacherModal');
    return { showForm, editingId, initModal, openCreate, openEdit, closeModal };
  },
  data() {
    return {
      adminAuth: useAdminAuth(),
      teachers: [],
      searchQuery: '',
      loading: false,
      error: null,
      showAccountModal: false,
      selectedTeacher: null,
      showPassword: false,
      submittingAccount: false,
      accountForm: {
        username: '',
        password: '',
        confirmPassword: '',
        bank_account: ''
      },
      showAvatarModal: false,
      avatarTeacher: null,
      avatarPreviewUrl: '',
      avatarInputUrl: '',
      avatarSelectedFile: null,
      uploadingAvatar: false
    };
  },
  computed: {
    isAdmin() {
      return this.adminAuth.currentRole === 'admin';
    },
    isTeacher() {
      return this.adminAuth.currentRole === 'teacher';
    },
    myTeacherId() {
      return this.adminAuth.currentUser?.teacher_id || null;
    }
  },
  mounted() {
    this.initModal();
  },
  created() {
    this.fetchTeachers();
  },
  methods: {
    async fetchTeachers() {
      this.loading = true;
      this.error = null;
      try {
        let endpoint = API_ENDPOINTS.TEACHERS;
        const params = new URLSearchParams();

        // 若為授課老師身分，只查詢並只顯示自己
        if (this.isTeacher && this.myTeacherId) {
          params.append('teacher_id', this.myTeacherId);
        } else if (this.searchQuery.trim()) {
          params.append('name', this.searchQuery.trim());
        }

        const queryString = params.toString();
        if (queryString) {
          endpoint += `?${queryString}`;
        }

        const data = await api.get(endpoint);
        let list = data.teachers || [];

        // 前端二次防護：若為老師身分，強制只保留屬於該老師本人的紀錄
        if (this.isTeacher) {
          if (this.myTeacherId) {
            list = list.filter(t => t.id === this.myTeacherId);
          } else if (this.adminAuth.currentUser?.username) {
            list = list.filter(t => t.account_username === this.adminAuth.currentUser.username);
          }
        }

        this.teachers = list;
      } catch (err) {
        console.error('獲取老師列表失敗:', err);
        this.error = '獲取老師列表失敗，請稍後再試。';
      } finally {
        this.loading = false;
      }
    },
    async toggleFeatured(teacher) {
      try {
        const res = await api.post(`/teachers/${teacher.id}/toggle-featured`);
        teacher.is_featured = res.is_featured ? 1 : 0;
        showToast(res.message || '更新主打星狀態成功！', 'success');
      } catch (err) {
        showToast('更新主打星失敗', 'error');
      }
    },
    openAccountModal(teacher) {
      this.selectedTeacher = teacher;
      this.accountForm = {
        username: teacher.account_username || `teacher_${teacher.id}`,
        password: '',
        confirmPassword: '',
        bank_account: teacher.bank_account || ''
      };
      this.showPassword = false;
      this.showAccountModal = true;
    },
    closeAccountModal() {
      this.showAccountModal = false;
      this.selectedTeacher = null;
    },
    async submitAccountForm() {
      if (this.accountForm.password && this.accountForm.password !== this.accountForm.confirmPassword) {
        showToast('兩次輸入的新密碼不相符，請確認！', 'error');
        return;
      }
      this.submittingAccount = true;
      try {
        await api.put(`/teachers/${this.selectedTeacher.id}/account`, {
          username: this.accountForm.username,
          password: this.accountForm.password,
          bank_account: this.accountForm.bank_account
        });
        showToast(`已成功更新 ${this.selectedTeacher.name} 的帳號與資料！`, 'success');
        this.closeAccountModal();
        this.fetchTeachers();
      } catch (err) {
        showToast(err.message || '更新失敗，請稍後重試', 'error');
      } finally {
        this.submittingAccount = false;
      }
    },
    async deleteTeacher(id) {
      const confirmed = await showConfirm('確定要刪除這位老師嗎？');
      if (!confirmed) return;

      try {
        await api.delete(`${API_ENDPOINTS.TEACHERS}/${id}`);
        showToast('老師已成功刪除！', 'success');
        this.fetchTeachers();
      } catch (err) {
        console.error('刪除老師失敗:', err);
        showToast('刪除老師失敗，請重試。', 'error');
      }
    },
    handleTeacherUpdated() {
      this.fetchTeachers();
      this.closeModal();
    },
    openAvatarModal(teacher) {
      this.avatarTeacher = teacher;
      this.avatarPreviewUrl = teacher.avatar_url || '';
      this.avatarInputUrl = teacher.avatar_url || '';
      this.avatarSelectedFile = null;
      this.showAvatarModal = true;
    },
    closeAvatarModal() {
      this.showAvatarModal = false;
      this.avatarTeacher = null;
      this.avatarPreviewUrl = '';
      this.avatarInputUrl = '';
      this.avatarSelectedFile = null;
    },
    onAvatarFileChanged(event) {
      const file = event.target.files?.[0];
      if (!file) return;
      if (!file.type.startsWith('image/')) {
        showToast('請選取有效的圖片檔案 (JPG, PNG, WEBP, GIF)！', 'error');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        showToast('圖片大小不得超過 10MB！', 'error');
        return;
      }
      this.avatarSelectedFile = file;
      this.avatarPreviewUrl = URL.createObjectURL(file);
    },
    onAvatarUrlInput() {
      this.avatarSelectedFile = null;
      this.avatarPreviewUrl = this.avatarInputUrl.trim();
    },
    async handleSaveAvatar() {
      if (!this.avatarTeacher) return;
      this.uploadingAvatar = true;
      try {
        if (this.avatarSelectedFile) {
          const formData = new FormData();
          formData.append('file', this.avatarSelectedFile);
          await api.post(`/teachers/${this.avatarTeacher.id}/avatar`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          showToast('大頭貼上傳成功！', 'success');
          this.closeAvatarModal();
          this.fetchTeachers();
        } else if (this.avatarInputUrl.trim()) {
          await api.post(`/teachers/${this.avatarTeacher.id}/avatar`, {
            avatar_url: this.avatarInputUrl.trim()
          });
          showToast('大頭貼更新成功！', 'success');
          this.closeAvatarModal();
          this.fetchTeachers();
        }
      } catch (err) {
        showToast(err.message || '大頭貼上傳失敗，請重試', 'error');
      } finally {
        this.uploadingAvatar = false;
      }
    },
    async handleRemoveAvatar() {
      if (!this.avatarTeacher) return;
      const confirmed = await showConfirm(`確定要移除 ${this.avatarTeacher.name} 老師的大頭貼嗎？`);
      if (!confirmed) return;
      this.uploadingAvatar = true;
      try {
        await api.delete(`/teachers/${this.avatarTeacher.id}/avatar`);
        showToast('大頭貼已成功移除！', 'success');
        this.closeAvatarModal();
        this.fetchTeachers();
      } catch (err) {
        showToast(err.message || '移除大頭貼失敗', 'error');
      } finally {
        this.uploadingAvatar = false;
      }
    }
  }
};
</script>

<style scoped>
.teachers {
  padding: 10px;
}
.teacher-avatar-btn {
  width: 44px;
  height: 44px;
  cursor: pointer;
  transition: transform 0.15s ease-in-out;
}
.teacher-avatar-btn:hover {
  transform: scale(1.08);
}
.teacher-avatar-img, .teacher-avatar-placeholder {
  width: 44px;
  height: 44px;
}
.avatar-badge {
  width: 17px;
  height: 17px;
  border: 1.5px solid #fff;
}
.avatar-preview-box {
  width: 120px;
  height: 120px;
}
</style>
