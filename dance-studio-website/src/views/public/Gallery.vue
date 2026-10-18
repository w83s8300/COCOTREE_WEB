<template>
  <div class="gallery-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=22" title="活動花絮 / GALLERY" />

    <!-- 2. Photo Albums -->
    <div class="container my-5">
      <div class="row">
        <div class="col-lg-4 col-md-6 mb-4" v-for="(album, albumIndex) in albums" :key="albumIndex" data-aos="fade-up">
          <div class="card gallery-card h-100 shadow-sm" @click="showAlbumModal(albumIndex)">
            <img :src="album.coverImage" class="card-img-top album-cover" :alt="album.title" loading="lazy">
            <div class="card-body text-center">
              <h5 class="card-title mb-0">{{ album.title }}</h5>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Album Detail Modal -->
    <div class="modal fade" id="albumModal" tabindex="-1" aria-labelledby="albumModalLabel" aria-hidden="true" ref="albumModalEl">
      <div class="modal-dialog modal-dialog-centered modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="albumModalLabel">{{ selectedAlbum ? selectedAlbum.title : '' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedAlbum">
              <div id="albumCarousel" class="carousel slide" data-bs-ride="carousel" ref="albumCarousel">
                <div class="carousel-inner">
                  <div class="carousel-item" :class="{ active: imgIndex === selectedImageIndex }" v-for="(image, imgIndex) in selectedAlbum.images" :key="imgIndex">
                    <img :src="image.src" class="d-block w-100 carousel-slide-img" :alt="image.description">
                  </div>
                </div>
                <button class="carousel-control-prev" type="button" data-bs-target="#albumCarousel" data-bs-slide="prev">
                  <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                  <span class="visually-hidden">Previous</span>
                </button>
                <button class="carousel-control-next" type="button" data-bs-target="#albumCarousel" data-bs-slide="next">
                  <span class="carousel-control-next-icon" aria-hidden="true"></span>
                  <span class="visually-hidden">Next</span>
                </button>
              </div>
              <div class="image-info text-center mt-3">
                <p class="mb-0 text-muted">{{ selectedAlbum.images[selectedImageIndex]?.description || '' }}</p>
              </div>
              <!-- Thumbnail Strip -->
              <div class="thumbnail-strip mt-3">
                <div class="thumbnails-container d-flex justify-content-center">
                  <img
                    v-for="(image, imgIndex) in selectedAlbum.images"
                    :key="imgIndex"
                    :src="image.src"
                    class="thumbnail-img mx-1 rounded"
                    :class="{ active: imgIndex === selectedImageIndex }"
                    @click="goToImage(imgIndex)"
                    :alt="`Thumbnail ${imgIndex + 1}`"
                  >
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">關閉</button>
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
      albums: [
        {
          title: '2023 年度成果展',
          coverImage: 'https://picsum.photos/600/400?random=23',
          images: [
            { src: 'https://picsum.photos/800/600?random=23', description: '學員們一年努力的成果展示 - 精彩瞬間1' },
            { src: 'https://picsum.photos/800/600?random=231', description: '學員們一年努力的成果展示 - 精彩瞬間2' },
            { src: 'https://picsum.photos/800/600?random=232', description: '學員們一年努力的成果展示 - 精彩瞬間3' },
          ],
        },
        {
          title: '街舞大賽',
          coverImage: 'https://picsum.photos/600/400?random=24',
          images: [
            { src: 'https://picsum.photos/800/600?random=24', description: '熱血沸騰的街舞對決 - 選手風采1' },
            { src: 'https://picsum.photos/800/600?random=241', description: '熱血沸騰的街舞對決 - 選手風采2' },
            { src: 'https://picsum.photos/800/600?random=242', description: '熱血沸騰的街舞對決 - 選手風采3' },
          ],
        },
        {
          title: '國際大師工作坊',
          coverImage: 'https://picsum.photos/600/400?random=25',
          images: [
            { src: 'https://picsum.photos/800/600?random=25', description: '與國際知名舞者近距離學習 - 大師授課' },
            { src: 'https://picsum.photos/800/600?random=251', description: '與國際知名舞者近距離學習 - 互動交流' },
          ],
        },
        {
          title: '聖誕派對',
          coverImage: 'https://picsum.photos/600/400?random=26',
          images: [
            { src: 'https://picsum.photos/800/600?random=26', description: '充滿歡樂與舞蹈的聖誕節 - 派對現場' },
            { src: 'https://picsum.photos/800/600?random=261', description: '充滿歡樂與舞蹈的聖誕節 - 聖誕表演' },
          ],
        },
        {
          title: '快閃活動',
          coverImage: 'https://picsum.photos/600/400?random=27',
          images: [
            { src: 'https://picsum.photos/800/600?random=27', description: '街頭突襲，展現舞蹈魅力 - 街頭快閃' },
            { src: 'https://picsum.photos/800/600?random=271', description: '街頭突襲，展現舞蹈魅力 - 觀眾互動' },
          ],
        },
        {
          title: '學員練習日常',
          coverImage: 'https://picsum.photos/600/400?random=28',
          images: [
            { src: 'https://picsum.photos/800/600?random=28', description: '舞者們日復一日的堅持與努力 - 練習剪影' },
            { src: 'https://picsum.photos/800/600?random=281', description: '舞者們日復一日的堅持與努力 - 汗水與堅持' },
          ],
        },
      ],
      selectedAlbum: null,
      selectedImageIndex: 0,
      albumModal: null
    };
  },
  mounted() {
    const el = document.getElementById('albumModal');
    if (el) {
      this.albumModal = new Modal(el);
    }
  },
  beforeUnmount() {
    if (this.albumModal) this.albumModal.dispose();
    if (this.carouselInstance) this.carouselInstance.dispose();
    this.cleanupSwipe();
  },
  methods: {
    showAlbumModal(albumIndex) {
      this.selectedAlbum = this.albums[albumIndex];
      this.selectedImageIndex = 0;

      this.$nextTick(() => {
        if (this.carouselInstance) {
          this.carouselInstance.dispose();
        }
        if (this.$refs.albumCarousel) {
          this.carouselInstance = new Carousel(this.$refs.albumCarousel);
          this.carouselInstance.to(0);
          this.setupSwipe();
        }
        this.albumModal?.show();
      });
    },
    goToImage(imgIndex) {
      this.selectedImageIndex = imgIndex;
      this.carouselInstance?.to(imgIndex);
    }
  }
};
</script>

<style scoped>
.gallery-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.gallery-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

.album-cover {
  height: 240px;
  object-fit: cover;
}

.carousel-slide-img {
  max-height: 550px;
  object-fit: contain;
  background-color: #000;
}

.thumbnail-strip {
  overflow-x: auto;
  white-space: nowrap;
  padding: 4px 0;
}

.thumbnails-container {
  display: inline-flex;
}

.thumbnail-img {
  width: 80px;
  height: 60px;
  object-fit: cover;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s ease;
}

.thumbnail-img.active {
  border-color: #0d6efd;
}
</style>