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
import { ref } from 'vue';
import { Modal, Carousel } from 'bootstrap';
import { useCarouselSwipe } from '@/composables/useCarouselSwipe';
import NewsList from '@/components/NewsList.vue';
import FeaturedInstructor from '@/components/FeaturedInstructor.vue';
import RecentEvents from '@/components/RecentEvents.vue';
import VideoGallery from '@/components/VideoGallery.vue';

export default {
  name: 'Home',
  components: {
    NewsList,
    FeaturedInstructor,
    RecentEvents,
    VideoGallery,
  },
  setup() {
    const heroCarousel = ref(null);
    const carouselInstance = ref(null);
    const { setupSwipe } = useCarouselSwipe(heroCarousel, carouselInstance);

    return { heroCarousel, carouselInstance, setupSwipe };
  },
  data() {
    return {
      selectedNews: {},
      selectedEvent: {},
      newsModal: null,
      eventModal: null,
      events: [
        {
          title: '年度成果展',
          shortDescription: '見證學員們一年來的努力與成長，帶來最精彩的演出。',
          fullContent: '一年一度的年度成果展即將盛大登場！本次展演將匯集各班級學員的精彩舞碼，從古典芭蕾到現代街舞，多元風格一次呈現。這不僅是學員們展現學習成果的舞台，更是對他們辛勤付出的最佳肯定。歡迎所有熱愛舞蹈的朋友們蒞臨觀賞，一同感受舞蹈的魅力與學員們的熱情！',
          date: '2024年12月15日',
          image: 'https://picsum.photos/600/400?random=5',
        },
        {
          title: '街舞比賽',
          shortDescription: '邀請各路好手一同切磋舞技，爭奪高額獎金。',
          fullContent: '熱血沸騰的街舞大賽即將引爆！無論你是 Locking、Popping、Breaking 還是 Hip-Hop 的高手，都歡迎你來挑戰。本次比賽設有豐厚獎金，並邀請業界知名舞者擔任評審，提供專業點評。這是一個展現自我、交流舞技的絕佳機會，快來報名，用你的舞步征服全場！',
          date: '2024年11月20日',
          image: 'https://picsum.photos/600/400?random=6',
        },
        {
          title: '國際大師工作坊',
          shortDescription: '難得的機會，邀請到國際知名舞者親自授課。',
          fullContent: '千載難逢的機會！我們榮幸邀請到國際頂尖舞者親臨本工作室，舉辦為期三天的舞蹈工作坊。大師將親自傳授其獨特的舞蹈技巧與表演理念，無論你是初學者還是資深舞者，都能從中獲益良多。名額有限，請盡速報名，把握與大師近距離學習的寶貴機會！',
          date: '2024年10月5日',
          image: 'https://picsum.photos/600/400?random=7',
        },
      ],
    };
  },
  mounted() {
    this.carouselInstance = new Carousel(this.$refs.heroCarousel);
    this.setupSwipe();

    // Create modals once, reuse them
    this.newsModal = new Modal(document.getElementById('newsDetailModal'));
    this.eventModal = new Modal(document.getElementById('eventDetailModal'));
  },
  beforeUnmount() {
    // Dispose modal instances to prevent memory leaks
    if (this.newsModal) this.newsModal.dispose();
    if (this.eventModal) this.eventModal.dispose();
    if (this.carouselInstance) this.carouselInstance.dispose();
  },
  methods: {
    showNewsDetail(newsItem) {
      this.selectedNews = newsItem;
      this.newsModal.show();
    },
    showEventDetail(eventItem) {
      this.selectedEvent = eventItem;
      this.eventModal.show();
    },
  },
};
</script>

<style scoped>
.carousel-item img {
  height: 600px;
  object-fit: cover;
}

.bg-light {
  background-color: #f8f9fa !important;
}

/* Recent Events Card Styling — needs :deep() for child component cards */
:deep(.card) {
  height: 100%;
}

:deep(.card-img-top) {
  height: 200px;
  object-fit: cover;
}

:deep(.card-body) {
  display: flex;
  flex-direction: column;
  min-height: 150px;
}

:deep(.card-text) {
  flex-grow: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

/* Ensure columns fill row height */
:deep(.container.my-5 > .row) {
  display: flex;
  align-items: stretch;
}

/* Add padding to content to prevent it from being hidden behind fixed navbar */
.content-wrapper {
  padding-top: 50px;
}

.carousel-inner img {
  pointer-events: none;
}

/* Disable text selection for the carousel */
#heroCarousel {
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
</style>
