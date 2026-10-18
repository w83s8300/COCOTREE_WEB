import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/public/Home.vue'),
    meta: { title: '首頁 - Dance Studio' }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/public/About.vue'),
    meta: { title: '關於我們 - Dance Studio' }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/public/History.vue'),
    meta: { title: '品牌沿革 - Dance Studio' }
  },
  {
    path: '/instructors',
    name: 'Instructors',
    component: () => import('../views/public/Instructors.vue'),
    meta: { title: '師資介紹 - Dance Studio' }
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('../views/public/Gallery.vue'),
    meta: { title: '活動花絮 - Dance Studio' }
  },
  {
    path: '/venue',
    name: 'Venue',
    component: () => import('../views/public/Venue.vue'),
    meta: { title: '場地租借 - Dance Studio' }
  },
  {
    path: '/faq',
    name: 'Faq',
    component: () => import('../views/public/Faq.vue'),
    meta: { title: '常見問題 - Dance Studio' }
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/public/Contact.vue'),
    meta: { title: '聯絡我們 - Dance Studio' }
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: () => import('../views/public/Pricing.vue'),
    meta: { title: '課程價目表 - Dance Studio' }
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('../views/student/Schedule.vue'),
    meta: { title: '課程表 - Dance Studio' }
  },
  {
    path: '/admin',
    component: () => import('../views/management/Admin.vue'),
    redirect: '/admin/students',
    meta: { title: '管理後台 - Dance Studio' },
    children: [
      {
        path: 'students',
        name: 'Students',
        component: () => import('../views/management/Students.vue'),
        meta: { title: '學生管理 - Dance Studio' }
      },
      {
        path: 'teachers',
        name: 'Teachers',
        component: () => import('../views/management/Teachers.vue'),
        meta: { title: '老師管理 - Dance Studio' }
      },
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('../views/management/Courses.vue'),
        meta: { title: '課程管理 - Dance Studio' }
      },
      {
        path: 'schedules',
        name: 'Schedules',
        component: () => import('../views/management/Schedules.vue'),
        meta: { title: '課程時間表 - Dance Studio' }
      },
      {
        path: 'rooms',
        name: 'Rooms',
        component: () => import('../views/management/Rooms.vue'),
        meta: { title: '教室管理 - Dance Studio' }
      },
      {
        path: 'styles',
        name: 'Styles',
        component: () => import('../views/management/Styles.vue'),
        meta: { title: '風格管理 - Dance Studio' }
      }
    ]
  },
  // 404 catch-all route
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: '找不到頁面 - Dance Studio' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

// Dynamic document title
router.afterEach((to) => {
  document.title = to.meta.title || 'Dance Studio'
})

export default router
