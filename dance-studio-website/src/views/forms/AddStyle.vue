<template>
  <div class="add-style">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="name" class="form-label">課程類型名稱:</label>
        <input type="text" id="name" class="form-control" v-model="style.name" placeholder="例如: K-POP、Hip Hop、基礎律動" required>
      </div>
      <div class="form-group">
        <label for="description" class="form-label">課程類型描述:</label>
        <textarea id="description" class="form-control" v-model="style.description" placeholder="簡短說明此類型的特色或適合對象..."></textarea>
      </div>
      <button type="submit" class="btn btn-primary" :disabled="submitting">
        <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
        {{ isEditMode ? '更新課程類型' : '新增課程類型' }}
      </button>
      <button type="button" class="btn btn-secondary ms-2" @click="closeModal">取消</button>
    </form>
  </div>
</template>

<script>
import api, { API_ENDPOINTS } from '@/utils/api';
import { showToast } from '@/utils/toast';

export default {
  props: {
    styleId: {
      type: Number,
      default: null
    }
  },
  emits: ['style-updated', 'close-modal'],
  data() {
    return {
      style: {
        name: '',
        description: ''
      },
      isEditMode: false,
      submitting: false
    };
  },
  watch: {
    styleId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.isEditMode = true;
          this.fetchStyle(newId);
        } else {
          this.isEditMode = false;
          this.resetForm();
        }
      }
    }
  },
  methods: {
    resetForm() {
      this.style = {
        name: '',
        description: ''
      };
    },
    fetchStyle(id) {
      api.get(`${API_ENDPOINTS.STYLES}/${id}`)
        .then(data => {
          this.style = data.style;
        })
        .catch(error => {
          console.error('獲取風格資料失敗:', error);
        });
    },
    submitForm() {
      if (this.isEditMode) {
        this.updateStyle();
      } else {
        this.addStyle();
      }
    },
    addStyle() {
      this.submitting = true;
      api.post(API_ENDPOINTS.STYLES, this.style)
        .then(() => {
          showToast('課程類型新增成功！', 'success');
          this.$emit('style-updated');
        })
        .catch(error => {
          console.error(error);
          showToast('新增課程類型失敗！', 'error');
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    updateStyle() {
      this.submitting = true;
      api.put(`${API_ENDPOINTS.STYLES}/${this.style.id}`, this.style)
        .then(() => {
          showToast('課程類型更新成功！', 'success');
          this.$emit('style-updated');
        })
        .catch(error => {
          console.error(error);
          showToast('更新課程類型失敗！', 'error');
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    closeModal() {
      this.$emit('close-modal');
    }
  }
};
</script>

<style scoped>
.add-style {
  padding: 20px;
}
.form-group {
  margin-bottom: 15px;
}
</style>
