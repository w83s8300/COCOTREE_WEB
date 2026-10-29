<template>
  <div class="about-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=9" title="關於我們 / ABOUT US" />

    <!-- 2. Introduction -->
    <div class="container my-5" data-aos="fade-up">
      <div class="row align-items-center">
        <div class="col-lg-6">
          <h2 class="mb-3">歡迎來到 Dance Studio</h2>
          <p class="text-start">
            我們是城市中最具活力的舞蹈綠洲，致力於為所有年齡和程度的舞蹈愛好者提供最專業、最多元的學習體驗。無論您是初學者還是經驗豐富的舞者，都能在這裡找到屬於您的舞台。
          </p>
          <p class="text-start">
            我們的師資團隊由業界頂尖的專業舞者組成，他們不僅擁有豐富的教學經驗，更對舞蹈充滿無限熱情。我們提供舒適、寬敞的學習環境，配備專業級的音響和地板，讓您在最佳的狀態下學習與成長。
          </p>
        </div>
        <div class="col-lg-6">
          <img src="https://picsum.photos/800/600?random=10" class="img-fluid rounded shadow-sm" alt="Studio Introduction" loading="lazy">
        </div>
      </div>
    </div>

    <!-- 3. Studio Environment (後台資料串接) -->
    <div class="bg-light py-5" data-aos="fade-up">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="fw-bold mb-2">環境介紹</h2>
          <p class="text-muted">專業舒適的舞蹈空間與齊全配備，提供最優質的排練與學習體驗</p>
        </div>

        <!-- 載入中狀態 -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">載入中...</span>
          </div>
          <p class="mt-2 text-muted">正在載入環境資料...</p>
        </div>

        <!-- 錯誤狀態 -->
        <div v-else-if="error" class="alert alert-danger text-center my-4" role="alert">
          <span>{{ error }}</span>
          <button @click="fetchRooms" class="btn btn-outline-danger btn-sm ms-3">重新載入</button>
        </div>

        <!-- 空資料狀態 -->
        <div v-else-if="rooms.length === 0" class="text-center py-5 text-muted">
          <p>目前尚無環境介紹資料。</p>
        </div>

        <!-- 環境/教室列表 -->
        <div v-else class="row g-4 justify-content-center">
          <div
            v-for="(room, index) in rooms"
            :key="room.id"
            class="col-md-6 col-lg-3"
          >
            <div class="card h-100 border-0 shadow-sm room-card overflow-hidden">
              <div class="room-img-container position-relative">
                <img
                  :src="getRoomImage(room, index)"
                  class="card-img-top room-img"
                  :alt="room.name"
                  loading="lazy"
                  @error="onImageError($event, index)"
                />
                <span
                  class="badge position-absolute top-0 end-0 m-3 px-3 py-2 rounded-pill shadow-sm"
                  :class="room.is_available ? 'bg-success' : 'bg-secondary'"
                >
                  <i :class="room.is_available ? 'bi bi-check-circle-fill' : 'bi bi-wrench-adjustable'" class="me-1"></i>
                  {{ room.is_available ? '開放預約中' : '維護中' }}
                </span>
                <span
                  v-if="room.capacity"
                  class="badge bg-dark bg-opacity-75 position-absolute bottom-0 start-0 m-3 px-2 py-1 rounded"
                >
                  <i class="bi bi-people-fill me-1"></i>容納 {{ room.capacity }} 人
                </span>
              </div>
              <div class="card-body d-flex flex-column p-3 p-xl-4">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <h5 class="card-title fw-bold mb-0 text-dark">{{ room.name }}</h5>
                  <span v-if="room.hourly_rate" class="badge bg-primary-subtle text-primary fw-bold">
                    ${{ room.hourly_rate }}/hr
                  </span>
                </div>
                <p class="card-text text-muted mb-3 flex-grow-1 text-start" style="line-height: 1.6; font-size: 0.95rem;">
                  {{ room.description || '專業舞蹈練習空間，配備完善設備。' }}
                </p>
                <div v-if="room.equipment" class="room-equipment pt-3 border-top text-start">
                  <div class="small fw-bold text-secondary mb-1">
                    <i class="bi bi-gear-wide-connected me-1 text-primary"></i>設備規格：
                  </div>
                  <div class="d-flex flex-wrap gap-1">
                    <span
                      v-for="(eq, eqIdx) in parseEquipment(room.equipment)"
                      :key="eqIdx"
                      class="badge bg-white text-secondary border small fw-normal"
                    >
                      {{ eq }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import PageBanner from '@/components/PageBanner.vue';
import api, { API_ENDPOINTS } from '@/utils/api';

const defaultRoomImages = [
  'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1547153760-18fc86324498?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1535525153412-5a42439a210d?auto=format&fit=crop&w=800&q=80'
];

export default {
  name: 'About',
  components: {
    PageBanner,
  },
  data() {
    return {
      rooms: [],
      loading: true,
      error: null
    };
  },
  created() {
    this.fetchRooms();
  },
  methods: {
    async fetchRooms() {
      this.loading = true;
      this.error = null;
      try {
        const res = await api.get(API_ENDPOINTS.ROOMS);
        this.rooms = res.rooms || res || [];
      } catch (err) {
        console.error('獲取環境資料失敗:', err);
        this.error = '無法載入環境資料，請稍後再試。';
      } finally {
        this.loading = false;
      }
    },
    getRoomImage(room, index) {
      if (room.image_url && room.image_url.trim()) {
        return room.image_url.trim();
      }
      return defaultRoomImages[index % defaultRoomImages.length];
    },
    onImageError(e, index) {
      e.target.src = defaultRoomImages[index % defaultRoomImages.length];
    },
    parseEquipment(equipment) {
      if (!equipment) return [];
      return equipment
        .split(/[,，\n]+/)
        .map(item => item.trim())
        .filter(item => item.length > 0);
    }
  }
}
</script>

<style scoped>
.bg-light {
  background-color: #f8f9fa !important;
}
.room-card {
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  border-radius: 12px;
}
.room-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important;
}
.room-img-container {
  height: 200px;
  overflow: hidden;
  background-color: #e9ecef;
}
.room-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.room-card:hover .room-img {
  transform: scale(1.05);
}
</style>