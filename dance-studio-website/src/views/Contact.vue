<template>
  <div class="contact-page">
    <!-- 1. Banner -->
    <div class="banner">
      <img src="https://picsum.photos/1920/500?random=34" alt="Contact Banner" class="banner-img">
      <div class="banner-text">
        <h1>聯絡我們 / CONTACT</h1>
      </div>
    </div>

    <div class="container my-5">
      <div class="row">
        <!-- Contact Info -->
        <div class="col-lg-6 text-start">
          <h3>工作室資訊</h3>
          <ul class="list-unstyled mb-4">
            <li><i class="bi bi-geo-alt-fill me-2"></i>地址：123 Dance Road, Dance City</li>
            <li><i class="bi bi-telephone-fill me-2"></i>電話：(02) 1234-5678</li>
            <li><i class="bi bi-envelope-fill me-2"></i>Email: contact@dancestudio.com</li>
            <li><i class="bi bi-clock-fill me-2"></i>營業時間：週一至週日 14:00 - 22:00</li>
          </ul>

          <h3>交通資訊</h3>
          <p>捷運：搭乘藍線至「舞蹈站」，由 2 號出口步行約 5 分鐘即可抵達。</p>
          
          <!-- Google Maps Embed -->
          <div class="map-responsive mt-4">
            <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3614.703564433023!2d121.5623316150061!3d25.04413408396739!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3442abadd161b43b%3A0x4d04b58847865560!2sTaipei%20101!5e0!3m2!1sen!2stw!4v1625123456789!5m2!1sen!2stw" width="100%" height="300" style="border:0;" allowfullscreen="" loading="lazy"></iframe>
          </div>
        </div>

        <!-- Contact Form -->
        <div class="col-lg-6">
          <h3>聯絡我們</h3>
          <form>
            <div class="mb-3">
              <label for="name" class="form-label">姓名</label>
              <input type="text" class="form-control" id="name">
            </div>
            <div class="mb-3">
              <label for="email" class="form-label">Email</label>
              <input type="email" class="form-control" id="email">
            </div>
            <div class="mb-3">
              <label for="subject" class="form-label">主旨</label>
              <input type="text" class="form-control" id="subject">
            </div>
            <div class="mb-3">
              <label for="message" class="form-label">訊息</label>
              <textarea class="form-control" id="message" rows="5"></textarea>
            </div>
            <button type="submit" class="btn btn-primary">送出</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Contact'
}
</script>

<style src="../assets/css/Contact.css"></style>