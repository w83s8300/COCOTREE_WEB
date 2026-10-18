<template>
  <div class="users-management">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>後台員工與權限帳號管理</h2>
      <button class="btn btn-success" @click="openCreateModal">
        <i class="bi bi-person-plus-fill me-1"></i>新增員工帳號
      </button>
    </div>

    <div class="alert alert-info py-2 small">
      <i class="bi bi-info-circle-fill me-1"></i>
      系統提供三種身分權限：<strong>管理員 (Admin)</strong>、<strong>櫃檯 (Desk)</strong>、<strong>老師 (Teacher)</strong>。不同權限登入後將顯示專屬管理選單。
    </div>

    <!-- 列表 -->
    <div class="card border-0 shadow-sm rounded-3">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th scope="col">ID</th>
              <th scope="col">登入帳號</th>
              <th scope="col">姓名</th>
              <th scope="col">權限角色</th>
              <th scope="col">時薪 (元/時)</th>
              <th scope="col">匯款銀行帳號</th>
              <th scope="col">關聯老師</th>
              <th scope="col">聯絡電話</th>
              <th scope="col" class="text-center" style="width: 140px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>#{{ u.id }}</td>
              <td class="fw-bold">{{ u.username }}</td>
              <td>{{ u.name }}</td>
              <td>
                <span class="badge" :class="getRoleBadge(u.role)">
                  {{ getRoleName(u.role) }}
                </span>
              </td>
              <td>
                <span v-if="u.hourly_rate > 0" class="fw-semibold text-primary">
                  NT$ {{ u.hourly_rate }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>
                <span v-if="u.bank_account" class="font-monospace small">
                  {{ u.bank_account }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td>{{ u.teacher_name || '-' }}</td>
              <td>{{ u.phone || '-' }}</td>
              <td class="text-center">
                <div class="d-flex justify-content-center gap-1">
                  <button 
                    @click="openEditModal(u)" 
                    class="btn btn-sm btn-outline-primary"
                    title="編輯員工帳號"
                  >
                    編輯
                  </button>
                  <button 
                    v-if="u.id !== 1" 
                    @click="deleteUser(u)" 
                    class="btn btn-sm btn-outline-danger"
                    title="刪除帳號"
                  >
                    刪除
                  </button>
                  <span v-else class="badge bg-secondary-subtle text-secondary border d-inline-flex align-items-center">預設</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新增 / 編輯帳號 Modal -->
    <div v-if="showModal" class="modal-backdrop fade show"></div>
    <div v-if="showModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">
              <i class="bi me-2" :class="isEditMode ? 'bi-pencil-square text-primary' : 'bi-person-plus-fill text-success'"></i>
              {{ isEditMode ? '編輯員工帳號' : '新增後台員工帳號' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <form @submit.prevent="submitUser">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label fw-semibold">登入帳號：</label>
                <input type="text" class="form-control" v-model="form.username" required placeholder="例如: staff01" />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">登入密碼：</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="form.password" 
                  :required="!isEditMode" 
                  :placeholder="isEditMode ? '留空表示不修改密碼' : '請設定登入密碼'" 
                />
                <div v-if="isEditMode" class="form-text">若不需修改密碼，保留空白即可</div>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">真實姓名：</label>
                <input type="text" class="form-control" v-model="form.name" required placeholder="例如: 王小明" />
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">權限角色：</label>
                <select class="form-select" v-model="form.role" required :disabled="isEditMode && editingUserId === 1">
                  <option value="desk">櫃檯客服 (可管理學生、課表、報名加學生，不顯示師資鐘點費)</option>
                  <option value="teacher">授課老師 (可查看課表點名、授課鐘點費試算、老師列表維護個人帳號密碼與銀行帳號)</option>
                  <option value="admin">系統管理員 (全權限開放)</option>
                </select>
                <div v-if="isEditMode && editingUserId === 1" class="form-text text-muted">系統最高管理員固定為管理員角色</div>
              </div>

              <!-- 櫃檯客服與一般員工薪資與匯款帳號 -->
              <div v-if="form.role === 'desk' || form.role === 'admin'" class="p-3 bg-light rounded-3 mb-3 border">
                <h6 class="fw-bold mb-2 text-dark small">
                  <i class="bi bi-cash-stack me-1 text-success"></i>
                  {{ form.role === 'desk' ? '櫃檯客服薪資與銀行帳號' : '員工薪資與銀行帳號' }}
                </h6>
                <div class="row g-2">
                  <div class="col-md-6">
                    <label class="form-label fw-semibold small">時薪 (元/小時)：</label>
                    <div class="input-group input-group-sm">
                      <span class="input-group-text">$</span>
                      <input 
                        type="number" 
                        class="form-control" 
                        v-model.number="form.hourly_rate" 
                        min="0" 
                        step="10" 
                        placeholder="例如: 200" 
                      />
                      <span class="input-group-text">/時</span>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label fw-semibold small">匯款銀行帳號：</label>
                    <input 
                      type="text" 
                      class="form-control form-control-sm" 
                      v-model="form.bank_account" 
                      placeholder="銀行代碼與帳號" 
                    />
                  </div>
                </div>
              </div>

              <div class="mb-3" v-if="form.role === 'teacher'">
                <label class="form-label fw-semibold">關聯師資名冊：</label>
                <select class="form-select" v-model="form.teacher_id">
                  <option :value="null">-- 未指定 (通用老師) --</option>
                  <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.name }}</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label fw-semibold">聯絡電話 (選填)：</label>
                <input type="text" class="form-control" v-model="form.phone" placeholder="例如: 0912345678" />
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
                {{ isEditMode ? '儲存變更' : '確認建立' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api, { API_ENDPOINTS } from '@/utils/api';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';
import { useAdminAuth } from '@/utils/adminAuth';

export default {
  name: 'Users',
  data() {
    return {
      adminAuth: useAdminAuth(),
      users: [],
      teachers: [],
      showModal: false,
      isEditMode: false,
      editingUserId: null,
      submitting: false,
      form: {
        username: '',
        password: '',
        name: '',
        role: 'desk',
        phone: '',
        hourly_rate: 0,
        bank_account: '',
        teacher_id: null
      }
    };
  },
  created() {
    this.fetchUsers();
    this.fetchTeachers();
  },
  methods: {
    getRoleName(role) {
      switch (role) {
        case 'admin': return '管理員';
        case 'desk': return '櫃檯';
        case 'teacher': return '老師';
        default: return role;
      }
    },
    getRoleBadge(role) {
      switch (role) {
        case 'admin': return 'bg-danger';
        case 'desk': return 'bg-success';
        case 'teacher': return 'bg-primary';
        default: return 'bg-secondary';
      }
    },
    openCreateModal() {
      this.isEditMode = false;
      this.editingUserId = null;
      this.form = {
        username: '',
        password: '',
        name: '',
        role: 'desk',
        phone: '',
        hourly_rate: 0,
        bank_account: '',
        teacher_id: null
      };
      this.showModal = true;
    },
    openEditModal(u) {
      this.isEditMode = true;
      this.editingUserId = u.id;
      this.form = {
        username: u.username,
        password: '',
        name: u.name,
        role: u.role,
        phone: u.phone || '',
        hourly_rate: u.hourly_rate ?? 0,
        bank_account: u.bank_account || '',
        teacher_id: u.teacher_id || null
      };
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.editingUserId = null;
    },
    async fetchUsers() {
      try {
        const res = await api.get('/admin/users');
        if (res.success) {
          this.users = res.users || [];
        }
      } catch (err) {
        console.error('獲取使用者失敗:', err);
      }
    },
    async fetchTeachers() {
      try {
        const res = await api.get(API_ENDPOINTS.TEACHERS);
        this.teachers = res.teachers || [];
      } catch (err) {
        console.error('獲取老師清單失敗:', err);
      }
    },
    async submitUser() {
      this.submitting = true;
      try {
        if (this.isEditMode) {
          const res = await api.put(`/admin/users/${this.editingUserId}`, this.form);
          if (res.success) {
            showToast(res.message || '更新成功！', 'success');
            // 若修改的是當前登入者，同步狀態
            if (this.adminAuth.currentUser?.id === this.editingUserId) {
              this.adminAuth.setUser({
                ...this.adminAuth.currentUser,
                username: this.form.username,
                name: this.form.name,
                role: this.form.role,
                phone: this.form.phone,
                hourly_rate: this.form.hourly_rate,
                bank_account: this.form.bank_account,
                teacher_id: this.form.teacher_id
              });
            }
            this.closeModal();
            this.fetchUsers();
          }
        } else {
          const res = await api.post('/admin/users', this.form);
          if (res.success) {
            showToast(res.message || '新增成功！', 'success');
            this.closeModal();
            this.fetchUsers();
          }
        }
      } catch (err) {
        showToast(err.message || (this.isEditMode ? '更新失敗' : '新增失敗'), 'error');
      } finally {
        this.submitting = false;
      }
    },
    async deleteUser(u) {
      const ok = await showConfirm(`確定要刪除帳號【${u.name} (${u.username})】嗎？`);
      if (!ok) return;
      try {
        const res = await api.delete(`/admin/users/${u.id}`);
        if (res.success) {
          showToast('帳號已刪除', 'success');
          this.fetchUsers();
        }
      } catch (err) {
        showToast(err.message || '刪除失敗', 'error');
      }
    }
  }
};
</script>

<style scoped>
.users-management {
  padding: 10px;
}
</style>

