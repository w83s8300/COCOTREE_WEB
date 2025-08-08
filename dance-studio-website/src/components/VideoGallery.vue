<template>
  <div class="bg-dark text-white py-5">
    <div class="container">
      <h2 class="text-center mb-4">影片藝廊</h2>
      <div class="row">
        <div class="col-md-6 mb-4">
          <div class="ratio ratio-16x9">
            <iframe src="https://www.youtube.com/embed/zpOULjyy-n8?rel=0" title="YouTube video" allowfullscreen></iframe>
          </div>
        </div>
        <div class="col-md-6 mb-4">
          <div class="ratio ratio-16x9">
            <iframe src="https://www.youtube.com/embed/Logy0_c2X3k?rel=0" title="YouTube video" allowfullscreen></iframe>
          </div>
        </div>
      </div>
      <div class="text-center">
        <a href="#" class="btn btn-outline-light">觀看更多</a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoGallery',
};
</script>

<style scoped>
/* Add any specific styles for VideoGallery here if needed */
</style>
