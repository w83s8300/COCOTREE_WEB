<template>
  <div class="venue-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=29" title="場地租借 / VENUE" />

    <div class="container my-5">
      <!-- 2. Venue Carousel & Specs -->
      <div class="row mb-5" data-aos="fade-up">
        <div class="col-lg-8 mb-4 mb-lg-0">
          <div id="venueCarousel" class="carousel slide rounded overflow-hidden shadow-sm" data-bs-ride="carousel" ref="venueCarousel">
            <div class="carousel-inner">
              <div class="carousel-item active">
                <img src="https://picsum.photos/800/600?random=30" class="d-block w-100 venue-carousel-img" alt="Venue Image 1">
              </div>
              <div class="carousel-item">
                <img src="https://picsum.photos/800/600?random=31" class="d-block w-100 venue-carousel-img" alt="Venue Image 2">
              </div>
              <div class="carousel-item">
                <img src="https://picsum.photos/800/600?random=32" class="d-block w-100 venue-carousel-img" alt="Venue Image 3">
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
          <h3 class="text-start mb-3">場地規格</h3>
          <ul class="list-group list-group-flush text-start shadow-sm rounded">
            <li class="list-group-item"><strong>坪數：</strong>約 40 坪</li>
            <li class="list-group-item"><strong>容納人數：</strong>建議 20-30 人</li>
            <li class="list-group-item"><strong>地板：</strong>專業舞蹈用防滑減震木質地板</li>
            <li class="list-group-item"><strong>鏡面：</strong>三面全身專業落地鏡</li>
            <li class="list-group-item"><strong>音響：</strong>專業級環繞立體音響 (支援藍芽/AUX)</li>
            <li class="list-group-item"><strong>空調：</strong>獨立變頻冷暖空調</li>
            <li class="list-group-item"><strong>附屬設施：</strong>更衣室、瑜珈墊、飲水機、高速 Wi-Fi</li>
          </ul>
        </div>
      </div>

      <!-- 3. Pricing Table -->
      <div class="mb-5" data-aos="fade-up">
        <h3 class="text-center mb-4">租借價目表</h3>
        <div class="table-responsive shadow-sm rounded">
          <table class="table table-bordered text-center align-middle mb-0">
            <thead class="table-dark">
              <tr>
                <th scope="col">時段</th>
                <th scope="col">平日 (週一至週五)</th>
                <th scope="col">假日 (週六、週日及國定假日)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="fw-bold">09:00 - 12:00</td>
                <td>$500 / 小時</td>
                <td>$700 / 小時</td>
              </tr>
              <tr>
                <td class="fw-bold">12:00 - 18:00</td>
                <td>$600 / 小時</td>
                <td>$800 / 小時</td>
              </tr>
              <tr>
                <td class="fw-bold">18:00 - 22:00</td>
                <td>$800 / 小時</td>
                <td>$1,000 / 小時</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="text-muted text-center mt-2 small">* 長期固定時段租借或商業活動用途另有專屬優惠，歡迎洽詢櫃檯。</p>
      </div>

      <!-- 4. Rental Policy -->
      <div class="text-start p-4 bg-light rounded shadow-sm" data-aos="fade-up">
        <h3 class="mb-3">租借須知與規章</h3>
        <ul class="list-unstyled lh-lg mb-0">
          <li><i class="bi bi-check-circle-fill text-success me-2"></i>預約請洽櫃檯或官方社群，並於使用日前三天完成預約及付訂。</li>
          <li><i class="bi bi-check-circle-fill text-success me-2"></i>如需取消或更改時間，請於 24 小時前告知。</li>
          <li><i class="bi bi-check-circle-fill text-success me-2"></i>教室內禁止攜帶非透明飲料及食物，僅可飲用白開水。</li>
          <li><i class="bi bi-check-circle-fill text-success me-2"></i>請穿著適合的運動服裝及乾淨室內鞋，嚴禁穿著室外髒鞋或釘鞋進入。</li>
          <li><i class="bi bi-check-circle-fill text-success me-2"></i>請愛護場地及音響設備，如有損壞須依市價賠償。</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { Carousel } from 'bootstrap';
import PageBanner from '@/components/PageBanner.vue';
import { useCarouselSwipe } from '@/composables/useCarouselSwipe';

export default {
  name: 'Venue',
  components: {
    PageBanner
  },
  setup() {
    const venueCarousel = ref(null);
    const carouselInstance = ref(null);
    const { setupSwipe, cleanupSwipe } = useCarouselSwipe(venueCarousel, carouselInstance);
    return { venueCarousel, carouselInstance, setupSwipe, cleanupSwipe };
  },
  mounted() {
    if (this.$refs.venueCarousel) {
      this.carouselInstance = new Carousel(this.$refs.venueCarousel);
      this.setupSwipe();
    }
  },
  beforeUnmount() {
    if (this.carouselInstance) this.carouselInstance.dispose();
    this.cleanupSwipe();
  }
};
</script>

<style scoped>
.venue-carousel-img {
  height: 420px;
  object-fit: cover;
}
</style>