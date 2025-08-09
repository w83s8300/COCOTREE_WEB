// 更新後的路由配置 - 支援模組化 views 結構
import { createRouter, createWebHistory } from 'vue-router';

// 公開頁面導入
import Home from '../views/public/Home.vue';

// 管理功能主頁面
import Admin from '../views/management/Admin.vue';

const routes = [
  // === 公開頁面路由 ===
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/public/About.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/public/History.vue')
  },
  {
    path: '/instructors',
    name: 'Instructors',
    component: () => import('../views/public/Instructors.vue')
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('../views/public/Gallery.vue')
  },
  {
    path: '/venue',
    name: 'Venue',
    component: () => import('../views/public/Venue.vue')
  },
  {
    path: '/faq',
    name: 'Faq',
    component: () => import('../views/public/Faq.vue')
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/public/Contact.vue')
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: () => import('../views/public/Pricing.vue')
  },
  
  // === 學生功能路由 ===
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('../views/student/Schedule.vue')
  },
  
  // === 管理功能路由 ===
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    children: [
      // 學生管理
      {
        path: 'students',
        name: 'Students',
        component: () => import('../views/management/Students.vue')
      },
      {
        path: 'add-student/:id?',
        name: 'AddStudent',
        component: () => import('../views/forms/AddStudent.vue')
      },
      
      // 老師管理
      {
        path: 'teachers',
        name: 'Teachers',
        component: () => import('../views/management/Teachers.vue')
      },
      {
        path: 'add-teacher/:id?',
        name: 'AddTeacher',
        component: () => import('../views/forms/AddTeacher.vue')
      },
      
      // 課程管理
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('../views/management/Courses.vue')
      },
      {
        path: 'add-course/:id?',
        name: 'AddCourse',
        component: () => import('../views/forms/AddCourse.vue')
      },
      
      // 教室管理
      {
        path: 'rooms',
        name: 'Rooms',
        component: () => import('../views/management/Rooms.vue')
      },
      {
        path: 'add-room',
        name: 'AddRoom',
        component: () => import('../views/forms/AddRoom.vue')
      },
      
      // 風格管理
      {
        path: 'styles',
        name: 'Styles',
        component: () => import('../views/management/Styles.vue')
      },
      {
        path: 'add-style/:id?',
        name: 'AddStyle',
        component: () => import('../views/forms/AddStyle.vue')
      },
      
      // 排程管理
      {
        path: 'schedules',
        name: 'Schedules',
        component: () => import('../views/management/Schedules.vue')
      },
      {
        path: 'add-schedule',
        name: 'AddSchedule',
        component: () => import('../views/forms/AddSchedule.vue')
      }
    ]
  }
];

const router = createRouter({
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
  history: createWebHistory(),
  routes
});

export default router;
