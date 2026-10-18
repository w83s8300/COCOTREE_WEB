import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Bootstrap CSS + selective JS modules (not the entire bundle)
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/js/dist/modal'
import 'bootstrap/js/dist/collapse'
import 'bootstrap/js/dist/carousel'
import 'bootstrap/js/dist/dropdown'
import 'bootstrap/js/dist/tab'

import './assets/css/app.css'

// AOS scroll animations
import AOS from 'aos'
import 'aos/dist/aos.css'

// Note: VCalendar is NOT registered globally anymore.
// It should be imported locally in components that need it (e.g., student/Schedule.vue).

const app = createApp(App)
app.use(router)
app.mount('#app')

// Initialize AOS with performance-friendly defaults
AOS.init({
  offset: 120,
  delay: 0,
  duration: 1000,
  easing: 'ease',
  once: true, // Changed: animate only once for better performance
  mirror: false,
})

// Re-trigger AOS on route changes (fixes animations not working after SPA navigation)
router.afterEach(() => {
  setTimeout(() => AOS.refresh(), 300)
})