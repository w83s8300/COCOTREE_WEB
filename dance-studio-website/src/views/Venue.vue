<template>
  <div class="venue-page">
    <!-- 1. Banner -->
    <div class="banner">
      <img src="https://picsum.photos/1920/500?random=29" alt="Venue Banner" class="banner-img">
      <div class="banner-text">
        <h1>場地租借 / VENUE</h1>
      </div>
    </div>

    <div class="container my-5">
      <!-- 2. Venue Carousel & Specs -->
      <div class="row mb-5">
        <div class="col-lg-8">
          <div id="venueCarousel" class="carousel slide" data-bs-ride="carousel" ref="venueCarousel">
            <div class="carousel-inner">
              <div class="carousel-item active">
                <img src="https://picsum.photos/800/600?random=30" class="d-block w-100" alt="Venue Image 1">
              </div>
              <div class="carousel-item">
                <img src="https://picsum.photos/800/600?random=31" class="d-block w-100" alt="Venue Image 2">
              </div>
              <div class="carousel-item">
                <img src="https://picsum.photos/800/600?random=32" class="d-block w-100" alt="Venue Image 3">
              </div>
            </div>
            <button class="carousel-control-prev" type="button" data-bs-target="#venueCarousel" data-bs-slide="prev">
              <span class="carousel-control-prev-icon" aria-hidden="true"></span>
              <span class="visually-hidden">Previous</span>
            </button>
            <button class="carousel-control-next" type="button" data-bs-target="#venueCarousel" data-bs-slide="next">
              <span class="carousel-control-next-icon" aria-hidden="true"></span>
              <span class="visually-hidden">Next</span>
            </button>
          </div>
        </div>
        <div class="col-lg-4">
          <h3 class="text-start">場地規格</h3>
          <ul class="list-group list-group-flush text-start">
            <li class="list-group-item">坪數：約 40 坪</li>
            <li class="list-group-item">容納人數：建議 20-30 人</li>
            <li class="list-group-item">地板：專業舞蹈用木質地板</li>
            <li class="list-group-item">鏡面：三面全身鏡</li>
            <li class="list-group-item">音響：專業級環繞音響 (可接藍芽)</li>
            <li class="list-group-item">空調：中央空調系統</li>
            <li class="list-group-item">其他：提供瑜珈墊、飲水機</li>
          </ul>
        </div>
      </div>

      <!-- 3. Pricing Table -->
      <div class="mb-5">
        <h3 class="text-center mb-4">租借價目表</h3>
        <table class="table table-bordered text-center venue-table">
          <thead class="table-dark">
            <tr>
              <th>時段</th>
              <th>平日 (週一至週五)</th>
              <th>假日 (週六、週日及國定假日)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>09:00 - 12:00</td>
              <td>$500 / 小時</td>
              <td>$700 / 小時</td>
            </tr>
            <tr>
              <td>12:00 - 18:00</td>
              <td>$600 / 小時</td>
              <td>$800 / 小時</td>
            </tr>
            <tr>
              <td>18:00 - 22:00</td>
              <td>$800 / 小時</td>
              <td>$1000 / 小時</td>
            </tr>
          </tbody>
        </table>
        <p class="text-muted text-center">* 長期租借或商業用途另有優惠，請洽詢櫃檯。</p>
      </div>

      <!-- 4. Rental Policy -->
      <div class="text-start">
        <h3>租借規章</h3>
        <ul class="list-unstyled">
          <li><i class="bi bi-check-circle-fill me-2"></i>預約請洽櫃檯或私訊社群媒體，並於三天前完成預約及付款。</li>
          <li><i class="bi bi-check-circle-fill me-2"></i>如需取消或更改時間，請於 24 小時前告知，否則將不予退款。</li>
          <li><i class="bi bi-check-circle-fill me-2"></i>禁止攜帶食物及飲料進入教室，可飲用白開水。</li>
          <li><i class="bi bi-check-circle-fill me-2"></i>請穿著適合的運動服裝及乾淨的運動鞋，禁止穿著高跟鞋或黑膠底鞋。</li>
          <li><i class="bi bi-check-circle-fill me-2"></i>請愛護場地設備，若有損壞需照價賠償。</li>
          <li><i class="bi bi-check-circle-fill me-2"></i>本工作室保有最終解釋權。</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { Carousel } from 'bootstrap';

export default {
  name: 'Venue',
  data() {
    return {
      carousel: null,
      startX: 0,
      isSwiping: false,
    };
  },
  mounted() {
    this.carousel = new Carousel(this.$refs.venueCarousel);
    const carouselElement = this.$refs.venueCarousel;

    carouselElement.addEventListener('mousedown', this.handleMouseDown);
  },
  beforeUnmount() {
    const carouselElement = this.$refs.venueCarousel;
    if (carouselElement) {
      carouselElement.removeEventListener('mousedown', this.handleMouseDown);
      document.removeEventListener('mousemove', this.handleMouseMove);
      document.removeEventListener('mouseup', this.handleMouseUp);
    }
  },
  methods: {
    handleMouseDown(e) {
      this.startX = e.pageX;
      this.isSwiping = true;
      document.addEventListener('mousemove', this.handleMouseMove);
      document.addEventListener('mouseup', this.handleMouseUp);
    },
    handleMouseMove(e) {
      if (!this.isSwiping) return;
      e.preventDefault();
    },
    handleMouseUp(e) {
      if (!this.isSwiping) return;
      this.isSwiping = false;
      const endX = e.pageX;
      const diffX = endX - this.startX;

      if (diffX > 50) {
        this.carousel.prev();
      } else if (diffX < -50) {
        this.carousel.next();
      }
      document.removeEventListener('mousemove', this.handleMouseMove);
      document.removeEventListener('mouseup', this.handleMouseUp);
    },
  },
};
</script>

<style src="../assets/css/Venue.css"></style>
<style>
.carousel-inner img {
  pointer-events: none;
}

/* Disable text selection for the carousel */
#venueCarousel {
  -webkit-touch-callout: none; /* iOS Safari */
  -webkit-user-select: none;   /* Safari */
  -khtml-user-select: none;    /* Konqueror HTML */
  -moz-user-select: none;      /* Old versions of Firefox */
  -ms-user-select: none;       /* Internet Explorer/Edge */
  user-select: none;           /* Non-prefixed version, currently supported by Chrome, Edge, Opera and Firefox */
}
</style>