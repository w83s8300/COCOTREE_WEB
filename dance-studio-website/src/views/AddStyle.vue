<template>
  <div class="add-style">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="name">風格名稱:</label>
        <input type="text" id="name" v-model="style.name" required>
      </div>
      <div class="form-group">
        <label for="description">風格描述:</label>
        <textarea id="description" v-model="style.description"></textarea>
      </div>
      <button type="submit" class="btn btn-primary">{{ isEditMode ? '更新' : '新增' }}</button>
      <button type="button" class="btn btn-secondary" @click="closeModal">取消</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    styleId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      style: {
        name: '',
        description: ''
      },
      isEditMode: false
    };
  },
  created() {
    if (this.styleId) {
      this.isEditMode = true;
      this.fetchStyle(this.styleId);
    }
  },
  methods: {
    fetchStyle(id) {
      axios.get(`http://localhost:8001/api/styles/${id}`)
        .then(response => {
          this.style = response.data.style;
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
      axios.post('http://localhost:8001/api/styles', this.style)
        .then(() => {
          alert('風格新增成功！');
          this.$emit('style-updated');
        })
        .catch(error => {
          console.error(error);
          alert('新增風格失敗！');
        });
    },
    updateStyle() {
      axios.put(`http://localhost:8001/api/styles/${this.style.id}`, this.style)
        .then(() => {
          alert('風格更新成功！');
          this.$emit('style-updated');
        })
        .catch(error => {
          console.error(error);
          alert('更新風格失敗！');
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
label {
  display: block;
  margin-bottom: 5px;
}
input, textarea {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
button {
  margin-right: 10px;
}
</style>
