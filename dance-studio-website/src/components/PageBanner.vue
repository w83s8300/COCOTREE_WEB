<template>
  <div class="page-banner position-relative">
    <img :src="displayImage" :alt="alt || displayTitle" class="page-banner__img" loading="lazy" @error="handleImgError">
    <div class="page-banner__overlay">
      <div class="text-center px-3">
        <h1 class="text-white fw-bold mb-2">{{ displayTitle }}</h1>
        <p v-if="displaySubtitle" class="text-white-50 lead mb-0 small-subtitle">
          {{ displaySubtitle }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/utils/api';

export default {
  name: 'PageBanner',
  props: {
    image: { type: String, required: true },
    title: { type: String, required: true },
    alt: { type: String, default: '' },
    pageKey: { type: String, default: '' }
  },
  data() {
    return {
      customImage: null,
      customTitle: null,
      customSubtitle: null
    };
  },
  computed: {
    computedPageKey() {
      if (this.pageKey) return this.pageKey;
      const pathKey = this.$route.path.replace(/^\//, '').split('/')[0];
      return pathKey || 'about';
    },
    displayImage() {
      return this.customImage || this.image;
    },
    displayTitle() {
      return this.customTitle || this.title;
    },
    displaySubtitle() {
      return this.customSubtitle || '';
    }
  },
  mounted() {
    this.fetchBannerData();
  },
  methods: {
    async fetchBannerData() {
      if (!this.computedPageKey) return;
      try {
        const res = await api.get(`/page-banners/${this.computedPageKey}`);
        if (res.success && res.banner) {
          if (res.banner.image_url) this.customImage = res.banner.image_url;
          if (res.banner.title) this.customTitle = res.banner.title;
          if (res.banner.subtitle) this.customSubtitle = res.banner.subtitle;
        }
      } catch (e) {
        // 使用 props 預設值
      }
    },
    handleImgError(e) {
      if (this.image && e.target.src !== this.image) {
        e.target.src = this.image;
      }
    }
  }
};
</script>

<style scoped>
.page-banner {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.page-banner__img {
  width: 100%;
  height: 480px;
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
  background: linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.65) 100%);
}

.page-banner__overlay h1 {
  color: white;
  font-size: 2.6rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.6);
}

.small-subtitle {
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.7);
  font-size: 1.15rem;
}

@media (max-width: 768px) {
  .page-banner__img {
    height: 320px;
  }
  .page-banner__overlay h1 {
    font-size: 1.8rem;
  }
}
</style>
