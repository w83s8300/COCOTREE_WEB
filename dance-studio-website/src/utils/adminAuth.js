import { reactive, computed } from 'vue'
import api from '@/utils/api'

const ADMIN_STORAGE_KEY = 'admin_user'
const ADMIN_TOKEN_KEY = 'admin_token'

function loadSavedAdmin() {
  try {
    const raw = localStorage.getItem(ADMIN_STORAGE_KEY)
    const token = localStorage.getItem(ADMIN_TOKEN_KEY)
    if (!token) return null
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
    '/admin/finance',
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
    '/admin/finance',
    '/admin/banners',
    '/admin/attendance',
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
    '/admin/teacher-attendance',
    '/admin/schedules',
    '/admin/teachers'
  ]
}

export const useAdminAuth = () => {
  const setUser = (userData, token = null) => {
    state.user = userData
    try {
      if (userData) {
        localStorage.setItem(ADMIN_STORAGE_KEY, JSON.stringify(userData))
        if (token) {
          localStorage.setItem(ADMIN_TOKEN_KEY, token)
        }
      } else {
        localStorage.removeItem(ADMIN_STORAGE_KEY)
        localStorage.removeItem(ADMIN_TOKEN_KEY)
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
      setUser(res.user, res.token)
      return res.user
    }
    throw new Error(res.error || '登入失敗')
  }

  const canAccess = (path) => {
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
      return !!state.user && !!state.user.id && !!localStorage.getItem(ADMIN_TOKEN_KEY)
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
      return state.user?.role === 'admin' || state.user?.role === 'teacher'
    },
    setUser,
    logout,
    login,
    canAccess,
    getFirstAllowedRoute
  }
}
