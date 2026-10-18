<template>
  <div class="container my-5">
    <h2 class="text-center mb-4">近期活動</h2>
    <div class="row">
      <div class="col-12 col-sm-6 col-md-4 mb-4" v-for="event in events" :key="event.title">
        <div class="card h-100">
          <img :src="event.image" class="card-img-top" :alt="event.title" loading="lazy">
          <div class="card-body">
            <h5 class="card-title">{{ event.title }}</h5>
            <p class="card-text">{{ event.shortDescription }}</p>
            <button @click="$emit('show-detail', event)" class="btn btn-primary">查看詳情</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecentEvents',
  emits: ['show-detail'],
  props: {
    events: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped>
/* Add any specific styles for RecentEvents here if needed */
</style>