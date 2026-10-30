<template>
  <div class="venue-page">
    <!-- 1. 頂部橫幅 -->
    <PageBanner image="https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=1920&q=80" title="場地租借 / VENUE" pageKey="venue" />

    <div class="container my-5">
      <!-- 頁頭介紹 -->
      <div class="text-center mb-5" data-aos="fade-up">
        <span class="badge bg-primary-subtle text-primary fw-bold px-3 py-2 rounded-pill mb-2">專業舞蹈空間出租</span>
        <h2 class="fw-bold mb-3">優質獨立舞蹈教室與練習空間</h2>
        <p class="text-muted mx-auto" style="max-width: 680px;">
          提供多間高規格獨立練習室，配備專業彈性避震木地板、全身落地鏡面與環繞音響，適合舞蹈排練、個人練習、瑜珈授課、商業攝影及團體活動包場。
        </p>
      </div>

      <!-- 載入中狀態 -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入教室資料中...</span>
        </div>
        <p class="mt-2 text-muted">正在載入後台最新教室與時段費率...</p>
      </div>

      <!-- 2. 主題教室焦點展示 (與後台教室管理連動) -->
      <div v-else class="row mb-5 align-items-stretch" data-aos="fade-up">
        <!-- 左側：教室輪播圖 -->
        <div class="col-lg-7 mb-4 mb-lg-0">
          <div id="venueCarousel" class="carousel slide rounded-4 overflow-hidden shadow h-100 position-relative bg-dark" data-bs-ride="carousel" ref="venueCarousel">
            <!-- 輪播指示條 -->
            <div v-if="rooms.length > 1" class="carousel-indicators">
              <button
                v-for="(r, idx) in rooms"
                :key="'indicator-' + r.id"
                type="button"
                data-bs-target="#venueCarousel"
                :data-bs-slide-to="idx"
                :class="{ active: idx === activeRoomIndex }"
                :aria-current="idx === activeRoomIndex ? 'true' : undefined"
                :aria-label="'Slide ' + (idx + 1)"
                @click="activeRoomIndex = idx"
              ></button>
            </div>

            <div class="carousel-inner h-100">
              <div
                v-for="(r, idx) in rooms"
                :key="r.id"
                class="carousel-item h-100"
                :class="{ active: idx === 0 }"
              >
                <div class="venue-img-wrapper h-100 position-relative">
                  <img
                    :src="r.image_url || getFallbackImg(idx)"
                    class="d-block w-100 h-100 object-fit-cover venue-carousel-img"
                    :alt="r.name"
                    @error="handleImgError"
                  >
                  <!-- 圖片浮水印標籤 -->
                  <div class="position-absolute bottom-0 start-0 end-0 p-3 bg-gradient-dark text-white d-flex justify-content-between align-items-end">
                    <div>
                      <h4 class="fw-bold mb-1 text-white text-shadow">{{ r.name }}</h4>
                      <span class="small text-white-50"><i class="bi bi-people-fill me-1"></i>容納 {{ r.capacity }} 人</span>
                    </div>
                    <span class="badge bg-warning text-dark fw-bold fs-6 px-3 py-2 shadow-sm">
                      ${{ r.hourly_rate }} / hr
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 輪播箭頭 -->
            <template v-if="rooms.length > 1">
              <button class="carousel-control-prev" type="button" data-bs-target="#venueCarousel" data-bs-slide="prev">
                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Previous</span>
              </button>
              <button class="carousel-control-next" type="button" data-bs-target="#venueCarousel" data-bs-slide="next">
                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Next</span>
              </button>
            </template>
          </div>
        </div>

        <!-- 右側：當前教室規格與設備詳情 -->
        <div class="col-lg-5">
          <div class="card h-100 border-0 shadow-sm rounded-4 p-4 d-flex flex-column justify-content-between bg-white">
            <div>
              <!-- 教室切換快捷選單 Pills -->
              <div class="d-flex flex-wrap gap-2 mb-3">
                <button
                  v-for="(r, idx) in rooms"
                  :key="'btn-' + r.id"
                  type="button"
                  class="btn btn-sm rounded-pill px-3"
                  :class="idx === activeRoomIndex ? 'btn-primary fw-bold shadow-sm' : 'btn-outline-secondary bg-light'"
                  @click="switchRoom(idx)"
                >
                  {{ r.name }}
                </button>
              </div>

              <!-- 當前教室資訊 -->
              <div v-if="currentRoom" class="text-start">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h3 class="fw-bold text-dark mb-0">{{ currentRoom.name }}</h3>
                  <span class="badge" :class="currentRoom.is_available ? 'bg-success' : 'bg-secondary'">
                    {{ currentRoom.is_available ? '● 開放租借中' : '維護整理中' }}
                  </span>
                </div>

                <div class="fs-4 fw-bold text-primary mb-3">
                  ${{ currentRoom.hourly_rate }} <span class="fs-6 text-muted fw-normal">/ 每小時</span>
                </div>

                <p class="text-muted small mb-4" style="line-height: 1.6;">
                  {{ currentRoom.description || '專業舞蹈練習空間，具備完善採光與舒適環境，歡迎各類舞蹈團體或個人洽詢租借。' }}
                </p>

                <!-- 規格列表 -->
                <h6 class="fw-bold text-dark border-bottom pb-2 mb-3">
                  <i class="bi bi-sliders me-1 text-primary"></i>空間規格與核心配備
                </h6>
                <ul class="list-unstyled text-start small mb-4">
                  <li class="py-1 d-flex justify-content-between">
                    <span class="text-muted"><i class="bi bi-person-fill text-secondary me-2"></i>建議容納：</span>
                    <strong class="text-dark">{{ currentRoom.capacity }} 人</strong>
                  </li>
                  <li class="py-1 d-flex justify-content-between">
                    <span class="text-muted"><i class="bi bi-clock text-secondary me-2"></i>租借費率：</span>
                    <strong class="text-dark">${{ currentRoom.hourly_rate }} / 小時</strong>
                  </li>
                  <li class="py-1 d-flex justify-content-between">
                    <span class="text-muted"><i class="bi bi-shield-check text-secondary me-2"></i>專業地板：</span>
                    <strong class="text-dark">專業防滑減震木質地板</strong>
                  </li>
                </ul>

                <!-- 包含設備標籤 -->
                <div class="mb-3">
                  <div class="small text-muted fw-bold mb-2">包含設備與附屬設施：</div>
                  <div class="d-flex flex-wrap gap-1">
                    <span
                      v-for="(eq, eqIdx) in parseEquipment(currentRoom.equipment)"
                      :key="eqIdx"
                      class="badge bg-light text-dark border py-1 px-2 small"
                    >
                      <i class="bi bi-check2 text-success me-1"></i>{{ eq }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 底部動作按鈕 -->
            <div class="pt-3 border-top mt-auto">
              <router-link to="/contact" class="btn btn-primary w-100 rounded-pill py-2 fw-bold shadow-sm d-flex justify-content-center align-items-center gap-2">
                <i class="bi bi-calendar2-check-fill"></i>立即預約洽詢租借
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. 所有教室一覽卡片區 (動態呈現所有教室) -->
      <div class="my-5" data-aos="fade-up">
        <div class="d-flex justify-content-between align-items-end mb-4">
          <div>
            <h3 class="fw-bold mb-1">各大練習室一覽 / STUDIOS OVERVIEW</h3>
            <p class="text-muted small mb-0">依據您的團隊人數與使用需求，挑選最適合的練習空間</p>
          </div>
          <router-link to="/schedule" class="btn btn-outline-dark btn-sm rounded-pill px-3 d-none d-md-inline-block">
            查看本週課程課表 <i class="bi bi-arrow-right ms-1"></i>
          </router-link>
        </div>

        <div class="row g-4">
          <div
            v-for="(room, idx) in rooms"
            :key="'card-' + room.id"
            class="col-md-6 col-lg-3"
          >
            <div class="card h-100 border-0 shadow-sm rounded-4 overflow-hidden room-card d-flex flex-column">
              <!-- 教室圖片 -->
              <div class="position-relative room-card-img-wrap" style="height: 190px;">
                <img
                  :src="room.image_url || getFallbackImg(idx)"
                  class="w-100 h-100 object-fit-cover"
                  :alt="room.name"
                  @error="handleImgError"
                >
                <span class="position-absolute top-0 end-0 m-2 badge" :class="room.is_available ? 'bg-success' : 'bg-secondary'">
                  {{ room.is_available ? '可租借' : '暫停' }}
                </span>
                <span class="position-absolute bottom-0 start-0 m-2 badge bg-dark bg-opacity-75 text-white fw-bold">
                  <i class="bi bi-people-fill me-1"></i>容納 {{ room.capacity }} 人
                </span>
              </div>

              <!-- 卡片內文 -->
              <div class="card-body p-3 d-flex flex-column text-start">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <h5 class="fw-bold mb-0 text-dark">{{ room.name }}</h5>
                  <span class="text-primary fw-bold fs-6">${{ room.hourly_rate }}/hr</span>
                </div>
                <p class="text-muted small flex-grow-1 mb-3" style="line-height: 1.5;">
                  {{ room.description || '配備高規格舞蹈設施，歡迎各類排舞與練習活動租借。' }}
                </p>

                <!-- 設備摘要標籤 -->
                <div class="d-flex flex-wrap gap-1 mb-3">
                  <span
                    v-for="(eq, eIdx) in parseEquipment(room.equipment).slice(0, 3)"
                    :key="eIdx"
                    class="badge bg-light text-secondary border small py-1"
                  >
                    {{ eq }}
                  </span>
                  <span v-if="parseEquipment(room.equipment).length > 3" class="badge bg-light text-muted border small py-1">
                    +{{ parseEquipment(room.equipment).length - 3 }}
                  </span>
                </div>

                <div class="pt-2 border-top mt-auto">
                  <router-link to="/contact" class="btn btn-outline-primary btn-sm w-100 rounded-pill fw-semibold">
                    <i class="bi bi-chat-dots me-1"></i>洽詢預約
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. 各教室費率收費表 (與後台即時連動) -->
      <div class="mb-5 pt-3" data-aos="fade-up">
        <div class="text-center mb-4">
          <h3 class="fw-bold mb-1">租借費率與時段對照表</h3>
          <p class="text-muted small">所有收費標準與後台系統即時連動，收費透明公正</p>
        </div>

        <div class="table-responsive shadow-sm rounded-4 overflow-hidden border">
          <table class="table table-hover table-striped text-center align-middle mb-0">
            <thead class="table-dark">
              <tr>
                <th scope="col" style="width: 20%;">教室名稱</th>
                <th scope="col" style="width: 15%;">建議容納人數</th>
                <th scope="col" style="width: 35%;">配備特色</th>
                <th scope="col" style="width: 15%;">每小時租借費率</th>
                <th scope="col" style="width: 15%;">狀態</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="room in rooms" :key="'table-' + room.id">
                <td class="fw-bold text-dark">{{ room.name }}</td>
                <td><span class="badge bg-light text-dark border">{{ room.capacity }} 人</span></td>
                <td class="text-start small">{{ room.equipment || '標準音響設備、落地鏡' }}</td>
                <td><strong class="text-primary fs-6">${{ room.hourly_rate }}</strong> / 小時</td>
                <td>
                  <span class="badge" :class="room.is_available ? 'bg-success' : 'bg-secondary'">
                    {{ room.is_available ? '開放租借' : '內部維護中' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="text-muted text-center mt-2 small">
          * 長期固定時段包期租借或商業活動/攝影棚包場另有專案優惠，歡迎點擊下方聯絡我們洽詢。
        </p>
      </div>

      <!-- 5. 租借須知與規章 -->
      <div class="text-start p-4 bg-light rounded-4 shadow-sm border" data-aos="fade-up">
        <h4 class="fw-bold text-dark mb-3">
          <i class="bi bi-info-circle-fill text-primary me-2"></i>場地租借須知與使用規章
        </h4>
        <div class="row g-3">
          <div class="col-md-6">
            <ul class="list-unstyled lh-lg mb-0 text-muted">
              <li><i class="bi bi-check-circle-fill text-success me-2"></i><strong>預約付訂：</strong>請洽櫃檯或官方 LINE，並於使用日前三天完成預約及付訂。</li>
              <li><i class="bi bi-check-circle-fill text-success me-2"></i><strong>更改取消：</strong>如需取消或變更時段，請至少於 24 小時前主動告知。</li>
              <li><i class="bi bi-check-circle-fill text-success me-2"></i><strong>飲水規範：</strong>教室內禁止攜帶外食與含糖飲料，僅可攜帶白開水或加蓋水瓶。</li>
            </ul>
          </div>
          <div class="col-md-6">
            <ul class="list-unstyled lh-lg mb-0 text-muted">
              <li><i class="bi bi-check-circle-fill text-success me-2"></i><strong>鞋履規範：</strong>嚴禁穿著室外髒鞋、高跟鞋或黑底鞋進入，請換穿乾淨室內舞鞋。</li>
              <li><i class="bi bi-check-circle-fill text-success me-2"></i><strong>設備愛護：</strong>請愛惜空調、落地鏡與音響設備，如有不當損壞須照市價賠償。</li>
              <li><i class="bi bi-check-circle-fill text-success me-2"></i><strong>場地復原：</strong>使用完畢請將個人垃圾帶走並關閉音響空調，恢復場地整潔。</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Carousel } from 'bootstrap';
import PageBanner from '@/components/PageBanner.vue';
import api, { API_ENDPOINTS } from '@/utils/api';

const FALLBACK_ROOMS = [
  {
    id: 1,
    name: 'Studio A',
    capacity: 20,
    equipment: '專業環繞音響, 落地大鏡面, 芭蕾把桿, 獨立空調',
    description: '大型練習室，適合芭蕾、當代舞、MV 排舞及大型團隊包場。',
    image_url: 'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=800&q=80',
    hourly_rate: '500',
    is_available: 1
  },
  {
    id: 2,
    name: 'Studio B',
    capacity: 15,
    equipment: '專業環繞音響, 落地鏡面, 獨立空調',
    description: '中型練習室，採光明亮，適合街舞律動、K-POP 及各舞風練習。',
    image_url: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80',
    hourly_rate: '400',
    is_available: 1
  },
  {
    id: 3,
    name: 'Studio C',
    capacity: 25,
    equipment: '專業舞臺級音響, 氣氛調光 LED, 雙面落地鏡, 獨立空調',
    description: '專業表演旗艦練習室，配備舞台氛圍燈光，適合排演與成果驗收。',
    image_url: 'https://images.unsplash.com/photo-1547153760-18fc86324498?auto=format&fit=crop&w=800&q=80',
    hourly_rate: '800',
    is_available: 1
  },
  {
    id: 4,
    name: 'Studio D',
    capacity: 10,
    equipment: '藍芽音響, 落地鏡, 瑜珈墊, 獨立空調',
    description: '精緻私人練習室，隱私性高，適合一對一私教課或個人自主訓練。',
    image_url: 'https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?auto=format&fit=crop&w=800&q=80',
    hourly_rate: '300',
    is_available: 1
  }
];

export default {
  name: 'Venue',
  components: {
    PageBanner
  },
  data() {
    return {
      rooms: [...FALLBACK_ROOMS],
      loading: false,
      activeRoomIndex: 0,
      carouselInstance: null
    };
  },
  computed: {
    currentRoom() {
      if (!this.rooms || this.rooms.length === 0) return null;
      return this.rooms[this.activeRoomIndex] || this.rooms[0];
    }
  },
  created() {
    this.fetchRooms();
  },
  mounted() {
    this.initCarousel();
  },
  beforeUnmount() {
    if (this.carouselInstance) {
      this.carouselInstance.dispose();
      this.carouselInstance = null;
    }
  },
  methods: {
    async fetchRooms() {
      this.loading = true;
      try {
        const res = await api.get(API_ENDPOINTS.ROOMS);
        if (res.success && Array.isArray(res.rooms) && res.rooms.length > 0) {
          this.rooms = res.rooms;
          this.activeRoomIndex = 0;
          this.$nextTick(() => {
            this.initCarousel();
          });
        }
      } catch (err) {
        console.warn('獲取後台教室列表失敗，使用預設備援資料:', err);
      } finally {
        this.loading = false;
      }
    },
    initCarousel() {
      if (this.carouselInstance) {
        this.carouselInstance.dispose();
        this.carouselInstance = null;
      }
      const el = this.$refs.venueCarousel;
      if (el) {
        this.carouselInstance = new Carousel(el, {
          interval: 4000,
          pause: 'hover'
        });

        // 監聽輪播滑動事件以同步右側教室詳情
        el.addEventListener('slid.bs.carousel', (e) => {
          this.activeRoomIndex = e.to;
        });
      }
    },
    switchRoom(index) {
      this.activeRoomIndex = index;
      if (this.carouselInstance) {
        this.carouselInstance.to(index);
      }
    },
    parseEquipment(raw) {
      if (!raw) return ['標準音響', '落地鏡面', '空調設備'];
      return String(raw)
        .split(/[,，、\n]+/)
        .map(s => s.trim())
        .filter(Boolean);
    },
    getFallbackImg(index) {
      const imgs = [
        'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1547153760-18fc86324498?auto=format&fit=crop&w=800&q=80',
        'https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?auto=format&fit=crop&w=800&q=80'
      ];
      return imgs[index % imgs.length];
    },
    handleImgError(e) {
      e.target.src = 'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=800&q=80';
    }
  }
};
</script>

<style scoped>
.venue-carousel-img {
  height: 440px;
  object-fit: cover;
}

.bg-gradient-dark {
  background: linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.85) 100%);
}

.text-shadow {
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
}

.room-card {
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.room-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12) !important;
}
</style>
