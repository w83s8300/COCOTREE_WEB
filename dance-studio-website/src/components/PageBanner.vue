<template>
  <div class="page-banner">
    <img :src="image" :alt="alt || title" class="page-banner__img" loading="lazy">
    <div class="page-banner__overlay">
      <h1>{{ title }}</h1>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PageBanner',
  props: {
    image: { type: String, required: true },
    title: { type: String, required: true },
    alt: { type: String, default: '' }
  }
}
</script>

<style scoped>
.page-banner {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.page-banner__img {
  width: 100%;
  height: 500px;
  object-fit: cover;
  display: block;
}

.page-banner__overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.4);
}

.page-banner__overlay h1 {
  color: white;
  font-size: 2.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

@media (max-width: 768px) {
  .page-banner__img {
    height: 300px;
  }
  .page-banner__overlay h1 {
    font-size: 1.8rem;
  }
}
</style>

