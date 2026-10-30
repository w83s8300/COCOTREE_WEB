import { reactive, computed } from 'vue'
import api from '@/utils/api'

const STORAGE_KEY = 'student_user'
const STUDENT_TOKEN_KEY = 'student_token'

function loadSavedStudent() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (e) {
    return null
  }
}

const state = reactive({
  student: loadSavedStudent(),
  showLoginModal: false,
  showProfileModal: false,
  authTab: 'login' // 'login' | 'register'
})

export const useStudentAuth = () => {
  const setStudent = (studentData, token = null) => {
    state.student = studentData
    try {
      if (studentData) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(studentData))
        if (token) {
          localStorage.setItem(STUDENT_TOKEN_KEY, token)
        }
      } else {
        localStorage.removeItem(STORAGE_KEY)
        localStorage.removeItem(STUDENT_TOKEN_KEY)
      }
    } catch (e) {
      console.error('儲存學員資料失敗:', e)
    }
  }

  const logout = () => {
    setStudent(null)
  }

  const refreshProfile = async () => {
    if (!state.student || !state.student.id) return null
    try {
      const data = await api.get(`/student/profile/${state.student.id}`)
      if (data.success && data.student) {
        setStudent({ ...state.student, ...data.student })
        return data.student
      }
    } catch (e) {
      console.error('更新學員資料失敗:', e)
    }
    return null
  }

  const openLoginModal = (tab = 'login') => {
    state.authTab = tab
    state.showLoginModal = true
  }

  const openRegisterModal = () => {
    state.authTab = 'register'
    state.showLoginModal = true
  }

  const closeLoginModal = () => {
    state.showLoginModal = false
  }

  const openProfileModal = () => {
    state.showProfileModal = true
  }

  const closeProfileModal = () => {
    state.showProfileModal = false
  }

  return {
    state,
    get isLoggedIn() {
      return !!state.student && !!state.student.id
    },
    get currentStudent() {
      return state.student
    },
    setStudent,
    logout,
    refreshProfile,
    openLoginModal,
    openRegisterModal,
    closeLoginModal,
    openProfileModal,
    closeProfileModal
  }
}
