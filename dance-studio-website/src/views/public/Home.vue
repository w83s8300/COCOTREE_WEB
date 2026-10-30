<template>
  <div class="home">
    <!-- 1. Hero Carousel (動態串接首頁橫幅 API) -->
    <div id="heroCarousel" class="carousel slide carousel-fade position-relative" data-bs-ride="carousel" ref="heroCarousel">
      <div v-if="banners.length > 1" class="carousel-indicators">
        <button
          v-for="(banner, index) in banners"
          :key="'indicator-' + (banner.id || index)"
          type="button"
          data-bs-target="#heroCarousel"
          :data-bs-slide-to="index"
          :class="{ active: index === 0 }"
          :aria-current="index === 0 ? 'true' : undefined"
          :aria-label="'Slide ' + (index + 1)"
        ></button>
      </div>

      <div class="carousel-inner">
        <div
          v-for="(banner, index) in banners"
          :key="banner.id || index"
          class="carousel-item"
          :class="{ active: index === 0 }"
          :data-bs-interval="banner.interval_ms || 5000"
        >
          <div class="carousel-overlay"></div>
          <img
            :src="banner.image_url"
            class="d-block w-100 hero-img"
            :alt="banner.title"
            @error="handleBannerImgError"
          >
          <div class="carousel-caption text-start pb-5">
            <span
              v-if="banner.badge_text"
              class="badge px-3 py-2 rounded-pill fw-bold mb-3 shadow-sm d-inline-block"
              :class="getBadgeClass(banner.badge_color)"
            >
              {{ banner.badge_text }}
            </span>
            <h1 class="display-4 fw-bold text-white mb-3 text-shadow">{{ banner.title }}</h1>
            <p v-if="banner.subtitle" class="lead text-white-50 mb-4 d-none d-md-block text-shadow" style="max-width: 650px;">
              {{ banner.subtitle }}
            </p>
            <div class="d-flex flex-wrap gap-3">
              <!-- 主要按鈕 -->
              <template v-if="banner.primary_button_text">
                <a
                  v-if="isExternalLink(banner.primary_button_link)"
                  :href="banner.primary_button_link"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-lg rounded-pill px-4 shadow"
                  :class="getBtnClass(banner.primary_button_style)"
                >
                  <i class="bi bi-box-arrow-up-right me-1 small"></i>{{ banner.primary_button_text }}
                </a>
                <router-link
                  v-else
                  :to="banner.primary_button_link || '/schedule'"
                  class="btn btn-lg rounded-pill px-4 shadow"
                  :class="getBtnClass(banner.primary_button_style)"
                >
                  <i v-if="banner.primary_button_link === '/schedule'" class="bi bi-calendar3 me-2"></i>
                  {{ banner.primary_button_text }}
                </router-link>
              </template>

              <!-- 次要按鈕 -->
              <template v-if="banner.secondary_button_text">
                <a
                  v-if="isExternalLink(banner.secondary_button_link)"
                  :href="banner.secondary_button_link"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-lg rounded-pill px-4"
                  :class="getBtnClass(banner.secondary_button_style)"
                >
                  {{ banner.secondary_button_text }}
                </a>
                <router-link
                  v-else
                  :to="banner.secondary_button_link || '/about'"
                  class="btn btn-lg rounded-pill px-4"
                  :class="getBtnClass(banner.secondary_button_style)"
                >
                  {{ banner.secondary_button_text }}
                </router-link>
              </template>
            </div>
          </div>
        </div>
      </div>

      <template v-if="banners.length > 1">
        <button class="carousel-control-prev" type="button" data-bs-target="#heroCarousel" data-bs-slide="prev">
          <span class="carousel-control-prev-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Previous</span>
        </button>
        <button class="carousel-control-next" type="button" data-bs-target="#heroCarousel" data-bs-slide="next">
          <span class="carousel-control-next-icon" aria-hidden="true"></span>
          <span class="visually-hidden">Next</span>
        </button>
      </template>
    </div>

    <!-- 2. Latest News Component (串接後台資料) -->
    <NewsList @show-detail="showNewsDetail" data-aos="fade-up" />

    <!-- 3. 熱門推薦課程 (串接後台 /api/courses) -->
    <div class="container my-5 py-3" data-aos="fade-up">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-end mb-4">
        <div>
          <h2 class="fw-bold mb-2">熱門精選課程 / FEATURED COURSES</h2>
          <p class="text-muted mb-0">專業多元的舞風系列，循序漸進引導你掌握身體律動</p>
        </div>
        <router-link to="/schedule" class="btn btn-outline-dark btn-sm rounded-pill mt-3 mt-md-0 px-3 align-self-start align-self-md-auto">
          完整課程表與報名 <i class="bi bi-arrow-right ms-1"></i>
        </router-link>
      </div>

      <div v-if="coursesLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
      </div>

      <div v-else class="row g-4 justify-content-center">
        <div
          v-for="(course, idx) in featuredCourses"
          :key="course.id"
          class="col-md-6 col-lg-3"
        >
          <div class="card h-100 border-0 shadow-sm course-card overflow-hidden">
            <div class="course-header p-3 text-white d-flex justify-content-between align-items-center" :style="{ backgroundColor: getCourseHeaderColor(idx) }">
              <span class="badge bg-white text-dark fw-bold shadow-sm">
                {{ course.style_name || '人氣舞風' }}
              </span>
              <span class="small fw-bold opacity-90">
                <i class="bi bi-stopwatch me-1"></i>{{ course.duration || 60 }} 分鐘
              </span>
            </div>
            <div class="card-body d-flex flex-column p-4 text-start">
              <h5 class="card-title fw-bold text-dark mb-2">{{ course.name }}</h5>
              <p class="card-text text-muted small flex-grow-1 mb-3" style="line-height: 1.6;">
                {{ course.description || '由專業舞蹈師資親自授課，結合基礎律動與熱門排舞教學。' }}
              </p>
              <div class="pt-3 border-top d-flex justify-content-between align-items-center">
                <div class="small text-secondary">
                  <i class="bi bi-person-fill text-primary me-1"></i>
                  <span class="fw-semibold text-dark">{{ course.teacher_name || '專業名師' }}</span>
                </div>
                <span v-if="course.difficulty" class="badge bg-light text-secondary border small">
                  {{ course.difficulty }}
                </span>
              </div>
              <router-link to="/schedule" class="btn btn-primary btn-sm rounded-pill mt-3 fw-bold py-2 shadow-sm">
                <i class="bi bi-calendar-check me-1"></i>預約課程
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. Featured Instructor Component (串接後台資料) -->
    <FeaturedInstructor data-aos="fade-up" />

    <!-- 5. Recent Events Component (串接後台活動資料) -->
    <RecentEvents :events="events" @show-detail="showEventDetail" data-aos="fade-up" />

    <!-- Modals (Teleport to body to prevent stacking context / backdrop overlay issues) -->
    <teleport to="body">
      <!-- News Detail Modal -->
      <div class="modal fade" id="newsDetailModal" tabindex="-1" aria-labelledby="newsDetailModalLabel" aria-hidden="true" data-bs-backdrop="true" style="z-index: 1070;">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
            <div class="modal-header bg-dark text-white p-4">
              <div>
                <span v-if="selectedNews.tag" class="badge bg-primary mb-2">{{ selectedNews.tag }}</span>
                <h5 class="modal-title fw-bold mb-0" id="newsDetailModalLabel">{{ selectedNews.title }}</h5>
              </div>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-4 text-start">
              <div class="small text-muted mb-3 d-flex align-items-center">
                <i class="bi bi-calendar-event me-2 text-primary"></i>發布日期：{{ selectedNews.publish_date || selectedNews.date }}
              </div>
              <p class="text-dark lh-lg" style="white-space: pre-line; font-size: 1.05rem;">
                {{ selectedNews.content || selectedNews.fullContent || selectedNews.summary }}
              </p>
            </div>
            <div class="modal-footer bg-light border-top-0 px-4 py-3">
              <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">關閉</button>
              <router-link to="/schedule" class="btn btn-primary rounded-pill px-4" data-bs-dismiss="modal">
                前往報名課程
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Event Detail Modal -->
      <div class="modal fade" id="eventDetailModal" tabindex="-1" aria-labelledby="eventDetailModalLabel" aria-hidden="true" data-bs-backdrop="true" style="z-index: 1070;">
        <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
            <div class="modal-header bg-dark text-white p-4">
              <div>
                <span v-if="selectedEvent.tag" class="badge bg-danger mb-2">{{ selectedEvent.tag }}</span>
                <h5 class="modal-title fw-bold mb-0" id="eventDetailModalLabel">{{ selectedEvent.title }}</h5>
              </div>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-4 text-start">
              <div v-if="selectedEvent.image_url || selectedEvent.image" class="mb-3 rounded-3 overflow-hidden" style="max-height: 320px;">
                <img :src="selectedEvent.image_url || selectedEvent.image" class="img-fluid w-100 object-fit-cover" :alt="selectedEvent.title">
              </div>
              <div class="small text-muted mb-3 d-flex align-items-center">
                <i class="bi bi-calendar-check me-2 text-danger"></i>活動日期：{{ selectedEvent.publish_date || selectedEvent.date }}
              </div>
              <p class="text-dark lh-lg" style="white-space: pre-line; font-size: 1.05rem;">
                {{ selectedEvent.content || selectedEvent.fullContent || selectedEvent.summary }}
              </p>
            </div>
            <div class="modal-footer bg-light border-top-0 px-4 py-3">
              <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">關閉</button>
              <router-link to="/contact" class="btn btn-primary rounded-pill px-4" data-bs-dismiss="modal">
                聯絡我們洽詢
              </router-link>
            </div>
          </div>
        </div>
      </div>



    </teleport>
  </div>
</template>

<script>
import { ref } from 'vue';
import { Modal, Carousel } from 'bootstrap';
import { useCarouselSwipe } from '@/composables/useCarouselSwipe';
import api, { API_ENDPOINTS } from '@/utils/api';
import NewsList from '@/components/NewsList.vue';
import FeaturedInstructor from '@/components/FeaturedInstructor.vue';
import RecentEvents from '@/components/RecentEvents.vue';

const FALLBACK_BANNERS = [
  {
    id: 1,
    title: '釋放你的節奏，舞出你的熱情',
    subtitle: '無論是零基礎新手或資深舞者，在 Dance Studio 都能找到最適合你的專屬舞台。',
    badge_text: '✨ 啟動你的舞蹈新生活',
    badge_color: 'warning',
    image_url: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=1920&q=80',
    primary_button_text: '立即預約課程',
    primary_button_link: '/schedule',
    primary_button_style: 'primary',
    secondary_button_text: '認識師資團隊',
    secondary_button_link: '/instructors',
    secondary_button_style: 'outline-light',
    interval_ms: 5000,
    sort_order: 1,
    is_active: true
  },
  {
    id: 2,
    title: '多元舞風體系 × 專業細膩教學',
    subtitle: '流行街舞、K-POP MV、抒情爵士、芭蕾律動，循序漸進拆解每個核心動作。',
    badge_text: '👑 頂尖專業名師陣容',
    badge_color: 'primary',
    image_url: 'https://images.unsplash.com/photo-1547153760-18fc86324498?auto=format&fit=crop&w=1920&q=80',
    primary_button_text: '查看本週課表',
    primary_button_link: '/schedule',
    primary_button_style: 'warning',
    secondary_button_text: '課程收費方案',
    secondary_button_link: '/pricing',
    secondary_button_style: 'outline-light',
    interval_ms: 5000,
    sort_order: 2,
    is_active: true
  },
  {
    id: 3,
    title: '高規格減震地板與專業環繞音響',
    subtitle: '四大獨立主題練習室，明亮寬敞的空間與貼心休息區，享受最極致的跳舞體驗。',
    badge_text: '🏢 專業國際級練習空間',
    badge_color: 'success',
    image_url: 'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=1920&q=80',
    primary_button_text: '參觀場地環境',
    primary_button_link: '/venue',
    primary_button_style: 'light',
    secondary_button_text: '關於我們',
    secondary_button_link: '/about',
    secondary_button_style: 'outline-light',
    interval_ms: 5000,
    sort_order: 3,
    is_active: true
  }
];

const FALLBACK_EVENTS = [
  {
    id: 4,
    title: '年度舞蹈成果發表會「舞動星芒」盛大登場',
    tag: '年度盛典',
    date: '2026-10-18',
    summary: '見證學員們一年來的努力與蛻變，帶來最震撼視覺與心靈的舞台演出！',
    content: '一年一度的年度大型舞蹈成果發表會即將震撼登場！本次展演匯集各班學員、人氣名師與特邀嘉賓的精彩舞碼，古典與現代交織，熱情綻放。誠摯邀請所有喜愛舞蹈的家人與朋友們蒞臨共襄盛舉！',
    image_url: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 5,
    title: '全台街舞爭霸賽 Street Battle 2026',
    tag: '賽事競技',
    date: '2026-10-13',
    summary: '集結各路街舞頂尖好手切磋交流，爭奪年度冠軍與高額獎金！',
    content: '熱血沸騰的年度街舞大賽即將引爆！無論你是 Locking、Popping、Breaking 還是 Hip-Hop 高手，都歡迎踏上舞台挑戰自我。特邀國際級評審陣容親臨點評，快帶上你的節奏與舞步來制霸全場！',
    image_url: 'https://images.unsplash.com/photo-1535525153412-5a42439a210d?auto=format&fit=crop&w=800&q=80',
  },
  {
    id: 6,
    title: '國際大師特別工作坊 Masterclass',
    tag: '大師專班',
    date: '2026-10-08',
    summary: '難得一見的跨國大師親臨現場，帶領學員體驗國際前沿舞蹈風格。',
    content: '我們特別邀請到享譽國際的頂尖舞者親臨本館，舉辦為期三天的密集大師工作坊。大師將親自傳授獨門編舞架構與身體控制心法，名額非常有限，把握千載難逢的近距離學習機會！',
    image_url: 'https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?auto=format&fit=crop&w=800&q=80',
  },
];

const COURSE_HEADER_COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#06b6d4'];

export default {
  name: 'Home',
  components: {
    NewsList,
    FeaturedInstructor,
    RecentEvents,
  },
  setup() {
    const heroCarousel = ref(null);
    const carouselInstance = ref(null);
    const { setupSwipe } = useCarouselSwipe(heroCarousel, carouselInstance);

    return { heroCarousel, carouselInstance, setupSwipe };
  },
  data() {
    return {
      banners: [...FALLBACK_BANNERS],
      selectedNews: {},
      selectedEvent: {},
      newsModal: null,
      eventModal: null,
      events: [...FALLBACK_EVENTS],
      featuredCourses: [],
      coursesLoading: false,
    };
  },
  created() {
    this.fetchBanners();
    this.fetchEvents();
    this.fetchFeaturedCourses();
  },
  mounted() {
    this.reinitCarousel();

    // Create modals once, reuse them
    this.newsModal = new Modal(document.getElementById('newsDetailModal'));
    this.eventModal = new Modal(document.getElementById('eventDetailModal'));
  },
  beforeUnmount() {
    if (this.newsModal) this.newsModal.dispose();
    if (this.eventModal) this.eventModal.dispose();
    if (this.carouselInstance) this.carouselInstance.dispose();
  },
  methods: {
    async fetchBanners() {
      try {
        const res = await api.get('/banners');
        if (res.success && Array.isArray(res.banners) && res.banners.length > 0) {
          this.banners = res.banners;
          this.$nextTick(() => {
            this.reinitCarousel();
          });
        }
      } catch (e) {
        // 保留 FALLBACK_BANNERS
      }
    },
    reinitCarousel() {
      if (this.carouselInstance) {
        this.carouselInstance.dispose();
      }
      if (this.$refs.heroCarousel) {
        this.carouselInstance = new Carousel(this.$refs.heroCarousel, {
          interval: 5000,
          pause: 'hover'
        });
        this.setupSwipe();
      }
    },
    handleBannerImgError(e) {
      e.target.src = 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=1920&q=80';
    },
    getBadgeClass(color) {
      const c = color || 'warning';
      const isLight = ['warning', 'light', 'info'].includes(c);
      return `bg-${c} ${isLight ? 'text-dark' : 'text-white'}`;
    },
    getBtnClass(style) {
      const s = (style || 'primary').trim();
      if (s.startsWith('btn-')) return s;
      if (s.startsWith('outline-')) return `btn-${s}`;
      if (s === 'light' || s === 'warning') return `btn-${s} text-dark fw-bold`;
      return `btn-${s}`;
    },
    isExternalLink(url) {
      if (!url) return false;
      return url.startsWith('http://') || url.startsWith('https://');
    },
    async fetchEvents() {
      try {
        const res = await api.get('/news?category=event');
        if (res.success && Array.isArray(res.news) && res.news.length > 0) {
          this.events = res.news;
        }
      } catch (e) {
        // Fallback to FALLBACK_EVENTS
      }
    },
    async fetchFeaturedCourses() {
      this.coursesLoading = true;
      try {
        const res = await api.get(API_ENDPOINTS.COURSES);
        const list = res.courses || res || [];
        if (Array.isArray(list) && list.length > 0) {
          this.featuredCourses = list.slice(0, 4);
        }
      } catch (e) {
        console.error('獲取精選課程失敗:', e);
      } finally {
        this.coursesLoading = false;
      }
    },
    getCourseHeaderColor(index) {
      return COURSE_HEADER_COLORS[index % COURSE_HEADER_COLORS.length];
    },
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
.carousel-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.7) 100%);
  z-index: 1;
}

.hero-img {
  height: 620px;
  object-fit: cover;
}

.carousel-caption {
  z-index: 2;
  bottom: 10%;
  left: 8%;
  right: 8%;
}

.course-card {
  border-radius: 14px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important;
}

.bg-light {
  background-color: #f8f9fa !important;
}

#heroCarousel {
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.text-shadow {
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.7);
}
</style>
