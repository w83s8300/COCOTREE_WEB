<template>
  <Teleport to="body">
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999;">
      <TransitionGroup name="toast">
        <div
          v-for="toast in state.toasts"
          :key="toast.id"
          class="toast show align-items-center border-0 mb-2"
          :class="toastClass(toast.type)"
          role="alert"
          aria-live="assertive"
          aria-atomic="true"
        >
          <div class="d-flex">
            <div class="toast-body">
              <i :class="iconClass(toast.type)" class="me-2"></i>
              {{ toast.message }}
            </div>
            <button
              type="button"
              class="btn-close btn-close-white me-2 m-auto"
              @click="remove(toast.id)"
              aria-label="Close"
            ></button>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script>
import { useToastState, removeToast } from '@/utils/toast'

export default {
  name: 'AppToast',
  setup() {
    const state = useToastState()

    const toastClass = (type) => ({
      'text-bg-success': type === 'success',
      'text-bg-danger': type === 'error',
      'text-bg-warning': type === 'warning',
      'text-bg-info': type === 'info'
    })

    const iconClass = (type) => ({
      'bi bi-check-circle-fill': type === 'success',
      'bi bi-x-circle-fill': type === 'error',
      'bi bi-exclamation-triangle-fill': type === 'warning',
      'bi bi-info-circle-fill': type === 'info'
    })

    return {
      state,
      remove: removeToast,
      toastClass,
      iconClass
    }
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>

