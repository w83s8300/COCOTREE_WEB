<template>
  <div class="about-page">
    <!-- 1. Banner -->
    <div class="banner">
      <img src="https://picsum.photos/1920/500?random=9" alt="About Us Banner" class="banner-img">
      <div class="banner-text">
        <h1>關於我們 / ABOUT US</h1>
      </div>
    </div>

    <!-- 2. Introduction -->
    <div class="container my-5">
      <div class="row align-items-center">
        <div class="col-lg-6">
          <h2 class="mb-3">歡迎來到 Dance Studio</h2>
          <p class="text-start">
            我們是城市中最具活力的舞蹈綠洲，致力於為所有年齡和程度的舞蹈愛好者提供最專業、最多元的學習體驗。無論您是初學者還是經驗豐富的舞者，都能在這裡找到屬於您的舞台。
          </p>
          <p class="text-start">
            我們的師資團隊由業界頂尖的專業舞者組成，他們不僅擁有豐富的教學經驗，更對舞蹈充滿無限熱情。我們提供舒適、寬敞的學習環境，配備專業級的音響和地板，讓您在最佳的狀態下學習與成長。
          </p>
        </div>
        <div class="col-lg-6">
          <img src="https://picsum.photos/800/600?random=10" class="img-fluid rounded" alt="Studio Introduction">
        </div>
      </div>
    </div>

    <!-- 3. Studio Environment -->
    <div class="bg-light py-5">
      <div class="container">
        <h2 class="text-center mb-4">環境介紹</h2>
        <div class="row">
          <div class="col-md-4 mb-4">
            <div class="card h-100">
              <img src="https://picsum.photos/600/400?random=11" class="card-img-top" alt="Studio A">
              <div class="card-body">
                <h5 class="card-title">A 教室</h5>
                <p class="card-text">寬敞明亮的空間，適合大型團體課程與排練。</p>
              </div>
            </div>
          </div>
          <div class="col-md-4 mb-4">
            <div class="card h-100">
              <img src="https://picsum.photos/600/400?random=12" class="card-img-top" alt="Studio B">
              <div class="card-body">
                <h5 class="card-title">B 教室</h5>
                <p class="card-text">配備專業燈光音響，適合 MV 拍攝與成果發表。</p>
              </div>
            </div>
          </div>
          <div class="col-md-4 mb-4">
            <div class="card h-100">
              <img src="https://picsum.photos/600/400?random=13" class="card-img-top" alt="Lounge Area">
              <div class="card-body">
                <h5 class="card-title">休息區</h5>
                <p class="card-text">舒適的休憩空間，提供學員課後交流與放鬆。</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'About'
}
</script>

<style src="../assets/css/About.css"></style>