<template>
  <div class="faq-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=33" title="常見問題 / FAQ" />

    <!-- 2. FAQ Section -->
    <div class="container my-5">
      <!-- Search Input -->
      <div class="row justify-content-center mb-4" data-aos="fade-up">
        <div class="col-md-6">
          <div class="input-group">
            <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
            <input 
              type="text" 
              class="form-control" 
              v-model="searchQuery" 
              placeholder="搜尋關鍵字，例如：基礎、服裝、請假..."
            />
          </div>
        </div>
      </div>

      <!-- FAQ Accordion -->
      <div class="accordion shadow-sm rounded" id="faqAccordion" data-aos="fade-up">
        <div v-if="filteredFaqs.length === 0" class="text-center py-5 text-muted">
          <p>找不到符合關鍵字的常見問題，歡迎直接透過「聯絡我們」與我們聯繫！</p>
        </div>

        <div 
          v-for="(faq, index) in filteredFaqs" 
          :key="faq.id" 
          class="accordion-item"
        >
          <h2 class="accordion-header" :id="'heading' + faq.id">
            <button 
              class="accordion-button" 
              :class="{ collapsed: index !== 0 }" 
              type="button" 
              data-bs-toggle="collapse" 
              :data-bs-target="'#collapse' + faq.id" 
              :aria-expanded="index === 0 ? 'true' : 'false'" 
              :aria-controls="'collapse' + faq.id"
            >
              {{ faq.question }}
            </button>
          </h2>
          <div 
            :id="'collapse' + faq.id" 
            class="accordion-collapse collapse" 
            :class="{ show: index === 0 }" 
            :aria-labelledby="'heading' + faq.id" 
            data-bs-parent="#faqAccordion"
          >
            <div class="accordion-body text-start lh-base">
              {{ faq.answer }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PageBanner from '@/components/PageBanner.vue';

export default {
  name: 'Faq',
  components: {
    PageBanner
  },
  data() {
    return {
      searchQuery: '',
      faqs: [
        {
          id: 1,
          question: '完全沒有舞蹈基礎，可以來上課嗎？',
          answer: '當然可以！我們專門為初學者規劃了「入門基礎班」，老師會從最基礎的重心移動、律動踩點與肢體協調教起，循序漸進，帶領您無壓力地進入舞蹈的美好世界。'
        },
        {
          id: 2,
          question: '需要一次報名一整期或長期綁約嗎？',
          answer: '完全不需要！我們提供單堂體驗價與彈性的堂數票卡方案（8堂、20堂、月費等），您可以根據自己的作息自由預約時段，不需要一次簽訂長期合約。'
        },
        {
          id: 3,
          question: '上課需要穿著什麼樣的服裝或裝備？',
          answer: '建議穿著輕便、吸汗有彈性的運動便服，並務必攜帶一雙乾淨的「室內運動鞋」更換入室。特定舞風如 Heels 建議自備粗跟高跟鞋，其他課程不需特殊器材。'
        },
        {
          id: 4,
          question: '如果臨時有事不能來，可以請假保留堂數嗎？',
          answer: '可以的！請最遲於上課時間開始前 2 小時透過線上系統取消或向官方 LINE 告知，即可保留該堂數並於期限內補課。'
        },
        {
          id: 5,
          question: '教室有提供淋浴間或更衣室嗎？',
          answer: '有的，工作室備有獨立男女更衣空間、個人置物櫃、飲水機與休息交誼區，但目前未設置淋浴設備。'
        }
      ]
    };
  },
  computed: {
    filteredFaqs() {
      if (!this.searchQuery.trim()) return this.faqs;
      const q = this.searchQuery.trim().toLowerCase();
      return this.faqs.filter(f => f.question.toLowerCase().includes(q) || f.answer.toLowerCase().includes(q));
    }
  }
};
</script>

<style scoped>
.accordion-button:not(.collapsed) {
  background-color: #e7f1ff;
  color: #0d6efd;
  font-weight: 600;
}
</style>