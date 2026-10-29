import { reactive, computed } from 'vue'
import api from '@/utils/api'

const ADMIN_STORAGE_KEY = 'admin_user'

function loadSavedAdmin() {
  try {
    const raw = localStorage.getItem(ADMIN_STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (e) {
    return null
  }
}

const state = reactive({
  user: loadSavedAdmin()
})

// 定義各權限可進入的路由
const ROLE_PERMISSIONS = {
  admin: [
    '/admin/banners',
    '/admin/attendance',
    '/admin/teacher-attendance',
    '/admin/schedules',
    '/admin/students',
    '/admin/courses',
    '/admin/teachers',
    '/admin/rooms',
    '/admin/styles',
    '/admin/users',
    '/admin/news',
    '/admin/pricing',
    '/admin/gallery',
    '/admin/line-settings'
  ],
  desk: [
    '/admin/banners',
    '/admin/attendance',
    '/admin/teacher-attendance',
    '/admin/schedules',
    '/admin/students',
    '/admin/courses',
    '/admin/rooms',
    '/admin/news',
    '/admin/pricing',
    '/admin/gallery',
    '/admin/line-settings'
  ],
  teacher: [
    '/admin/banners',
    '/admin/teacher-attendance',
    '/admin/schedules',
    '/admin/teachers'
  ]
}

export const useAdminAuth = () => {
  const setUser = (userData) => {
    state.user = userData
    try {
      if (userData) {
        localStorage.setItem(ADMIN_STORAGE_KEY, JSON.stringify(userData))
      } else {
        localStorage.removeItem(ADMIN_STORAGE_KEY)
      }
    } catch (e) {
      console.error('儲存後台使用者資料失敗:', e)
    }
  }

  const logout = () => {
    setUser(null)
  }

  const login = async (username, password) => {
    const res = await api.post('/admin/login', { username, password })
    if (res.success && res.user) {
      setUser(res.user)
      return res.user
    }
    throw new Error(res.error || '登入失敗')
  }

  const canAccess = (path) => {
    if (path.startsWith('/admin/banners')) return true
    if (!state.user || !state.user.role) return true
    if (state.user.role === 'admin') return true
    const allowed = ROLE_PERMISSIONS[state.user.role] || []
    return allowed.some(route => path.startsWith(route))
  }

  const getFirstAllowedRoute = () => {
    if (!state.user || !state.user.role) return '/admin/login'
    const allowed = ROLE_PERMISSIONS[state.user.role] || []
    return allowed[0] || '/admin/schedules'
  }

  return {
    state,
    get isLoggedIn() {
      return !!state.user && !!state.user.id
    },
    get currentUser() {
      return state.user
    },
    get currentRole() {
      return state.user?.role || ''
    },
    get roleLabel() {
      switch (state.user?.role) {
        case 'admin':
          return '系統管理員'
        case 'desk':
          return '櫃檯客服'
        case 'teacher':
          return '授課老師'
        default:
          return '訪客'
      }
    },
    get roleBadgeClass() {
      switch (state.user?.role) {
        case 'admin':
          return 'bg-danger'
        case 'desk':
          return 'bg-success'
        case 'teacher':
          return 'bg-primary'
        default:
          return 'bg-secondary'
      }
    },
    get canViewSalary() {
      // 只有管理員 (admin) 與老師 (teacher) 可查看師資授課鐘點費，櫃檯客服 (desk) 不顯示
      return state.user?.role === 'admin' || state.user?.role === 'teacher';
    },
    setUser,
    logout,
    login,
    canAccess,
    getFirstAllowedRoute
  }
}

