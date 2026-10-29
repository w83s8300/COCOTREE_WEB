<template>
  <div class="container my-5">
    <div class="text-center mb-4">
      <h2 class="fw-bold mb-2">最新消息 / LATEST NEWS</h2>
      <p class="text-muted">掌握 Dance Studio 最新熱門課程、重要公告與專屬優惠</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="news.length === 0" class="text-center py-4 text-muted">
      <p>目前尚無最新消息。</p>
    </div>

    <!-- News List (最多顯示 3 則，超過透過彈窗查看全部) -->
    <div v-else>
      <div class="list-group shadow-sm border-0 rounded-4 overflow-hidden mb-3">
        <button
          type="button"
          class="list-group-item list-group-item-action p-3 p-md-4 border-bottom news-item-btn"
          v-for="newsItem in displayedNews"
          :key="newsItem.id || newsItem.title"
          @click.prevent="emitShowDetail(newsItem)"
        >
          <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2 mb-2">
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <span class="badge" :class="getTagBadgeClass(newsItem.tag)">
                {{ newsItem.tag || '公告' }}
              </span>
              <h5 class="mb-0 fw-bold text-dark">{{ newsItem.title }}</h5>
            </div>
            <small class="text-muted text-nowrap">
              <i class="bi bi-clock me-1"></i>{{ newsItem.publish_date || newsItem.date }}
            </small>
          </div>
          <p class="mb-0 text-muted text-start text-truncate-2" style="line-height: 1.6;">
            {{ newsItem.summary }}
          </p>
        </button>
      </div>

      <!-- 超過 3 則顯示查看更多彈窗按鈕 -->
      <div v-if="news.length > 3" class="text-center mt-3">
        <button
          type="button"
          class="btn btn-outline-dark rounded-pill px-4 py-2 shadow-sm d-inline-flex align-items-center gap-2"
          @click="openAllNewsModal"
        >
          <i class="bi bi-collection"></i>
          <span>查看更多最新消息 (共 {{ news.length }} 則)</span>
          <i class="bi bi-arrow-right"></i>
        </button>
      </div>
    </div>

    <!-- 全部最新消息彈窗 (超過 3 則時跳窗展示，使用 Teleport 脫離父層 AOS transform 堆疊上下文) -->
    <teleport to="body">
      <div
        class="modal fade"
        id="allNewsModal"
        tabindex="-1"
        aria-labelledby="allNewsModalLabel"
        aria-hidden="true"
        ref="allNewsModalRef"
        style="z-index: 1060;"
      >
        <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
          <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
            <div class="modal-header bg-dark text-white p-4">
              <div>
                <h5 class="modal-title fw-bold mb-1" id="allNewsModalLabel">
                  <i class="bi bi-newspaper me-2 text-primary"></i>全部最新消息
                </h5>
                <small class="text-white-50">Dance Studio 歷年課程公告與優惠消息 (共 {{ news.length }} 則)</small>
              </div>
              <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-3 p-md-4 bg-light">
              <div class="list-group shadow-sm border-0 rounded-4 overflow-hidden">
                <button
                  type="button"
                  class="list-group-item list-group-item-action p-3 p-md-4 border-bottom news-item-btn bg-white"
                  v-for="item in news"
                  :key="'modal-' + (item.id || item.title)"
                  @click.prevent="handleSelectNewsFromModal(item)"
                >
                  <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2 mb-2">
                    <div class="d-flex align-items-center gap-2 flex-wrap">
                      <span class="badge" :class="getTagBadgeClass(item.tag)">
                        {{ item.tag || '公告' }}
                      </span>
                      <h6 class="mb-0 fw-bold text-dark fs-6">{{ item.title }}</h6>
                    </div>
                    <small class="text-muted text-nowrap">
                      <i class="bi bi-clock me-1"></i>{{ item.publish_date || item.date }}
                    </small>
                  </div>
                  <p class="mb-0 text-muted text-start text-truncate-2 small" style="line-height: 1.6;">
                    {{ item.summary }}
                  </p>
                </button>
              </div>
            </div>
            <div class="modal-footer bg-white border-top-0 px-4 py-3">
              <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">關閉</button>
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import api from '@/utils/api';

const FALLBACK_NEWS = [
  {
    id: 1,
    title: '2026 舞蹈常態密集班全面開放預約',
    tag: '課程公告',
    date: '2026-10-18',
    summary: '新學期常態課程與密集專班現已開放線上預約！早鳥報名享單堂或套票專屬優惠。',
    content: '一年一度的全新常態與密集舞蹈專班現已開放報名！我們提供街舞、K-POP MV、抒情爵士、當代舞等多種風格課程，適合各程度學員。無論您是零基礎初學者還是想精進舞技的舞者，歡迎即刻透過官網線上預約或洽詢櫃檯！',
  },
  {
    id: 2,
    title: '週末特別企劃：韓風 K-POP MV Dance 專攻班',
    tag: '熱門推薦',
    date: '2026-10-15',
    summary: '想在短短兩小時內完整學會最新爆紅 K-POP 舞蹈副歌嗎？千萬別錯過！',
    content: '本週末特別推出韓風 K-POP MV Dance 舞蹈專班，由專業授課老師手把手帶領拆解動作細節與走位。小班制互動教學，名額有限，立即線上預約卡位！',
  },
  {
    id: 3,
    title: '平日下午時段場地租借優惠實施中',
    tag: '場地優惠',
    date: '2026-10-11',
    summary: '平日 13:00-17:00 租借各大教室全面享 8 折特惠，適合個人自主排練與舞團集訓。',
    content: '為回饋廣大學員與舞團，即日起平日下午離峰時段（週一至週五 13:00-17:00）全館教室租借全面享八折優惠。教室配備專業級落地鏡、環繞音響與減震木地板，歡迎來電或加入官方社群預約！',
  },
];

export default {
  name: 'NewsList',
  emits: ['show-detail'],
  data() {
    return {
      news: [...FALLBACK_NEWS],
      loading: false,
      allNewsModalInstance: null
    };
  },
  computed: {
    // 首頁列表固定只顯示最新 3 則
    displayedNews() {
      return this.news.slice(0, 3);
    }
  },
  created() {
    this.fetchNews();
  },
  mounted() {
    if (this.$refs.allNewsModalRef) {
      this.allNewsModalInstance = new Modal(this.$refs.allNewsModalRef);
    }
  },
  beforeUnmount() {
    if (this.allNewsModalInstance) {
      this.allNewsModalInstance.dispose();
    }
  },
  methods: {
    async fetchNews() {
      this.loading = true;
      try {
        const res = await api.get('/news?category=news');
        if (res.success && Array.isArray(res.news) && res.news.length > 0) {
          this.news = res.news;
        }
      } catch (err) {
        // Fallback to initial seed news
      } finally {
        this.loading = false;
      }
    },
    emitShowDetail(newsItem) {
      this.$emit('show-detail', newsItem);
    },
    openAllNewsModal() {
      if (this.allNewsModalInstance) {
        this.allNewsModalInstance.show();
      }
    },
    handleSelectNewsFromModal(item) {
      if (this.allNewsModalInstance) {
        this.allNewsModalInstance.hide();
      }
      setTimeout(() => {
        this.emitShowDetail(item);
      }, 250);
    },
    getTagBadgeClass(tag) {
      if (!tag) return 'bg-primary';
      if (tag.includes('課程')) return 'bg-success';
      if (tag.includes('推薦') || tag.includes('熱門')) return 'bg-danger';
      if (tag.includes('優惠') || tag.includes('特惠')) return 'bg-warning text-dark';
      if (tag.includes('會員')) return 'bg-info text-dark';
      return 'bg-primary';
    }
  },
};
</script>

<style scoped>
.news-item-btn {
  transition: background-color 0.2s ease, transform 0.15s ease;
}
.news-item-btn:hover {
  background-color: #f8f9fa;
  transform: translateX(4px);
}
.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
