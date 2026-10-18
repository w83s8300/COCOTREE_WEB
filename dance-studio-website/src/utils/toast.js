import { reactive } from 'vue'

/**
 * Global toast notification system.
 * Replaces native browser alert() with non-blocking Bootstrap Toasts.
 */

const state = reactive({
  toasts: []
})

let nextId = 0

/**
 * Show a toast notification.
 * @param {string} message - Toast message
 * @param {'success'|'error'|'warning'|'info'} type - Toast type (determines color)
 * @param {number} duration - Auto-dismiss duration in ms (0 = no auto-dismiss)
 */
export function showToast(message, type = 'success', duration = 3000) {
  const id = nextId++
  state.toasts.push({ id, message, type })
  if (duration > 0) {
    setTimeout(() => removeToast(id), duration)
  }
}

/**
 * Remove a toast by id.
 * @param {number} id
 */
export function removeToast(id) {
  const index = state.toasts.findIndex(t => t.id === id)
  if (index > -1) state.toasts.splice(index, 1)
}

/**
 * Get reactive toast state. Used by AppToast component.
 * @returns {{ toasts: Array<{ id: number, message: string, type: string }> }}
 */
export function useToastState() {
  return state
}

