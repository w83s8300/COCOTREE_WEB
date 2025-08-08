<template>
  <div class="gallery-page">
    <!-- 1. Banner -->
    <div class="banner">
      <img src="https://picsum.photos/1920/500?random=22" alt="Gallery Banner" class="banner-img">
      <div class="banner-text">
        <h1>活動花絮 / GALLERY</h1>
      </div>
    </div>

    <!-- 2. Photo Albums -->
    <div class="container my-5">
      <div class="row">
        <div class="col-lg-4 col-md-6 mb-4" v-for="(album, albumIndex) in albums" :key="albumIndex">
          <div class="card gallery-card" @click="showAlbumModal(albumIndex)">
            <img :src="album.coverImage" class="card-img-top" :alt="album.title">
            <div class="card-body">
              <h5 class="card-title">{{ album.title }}</h5>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Album Detail Modal -->
    <div class="modal fade" id="albumModal" tabindex="-1" aria-labelledby="albumModalLabel" aria-hidden="true">
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
                    <img :src="image.src" class="d-block w-100" :alt="image.description">
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
                <p class="mb-0">{{ selectedAlbum.images[selectedImageIndex] ? selectedAlbum.images[selectedImageIndex].description : '' }}</p>
              </div>
              <!-- Thumbnail Strip -->
              <div class="thumbnail-strip mt-3">
                <div class="thumbnails-container d-flex justify-content-center">
                  <img v-for="(image, imgIndex) in selectedAlbum.images" :key="imgIndex" :src="image.src" class="thumbnail-img mx-1" :class="{ active: imgIndex === selectedImageIndex }" @click="goToImage(imgIndex)" :alt="`Thumbnail ${imgIndex + 1}`">
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
import { Modal, Carousel } from 'bootstrap';

export default {
  name: 'Gallery',
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
      albumCarousel: null,
      startX: 0,
      isSwiping: false,
    };
  },
  methods: {
    showAlbumModal(albumIndex) {
      this.selectedAlbum = this.albums[albumIndex];
      this.selectedImageIndex = 0; // Reset to the first image of the selected album

      this.$nextTick(() => {
        // Re-initialize carousel for the new album
        if (this.albumCarousel) {
          this.albumCarousel.dispose(); // Dispose previous instance if exists
        }
        this.albumCarousel = new Carousel(this.$refs.albumCarousel);
        this.albumCarousel.to(this.selectedImageIndex);

        // Add event listener for when the carousel slides to update selectedImageIndex
        this.$refs.albumCarousel.addEventListener('slid.bs.carousel', this.updateSelectedImageIndex);

        const albumModal = new Modal(document.getElementById('albumModal'));
        albumModal.show();

        // Add event listeners for swipe after modal is shown and carousel is initialized
        const carouselElement = this.$refs.albumCarousel;
        if (carouselElement) {
          carouselElement.addEventListener('mousedown', this.handleMouseDown);
        }
      });
    },
    updateSelectedImageIndex(event) {
      // Find the index of the new active item from the event's relatedTarget
      const activeItem = event.relatedTarget;
      if (activeItem) {
        const items = Array.from(activeItem.parentElement.children);
        const newIndex = items.indexOf(activeItem);
        if (newIndex > -1) {
          this.selectedImageIndex = newIndex;
        }
      }
    },
    handleMouseDown(e) {
      this.startX = e.pageX;
      this.isSwiping = true;
      document.addEventListener('mousemove', this.handleMouseMove);
      document.addEventListener('mouseup', this.handleMouseUp);
    },
    handleMouseMove(e) {
      if (!this.isSwiping) return;
      e.preventDefault();
    },
    handleMouseUp(e) {
      if (!this.isSwiping) return;
      this.isSwiping = false;
      const endX = e.pageX;
      const diffX = endX - this.startX;

      if (diffX > 50) {
        this.albumCarousel.prev();
      } else if (diffX < -50) {
        this.albumCarousel.next();
      }
      document.removeEventListener('mousemove', this.handleMouseMove);
      document.removeEventListener('mouseup', this.handleMouseUp);
    },
    goToImage(imgIndex) {
      this.albumCarousel.to(imgIndex);
    },
  },
  beforeUnmount() {
    const carouselElement = this.$refs.albumCarousel;
    if (carouselElement) {
      carouselElement.removeEventListener('mousedown', this.handleMouseDown);
      document.removeEventListener('mousemove', this.handleMouseMove);
      document.removeEventListener('mouseup', this.handleMouseUp);
      carouselElement.removeEventListener('slid.bs.carousel', this.updateSelectedImageIndex);
    }
  },
};
</script>

<style src="../assets/css/Gallery.css"></style>
<style>
.gallery-card {
  cursor: pointer;
}

.modal-body .carousel-inner img {
  pointer-events: none;
}

#albumCarousel {
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.thumbnail-strip {
  overflow-x: auto;
  white-space: nowrap;
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
  transition: border-color 0.3s ease;
}

.thumbnail-img.active {
  border-color: #007bff;
}
</style>