<template>
  <div class="admin-layout container-fluid px-0">
    <!-- 行動版背景遮罩 (點擊背景可關閉選單) -->
    <div
      v-if="isSidebarOpen"
      class="sidebar-backdrop d-md-none"
      @click="closeSidebar"
    ></div>

    <!-- 行動版管理快捷置頂列 (固定在Navbar下方，滾動頁面時保持置頂可見) -->
    <div class="admin-mobile-header d-md-none px-3 py-2 bg-light border-bottom d-flex justify-content-between align-items-center">
      <div class="d-flex align-items-center">
        <button
          class="btn btn-dark btn-sm me-2 d-flex align-items-center px-3 shadow-sm"
          @click="toggleSidebar"
          aria-label="開啟管理選單"
        >
          <i class="bi bi-list fs-5 me-1"></i>
          <span class="fw-bold">後台選單</span>
        </button>
        <span class="badge" :class="adminAuth.roleBadgeClass">{{ adminAuth.roleLabel }}</span>
      </div>
      <div class="d-flex align-items-center">
        <span class="small fw-semibold text-muted me-2 text-truncate" style="max-width: 100px;">
          {{ adminAuth.currentUser?.name }}
        </span>
        <button class="btn btn-sm btn-outline-danger" @click="handleLogout" title="登出後台">
          <i class="bi bi-box-arrow-right"></i>
        </button>
      </div>
    </div>

    <div class="d-flex position-relative">
      <!-- 側邊選單：電腦版為常駐側邊欄，手機版為抽屜式滑動側邊選單 -->
      <aside
        class="sidebar bg-light border-end"
        :class="{ 'is-open': isSidebarOpen }"
        aria-label="管理後台選單"
      >
        <div class="p-3 sidebar-inner">
          <!-- 行動版專用頂部關閉列 -->
          <div class="d-md-none d-flex justify-content-between align-items-center pb-3 mb-3 border-bottom">
            <div class="d-flex align-items-center">
              <span class="fs-4 me-2">🎭</span>
              <span class="fw-bold fs-6 text-dark">後台管理選單</span>
            </div>
            <button
              type="button"
              class="btn-close"
              aria-label="關閉選單"
              @click="closeSidebar"
            ></button>
          </div>

          <!-- 使用者身分資訊卡片 -->
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
                  @click="closeSidebar"
                >
                  <i :class="item.icon" class="me-2 fs-5"></i>
                  <span>{{ item.label }}</span>
                  <span v-if="item.badge" class="badge bg-warning text-dark ms-auto small fw-bold">{{ item.badge }}</span>
                </router-link>
              </li>
            </ul>
          </nav>
        </div>
      </aside>

      <main class="main-content flex-grow-1 p-3 p-md-4">
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
        { to: '/admin/schedules', label: '課程時間表', icon: 'bi bi-calendar3' },
        { to: '/admin/teacher-attendance', label: '老師授課打卡', icon: 'bi bi-person-video3' },
        { to: '/admin/attendance', label: '上下班打卡 (櫃檯)', icon: 'bi bi-clock-history' },
        { to: '/admin/students', label: '學生列表', icon: 'bi bi-people' },
        { to: '/admin/courses', label: '課程管理', icon: 'bi bi-journal-bookmark' },
        { to: '/admin/teachers', label: '老師列表', icon: 'bi bi-person-badge' },
        { to: '/admin/pricing', label: '課程價目表管理', icon: 'bi bi-tags' },
        { to: '/admin/news', label: '消息與活動管理', icon: 'bi bi-newspaper' },
        { to: '/admin/gallery', label: '活動花絮管理', icon: 'bi bi-images' },
        { to: '/admin/banners', label: 'LOGO與橫幅管理', icon: 'bi bi-card-image', badge: '全站' },
        { to: '/admin/rooms', label: '教室管理', icon: 'bi bi-door-open' },
        { to: '/admin/styles', label: '舞風管理', icon: 'bi bi-music-note-beamed' },
        { to: '/admin/line-settings', label: 'LINE 整合設定', icon: 'bi bi-line' },
        { to: '/admin/users', label: '權限帳號管理', icon: 'bi bi-shield-lock' }
      ]
    };
  },
  computed: {
    filteredNavItems() {
      return this.allNavItems.filter(item => {
        // 若為系統管理員或尚未登入，全數顯示
        if (!this.adminAuth?.isLoggedIn || this.adminAuth?.currentRole === 'admin') return true;
        return this.adminAuth.canAccess(item.to);
      });
    }
  },
  watch: {
    isSidebarOpen(val) {
      if (typeof window !== 'undefined' && window.innerWidth < 768) {
        if (val) {
          document.body.style.overflow = 'hidden';
        } else {
          document.body.style.overflow = '';
        }
      }
    },
    $route() {
      // 路由改變時關閉行動版側邊欄
      this.closeSidebar();
    }
  },
  methods: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen;
    },
    closeSidebar() {
      this.isSidebarOpen = false;
      if (typeof document !== 'undefined') {
        document.body.style.overflow = '';
      }
    },
    handleLogout() {
      this.closeSidebar();
      this.adminAuth.logout();
      showToast('您已成功登出管理後台', 'info');
      this.$router.push('/admin/login');
    },
    handleKeyDown(e) {
      if (e.key === 'Escape' && this.isSidebarOpen) {
        this.closeSidebar();
      }
    }
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeyDown);
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeyDown);
    if (typeof document !== 'undefined') {
      document.body.style.overflow = '';
    }
  }
};
</script>

<style scoped>
.admin-layout {
  min-height: calc(100vh - 70px);
}

/* 行動版快捷置頂列：黏貼在頂部導航列 (70px) 下方，頁面滾動時保持置頂 */
.admin-mobile-header {
  position: sticky;
  top: 70px;
  z-index: 1020;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

/* 電腦版常駐側邊欄 */
.sidebar {
  width: 250px;
  min-width: 250px;
  height: calc(100vh - 70px);
  position: sticky;
  top: 70px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.sidebar-inner {
  padding-bottom: 5rem;
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

/* 行動版抽屜式側邊選單與遮罩 */
@media (max-width: 767.98px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 290px;
    max-width: 85vw;
    height: 100%;
    height: 100vh;
    height: 100dvh;
    z-index: 1045;
    background-color: #f8f9fa !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.28);
    transform: translateX(-100%);
    transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    overflow-y: auto !important;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
    overscroll-behavior: contain;
  }

  .sidebar.is-open {
    transform: translateX(0);
  }

  .sidebar-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    height: 100vh;
    height: 100dvh;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 1040;
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(2px);
  }
}
</style>
