import { createRouter, createWebHistory } from 'vue-router'
import { useAdminAuth } from '@/utils/adminAuth'

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
    path: '/line-callback',
    name: 'LineCallback',
    component: () => import('../views/public/LineCallback.vue'),
    meta: { title: 'LINE 登入驗證 - Dance Studio' }
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('../views/student/Schedule.vue'),
    meta: { title: '報名課程 - Dance Studio' }
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/management/AdminLogin.vue'),
    meta: { title: '後台登入 - Dance Studio' }
  },
  {
    path: '/admin',
    component: () => import('../views/management/Admin.vue'),
    meta: { title: '管理後台 - Dance Studio' },
    children: [
      {
        path: '',
        name: 'AdminRoot',
        redirect: () => {
          const adminAuth = useAdminAuth();
          return adminAuth.isLoggedIn ? adminAuth.getFirstAllowedRoute() : '/admin/login';
        }
      },
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
      },
      {
        path: 'attendance',
        name: 'Attendance',
        component: () => import('../views/management/Attendance.vue'),
        meta: { title: '上下班打卡 - Dance Studio' }
      },
      {
        path: 'teacher-attendance',
        name: 'TeacherAttendance',
        component: () => import('../views/management/TeacherAttendance.vue'),
        meta: { title: '上課下課打卡 - Dance Studio' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/management/Users.vue'),
        meta: { title: '權限帳號管理 - Dance Studio' }
      },
      {
        path: 'news',
        name: 'News',
        component: () => import('../views/management/News.vue'),
        meta: { title: '最新消息管理 - Dance Studio' }
      },
      {
        path: 'banners',
        name: 'BannerManagement',
        component: () => import('../views/management/BannerManagement.vue'),
        meta: { title: '首頁橫幅管理 - Dance Studio' }
      },
      {
        path: 'pricing',
        name: 'PricingManagement',
        component: () => import('../views/management/PricingManagement.vue'),
        meta: { title: '課程價目表管理 - Dance Studio' }
      },
      {
        path: 'line-settings',
        name: 'LineSettings',
        component: () => import('../views/management/LineSettings.vue'),
        meta: { title: 'LINE 整合設定 - Dance Studio' }
      },
      {
        path: 'gallery',
        name: 'GalleryManagement',
        component: () => import('../views/management/GalleryManagement.vue'),
        meta: { title: '活動花絮管理 - Dance Studio' }
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

// 後台管理權限與登入守衛 (Navigation Guard)
router.beforeEach((to, from, next) => {
  if (to.path.startsWith('/admin')) {
    const adminAuth = useAdminAuth();

    // 1. 若訪問登入頁
    if (to.path === '/admin/login') {
      if (adminAuth.isLoggedIn) {
        // 已登入則自動轉導至其權限可訪問之首頁
        return next(adminAuth.getFirstAllowedRoute());
      }
      return next();
    }

    // 2. 訪問其他後台頁面，未登入一律轉至登入頁
    if (!adminAuth.isLoggedIn) {
      return next('/admin/login');
    }

    // 3. 已登入但訪問 /admin 根路徑
    if (to.path === '/admin' || to.path === '/admin/') {
      return next(adminAuth.getFirstAllowedRoute());
    }

    // 4. 檢查該身分是否有訪問此子路由之權限
    if (!adminAuth.canAccess(to.path)) {
      return next(adminAuth.getFirstAllowedRoute());
    }

    return next();
  }

  next();
});

// Dynamic document title
router.afterEach((to) => {
  document.title = to.meta.title || 'Dance Studio'
})

export default router
