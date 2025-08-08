
<template>
  <div class="pricing-page">
    <!-- 1. Banner -->
    <div class="banner">
      <img src="https://picsum.photos/1920/500?random=35" alt="Pricing Banner" class="banner-img">
      <div class="banner-text">
        <h1>課程價目表 / PRICING</h1>
      </div>
    </div>

    <!-- 2. Pricing Cards -->
    <div class="container my-5">
      <div class="row">
        <!-- Card 1: Single Class -->
        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card text-center h-100">
            <div class="card-header"><h4>單堂體驗</h4></div>
            <div class="card-body">
              <h5 class="card-title">$500</h5>
              <p class="card-text">/ 堂</p>
              <ul class="list-unstyled mt-3 mb-4">
                <li>適合初次體驗的學員</li>
                <li>任選一堂常規課程</li>
                <li>-</li>
                <li>-</li>
              </ul>
            </div>
          </div>
        </div>
        <!-- Card 2: 8 Classes -->
        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card text-center h-100">
            <div class="card-header"><h4>小資方案</h4></div>
            <div class="card-body">
              <h5 class="card-title">$3,200</h5>
              <p class="card-text">/ 8 堂</p>
              <ul class="list-unstyled mt-3 mb-4">
                <li>平均 $400/堂</li>
                <li>使用期限 2 個月</li>
                <li>適合規律學習者</li>
                <li>-</li>
              </ul>
            </div>
          </div>
        </div>
        <!-- Card 3: 20 Classes -->
        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card text-center h-100">
            <div class="card-header"><h4>熱血方案</h4></div>
            <div class="card-body">
              <h5 class="card-title">$6,000</h5>
              <p class="card-text">/ 20 堂</p>
              <ul class="list-unstyled mt-3 mb-4">
                <li>平均 $300/堂</li>
                <li>使用期限 4 個月</li>
                <li>適合重度舞蹈愛好者</li>
                <li>贈送品牌毛巾</li>
              </ul>
            </div>
          </div>
        </div>
        <!-- Card 4: VIP -->
        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card text-center h-100 ">
            <div class="card-header"><h4> 月費</h4></div>
            <div class="card-body">
              <h5 class="card-title">$8,000</h5>
              <p class="card-text">/ 月</p>
              <ul class="list-unstyled mt-3 mb-4">
                <li>一個月內無限上課</li>
                <li>所有常規課程適用</li>
                <li>場地租借 8 折優惠</li>
                <li>商品購買 9 折優惠</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Important Notes -->
      <div class="notes-section mt-5 text-start">
        <h3>報名須知</h3>
        <ul>
          <li>所有課程皆需提前預約，可透過官方 LINE 或電話預約。</li>
          <li>堂數卡限本人使用，不得轉讓。</li>
          <li>購買後恕不退費，請於有效期限內使用完畢。</li>
          <li>若需請假，請於課程開始前 2 小時告知，否則將視為曠課，不予補課。</li>
          <li>本工作室保有課程及師資調整之權利。</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Pricing'
}
</script>

<style src="../assets/css/Pricing.css"></style>
