<template>
  <div class="container my-5">
    <h2 class="text-center mb-4">近期活動</h2>
    <div class="row">
      <div class="col-12 col-sm-6 col-md-4 mb-4" v-for="(event, index) in events" :key="index">
        <div class="card h-100">
          <img :src="event.image" class="card-img-top" :alt="event.title">
          <div class="card-body">
            <h5 class="card-title">{{ event.title }}</h5>
            <p class="card-text">{{ event.shortDescription }}</p>
            <!-- Removed modal trigger, consider adding a link to a detail page if needed -->
            <button @click="$emit('show-detail', event)" class="btn btn-primary">查看詳情</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
export default {
  name: 'RecentEvents',
  props: {
    events: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      selectedNews: {},
      selectedEvent: {},
      carousel: null,
      startX: 0,
      isSwiping: false,
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
  methods: {
  },
};
</script>

<style scoped>
/* Add any specific styles for RecentEvents here if needed */
</style>