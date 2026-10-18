<template>
  <div class="admin-layout container-fluid px-0">
    <!-- 行動版側邊欄開關按鈕 -->
    <div class="d-md-none p-3 bg-light border-bottom d-flex justify-content-between align-items-center">
      <span class="fw-bold">後台管理系統</span>
      <button class="btn btn-sm btn-outline-dark" @click="isSidebarOpen = !isSidebarOpen">
        <i class="bi bi-list"></i> 選單
      </button>
    </div>

    <div class="d-flex">
      <aside class="sidebar bg-light border-end" :class="{ 'd-none d-md-block': !isSidebarOpen }">
        <div class="p-3">
          <h5 class="sidebar-title mb-4 text-center fw-bold">管理選單</h5>
          <nav aria-label="管理選單導航">
            <ul class="nav nav-pills flex-column mb-auto">
              <li class="nav-item mb-2" v-for="item in navItems" :key="item.to">
                <router-link
                  :to="item.to"
                  class="nav-link text-dark"
                  active-class="active text-white"
                  @click="isSidebarOpen = false"
                >
                  <i :class="item.icon" class="me-2"></i>{{ item.label }}
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
export default {
  name: 'Admin',
  data() {
    return {
      isSidebarOpen: false,
      navItems: [
        { to: '/admin/students', label: '學生管理', icon: 'bi bi-people' },
        { to: '/admin/teachers', label: '老師管理', icon: 'bi bi-person-badge' },
        { to: '/admin/courses', label: '課程管理', icon: 'bi bi-journal-bookmark' },
        { to: '/admin/schedules', label: '課程時間表', icon: 'bi bi-calendar3' },
        { to: '/admin/rooms', label: '教室管理', icon: 'bi bi-door-open' },
        { to: '/admin/styles', label: '舞風管理', icon: 'bi bi-music-note-beamed' }
      ]
    };
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
  border-radius: 6px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.nav-link:hover:not(.active) {
  background-color: #e9ecef;
}

.nav-link.active {
  background-color: #0d6efd;
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
