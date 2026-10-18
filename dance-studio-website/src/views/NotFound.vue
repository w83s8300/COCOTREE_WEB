<template>
  <div class="not-found text-center">
    <div class="container">
      <h1 class="display-1 fw-bold text-muted">404</h1>
      <h2 class="mb-3">找不到頁面</h2>
      <p class="text-muted mb-4">您要找的頁面不存在或已被移除。</p>
      <router-link to="/" class="btn btn-primary">
        <i class="bi bi-house-fill me-2"></i>回到首頁
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style scoped>
.not-found {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
}

.display-1 {
  font-size: 8rem;
}
</style>

