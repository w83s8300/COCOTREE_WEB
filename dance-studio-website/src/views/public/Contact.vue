<template>
  <div class="contact-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=34" title="聯絡我們 / CONTACT" />

    <div class="container my-5">
      <div class="row">
        <!-- Contact Info -->
        <div class="col-lg-6 text-start mb-4 mb-lg-0" data-aos="fade-right">
          <h3 class="mb-3">工作室資訊</h3>
          <ul class="list-unstyled mb-4 lh-lg">
            <li><i class="bi bi-geo-alt-fill text-primary me-2"></i>地址：402台中市南區工學路169號2樓</li>
            <li><i class="bi bi-telephone-fill text-primary me-2"></i>電話：(02) 1234-5678</li>
            <li><i class="bi bi-envelope-fill text-primary me-2"></i>Email: contact@dancestudio.com</li>
            <li><i class="bi bi-clock-fill text-primary me-2"></i>營業時間：週一至週日 14:00 - 22:00</li>
          </ul>

          <h3 class="mb-3">交通資訊</h3>
          <p>搭乘大眾運輸至「工學站」，下車後步行約 3 分鐘即可抵達；門口設有機車及汽車收費停車格。</p>
          
          <!-- Map Embed -->
          <div class="map-responsive mt-3 rounded overflow-hidden shadow-sm">
            <iframe 
              src="https://maps.google.com/maps?q=台中市南區工學路169號&t=&z=16&ie=UTF8&iwloc=&output=embed" 
              width="100%" 
              height="300" 
              style="border:0;" 
              allowfullscreen="" 
              loading="lazy">
            </iframe>
          </div>
        </div>

        <!-- Contact Form -->
        <div class="col-lg-6" data-aos="fade-left">
          <h3 class="mb-3">發送訊息給我們</h3>
          <form @submit.prevent="submitForm" class="p-4 border rounded bg-light shadow-sm">
            <div class="mb-3">
              <label for="name" class="form-label">姓名 <span class="text-danger">*</span></label>
              <input type="text" class="form-control" id="name" v-model="form.name" required placeholder="請輸入您的姓名">
            </div>
            <div class="mb-3">
              <label for="email" class="form-label">Email <span class="text-danger">*</span></label>
              <input type="email" class="form-control" id="email" v-model="form.email" required placeholder="example@email.com">
            </div>
            <div class="mb-3">
              <label for="subject" class="form-label">主旨 <span class="text-danger">*</span></label>
              <input type="text" class="form-control" id="subject" v-model="form.subject" required placeholder="想詢問的項目">
            </div>
            <div class="mb-3">
              <label for="message" class="form-label">訊息內容 <span class="text-danger">*</span></label>
              <textarea class="form-control" id="message" v-model="form.message" rows="5" required placeholder="請詳細描述您的問題或需求..."></textarea>
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
              {{ submitting ? '發送中...' : '送出訊息' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PageBanner from '@/components/PageBanner.vue';
import { showToast } from '@/utils/toast';

export default {
  name: 'Contact',
  components: {
    PageBanner
  },
  data() {
    return {
      submitting: false,
      form: {
        name: '',
        email: '',
        subject: '',
        message: ''
      }
    };
  },
  methods: {
    async submitForm() {
      this.submitting = true;
      try {
        // 模擬發送諮詢訊息
        await new Promise(resolve => setTimeout(resolve, 800));
        showToast('謝謝您的來信！我們將盡快與您聯繫。', 'success');
        this.form = {
          name: '',
          email: '',
          subject: '',
          message: ''
        };
      } catch (err) {
        showToast('訊息送出失敗，請稍後重試。', 'error');
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>

<style scoped>
.contact-page {
  text-align: left;
}
.map-responsive {
  border: 1px solid #dee2e6;
}
</style>