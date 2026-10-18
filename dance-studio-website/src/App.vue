<template>
  <div id="app">
    <!-- Splash Screen -->
    <Transition name="fade">
      <div v-if="showSplash" class="splash-screen">
        <img src="/favicon.ico" alt="Dance Studio Logo" class="splash-logo">
      </div>
    </Transition>

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top" aria-label="主導航列">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/">Dance Studio</router-link>
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
          <ul class="navbar-nav">
            <li v-for="link in navLinks" :key="link.to" class="nav-item">
              <router-link class="nav-link" :to="link.to" @click="closeNavbar">
                {{ link.label }}
              </router-link>
            </li>
          </ul>
        </div>
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
            <p class="mb-0">地址：402台中市南區工學路169號2樓</p>
            <p class="mb-0">電話：(02) 1234-5678</p>
          </div>
        </div>
      </div>
    </footer>

    <!-- Global UI Components -->
    <ConfirmModal />
    <AppToast />
  </div>
</template>

<script>
import { Collapse } from 'bootstrap'
import ConfirmModal from './components/ConfirmModal.vue'
import AppToast from './components/AppToast.vue'

export default {
  name: 'App',
  components: { ConfirmModal, AppToast },
  data() {
    return {
      showSplash: true,
      navLinks: [
        { to: '/', label: '首頁' },
        { to: '/about', label: '關於我們' },
        { to: '/history', label: '歷史' },
        { to: '/instructors', label: '師資介紹' },
        { to: '/schedule', label: '課程表' },
        { to: '/pricing', label: '費用' },
        { to: '/gallery', label: '畫廊' },
        { to: '/venue', label: '場地' },
        { to: '/faq', label: '常見問題' },
        { to: '/contact', label: '聯絡我們' },
      ]
    }
  },
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  },
  methods: {
    closeNavbar() {
      const navbarNav = this.$refs.navbarNav
      if (navbarNav && navbarNav.classList.contains('show')) {
        const collapse = Collapse.getOrCreateInstance(navbarNav)
        collapse.hide()
      }
    }
  },
  mounted() {
    // Shorter splash - dismiss after 1.2s (was 2.5s)
    setTimeout(() => {
      this.showSplash = false
    }, 1200)
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
  width: 150px;
  height: 150px;
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

/* Content layout - prevents content from hiding behind fixed navbar */
.content-wrapper {
  padding-top: 70px;
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
