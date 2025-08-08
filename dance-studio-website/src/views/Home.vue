<template>
  <div class="home">
    <!-- 1. Hero Carousel -->
    <div id="heroCarousel" class="carousel slide" data-bs-ride="carousel" ref="heroCarousel">
      <div class="carousel-inner">
        <div class="carousel-item active">
          <img src="https://picsum.photos/1920/1080?random=1" class="d-block w-100" alt="Dance Studio Image 1">
        </div>
        <div class="carousel-item">
          <img src="https://picsum.photos/1920/1080?random=2" class="d-block w-100" alt="Dance Studio Image 2">
        </div>
        <div class="carousel-item">
          <img src="https://picsum.photos/1920/1080?random=3" class="d-block w-100" alt="Dance Studio Image 3">
        </div>
      </div>
      <button class="carousel-control-prev" type="button" data-bs-target="#heroCarousel" data-bs-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Previous</span>
      </button>
      <button class="carousel-control-next" type="button" data-bs-target="#heroCarousel" data-bs-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Next</span>
      </button>
    </div>

    <!-- 2. Latest News Component -->
    <NewsList @show-detail="showNewsDetail" data-aos="fade-up" />

    <!-- News Detail Modal -->
    <div class="modal fade" id="newsDetailModal" tabindex="-1" aria-labelledby="newsDetailModalLabel" aria-hidden="true" data-bs-backdrop="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="newsDetailModalLabel">{{ selectedNews.title }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>{{ selectedNews.fullContent }}</p>
            <small class="text-muted">{{ selectedNews.date }}</small>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">關閉</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Detail Modal -->
    <div class="modal fade" id="eventDetailModal" tabindex="-1" aria-labelledby="eventDetailModalLabel" aria-hidden="true" data-bs-backdrop="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="eventDetailModalLabel">{{ selectedEvent.title }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <img :src="selectedEvent.image" class="img-fluid mb-3" :alt="selectedEvent.title" v-if="selectedEvent.image">
            <p>{{ selectedEvent.fullContent }}</p>
            <small class="text-muted">{{ selectedEvent.date }}</small>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">關閉</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Featured Instructor Component -->
    <FeaturedInstructor data-aos="fade-up" />

    <!-- 4. Recent Events Component -->
    <RecentEvents :events="events" @show-detail="showEventDetail" data-aos="fade-up" />

    <!-- 5. Video Gallery Component -->
    <VideoGallery data-aos="fade-up" />

  </div>
</template>

<script>
import { Modal, Carousel } from 'bootstrap';
import NewsList from '../components/NewsList.vue';
import FeaturedInstructor from '../components/FeaturedInstructor.vue';
import RecentEvents from '../components/RecentEvents.vue';
import VideoGallery from '../components/VideoGallery.vue';

export default {
  name: 'Home',
  components: {
    NewsList,
    FeaturedInstructor,
    RecentEvents,
    VideoGallery,
  },
  data() {
    return {
      selectedNews: {},
      selectedEvent: {},
      carousel: null,
      startX: 0,
      isSwiping: false,
      
    };
  },
  mounted() {
    this.carousel = new Carousel(this.$refs.heroCarousel);
    const carouselElement = this.$refs.heroCarousel;

    carouselElement.addEventListener('mousedown', this.handleMouseDown);
  },
  beforeUnmount() {
    const carouselElement = this.$refs.heroCarousel;
    if (carouselElement) {
      carouselElement.removeEventListener('mousedown', this.handleMouseDown);
      document.removeEventListener('mousemove', this.handleMouseMove);
      document.removeEventListener('mouseup', this.handleMouseUp);
    }
  },
  methods: {
    showNewsDetail(newsItem) {
      this.selectedNews = newsItem;
      const newsDetailModal = new Modal(document.getElementById('newsDetailModal'));
      newsDetailModal.show();
    },
    showEventDetail(eventItem) {
      this.selectedEvent = eventItem;
      const eventDetailModal = new Modal(document.getElementById('eventDetailModal'));
      eventDetailModal.show();
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
        this.carousel.prev();
      } else if (diffX < -50) {
        this.carousel.next();
      }
      document.removeEventListener('mousemove', this.handleMouseMove);
      document.removeEventListener('mouseup', this.handleMouseUp);
    },
    handleMouseLeave() {
      // This event listener is no longer strictly necessary for stopping swipe, as mouseup on document handles it.
      // However, if you want to stop swiping specifically when the mouse leaves the carousel element *without* releasing the button,
      // you might keep it and remove the document listeners here too.
      // For now, let's rely on mouseup on document.
      // If you re-enable this, make sure to remove document listeners here as well.
    },
  },
};
</script>

<style src="../assets/css/Home.css"></style>
<style>
.carousel-inner img {
  pointer-events: none;
}

/* Disable text selection for the carousel */
#heroCarousel {
  -webkit-touch-callout: none; /* iOS Safari */
  -webkit-user-select: none;   /* Safari */
  -khtml-user-select: none;    /* Konqueror HTML */
  -moz-user-select: none;      /* Old versions of Firefox */
  -ms-user-select: none;       /* Internet Explorer/Edge */
  user-select: none;           /* Non-prefixed version, currently supported by Chrome, Edge, Opera and Firefox */
}
</style>
