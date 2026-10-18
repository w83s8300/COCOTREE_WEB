<template>
  <div class="pricing-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=35" title="課程價目表 / PRICING" />

    <!-- 2. Pricing Cards -->
    <div class="container my-5">
      <div class="row">
        <div class="col-lg-3 col-md-6 mb-4" v-for="plan in plans" :key="plan.title" data-aos="fade-up">
          <div class="card text-center h-100 shadow-sm pricing-card" :class="{ 'border-primary': plan.isPopular }">
            <div class="card-header py-3" :class="plan.isPopular ? 'bg-primary text-white' : 'bg-light'">
              <span v-if="plan.isPopular" class="badge bg-warning text-dark mb-1">熱門推薦</span>
              <h4 class="my-0 fw-bold">{{ plan.title }}</h4>
            </div>
            <div class="card-body d-flex flex-column">
              <h2 class="card-title pricing-card-title fw-bold text-primary">{{ plan.price }}</h2>
              <small class="text-muted mb-4">{{ plan.unit }}</small>
              <ul class="list-unstyled mb-4 text-start flex-grow-1">
                <li v-for="(feature, fIndex) in plan.features" :key="fIndex" class="mb-2">
                  <i class="bi bi-check-circle-fill text-success me-2"></i>{{ feature }}
                </li>
              </ul>
              <router-link to="/contact" class="btn w-100" :class="plan.isPopular ? 'btn-primary' : 'btn-outline-primary'">
                立即預約
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Important Notes -->
      <div class="notes-section mt-5 p-4 bg-light rounded text-start shadow-sm" data-aos="fade-up">
        <h4 class="fw-bold mb-3">學員報名與上課須知</h4>
        <ul class="lh-lg mb-0">
          <li>所有常規課程皆需提前於線上系統或向官方 LINE 預約登記。</li>
          <li>堂數方案為個人專屬權益，限本人上課使用，不得轉讓或轉售他人。</li>
          <li>方案自購買啟用起計，請於各方案指定之有效期限內使用完畢。</li>
          <li>若需取消或請假，請最晚於課程開始前 2 小時完成線上取消，以免扣除堂數。</li>
          <li>如遇天然災害或政府宣佈停班停課，本工作室常規課程將自動順延。</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import PageBanner from '@/components/PageBanner.vue';

export default {
  name: 'Pricing',
  components: {
    PageBanner
  },
  data() {
    return {
      plans: [
        {
          title: '單堂體驗',
          price: '$500',
          unit: '/ 堂',
          isPopular: false,
          features: [
            '適合初次體驗的學員',
            '可任選一堂常規舞蹈課',
            '專業教練動作引導',
            '課後舞風諮詢'
          ]
        },
        {
          title: '小資方案',
          price: '$3,200',
          unit: '/ 8 堂 (平均 $400/堂)',
          isPopular: false,
          features: [
            '適合規律每週練習者',
            '使用期限 2 個月',
            '全時段常規課程皆適用',
            '請假彈性保留堂數'
          ]
        },
        {
          title: '熱血方案',
          price: '$6,000',
          unit: '/ 20 堂 (平均 $300/堂)',
          isPopular: true,
          features: [
            '適合重度舞蹈愛好者',
            '使用期限 4 個月',
            '全常規課程自由選修',
            '贈送專屬品牌運動毛巾',
            '享成果發表報名優先權'
          ]
        },
        {
          title: '尊榮月費',
          price: '$8,000',
          unit: '/ 月 (無限堂數)',
          isPopular: false,
          features: [
            '當月份不限堂數暢快跳',
            '全常規課程皆可預約',
            '場地個人租借 8 折特惠',
            '周邊服飾商品 9 折優惠'
          ]
        }
      ]
    };
  }
};
</script>

<style scoped>
.pricing-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.pricing-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12) !important;
}
</style>
