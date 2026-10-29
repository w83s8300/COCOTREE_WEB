<template>
  <div class="gallery-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=22" title="活動花絮 / GALLERY" />

    <!-- 2. Photo Albums Container -->
    <div class="container my-5">
      <!-- 載入中 -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入花絮相簿中...</span>
        </div>
        <p class="mt-2 text-muted">正在載入活動精彩花絮...</p>
      </div>

      <!-- 無相簿空狀態 -->
      <div v-else-if="albums.length === 0" class="text-center py-5 bg-light rounded-4 shadow-sm border">
        <i class="bi bi-images text-muted fs-1 opacity-50"></i>
        <h5 class="fw-bold text-dark mt-3 mb-1">目前尚無公開的活動花絮</h5>
        <p class="text-muted small mb-0">敬請期待我們近期的精彩活動記錄與學員成果發表！</p>
      </div>

      <!-- 相簿卡片列表 -->
      <div v-else class="row g-4">
        <div
          class="col-lg-4 col-md-6"
          v-for="(album, albumIndex) in albums"
          :key="album.id || albumIndex"
          data-aos="fade-up"
        >
          <div class="card gallery-card h-100 shadow-sm border-0 overflow-hidden" @click="showAlbumModal(albumIndex)">
            <!-- 封面相片 -->
            <div class="album-cover-container position-relative">
              <img
                :src="album.coverImage || album.cover_image || 'https://picsum.photos/600/400?random=' + (albumIndex + 20)"
                class="card-img-top album-cover"
                :alt="album.title"
                loading="lazy"
              />
              <div class="cover-overlay d-flex align-items-center justify-content-center">
                <span class="btn btn-sm btn-light rounded-pill px-3 py-1 fw-bold shadow-sm">
                  <i class="bi bi-eye me-1"></i>瀏覽相簿
                </span>
              </div>
              <!-- 照片張數標籤 -->
              <span class="badge bg-dark bg-opacity-75 text-white position-absolute bottom-0 end-0 m-2 px-2 py-1 shadow-sm small">
                <i class="bi bi-camera me-1"></i>{{ (album.images || album.photos || []).length }} 張
              </span>
            </div>

            <!-- 卡片內容 -->
            <div class="card-body text-center p-3">
              <h5 class="card-title fw-bold mb-1 text-dark">{{ album.title }}</h5>
              <div v-if="album.event_date" class="text-muted small mb-2">
                <i class="bi bi-calendar-event me-1 text-primary"></i>{{ album.event_date }}
              </div>
              <p v-if="album.description" class="text-muted small album-brief mb-0">
                {{ album.description }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Album Detail Modal -->
    <div class="modal fade" id="albumModal" tabindex="-1" aria-labelledby="albumModalLabel" aria-hidden="true" ref="albumModalEl">
      <div class="modal-dialog modal-dialog-centered modal-xl">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-dark text-white">
            <div>
              <h5 class="modal-title fw-bold" id="albumModalLabel">
                {{ selectedAlbum ? selectedAlbum.title : '' }}
              </h5>
              <div class="small text-white-50 mt-1 d-flex gap-3 align-items-center">
                <span v-if="selectedAlbum?.event_date">
                  <i class="bi bi-calendar3 me-1"></i>{{ selectedAlbum.event_date }}
                </span>
                <span>
                  <i class="bi bi-image me-1"></i>
                  第 {{ currentPhotos.length > 0 ? (selectedImageIndex + 1) : 0 }} / {{ currentPhotos.length }} 張
                </span>
              </div>
            </div>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>

          <div class="modal-body p-3 bg-black">
            <div v-if="selectedAlbum && currentPhotos.length > 0">
              <div id="albumCarousel" class="carousel slide" data-bs-ride="carousel" ref="albumCarousel">
                <div class="carousel-inner">
                  <div
                    class="carousel-item"
                    :class="{ active: imgIndex === selectedImageIndex }"
                    v-for="(image, imgIndex) in currentPhotos"
                    :key="imgIndex"
                  >
                    <img
                      :src="image.src || image.image_url"
                      class="d-block w-100 carousel-slide-img"
                      :alt="image.description || selectedAlbum.title"
                    />
                  </div>
                </div>
                <button
                  v-if="currentPhotos.length > 1"
                  class="carousel-control-prev"
                  type="button"
                  data-bs-target="#albumCarousel"
                  data-bs-slide="prev"
                >
                  <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                  <span class="visually-hidden">Previous</span>
                </button>
                <button
                  v-if="currentPhotos.length > 1"
                  class="carousel-control-next"
                  type="button"
                  data-bs-target="#albumCarousel"
                  data-bs-slide="next"
                >
                  <span class="carousel-control-next-icon" aria-hidden="true"></span>
                  <span class="visually-hidden">Next</span>
                </button>
              </div>

              <!-- 照片圖說說明 -->
              <div class="image-info text-center mt-3 p-2 bg-dark rounded">
                <p class="mb-0 text-white-50">
                  {{ currentPhotos[selectedImageIndex]?.description || selectedAlbum.description || '活動花絮精彩瞬間' }}
                </p>
              </div>

              <!-- 底部縮圖滑動列 Thumbnail Strip -->
              <div v-if="currentPhotos.length > 1" class="thumbnail-strip mt-3">
                <div class="thumbnails-container d-flex justify-content-center">
                  <img
                    v-for="(image, imgIndex) in currentPhotos"
                    :key="imgIndex"
                    :src="image.src || image.image_url"
                    class="thumbnail-img mx-1 rounded shadow-sm"
                    :class="{ active: imgIndex === selectedImageIndex }"
                    @click="goToImage(imgIndex)"
                    :alt="`Thumbnail ${imgIndex + 1}`"
                  />
                </div>
              </div>
            </div>

            <!-- 相簿尚無相片提示 -->
            <div v-else class="text-center py-5 text-white-50">
              <i class="bi bi-image fs-1 opacity-50"></i>
              <p class="mt-2 mb-0">此相簿目前尚未上傳相片</p>
            </div>
          </div>

          <div class="modal-footer bg-dark border-secondary">
            <button type="button" class="btn btn-outline-light btn-sm px-4 rounded-pill" data-bs-dismiss="modal">
              關閉
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { Modal, Carousel } from 'bootstrap';
import PageBanner from '@/components/PageBanner.vue';
import { useCarouselSwipe } from '@/composables/useCarouselSwipe';
import api from '@/utils/api';

export default {
  name: 'Gallery',
  components: {
    PageBanner
  },
  setup() {
    const albumCarousel = ref(null);
    const carouselInstance = ref(null);
    const { setupSwipe, cleanupSwipe } = useCarouselSwipe(albumCarousel, carouselInstance);
    return { albumCarousel, carouselInstance, setupSwipe, cleanupSwipe };
  },
  data() {
    return {
      albums: [],
      loading: true,
      selectedAlbum: null,
      selectedImageIndex: 0,
      albumModal: null
    };
  },
  computed: {
    currentPhotos() {
      if (!this.selectedAlbum) return [];
      return this.selectedAlbum.images || this.selectedAlbum.photos || [];
    }
  },
  async mounted() {
    const el = document.getElementById('albumModal');
    if (el) {
      this.albumModal = new Modal(el);
      // 監聽輪播切換事件以同步縮圖與指示
      el.addEventListener('slid.bs.carousel', this.handleCarouselSlid);
    }
    await this.fetchAlbums();
  },
  beforeUnmount() {
    const el = document.getElementById('albumModal');
    if (el) {
      el.removeEventListener('slid.bs.carousel', this.handleCarouselSlid);
    }
    if (this.albumModal) this.albumModal.dispose();
    if (this.carouselInstance) this.carouselInstance.dispose();
    this.cleanupSwipe();
  },
  methods: {
    async fetchAlbums() {
      this.loading = true;
      try {
        const res = await api.get('/gallery/albums');
        if (res && res.albums) {
          this.albums = res.albums;
        }
      } catch (err) {
        console.warn('載入活動花絮 API 失敗，使用預設備用展示:', err);
      } finally {
        this.loading = false;
      }
    },

    showAlbumModal(albumIndex) {
      this.selectedAlbum = this.albums[albumIndex];
      this.selectedImageIndex = 0;

      this.$nextTick(() => {
        if (this.carouselInstance) {
          this.carouselInstance.dispose();
        }
        if (this.$refs.albumCarousel) {
          this.carouselInstance = new Carousel(this.$refs.albumCarousel, {
            interval: 4000,
            wrap: true
          });
          this.carouselInstance.to(0);
          this.setupSwipe();
        }
        this.albumModal?.show();
      });
    },

    goToImage(imgIndex) {
      this.selectedImageIndex = imgIndex;
      this.carouselInstance?.to(imgIndex);
    },

    handleCarouselSlid(event) {
      if (typeof event.to === 'number') {
        this.selectedImageIndex = event.to;
      }
    }
  }
};
</script>

<style scoped>
.gallery-card {
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  border-radius: 12px;
}

.gallery-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12) !important;
}

.album-cover-container {
  overflow: hidden;
  background-color: #f1f3f5;
  height: 240px;
}

.album-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.35s ease;
}

.gallery-card:hover .album-cover {
  transform: scale(1.06);
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.25);
  opacity: 0;
  transition: opacity 0.25s ease;
}

.gallery-card:hover .cover-overlay {
  opacity: 1;
}

.album-brief {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.carousel-slide-img {
  max-height: 580px;
  object-fit: contain;
  background-color: #000;
}

.thumbnail-strip {
  overflow-x: auto;
  white-space: nowrap;
  padding: 6px 0;
}

.thumbnails-container {
  display: inline-flex;
}

.thumbnail-img {
  width: 80px;
  height: 60px;
  object-fit: cover;
  cursor: pointer;
  opacity: 0.55;
  border: 2px solid transparent;
  transition: opacity 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.thumbnail-img:hover {
  opacity: 0.85;
}

.thumbnail-img.active {
  opacity: 1;
  border-color: #0d6efd;
  transform: scale(1.05);
}
</style>
