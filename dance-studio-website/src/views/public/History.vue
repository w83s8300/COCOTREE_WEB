<template>
  <div class="history-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=8" title="品牌沿革 / HISTORY" />

    <!-- 2. Timeline -->
    <div class="container my-5">
      <div class="timeline">
        <div 
          v-for="item in milestones" 
          :key="item.year" 
          class="timeline-item"
          data-aos="fade-up"
        >
          <div class="timeline-year shadow">{{ item.year }}</div>
          <div class="timeline-content">
            <h5 class="fw-bold mb-2">{{ item.title }}</h5>
            <p class="text-muted lh-base mb-0">{{ item.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Brand Spirit & Philosophy -->
    <div class="bg-light py-5" data-aos="fade-up">
      <div class="container">
        <div class="row">
          <div class="col-md-6 mb-4 mb-md-0 text-start">
            <h3 class="text-center mb-3 fw-bold">品牌精神</h3>
            <p class="lh-lg text-muted">
              我們堅信，舞蹈是人類與生俱來的本能，更是跨越語言界限的靈魂共鳴。我們的使命是營造一個專業、多元且無拘無束的創作空間，讓每位走進教室的舞者都能找尋到自己的心跳節奏，自在展現真實自我的生命光芒。
            </p>
          </div>
          <div class="col-md-6 text-start">
            <h3 class="text-center mb-3 fw-bold">我們的堅持</h3>
            <p class="lh-lg text-muted">
              從極致嚴選的專業師資陣容、科學循序漸進的課綱設計，到嚴選防滑避震的舞蹈地板與環繞音響，我們對每一個環節絕不妥協。您的每一次揮灑汗水與成長喜悅，都是我們持續前行最大的驕傲。
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PageBanner from '@/components/PageBanner.vue';

export default {
  name: 'History',
  components: {
    PageBanner
  },
  data() {
    return {
      milestones: [
        {
          year: '2015',
          title: '創始啟程',
          description: '憑藉對舞蹈的純粹熱情，我們在一個小小的地下室建立了第一間舞蹈教室。雖然空間有限，但夢想無限。'
        },
        {
          year: '2017',
          title: '擴大經營',
          description: '隨著學員人數的快速增長，我們搬遷至市中心全新旗艦場地，引進多元舞風師資，吸引了更多熱愛跳舞的朋友。'
        },
        {
          year: '2020',
          title: '挑戰與數位轉型',
          description: '面對全球疫情的嚴峻挑戰，我們率先推出高畫質線上互動直播課程，讓學員在家也能不間斷練習，並拓展了海外學員網絡。'
        },
        {
          year: '2023',
          title: '舉辦全國舞蹈大賽',
          description: '成功籌辦第一屆「Dance Soul Cup」全國街舞大賽，匯聚全台數百位頂尖舞者同台競技，成為年度舞壇指標盛事。'
        },
        {
          year: 'Today',
          title: '持續深耕・展望未來',
          description: '我們將持續深化舞蹈教育體系，並積極引進國際大師工作坊，期待與每一位舞者一同踏出更多耀眼的舞步。'
        }
      ]
    };
  }
};
</script>

<style scoped>
.timeline {
  position: relative;
  padding: 2rem 0;
}

.timeline::before {
  content: '';
  position: absolute;
  top: 0;
  left: 15%;
  height: 100%;
  width: 4px;
  background: #e9ecef;
}

.timeline-item {
  margin-bottom: 2.5rem;
  position: relative;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-year {
  position: absolute;
  left: 15%;
  transform: translateX(-50%);
  top: 0;
  font-weight: bold;
  font-size: 1.1rem;
  background: linear-gradient(135deg, #212529 0%, #343a40 100%);
  color: white;
  border-radius: 50%;
  width: 75px;
  height: 75px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.timeline-content {
  margin-left: calc(15% + 55px);
  padding: 10px 20px;
  background: #ffffff;
  border-left: 3px solid #0d6efd;
  border-radius: 4px;
  text-align: left;
}

@media (max-width: 768px) {
  .timeline::before {
    left: 40px;
  }
  .timeline-year {
    left: 40px;
    width: 60px;
    height: 60px;
    font-size: 0.9rem;
  }
  .timeline-content {
    margin-left: 90px;
    padding-left: 10px;
  }
}
</style>