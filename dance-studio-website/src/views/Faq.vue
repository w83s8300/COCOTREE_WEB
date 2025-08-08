<template>
  <div class="faq-page">
    <!-- 1. Banner -->
    <div class="banner">
      <img src="https://picsum.photos/1920/500?random=33" alt="FAQ Banner" class="banner-img">
      <div class="banner-text">
        <h1>常見問題 / FAQ</h1>
      </div>
    </div>

    <!-- 2. FAQ Accordion -->
    <div class="container my-5">
      <div class="accordion" id="faqAccordion">
        <!-- FAQ 1 -->
        <div class="accordion-item">
          <h2 class="accordion-header" id="headingOne">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
              完全沒有舞蹈基礎，可以上課嗎？
            </button>
          </h2>
          <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#faqAccordion">
            <div class="accordion-body text-start">
              當然可以！我們有專為初學者設計的入門課程，老師會從最基本的動作開始教起，帶領您輕鬆進入舞蹈的世界。
            </div>
          </div>
        </div>
        <!-- FAQ 2 -->
        <div class="accordion-item">
          <h2 class="accordion-header" id="headingTwo">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
              需要自己先報名一整期的課程嗎？
            </button>
          </h2>
          <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo" data-bs-parent="#faqAccordion">
            <div class="accordion-body text-start">
              我們提供單堂體驗課和多樣的堂數卡方案，您可以根據自己的時間和需求彈性選擇，無需一次綁定長期課程。
            </div>
          </div>
        </div>
        <!-- FAQ 3 -->
        <div class="accordion-item">
          <h2 class="accordion-header" id="headingThree">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
              上課需要穿著什麼樣的服裝？
            </button>
          </h2>
          <div id="collapseThree" class="accordion-collapse collapse" aria-labelledby="headingThree" data-bs-parent="#faqAccordion">
            <div class="accordion-body text-start">
              建議穿著輕便、有彈性的運動服裝，並穿著乾淨的運動鞋。特殊課程如 Heels 則建議穿著有跟的舞鞋。
            </div>
          </div>
        </div>
        <!-- FAQ 4 -->
        <div class="accordion-item">
          <h2 class="accordion-header" id="headingFour">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFour" aria-expanded="false" aria-controls="collapseFour">
              如果臨時有事不能來上課，可以請假嗎？
            </button>
          </h2>
          <div id="collapseFour" class="accordion-collapse collapse" aria-labelledby="headingFour" data-bs-parent="#faqAccordion">
            <div class="accordion-body text-start">
              可以的。請您最晚於課程開始前 2 小時透過官方 LINE 或電話完成請假手續，我們將為您保留堂數。
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Faq'
}
</script>

<style src="../assets/css/Faq.css"></style>