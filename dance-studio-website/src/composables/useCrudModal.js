import { ref, nextTick } from 'vue'
import { Modal } from 'bootstrap'

/**
 * Composable for managing Bootstrap modal CRUD lifecycle.
 * Eliminates duplicated modal init/open/close/cleanup code across management views.
 *
 * @param {string} modalId - The DOM id of the modal element
 * @returns {Object} Modal control functions and reactive state
 *
 * @example
 * // In Options API setup() or <script setup>:
 * const { showForm, editingId, initModal, openCreate, openEdit, closeModal } = useCrudModal('editCourseModal')
 * onMounted(() => initModal())
 */
export function useCrudModal(modalId) {
  const modalInstance = ref(null)
  const showForm = ref(false)
  const editingId = ref(null)
  let cleanupFn = null

  /** Initialize modal instance and attach hidden event listener. Call in onMounted. */
  function initModal() {
    const el = document.getElementById(modalId)
    if (!el) {
      console.warn(`[useCrudModal] Element #${modalId} not found`)
      return
    }
    modalInstance.value = new Modal(el)

    const onHidden = () => {
      showForm.value = false
      editingId.value = null
    }
    el.addEventListener('hidden.bs.modal', onHidden)
    cleanupFn = () => el.removeEventListener('hidden.bs.modal', onHidden)
  }

  /** Open modal in create mode (editingId = null) */
  function openCreate() {
    editingId.value = null
    showForm.value = true
    nextTick(() => modalInstance.value?.show())
  }

  /** Open modal in edit mode with given id */
  function openEdit(id) {
    editingId.value = id
    showForm.value = true
    nextTick(() => modalInstance.value?.show())
  }

  /** Hide the modal */
  function closeModal() {
    modalInstance.value?.hide()
  }

  /** Dispose modal instance. Call in onUnmounted if needed. */
  function destroyModal() {
    if (cleanupFn) cleanupFn()
    modalInstance.value?.dispose()
    modalInstance.value = null
  }

  return {
    showForm,
    editingId,
    initModal,
    openCreate,
    openEdit,
    closeModal,
    destroyModal
  }
}

