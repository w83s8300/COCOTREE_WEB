import { ref } from 'vue'

/**
 * Global confirmation dialog system.
 * Replaces native browser confirm() with a non-blocking Bootstrap Modal.
 * Returns a Promise<boolean> so it can be used with async/await.
 */

const isVisible = ref(false)
const dialogMessage = ref('')
const dialogTitle = ref('確認')
let resolvePromise = null

/**
 * Show a confirmation dialog.
 * @param {string} message - Confirmation message
 * @param {string} [title='確認'] - Dialog title
 * @returns {Promise<boolean>} - Resolves true if confirmed, false if cancelled
 *
 * @example
 * const ok = await showConfirm('確定要刪除嗎？')
 * if (ok) { ... }
 */
export async function showConfirm(message, title = '確認') {
  dialogMessage.value = message
  dialogTitle.value = title
  isVisible.value = true
  return new Promise(resolve => {
    resolvePromise = resolve
  })
}

/**
 * Resolve the current dialog. Called by ConfirmModal component.
 * @param {boolean} result
 */
export function resolveDialog(result) {
  isVisible.value = false
  if (resolvePromise) {
    resolvePromise(result)
    resolvePromise = null
  }
}

/**
 * Get reactive dialog state. Used by ConfirmModal component.
 */
export function useDialogState() {
  return { isVisible, dialogMessage, dialogTitle }
}

