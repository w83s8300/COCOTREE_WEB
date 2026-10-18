<template>
  <Teleport to="body">
    <div v-if="isVisible" class="confirm-overlay" @click.self="cancel">
      <div class="modal fade show d-block" tabindex="-1" role="dialog" aria-modal="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">{{ title }}</h5>
              <button type="button" class="btn-close" @click="cancel" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <p class="mb-0">{{ message }}</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="cancel">取消</button>
              <button type="button" class="btn btn-danger" @click="confirm" ref="confirmBtn">確定</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { watch, nextTick } from 'vue'
import { useDialogState, resolveDialog } from '@/utils/dialog'

export default {
  name: 'ConfirmModal',
  setup() {
    const { isVisible, dialogMessage, dialogTitle } = useDialogState()
    const confirmBtn = null

    // Auto-focus confirm button when dialog appears
    watch(isVisible, (visible) => {
      if (visible) {
        nextTick(() => {
          const btn = document.querySelector('.confirm-overlay .btn-danger')
          btn?.focus()
        })
      }
    })

    return {
      isVisible,
      message: dialogMessage,
      title: dialogTitle,
      confirm: () => resolveDialog(true),
      cancel: () => resolveDialog(false)
    }
  }
}
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

