import axios from 'axios'

/**
 * Unified API service for the Dance Studio application.
 *
 * Architecture:
 * - Development: Browser → Vite dev proxy (/api) → Backend (localhost:8001 or Docker backend:8001)
 * - Production:  Browser → Nginx proxy (/api) → Backend
 *
 * The baseURL is always '/api' (relative), letting the dev server or reverse proxy handle routing.
 * Override with VITE_API_BASE_URL env var if needed.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

/**
 * Response interceptor:
 * - Success: auto-unwraps response.data so callers get parsed JSON directly
 * - Error: extracts error message and rejects with a structured error object
 */
api.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.error
      || error.response?.data?.message
      || error.message
      || '請求失敗'
    const status = error.response?.status

    if (import.meta.env.DEV) {
      console.error(`[API Error] ${status || 'Network'}: ${message}`)
    }

    return Promise.reject({ message, status, raw: error })
  }
)

/**
 * API endpoint constants (relative paths).
 * The axios instance baseURL ('/api') is automatically prepended.
 */
export const API_ENDPOINTS = {
  TEACHERS: '/teachers',
  STUDENTS: '/students',
  STYLES: '/styles',
  ROOMS: '/rooms',
  COURSES: '/courses',
  SCHEDULES: '/schedules',
  ENROLLMENTS: '/enrollments'
}

/**
 * Build a clean API path from an endpoint string.
 * Handles backward compatibility with paths that include '/api' prefix.
 *
 * @param {string} endpoint - API endpoint path (e.g., '/enrollments/123' or '/api/enrollments/123')
 * @returns {string} Clean path without '/api' prefix
 */
export const buildApiUrl = (endpoint) => {
  let clean = endpoint.replace(/^\/api/, '')
  if (!clean.startsWith('/')) clean = '/' + clean
  return clean
}

export default api
