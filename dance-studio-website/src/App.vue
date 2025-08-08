<template>
  <div id="app">
    <!-- Splash Screen -->
    <div v-if="showSplash" :class="{'splash-screen': true, 'hidden': hideSplash}">
      <img src="/favicon.ico" alt="Logo" class="splash-logo">
    </div>

    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
      <div class="container-fluid">
        <a class="navbar-brand" href="./">Dance Studio</a>
        <button ref="navbarToggler" class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div ref="navbarNav" class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" to="/" @click="closeNavbar">首頁</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/about" @click="closeNavbar">關於我們</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/history" @click="closeNavbar">歷史</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/instructors" @click="closeNavbar">師資介紹</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/schedule" @click="closeNavbar">課程表</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/pricing" @click="closeNavbar">費用</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/gallery" @click="closeNavbar">畫廊</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/venue" @click="closeNavbar">場地</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/faq" @click="closeNavbar">常見問題</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/contact" @click="closeNavbar">聯絡我們</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin" @click="closeNavbar">管理</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <main class="content-wrapper">
      <router-view/>
    </main>

    <footer class="footer bg-dark text-white py-4">
      <div class="container">
        <div class="row">
          <div class="col-md-6 text-center text-md-start">
            <p>&copy; 2024 Dance Studio. All rights reserved.</p>
            <div class="social-icons mb-3 mb-md-0">
              <a href="#" class="text-white me-3"><i class="bi bi-facebook"></i></a>
              <a href="#" class="text-white me-3"><i class="bi bi-instagram"></i></a>
              <a href="#" class="text-white"><i class="bi bi-youtube"></i></a>
            </div>
          </div>
          <div class="col-md-6 text-center text-md-end">
            <p class="mb-0">地址：402台中市南區工學路169號2樓</p>
            <p class="mb-0">電話：(02) 1234-5678</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      showSplash: true,
      hideSplash: false,
    };
  },
  methods: {
    closeNavbar() {
      // Check if the navbar collapse element is currently shown
      if (this.$refs.navbarNav.classList.contains('show')) {
        // Programmatically click the toggler button to close the navbar
        this.$refs.navbarToggler.click();
      }
    },
  },
  mounted() {
    // Hide splash screen after a delay
    setTimeout(() => {
      this.hideSplash = true;
      setTimeout(() => {
        this.showSplash = false;
      }, 1000); // Corresponds to CSS transition
    }, 1500); // Show splash for 1.5s
  },
};
</script>

<style>
/* Global styles for App.vue */
.splash-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #000; /* Black background */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; /* Ensure it's on top of everything */
  transition: opacity 1s ease-out; /* Fade out animation duration */
}

.splash-screen.hidden {
  opacity: 0;
  pointer-events: none; /* Disable interactions after fading out */
}

.splash-logo {
  width: 150px; /* Adjust size as needed */
  height: 150px;
  animation: pulse 1.5s infinite alternate; /* Simple pulse animation for the logo */
}

@keyframes pulse {
  from { transform: scale(1); }
  to { transform: scale(1.1); }
}

/* Add padding to content to prevent it from being hidden behind fixed navbar */
.content-wrapper {
  padding-top: 70px; /* Adjust this value based on your navbar's actual height */
  min-height: calc(100vh - 70px - 150px); /* Adjust 150px based on actual footer height */
}

.footer {
  /* Add any specific styles for the footer here */
  /* For example, to push it to the bottom if content is short */
  margin-top: auto; /* Pushes the footer to the bottom */
}

.social-icons a {
  font-size: 1.5rem;
}
</style>
