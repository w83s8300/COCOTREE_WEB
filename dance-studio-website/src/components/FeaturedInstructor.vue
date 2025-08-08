<template>
  <div class="bg-light py-5">
    <div class="container">
      <h2 class="text-center mb-4">本月主打星</h2>
      <div class="row align-items-center">
        <div class="col-md-4">
          <img src="https://picsum.photos/800/800?random=4" class="img-fluid rounded-circle" alt="Featured Instructor">
        </div>
        <div class="col-md-8">
          <h3>Teacher Name</h3>
          <p class="lead">專長：Hip Hop, Locking</p>
          <p>老師擁有超過十年的舞蹈經驗，活躍於各大舞蹈比賽與商業演出。教學風格風趣幽默，深受學生喜愛。老師相信，舞蹈不僅是技巧的展現，更是情感的表達，希望能帶領學生找到屬於自己的舞蹈靈魂。</p>
          <router-link to="/instructors" class="btn btn-outline-dark">了解更多</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FeaturedInstructor',
};
</script>

<style scoped>
/* Add any specific styles for FeaturedInstructor here if needed */
</style>
