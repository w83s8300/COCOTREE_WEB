<template>
  <div class="container my-5">
    <div class="text-center mb-5">
      <h2 class="fw-bold mb-2">近期活動 / RECENT EVENTS</h2>
      <p class="text-muted">精彩賽事、年度盛典與大師專班，帶你感受最純粹的舞蹈熱血</p>
    </div>

    <div v-if="events.length === 0" class="text-center py-4 text-muted">
      <p>目前尚無近期活動。</p>
    </div>

    <div v-else class="row g-4 justify-content-center">
      <div class="col-12 col-sm-6 col-md-4" v-for="event in events" :key="event.id || event.title">
        <div class="card h-100 border-0 shadow-sm event-card overflow-hidden">
          <div class="event-img-wrap position-relative">
            <img
              :src="event.image_url || event.image"
              class="card-img-top event-img"
              :alt="event.title"
              loading="lazy"
              @error="handleImageError"
            >
            <span v-if="event.tag" class="badge bg-danger position-absolute top-0 end-0 m-3 px-3 py-2 rounded-pill shadow-sm fw-bold">
              {{ event.tag }}
            </span>
          </div>
          <div class="card-body d-flex flex-column p-4 text-start">
            <div class="small text-muted mb-2">
              <i class="bi bi-calendar-event me-1 text-primary"></i>{{ event.publish_date || event.date }}
            </div>
            <h5 class="card-title fw-bold text-dark mb-2">{{ event.title }}</h5>
            <p class="card-text text-muted flex-grow-1" style="line-height: 1.6;">
              {{ event.summary || event.shortDescription }}
            </p>
            <button
              @click="$emit('show-detail', event)"
              class="btn btn-outline-primary btn-sm rounded-pill mt-3 align-self-start px-3"
            >
              查看詳情 <i class="bi bi-arrow-right ms-1"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const FALLBACK_EVENT_IMG = 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80';

export default {
  name: 'RecentEvents',
  emits: ['show-detail'],
  props: {
    events: {
      type: Array,
      required: true,
    },
  },
  methods: {
    handleImageError(e) {
      e.target.src = FALLBACK_EVENT_IMG;
    }
  }
};
</script>

<style scoped>
.event-card {
  border-radius: 14px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.event-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important;
}
.event-img-wrap {
  height: 210px;
  overflow: hidden;
  background-color: #e9ecef;
}
.event-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.event-card:hover .event-img {
  transform: scale(1.05);
}
</style>