<template>
  <div class="add-room">
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="name">教室名稱:</label>
        <input type="text" id="name" v-model="room.name" required>
      </div>
      <div class="form-group">
        <label for="capacity">容量:</label>
        <input type="number" id="capacity" v-model="room.capacity">
      </div>
      <div class="form-group">
        <label for="equipment">設備:</label>
        <textarea id="equipment" v-model="room.equipment"></textarea>
      </div>
      <div class="form-group">
        <label for="description">描述:</label>
        <textarea id="description" v-model="room.description"></textarea>
      </div>
      <div class="form-group">
        <label for="hourly_rate">時租費率:</label>
        <input type="number" id="hourly_rate" v-model="room.hourly_rate">
      </div>
      <div class="form-group">
        <input type="checkbox" id="is_available" v-model="room.is_available">
        <label for="is_available">是否可用</label>
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
    roomId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      room: {
        name: '',
        capacity: 20,
        equipment: '',
        description: '',
        hourly_rate: null,
        is_available: true
      },
      isEditMode: false
    };
  },
  created() {
    if (this.roomId) {
      this.isEditMode = true;
      this.fetchRoom(this.roomId);
    }
  },
  methods: {
    fetchRoom(id) {
      axios.get(`http://localhost:8001/api/rooms/${id}`)
        .then(response => {
          this.room = response.data.room;
        })
        .catch(error => {
          console.error('獲取教室資料失敗:', error);
        });
    },
    submitForm() {
      if (this.isEditMode) {
        this.updateRoom();
      } else {
        this.addRoom();
      }
    },
    addRoom() {
      axios.post('http://localhost:8001/api/rooms', this.room)
        .then(() => {
          alert('教室新增成功！');
          this.$emit('room-updated');
        })
        .catch(error => {
          console.error(error);
          alert('新增教室失敗！');
        });
    },
    updateRoom() {
      axios.put(`http://localhost:8001/api/rooms/${this.room.id}`, this.room)
        .then(() => {
          alert('教室更新成功！');
          this.$emit('room-updated');
        })
        .catch(error => {
          console.error(error);
          alert('更新教室失敗！');
        });
    },
    closeModal() {
      this.$emit('close-modal');
    }
  }
};
</script>

<style scoped>
.add-room {
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
  padding: 10px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
