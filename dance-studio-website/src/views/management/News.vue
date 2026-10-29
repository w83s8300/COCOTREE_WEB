<template>
  <div class="news-management">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
      <div>
        <h2 class="fw-bold mb-1">最新消息與活動管理</h2>
        <p class="text-muted small mb-0">管理官網首頁的最新消息公告與近期活動展示</p>
      </div>
      <button @click="openCreateModal" class="btn btn-success d-flex align-items-center gap-1 shadow-sm">
        <i class="bi bi-plus-lg"></i>
        <span>新增消息 / 活動</span>
      </button>
    </div>

    <!-- 篩選與搜尋列 -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body p-3">
        <div class="row g-2 align-items-center">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-white text-muted"><i class="bi bi-search"></i></span>
              <input
                type="text"
                v-model="searchQuery"
                class="form-control"
                placeholder="搜尋標題、摘要或內文..."
              >
            </div>
          </div>
          <div class="col-md-3">
            <select v-model="filterCategory" class="form-select">
              <option value="">全部類型 (消息與活動)</option>
              <option value="news">最新消息</option>
              <option value="event">近期活動</option>
            </select>
          </div>
          <div class="col-md-auto ms-auto text-muted small">
            共 {{ filteredNews.length }} 則公告活動
          </div>
        </div>
      </div>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入資料...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ error }}</span>
      <button @click="fetchNewsList" class="btn btn-outline-danger btn-sm">重新嘗試</button>
    </div>

    <!-- 空資料狀態 -->
    <div v-else-if="filteredNews.length === 0" class="text-center py-5 text-muted bg-white rounded-3 shadow-sm border">
      <i class="bi bi-newspaper fs-1 text-muted opacity-50"></i>
      <p class="mt-2 mb-0">尚無符合條件的消息或活動</p>
    </div>

    <!-- 資料表格 -->
    <div v-else class="card border-0 shadow-sm overflow-hidden">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th scope="col" style="width: 80px;" class="text-center">照片</th>
              <th scope="col" style="width: 100px;">類型</th>
              <th scope="col" style="width: 110px;">標籤</th>
              <th scope="col">標題與摘要</th>
              <th scope="col" style="width: 120px;">發布日期</th>
              <th scope="col" style="width: 90px;" class="text-center">狀態</th>
              <th scope="col" style="width: 140px;" class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredNews" :key="item.id">
              <td class="text-center p-2">
                <img
                  v-if="item.image_url"
                  :src="item.image_url"
                  class="rounded object-fit-cover shadow-sm border"
                  style="width: 65px; height: 45px;"
                  :alt="item.title"
                />
                <span v-else class="badge bg-light text-muted border small">無圖片</span>
              </td>
              <td>
                <span class="badge" :class="item.category === 'event' ? 'bg-danger-subtle text-danger' : 'bg-primary-subtle text-primary'">
                  {{ item.category === 'event' ? '近期活動' : '最新消息' }}
                </span>
              </td>
              <td>
                <span class="badge bg-light text-dark border">
                  {{ item.tag || '一般' }}
                </span>
              </td>
              <td>
                <div class="fw-bold text-dark mb-1">{{ item.title }}</div>
                <div class="small text-muted text-truncate" style="max-width: 380px;">
                  {{ item.summary || item.content }}
                </div>
              </td>
              <td class="small text-muted font-monospace">
                {{ item.publish_date }}
              </td>
              <td class="text-center">
                <span class="badge" :class="item.is_published ? 'bg-success' : 'bg-secondary'">
                  {{ item.is_published ? '公開中' : '草稿' }}
                </span>
              </td>
              <td class="text-center">
                <button @click="openEditModal(item)" class="btn btn-outline-primary btn-sm me-1" title="編輯">
                  <i class="bi bi-pencil-square"></i>
                </button>
                <button @click="deleteItem(item)" class="btn btn-outline-danger btn-sm" title="刪除">
                  <i class="bi bi-trash3"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新增 / 編輯彈窗 -->
    <div class="modal fade" id="newsFormModal" tabindex="-1" aria-labelledby="newsFormModalLabel" aria-hidden="true" ref="newsModalRef">
      <div class="modal-dialog modal-lg">
        <div class="modal-content border-0 shadow-lg rounded-4">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold" id="newsFormModalLabel">
              {{ editingItem.id ? '編輯消息 / 活動' : '新增消息 / 活動' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <form @submit.prevent="submitForm">
            <div class="modal-body p-4">
              <!-- 類型與標籤 -->
              <div class="row g-3 mb-3">
                <div class="col-md-6">
                  <label class="form-label fw-bold small">分類類型 <span class="text-danger">*</span></label>
                  <select v-model="form.category" class="form-select" required>
                    <option value="news">最新消息 (首頁消息公告)</option>
                    <option value="event">近期活動 (首頁活動專區)</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold small">標籤名稱</label>
                  <input
                    type="text"
                    v-model="form.tag"
                    class="form-control"
                    placeholder="例如：課程公告、年度盛典、場地優惠"
                  >
                </div>
              </div>

              <!-- 標題 -->
              <div class="mb-3">
                <label class="form-label fw-bold small">標題 <span class="text-danger">*</span></label>
                <input
                  type="text"
                  v-model="form.title"
                  class="form-control"
                  placeholder="請輸入消息或活動標題"
                  required
                >
              </div>

              <!-- 封面圖片上傳與網址 -->
              <div class="mb-3 p-3 bg-light rounded-3 border">
                <label class="form-label fw-bold small mb-2 d-block">封面圖片</label>
                <div class="d-flex flex-column flex-sm-row gap-3 align-items-center">
                  <div
                    class="position-relative rounded-3 overflow-hidden border bg-white shadow-sm flex-shrink-0"
                    style="width: 140px; height: 90px; cursor: pointer;"
                    @click="$refs.newsFileInput.click()"
                    title="點擊上傳圖片"
                  >
                    <img
                      v-if="form.image_url"
                      :src="form.image_url"
                      class="w-100 h-100 object-fit-cover"
                      alt="圖片預覽"
                    >
                    <div v-else class="w-100 h-100 d-flex flex-column align-items-center justify-content-center text-muted">
                      <i class="bi bi-camera fs-3"></i>
                      <span style="font-size: 11px;">點擊選圖</span>
                    </div>
                  </div>
                  <input
                    type="file"
                    ref="newsFileInput"
                    class="d-none"
                    accept="image/*"
                    @change="handleFileUpload"
                  >
                  <div class="flex-grow-1 w-100">
                    <div class="input-group input-group-sm mb-2">
                      <span class="input-group-text"><i class="bi bi-link-45deg"></i></span>
                      <input
                        type="text"
                        v-model="form.image_url"
                        class="form-control"
                        placeholder="或直接輸入圖片網址 (URL)..."
                      >
                    </div>
                    <div class="d-flex gap-2">
                      <button
                        type="button"
                        class="btn btn-outline-primary btn-sm"
                        @click="$refs.newsFileInput.click()"
                        :disabled="uploadingImage"
                      >
                        <span v-if="uploadingImage" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-upload me-1"></i>上傳照片
                      </button>
                      <button
                        type="button"
                        v-if="form.image_url"
                        class="btn btn-outline-danger btn-sm"
                        @click="form.image_url = ''"
                      >
                        移除
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 簡短摘要 -->
              <div class="mb-3">
                <label class="form-label fw-bold small">簡短摘要 (卡片上顯示的介紹)</label>
                <textarea
                  v-model="form.summary"
                  class="form-control"
                  rows="2"
                  placeholder="以 1~2 句話吸引學員閱讀..."
                ></textarea>
              </div>

              <!-- 詳細內文 -->
              <div class="mb-3">
                <label class="form-label fw-bold small">詳細內文 (彈窗完整內容) <span class="text-danger">*</span></label>
                <textarea
                  v-model="form.content"
                  class="form-control"
                  rows="5"
                  placeholder="請輸入詳細內容、規則或報名說明..."
                  required
                ></textarea>
              </div>

              <!-- 發布日期與上架狀態 -->
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-bold small">發布日期</label>
                  <input type="date" v-model="form.publish_date" class="form-control">
                </div>
                <div class="col-md-6 d-flex align-items-center pt-md-4">
                  <div class="form-check form-switch">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      id="isPublishedSwitch"
                      v-model="form.is_published"
                    >
                    <label class="form-check-label fw-bold" for="isPublishedSwitch">立即公開發布於官網</label>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer bg-light px-4 py-3">
              <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">取消</button>
              <button type="submit" class="btn btn-primary rounded-pill px-4" :disabled="submitting || uploadingImage">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
                {{ editingItem.id ? '儲存變更' : '建立發布' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import api from '@/utils/api';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';

export default {
  name: 'NewsManagement',
  data() {
    return {
      newsList: [],
      loading: true,
      error: null,
      submitting: false,
      uploadingImage: false,
      searchQuery: '',
      filterCategory: '',
      modalInstance: null,
      editingItem: {},
      form: {
        category: 'news',
        tag: '公告',
        title: '',
        image_url: '',
        summary: '',
        content: '',
        publish_date: new Date().toISOString().substring(0, 10),
        is_published: true
      }
    };
  },
  computed: {
    filteredNews() {
      return this.newsList.filter(item => {
        const matchesCategory = !this.filterCategory || item.category === this.filterCategory;
        const query = this.searchQuery.trim().toLowerCase();
        const matchesQuery = !query
          || (item.title && item.title.toLowerCase().includes(query))
          || (item.summary && item.summary.toLowerCase().includes(query))
          || (item.content && item.content.toLowerCase().includes(query))
          || (item.tag && item.tag.toLowerCase().includes(query));
        return matchesCategory && matchesQuery;
      });
    }
  },
  mounted() {
    this.modalInstance = new Modal(this.$refs.newsModalRef);
    this.fetchNewsList();
  },
  beforeUnmount() {
    if (this.modalInstance) {
      this.modalInstance.dispose();
    }
  },
  methods: {
    async fetchNewsList() {
      this.loading = true;
      this.error = null;
      try {
        const res = await api.get('/news');
        this.newsList = res.news || [];
      } catch (err) {
        this.error = '無法取得最新消息列表，請檢查後端連線。';
      } finally {
        this.loading = false;
      }
    },
    openCreateModal() {
      this.editingItem = {};
      this.form = {
        category: 'news',
        tag: '課程公告',
        title: '',
        image_url: '',
        summary: '',
        content: '',
        publish_date: new Date().toISOString().substring(0, 10),
        is_published: true
      };
      this.modalInstance.show();
    },
    openEditModal(item) {
      this.editingItem = { ...item };
      this.form = {
        category: item.category || 'news',
        tag: item.tag || '公告',
        title: item.title || '',
        image_url: item.image_url || '',
        summary: item.summary || '',
        content: item.content || '',
        publish_date: item.publish_date || new Date().toISOString().substring(0, 10),
        is_published: Boolean(item.is_published)
      };
      this.modalInstance.show();
    },
    async handleFileUpload(e) {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!file.type.startsWith('image/')) {
        showToast('請選取有效的圖片檔案！', 'error');
        return;
      }
      this.uploadingImage = true;
      try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await api.post('/upload/room-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        if (res.image_url) {
          this.form.image_url = res.image_url;
          showToast('圖片上傳成功！', 'success');
        }
      } catch (err) {
        showToast('圖片上傳失敗', 'error');
      } finally {
        this.uploadingImage = false;
        if (e.target) e.target.value = '';
      }
    },
    async submitForm() {
      this.submitting = true;
      try {
        if (this.editingItem.id) {
          await api.put(`/news/${this.editingItem.id}`, this.form);
          showToast('消息更新成功！', 'success');
        } else {
          await api.post('/news', this.form);
          showToast('消息發布成功！', 'success');
        }
        this.modalInstance.hide();
        await this.fetchNewsList();
      } catch (err) {
        showToast(err.message || '儲存失敗', 'error');
      } finally {
        this.submitting = false;
      }
    },
    async deleteItem(item) {
      const ok = await showConfirm(`確定要刪除「${item.title}」嗎？此動作無法復原。`, '確認刪除');
      if (!ok) return;
      try {
        await api.delete(`/news/${item.id}`);
        showToast('已成功刪除', 'success');
        await this.fetchNewsList();
      } catch (err) {
        showToast('刪除失敗', 'error');
      }
    }
  }
};
</script>

<style scoped>
.news-management {
  padding: 10px;
}
</style>

