
import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';

import Admin from '../views/Admin.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue')
  },
  {
    path: '/instructors',
    name: 'Instructors',
    component: () => import('../views/Instructors.vue')
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('../views/Gallery.vue')
  },
  {
    path: '/venue',
    name: 'Venue',
    component: () => import('../views/Venue.vue')
  },
  {
    path: '/faq',
    name: 'Faq',
    component: () => import('../views/Faq.vue')
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/Contact.vue')
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: () => import('../views/Pricing.vue')
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('../views/Schedule.vue')
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    children: [
      {
        path: 'add-student/:id?',
        name: 'AddStudent',
        component: () => import('../views/AddStudent.vue')
      },
      {
        path: 'styles',
        name: 'Styles',
        component: () => import('../views/Styles.vue')
      },
      {
        path: 'add-teacher/:id?',
        name: 'AddTeacher',
        component: () => import('../views/AddTeacher.vue')
      },
      {
        path: 'teachers',
        name: 'Teachers',
        component: () => import('../views/Teachers.vue')
      },
      {
        path: 'students',
        name: 'Students',
        component: () => import('../views/Students.vue')
      },
      {
        path: 'add-course/:id?',
        name: 'AddCourse',
        component: () => import('../views/AddCourse.vue')
      },
      {
        path: 'add-room',
        name: 'AddRoom',
        component: () => import('../views/AddRoom.vue')
      },
      {
        path: 'rooms',
        name: 'Rooms',
        component: () => import('../views/Rooms.vue')
      },
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('../views/Courses.vue')
      },
      {
        path: 'add-schedule',
        name: 'AddSchedule',
        component: () => import('../views/AddSchedule.vue')
      },
      {
        path: 'schedules',
        name: 'Schedules',
        component: () => import('../views/Schedules.vue')
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
