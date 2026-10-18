<template>
  <div class="admin-layout container-fluid px-0">
    <!-- 行動版側邊欄開關按鈕 -->
    <div class="d-md-none p-3 bg-light border-bottom d-flex justify-content-between align-items-center">
      <div>
        <span class="fw-bold me-2">{{ adminAuth.currentUser?.name }}</span>
        <span class="badge" :class="adminAuth.roleBadgeClass">{{ adminAuth.roleLabel }}</span>
      </div>
      <div>
        <button class="btn btn-sm btn-outline-dark me-1" @click="isSidebarOpen = !isSidebarOpen">
          <i class="bi bi-list"></i> 選單
        </button>
        <button class="btn btn-sm btn-outline-danger" @click="handleLogout" title="登出">
          <i class="bi bi-box-arrow-right"></i>
        </button>
      </div>
    </div>

    <div class="d-flex">
      <aside class="sidebar bg-light border-end" :class="{ 'd-none d-md-block': !isSidebarOpen }">
        <div class="p-3">
          <!-- 使用者身分資訊 -->
          <div class="user-card mb-4 p-3 bg-white rounded-3 border shadow-sm text-center">
            <div class="fs-4 mb-1">
              <span v-if="adminAuth.currentRole === 'admin'">👑</span>
              <span v-else-if="adminAuth.currentRole === 'teacher'">💃</span>
              <span v-else>🛎️</span>
            </div>
            <h6 class="fw-bold mb-1 text-dark">{{ adminAuth.currentUser?.name }}</h6>
            <div class="mb-2">
              <span class="badge" :class="adminAuth.roleBadgeClass">{{ adminAuth.roleLabel }}</span>
            </div>
            <div class="small text-muted mb-2 font-monospace">@{{ adminAuth.currentUser?.username }}</div>
            <!-- 櫃檯客服資訊：時薪與銀行帳號 -->
            <div v-if="adminAuth.currentRole === 'desk' && (adminAuth.currentUser?.hourly_rate || adminAuth.currentUser?.bank_account)" class="mb-3 p-2 bg-light rounded text-start small border">
              <div v-if="adminAuth.currentUser?.hourly_rate > 0" class="mb-1 text-secondary">
                <i class="bi bi-clock-history me-1 text-primary"></i>時薪: <strong class="text-dark">NT$ {{ adminAuth.currentUser.hourly_rate }}/時</strong>
              </div>
              <div v-if="adminAuth.currentUser?.bank_account" class="text-secondary text-truncate" :title="adminAuth.currentUser.bank_account">
                <i class="bi bi-bank me-1 text-success"></i>帳號: {{ adminAuth.currentUser.bank_account }}
              </div>
            </div>
            <button class="btn btn-outline-danger btn-sm w-100" @click="handleLogout">
              <i class="bi bi-box-arrow-right me-1"></i>登出後台
            </button>
          </div>

          <h6 class="sidebar-title mb-3 px-2 text-muted fw-bold text-uppercase small">
            <i class="bi bi-grid-fill me-1"></i>管理選單 ({{ filteredNavItems.length }})
          </h6>

          <nav aria-label="管理選單導航">
            <ul class="nav nav-pills flex-column mb-auto">
              <li class="nav-item mb-2" v-for="item in filteredNavItems" :key="item.to">
                <router-link
                  :to="item.to"
                  class="nav-link text-dark d-flex align-items-center"
                  active-class="active text-white"
                  @click="isSidebarOpen = false"
                >
                  <i :class="item.icon" class="me-2 fs-5"></i>
                  <span>{{ item.label }}</span>
                </router-link>
              </li>
            </ul>
          </nav>
        </div>
      </aside>

      <main class="main-content flex-grow-1 p-4">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script>
import { useAdminAuth } from '@/utils/adminAuth';
import { showToast } from '@/utils/toast';

export default {
  name: 'Admin',
  data() {
    return {
      adminAuth: useAdminAuth(),
      isSidebarOpen: false,
      allNavItems: [
        { to: '/admin/attendance', label: '上下班打卡', icon: 'bi bi-clock-history' },
        { to: '/admin/teacher-attendance', label: '上課下課打卡', icon: 'bi bi-person-video3' },
        { to: '/admin/schedules', label: '課程時間表', icon: 'bi bi-calendar3' },
        { to: '/admin/students', label: '學生列表', icon: 'bi bi-people' },
        { to: '/admin/courses', label: '課程管理', icon: 'bi bi-journal-bookmark' },
        { to: '/admin/teachers', label: '老師列表', icon: 'bi bi-person-badge' },
        { to: '/admin/rooms', label: '教室管理', icon: 'bi bi-door-open' },
        { to: '/admin/styles', label: '舞風管理', icon: 'bi bi-music-note-beamed' },
        { to: '/admin/users', label: '權限帳號管理', icon: 'bi bi-shield-lock' }
      ]
    };
  },
  computed: {
    filteredNavItems() {
      return this.allNavItems.filter(item => this.adminAuth.canAccess(item.to));
    }
  },
  methods: {
    handleLogout() {
      this.adminAuth.logout();
      showToast('您已成功登出管理後台', 'info');
      this.$router.push('/admin/login');
    }
  }
};
</script>

<style scoped>
.admin-layout {
  min-height: calc(100vh - 70px);
}

.sidebar {
  width: 250px;
  min-height: calc(100vh - 70px);
  position: sticky;
  top: 70px;
}

.nav-link {
  border-radius: 8px;
  transition: all 0.2s ease;
  font-weight: 500;
  padding: 10px 14px;
}

.nav-link:hover:not(.active) {
  background-color: #e9ecef;
}

.nav-link.active {
  background-color: #0d6efd;
  box-shadow: 0 4px 10px rgba(13, 110, 253, 0.25);
}

.main-content {
  min-width: 0;
  background-color: #fff;
}

@media (max-width: 767.98px) {
  .sidebar {
    position: fixed;
    top: 120px;
    left: 0;
    z-index: 1040;
    width: 260px;
    height: calc(100vh - 120px);
    box-shadow: 4px 0 10px rgba(0, 0, 0, 0.1);
  }
}
</style>
