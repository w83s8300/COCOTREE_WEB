<template>
  <div class="container my-5">
    <h2 class="text-center mb-4">最新消息</h2>
    <div class="list-group">
      <button type="button" class="list-group-item list-group-item-action" v-for="(newsItem, index) in news" :key="index" @click.prevent="emitShowDetail(newsItem)">
        <div class="d-flex w-100 justify-content-between">
          <h5 class="mb-1">{{ newsItem.title }}</h5>
          <small>{{ newsItem.date }}</small>
        </div>
        <p class="mb-1">{{ newsItem.summary }}</p>
      </button>
      <!-- <a class="list-group-item list-group-item-action" v-for="(newsItem, index) in news" :key="index" @click.prevent="emitShowDetail(newsItem)">
        <div class="d-flex w-100 justify-content-between">
          <h5 class="mb-1">{{ newsItem.title }}</h5>
          <small>{{ newsItem.date }}</small>
        </div>
        <p class="mb-1">{{ newsItem.summary }}</p>
      </a> -->
    </div>
  </div>
</template>

<script>
export default {
  name: 'NewsList',
  data() {
    return {
      news: [
        {
          title: '暑期舞蹈密集班開放報名',
          date: '3 days ago',
          summary: '一年一度的暑期密集班來囉！早鳥優惠實施中。',
          fullContent: '詳細內容：一年一度的暑期密集班現已開放報名！我們提供多種舞風課程，適合不同程度的學員。現在報名可享早鳥優惠，名額有限，請盡速報名！詳細課程內容和報名方式請參考官方網站。',
        },
        {
          title: '週末特別課程：MV Dance',
          date: '1 week ago',
          summary: '想學最新最流行的 K-POP 舞蹈嗎？千萬不要錯過！',
          fullContent: '詳細內容：本週末特別推出 MV Dance 課程，由專業老師帶領您學習最新最流行的 K-POP 舞蹈。無論您是初學者還是有經驗的舞者，都能在這裡找到樂趣。名額有限，請提早預約！',
        },
        {
          title: '工作室場地租借優惠',
          date: '2 weeks ago',
          summary: '平日下午時段場地租借全面八折。',
          fullContent: '詳細內容：為回饋廣大學員，即日起平日下午時段（週一至週五 13:00-17:00）工作室場地租借全面八折優惠。適合團體練習、個人排練或舉辦小型活動。歡迎來電洽詢預約！',
        },
      ],
    };
  },
  methods: {
    emitShowDetail(newsItem) {
      this.$emit('show-detail', newsItem);
    },
  },
};
</script>

<style scoped>
/* Add any specific styles for NewsList here if needed */
</style>
