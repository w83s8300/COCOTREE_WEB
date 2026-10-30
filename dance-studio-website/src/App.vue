<template>
  <div id="app">
    <!-- Splash Screen -->
    <Transition name="fade">
      <div v-if="showSplash" class="splash-screen">
        <img
          :src="currentSplashImage"
          alt="Dance Studio Logo"
          class="splash-logo"
        />
      </div>
    </Transition>

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top" aria-label="主導航列">
      <div class="container-fluid">
        <router-link class="navbar-brand d-flex align-items-center" to="/">
          <template v-if="logoSettings.logo_type === 'image' && logoSettings.logo_image">
            <img
              :src="logoSettings.logo_image"
              :alt="logoSettings.logo_text || 'Dance Studio Logo'"
              class="navbar-logo-img"
              style="max-height: 40px; width: auto; object-fit: contain;"
            />
          </template>
          <template v-else>
            <span class="fw-bold">{{ logoSettings.logo_text || 'Dance Studio' }}</span>
          </template>
        </router-link>

        <!-- 管理後台模式：僅顯示返回前台按鈕，不顯示前台漢堡選單與學員登入，避免手機版出現兩個選單按鈕 -->
        <div v-if="isAdminRoute" class="d-flex align-items-center ms-auto">
          <router-link to="/" class="btn btn-outline-light btn-sm rounded-pill px-3 py-1">
            <i class="bi bi-arrow-left me-1"></i>回官網首頁
          </router-link>
        </div>

        <!-- 一般前台模式：顯示學員登入/會員註冊 與 導航欄 -->
        <template v-else>
          <!-- 學員登入 / 狀態選單 (置於右上角，無論手機或電腦皆直接顯示) -->
          <div class="d-flex align-items-center order-lg-last ms-auto ms-lg-3 me-2 me-lg-0">
            <!-- 未登入狀態（合併為單一按鈕） -->
            <div v-if="!isLoggedIn" class="d-flex align-items-center">
              <button
                class="btn btn-outline-light btn-sm d-flex align-items-center px-3 rounded-pill shadow-sm"
                @click="openLoginModal"
              >
                <i class="bi bi-person-circle me-1"></i>
                <span><span class="d-none d-sm-inline">學員</span>登入 / 註冊</span>
              </button>
            </div>

            <!-- 已登入狀態 -->
            <div v-else class="dropdown position-relative" ref="userDropdownWrapper">
              <button
                class="btn btn-primary btn-sm dropdown-toggle d-flex align-items-center px-3 shadow-sm"
                type="button"
                @click.stop="toggleUserDropdown"
              >
                <i class="bi bi-person-circle me-1"></i>
                <span class="fw-bold">{{ currentStudent?.name }}</span>
                <span class="badge bg-light text-primary ms-2 fw-bold">{{ currentStudent?.remaining_classes ?? 0 }} 堂</span>
              </button>
              <ul
                class="dropdown-menu dropdown-menu-end shadow"
                :class="{ show: userDropdownOpen }"
                style="position: absolute; right: 0; left: auto; min-width: 220px;"
              >
                <li class="px-3 py-2 border-bottom bg-light">
                  <div class="small text-muted">目前登入學員</div>
                  <div class="fw-bold text-dark fs-6">{{ currentStudent?.name }}</div>
                  <div class="small text-primary fw-bold">剩餘：{{ currentStudent?.remaining_classes ?? 0 }} 堂課</div>
                </li>
                <li>
                  <a class="dropdown-item py-2" href="javascript:void(0)" @click="openProfileModal">
                    <i class="bi bi-person-vcard me-2 text-primary"></i>會員中心 / 預約紀錄
                  </a>
                </li>
                <li><hr class="dropdown-divider my-1"></li>
                <li>
                  <a class="dropdown-item py-2 text-danger" href="javascript:void(0)" @click="handleLogout">
                    <i class="bi bi-box-arrow-right me-2"></i>登出帳號
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <button
            ref="navbarToggler"
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="切換導航"
          >
            <span class="navbar-toggler-icon"></span>
          </button>

          <div ref="navbarNav" class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
              <li v-for="link in navLinks" :key="link.to" class="nav-item">
                <router-link class="nav-link" :to="link.to" @click="closeNavbar">
                  {{ link.label }}
                </router-link>
              </li>
            </ul>
          </div>
        </template>
      </div>
    </nav>

    <main class="content-wrapper">
      <router-view />
    </main>

    <footer class="footer bg-dark text-white py-4">
      <div class="container">
        <div class="row">
          <div class="col-md-6 text-center text-md-start">
            <p>&copy; {{ currentYear }} Dance Studio. All rights reserved.</p>
            <div class="social-icons mb-3 mb-md-0">
              <a href="#" class="text-white me-3" aria-label="Facebook"><i class="bi bi-facebook"></i></a>
              <a href="#" class="text-white me-3" aria-label="Instagram"><i class="bi bi-instagram"></i></a>
              <a href="#" class="text-white" aria-label="YouTube"><i class="bi bi-youtube"></i></a>
            </div>
          </div>
          <div class="col-md-6 text-center text-md-end">
            <p class="mb-1">地址：402台中市南區工學路169號2樓</p>
            <p class="mb-0">電話：(02) 1234-5678</p>
          </div>
        </div>
      </div>
    </footer>

    <!-- Global UI Components -->
    <ConfirmModal />
    <AppToast />
    <StudentLoginModal />
    <StudentProfileModal />
  </div>
</template>

<script>
import { Collapse } from 'bootstrap'
import ConfirmModal from './components/ConfirmModal.vue'
import AppToast from './components/AppToast.vue'
import StudentLoginModal from './components/StudentLoginModal.vue'
import StudentProfileModal from './components/StudentProfileModal.vue'
import { useStudentAuth } from './utils/auth'
import { showToast } from './utils/toast'
import api from './utils/api'

export default {
  name: 'App',
  components: {
    ConfirmModal,
    AppToast,
    StudentLoginModal,
    StudentProfileModal
  },
  data() {
    return {
      showSplash: true,
      auth: useStudentAuth(),
      userDropdownOpen: false,
      logoSettings: {
        logo_type: 'text',
        logo_text: 'Dance Studio',
        logo_image: '',
        splash_image: ''
      },
      navLinks: [
        { to: '/', label: '首頁' },
        { to: '/about', label: '關於我們' },
        { to: '/history', label: '歷史' },
        { to: '/instructors', label: '師資介紹' },
        { to: '/schedule', label: '報名課程' },
        { to: '/pricing', label: '費用' },
        { to: '/gallery', label: '活動花絮' },
        { to: '/venue', label: '場地' },
        { to: '/faq', label: '常見問題' },
        { to: '/contact', label: '聯絡我們' },
      ]
    }
  },
  computed: {
    currentYear() {
      return new Date().getFullYear()
    },
    isAdminRoute() {
      return this.$route.path.startsWith('/admin')
    },
    isLoggedIn() {
      return !!this.auth.state.student && !!this.auth.state.student.id
    },
    currentStudent() {
      return this.auth.state.student
    },
    currentSplashImage() {
      if (this.logoSettings.splash_image) {
        return this.logoSettings.splash_image
      }
      if (this.logoSettings.logo_type === 'image' && this.logoSettings.logo_image) {
        return this.logoSettings.logo_image
      }
      return '/favicon.ico'
    }
  },
  methods: {
    closeNavbar() {
      const navbarNav = this.$refs.navbarNav
      if (navbarNav && navbarNav.classList.contains('show')) {
        const collapse = Collapse.getOrCreateInstance(navbarNav)
        collapse.hide()
      }
      this.userDropdownOpen = false
    },
    toggleUserDropdown() {
      this.userDropdownOpen = !this.userDropdownOpen
    },
    openLoginModal() {
      this.closeNavbar()
      this.auth.openLoginModal('login')
    },
    openRegisterModal() {
      this.closeNavbar()
      this.auth.openRegisterModal()
    },
    openProfileModal() {
      this.userDropdownOpen = false
      this.closeNavbar()
      this.auth.openProfileModal()
    },
    handleLogout() {
      this.userDropdownOpen = false
      this.closeNavbar()
      this.auth.logout()
      showToast('已成功登出', 'info')
    },
    handleClickOutside(e) {
      if (this.userDropdownOpen && this.$refs.userDropdownWrapper && !this.$refs.userDropdownWrapper.contains(e.target)) {
        this.userDropdownOpen = false
      }
    },
    async fetchLogoSettings() {
      try {
        const res = await api.get('/site-settings/logo')
        if (res && (res.success || res.logo_type)) {
          this.logoSettings = {
            logo_type: res.logo_type || 'text',
            logo_text: res.logo_text || 'Dance Studio',
            logo_image: res.logo_image || '',
            splash_image: res.splash_image || ''
          }
        }
      } catch (err) {
        // 載入失敗使用預設文字
      }
    },
    onLogoSettingsUpdated(e) {
      if (e?.detail) {
        this.logoSettings = { ...this.logoSettings, ...e.detail }
      }
    }
  },
  mounted() {
    this.fetchLogoSettings()
    window.addEventListener('logo-settings-updated', this.onLogoSettingsUpdated)

    // Shorter splash - dismiss after 1.2s (was 2.5s)
    setTimeout(() => {
      this.showSplash = false
    }, 1200)

    document.addEventListener('click', this.handleClickOutside)

    // Automatically refresh student profile if logged in
    if (this.isLoggedIn) {
      this.auth.refreshProfile()
    }
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
    window.removeEventListener('logo-settings-updated', this.onLogoSettingsUpdated)
  }
}
</script>

<style>
/* Splash Screen */
.splash-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.splash-logo {
  max-width: 200px;
  max-height: 200px;
  width: auto;
  height: auto;
  object-fit: contain;
  animation: pulse 1.5s infinite alternate;
}

@keyframes pulse {
  from { transform: scale(1); }
  to { transform: scale(1.1); }
}

/* Vue Transition for splash */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.8s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Content layout - seamlessly attaches to fixed navbar without white gap */
.content-wrapper {
  padding-top: 56px;
  min-height: calc(100vh - 220px);
}

.footer {
  margin-top: auto;
}

.social-icons a {
  font-size: 1.5rem;
  transition: opacity 0.3s;
}

.social-icons a:hover {
  opacity: 0.7;
}
</style>
