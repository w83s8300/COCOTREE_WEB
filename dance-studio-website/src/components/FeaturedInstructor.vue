<template>
  <div class="bg-light py-5">
    <div class="container">
      <div class="text-center mb-5">
        <h2 class="fw-bold mb-2">本月主打星 / FEATURED INSTRUCTORS</h2>
        <p class="text-muted">頂尖專業師資團隊，傾注熱情帶領你探索身體的無限可能</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
      </div>

      <!-- 空資料狀態 -->
      <div v-else-if="instructors.length === 0" class="text-center py-4 text-muted">
        <p>目前尚無主打星資料。</p>
      </div>

      <!-- 模式一：僅 1 位主打星時的大版型聚焦展示 -->
      <div v-else-if="instructors.length === 1" class="row align-items-center justify-content-center g-4">
        <div class="col-md-5 col-lg-4 text-center">
          <div class="instructor-avatar-wrap mx-auto position-relative">
            <img
              :src="instructors[0].image"
              class="img-fluid rounded-circle shadow-lg instructor-avatar border border-4 border-white"
              :alt="instructors[0].name"
              loading="lazy"
              @error="handleImageError($event, 0)"
            >
            <span class="badge bg-warning text-dark position-absolute bottom-0 end-0 px-3 py-2 rounded-pill shadow-sm fw-bold">
              👑 人氣主打星
            </span>
          </div>
        </div>
        <div class="col-md-7 col-lg-6 text-start">
          <div class="d-flex align-items-center gap-2 mb-2">
            <h3 class="fw-bold mb-0 text-dark">{{ instructors[0].name }}</h3>
            <span v-if="instructors[0].experience_years" class="badge bg-primary-subtle text-primary fw-bold">
              教學 {{ instructors[0].experience_years }} 年
            </span>
          </div>
          <p class="lead text-primary fw-semibold mb-3">
            <i class="bi bi-stars me-1"></i>專長舞風：{{ instructors[0].specialty }}
          </p>
          <p class="text-muted lh-lg mb-4" style="font-size: 1.05rem;">
            {{ instructors[0].bio }}
          </p>
          <div class="d-flex gap-3">
            <router-link to="/instructors" class="btn btn-dark rounded-pill px-4 py-2 shadow-sm">
              <i class="bi bi-people-fill me-1"></i>認識全體師資
            </router-link>
            <router-link to="/schedule" class="btn btn-outline-primary rounded-pill px-4 py-2">
              <i class="bi bi-calendar3 me-1"></i>預約老師課程
            </router-link>
          </div>
        </div>
      </div>

      <!-- 模式二：複數（多位）主打星時的卡片式並列展示 -->
      <div v-else class="row g-4 justify-content-center">
        <div
          v-for="(inst, idx) in instructors"
          :key="inst.id || inst.name"
          :class="instructors.length === 2 ? 'col-md-6 col-lg-5' : 'col-md-6 col-lg-4'"
        >
          <div class="card h-100 border-0 shadow-sm featured-card overflow-hidden text-center p-4">
            <div class="position-relative d-inline-block mx-auto mb-3">
              <div class="multi-avatar-wrap position-relative">
                <img
                  :src="inst.image"
                  class="rounded-circle shadow multi-avatar border border-3 border-white"
                  :alt="inst.name"
                  loading="lazy"
                  @error="handleImageError($event, idx)"
                >
                <span class="badge bg-warning text-dark position-absolute bottom-0 end-0 px-2 py-1 rounded-pill shadow-sm small fw-bold">
                  👑 主打星
                </span>
              </div>
            </div>

            <div class="card-body p-0 d-flex flex-column">
              <div class="d-flex align-items-center justify-content-center gap-2 mb-2">
                <h4 class="fw-bold mb-0 text-dark">{{ inst.name }}</h4>
                <span v-if="inst.experience_years" class="badge bg-primary-subtle text-primary small">
                  {{ inst.experience_years }} 年教學
                </span>
              </div>

              <div class="text-primary small fw-semibold mb-3">
                <i class="bi bi-stars me-1"></i>{{ inst.specialty }}
              </div>

              <p class="text-muted small flex-grow-1 mb-4 text-start line-clamp-3" style="line-height: 1.6;">
                {{ inst.bio }}
              </p>

              <div class="d-flex justify-content-center gap-2 pt-3 border-top mt-auto">
                <router-link to="/schedule" class="btn btn-primary btn-sm rounded-pill px-3 py-2 fw-bold flex-fill shadow-sm">
                  <i class="bi bi-calendar-check me-1"></i>預約課表
                </router-link>
                <router-link to="/instructors" class="btn btn-outline-dark btn-sm rounded-pill px-3 py-2 flex-fill">
                  師資檔案
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/utils/api';

const DEFAULT_AVATARS = [
  'https://images.unsplash.com/photo-1547153760-18fc86324498?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1535525153412-5a42439a210d?auto=format&fit=crop&w=800&q=80'
];

export default {
  name: 'FeaturedInstructor',
  data() {
    return {
      loading: false,
      instructors: [],
    };
  },
  created() {
    this.fetchFeaturedTeachers();
  },
  methods: {
    async fetchFeaturedTeachers() {
      this.loading = true;
      try {
        const data = await api.get('/teachers');
        if (data.success && Array.isArray(data.teachers) && data.teachers.length > 0) {
          // 篩選標記為本月主打星 (is_featured === 1) 的老師
          const featured = data.teachers.filter(t => Boolean(t.is_featured));

          // 若後台未特定標記任何主打星，預設挑選前 2 位老師
          const list = featured.length > 0 ? featured : data.teachers.slice(0, 2);

          this.instructors = list.map((t, idx) => {
            const specialties = Array.isArray(t.styles) && t.styles.length > 0
              ? t.styles.map(s => s.name || s).join(', ')
              : (t.specialty || 'Hip Hop, K-POP, Jazz');

            return {
              id: t.id,
              name: t.name,
              specialty: specialties,
              bio: t.bio || '老師擁有多年專業舞蹈經驗，教學熱情風趣，善於啟發每位學員的身體潛能與自信。',
              image: t.avatar_url || t.image || DEFAULT_AVATARS[idx % DEFAULT_AVATARS.length],
              experience_years: t.experience_years || 5
            };
          });
        }
      } catch (err) {
        console.error('獲取主打星資料失敗:', err);
      } finally {
        this.loading = false;
      }
    },
    handleImageError(e, idx) {
      e.target.src = DEFAULT_AVATARS[idx % DEFAULT_AVATARS.length];
    }
  },
};
</script>

<style scoped>
.instructor-avatar-wrap {
  width: 240px;
  height: 240px;
}
.instructor-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.instructor-avatar:hover {
  transform: scale(1.03);
}

.multi-avatar-wrap {
  width: 130px;
  height: 130px;
}
.multi-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.featured-card:hover .multi-avatar {
  transform: scale(1.05);
}

.featured-card {
  border-radius: 16px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  background-color: #ffffff;
}
.featured-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.08) !important;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
