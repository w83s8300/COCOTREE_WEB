<template>
  <div class="gallery-management">
    <!-- 頂部標題與操作列 -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
      <div>
        <h2 class="fw-bold mb-1 d-flex align-items-center gap-2">
          <i class="bi bi-images text-primary"></i>
          <span>活動花絮與相簿管理</span>
        </h2>
        <p class="text-muted small mb-0">管理官網活動花絮相簿、批量上傳活動照片、編輯圖說並設定精選封面</p>
      </div>
      <div class="d-flex gap-2">
        <button @click="openCreateAlbumModal" class="btn btn-primary d-flex align-items-center gap-2 shadow-sm">
          <i class="bi bi-folder-plus"></i>
          <span>新增相簿</span>
        </button>
      </div>
    </div>

    <!-- 統計與搜尋列 -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body p-3">
        <div class="row g-3 align-items-center">
          <div class="col-md-5">
            <div class="input-group">
              <span class="input-group-text bg-white text-muted border-end-0">
                <i class="bi bi-search"></i>
              </span>
              <input
                type="text"
                v-model="searchQuery"
                class="form-control border-start-0"
                placeholder="搜尋相簿名稱、活動描述或日期..."
              />
              <button v-if="searchQuery" class="btn btn-outline-secondary" type="button" @click="searchQuery = ''">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
          </div>
          <div class="col-md-3">
            <select v-model="filterStatus" class="form-select">
              <option value="all">全部狀態 (發布與隱藏)</option>
              <option value="published">僅顯示已發布</option>
              <option value="unpublished">僅顯示未發布 (隱藏)</option>
            </select>
          </div>
          <div class="col-md-4 text-md-end text-muted small">
            <span class="badge bg-primary-subtle text-primary border border-primary-subtle me-2 px-2 py-1">
              相簿：{{ filteredAlbums.length }} 本
            </span>
            <span class="badge bg-secondary-subtle text-secondary border border-secondary-subtle px-2 py-1">
              總照片：{{ totalPhotosCount }} 張
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入活動花絮資料...</p>
    </div>

    <!-- 錯誤狀態 -->
    <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <div>
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        <span>{{ error }}</span>
      </div>
      <button @click="fetchAlbums" class="btn btn-outline-danger btn-sm">重新嘗試</button>
    </div>

    <!-- 空資料狀態 -->
    <div v-else-if="filteredAlbums.length === 0" class="text-center py-5 text-muted bg-white rounded-3 shadow-sm border">
      <i class="bi bi-images fs-1 text-muted opacity-50"></i>
      <p class="mt-2 mb-2">尚無符合條件的活動花絮相簿</p>
      <button @click="openCreateAlbumModal" class="btn btn-outline-primary btn-sm">
        <i class="bi bi-plus-lg me-1"></i>建立第一本相簿
      </button>
    </div>

    <!-- 相簿網格卡片列表 -->
    <div v-else class="row g-4">
      <div
        v-for="album in filteredAlbums"
        :key="album.id"
        class="col-xl-4 col-md-6"
      >
        <div class="card album-card h-100 border-0 shadow-sm overflow-hidden">
          <!-- 封面圖區塊 -->
          <div class="position-relative album-cover-wrap" @click="openPhotosModal(album)">
            <img
              v-if="album.cover_image"
              :src="album.cover_image"
              class="card-img-top album-cover-img"
              :alt="album.title"
              loading="lazy"
            />
            <div v-else class="album-cover-placeholder d-flex flex-column align-items-center justify-content-center text-muted">
              <i class="bi bi-image fs-1 opacity-25"></i>
              <span class="small mt-1">暫無相簿封面</span>
            </div>

            <!-- 照片數量浮水印標籤 -->
            <span class="badge bg-dark bg-opacity-75 text-white position-absolute bottom-0 end-0 m-2 px-2 py-1 shadow-sm">
              <i class="bi bi-camera me-1"></i>{{ album.photo_count || 0 }} 張相片
            </span>

            <!-- 發布狀態標籤 -->
            <span
              class="badge position-absolute top-0 start-0 m-2 shadow-sm"
              :class="album.is_published ? 'bg-success' : 'bg-secondary'"
            >
              {{ album.is_published ? '已發布' : '未發布 (隱藏)' }}
            </span>

            <!-- 排序順序標籤 -->
            <span v-if="album.sort_order > 0" class="badge bg-light text-dark border position-absolute top-0 end-0 m-2 shadow-sm">
              順序: {{ album.sort_order }}
            </span>
          </div>

          <!-- 卡片內容區 -->
          <div class="card-body d-flex flex-column p-3">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title fw-bold text-dark text-truncate mb-0" :title="album.title">
                {{ album.title }}
              </h5>
            </div>

            <!-- 活動日期 -->
            <div class="text-muted small mb-2 d-flex align-items-center">
              <i class="bi bi-calendar-event me-1 text-primary"></i>
              <span>{{ album.event_date || '未設定活動日期' }}</span>
            </div>

            <!-- 描述 -->
            <p class="card-text text-secondary small album-desc flex-grow-1 mb-3">
              {{ album.description || '尚無相簿活動詳細介紹說明。' }}
            </p>

            <!-- 底部操作列 -->
            <div class="pt-2 border-top d-flex justify-content-between align-items-center">
              <!-- 快速切換前台發布 -->
              <div class="form-check form-switch mb-0" title="切換官網是否顯示此相簿">
                <input
                  class="form-check-input"
                  type="checkbox"
                  role="switch"
                  :id="'publishSwitch_' + album.id"
                  :checked="album.is_published"
                  @change="toggleAlbumPublish(album)"
                />
                <label class="form-check-label small text-muted" :for="'publishSwitch_' + album.id">
                  {{ album.is_published ? '公開' : '隱藏' }}
                </label>
              </div>

              <!-- 按鈕組 -->
              <div class="btn-group btn-group-sm">
                <button
                  type="button"
                  class="btn btn-outline-primary"
                  @click="openPhotosModal(album)"
                  title="管理此相簿內的相片"
                >
                  <i class="bi bi-images me-1"></i>管理相片 ({{ album.photo_count || 0 }})
                </button>
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  @click="openEditAlbumModal(album)"
                  title="編輯相簿標題與介紹"
                >
                  <i class="bi bi-pencil"></i>
                </button>
                <button
                  type="button"
                  class="btn btn-outline-danger"
                  @click="deleteAlbum(album)"
                  title="刪除此相簿"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================== -->
    <!-- Modal 1: 建立 / 編輯相簿基本資訊彈窗 -->
    <!-- ============================================== -->
    <div class="modal fade" id="albumInfoModal" tabindex="-1" ref="albumInfoModalRef">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content shadow border-0">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">
              <i class="bi" :class="editingAlbum.id ? 'bi-pencil-square text-primary' : 'bi-folder-plus text-success'"></i>
              <span class="ms-2">{{ editingAlbum.id ? '編輯相簿資訊' : '新增活動花絮相簿' }}</span>
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <form @submit.prevent="submitAlbumForm">
            <div class="modal-body p-4">
              <!-- 相簿標題 -->
              <div class="mb-3">
                <label class="form-label fw-bold">
                  相簿名稱 <span class="text-danger">*</span>
                </label>
                <input
                  type="text"
                  v-model="albumForm.title"
                  class="form-control"
                  placeholder="例如：2024 夏季街舞成果展"
                  required
                />
              </div>

              <!-- 活動日期 與 排序順序 -->
              <div class="row g-3 mb-3">
                <div class="col-6">
                  <label class="form-label fw-bold">活動日期</label>
                  <input
                    type="date"
                    v-model="albumForm.event_date"
                    class="form-control"
                  />
                </div>
                <div class="col-6">
                  <label class="form-label fw-bold">排序權重 (越小越前)</label>
                  <input
                    type="number"
                    v-model.number="albumForm.sort_order"
                    class="form-control"
                    min="0"
                    placeholder="0"
                  />
                </div>
              </div>

              <!-- 相簿封面照片 -->
              <div class="mb-3">
                <label class="form-label fw-bold">封面照片</label>
                <div class="d-flex align-items-center gap-3 mb-2">
                  <div
                    class="album-cover-preview rounded border bg-light overflow-hidden d-flex align-items-center justify-content-center"
                    style="width: 100px; height: 70px; flex-shrink: 0;"
                  >
                    <img
                      v-if="albumForm.cover_image"
                      :src="albumForm.cover_image"
                      alt="封面預覽"
                      class="w-100 h-100 object-fit-cover"
                    />
                    <i v-else class="bi bi-image text-muted fs-4"></i>
                  </div>
                  <div class="flex-grow-1">
                    <input
                      type="file"
                      ref="coverFileInput"
                      class="d-none"
                      accept="image/*"
                      @change="handleCoverUpload"
                    />
                    <button
                      type="button"
                      class="btn btn-outline-primary btn-sm mb-1 d-flex align-items-center gap-1"
                      :disabled="uploadingCover"
                      @click="$refs.coverFileInput.click()"
                    >
                      <span v-if="uploadingCover" class="spinner-border spinner-border-sm"></span>
                      <i v-else class="bi bi-cloud-arrow-up"></i>
                      <span>{{ uploadingCover ? '上傳中...' : '上傳封面照片' }}</span>
                    </button>
                    <div class="form-text small">支援 JPG、PNG、WEBP 圖片</div>
                  </div>
                </div>
                <div class="input-group input-group-sm">
                  <span class="input-group-text bg-light text-muted">或輸入圖片網址</span>
                  <input
                    type="text"
                    v-model="albumForm.cover_image"
                    class="form-control"
                    placeholder="https://... 或 /api/uploads/..."
                  />
                  <button
                    v-if="albumForm.cover_image"
                    class="btn btn-outline-secondary"
                    type="button"
                    @click="albumForm.cover_image = ''"
                  >
                    清除
                  </button>
                </div>
              </div>

              <!-- 相簿活動介紹 -->
              <div class="mb-3">
                <label class="form-label fw-bold">活動花絮描述 / 介紹</label>
                <textarea
                  v-model="albumForm.description"
                  class="form-control"
                  rows="3"
                  placeholder="介紹這次活動的精彩花絮、亮點或學員心得..."
                ></textarea>
              </div>

              <!-- 發布開關 -->
              <div class="form-check form-switch">
                <input
                  class="form-check-input"
                  type="checkbox"
                  role="switch"
                  id="albumPublishSwitch"
                  v-model="albumForm.is_published"
                />
                <label class="form-check-label fw-bold" for="albumPublishSwitch">
                  立即於官網活動花絮專區公開展示
                </label>
              </div>
            </div>
            <div class="modal-footer bg-light">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="submittingAlbum">
                <span v-if="submittingAlbum" class="spinner-border spinner-border-sm me-1"></span>
                <span>{{ editingAlbum.id ? '儲存變更' : '建立相簿' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- ============================================== -->
    <!-- Modal 2: 相簿照片管理與批量上傳彈窗 -->
    <!-- ============================================== -->
    <div class="modal fade" id="photosModal" tabindex="-1" ref="photosModalRef" data-bs-backdrop="static">
      <div class="modal-dialog modal-dialog-centered modal-xl modal-dialog-scrollable">
        <div class="modal-content shadow border-0">
          <div class="modal-header bg-light">
            <div>
              <h5 class="modal-title fw-bold text-dark d-flex align-items-center gap-2">
                <i class="bi bi-camera-reels text-primary"></i>
                <span>管理相片 — {{ activeAlbum?.title }}</span>
              </h5>
              <div class="small text-muted mt-1">
                <span>目前共有 {{ activeAlbumPhotos.length }} 張相片</span>
                <span v-if="activeAlbum?.event_date" class="ms-2">
                  <i class="bi bi-calendar3 me-1"></i>{{ activeAlbum.event_date }}
                </span>
              </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" @click="closePhotosModal"></button>
          </div>

          <div class="modal-body p-4">
            <!-- 批量上傳與新增相片工具列 -->
            <div class="card border-0 bg-light rounded-3 p-3 mb-4">
              <div class="row g-3 align-items-center">
                <!-- 批量上傳按鈕 -->
                <div class="col-md-auto">
                  <input
                    type="file"
                    ref="batchFileInput"
                    class="d-none"
                    multiple
                    accept="image/*"
                    @change="handleBatchUpload"
                  />
                  <button
                    type="button"
                    class="btn btn-success d-flex align-items-center gap-2 shadow-sm"
                    :disabled="uploadingBatch"
                    @click="$refs.batchFileInput.click()"
                  >
                    <span v-if="uploadingBatch" class="spinner-border spinner-border-sm"></span>
                    <i v-else class="bi bi-cloud-arrow-up-fill fs-5"></i>
                    <span class="fw-bold">{{ uploadingBatch ? '照片上傳處理中...' : '批量上傳相片 (可多選)' }}</span>
                  </button>
                </div>

                <!-- 或透過網址加入照片 -->
                <div class="col-md">
                  <div class="input-group">
                    <span class="input-group-text bg-white text-muted">
                      <i class="bi bi-link-45deg"></i>
                    </span>
                    <input
                      type="text"
                      v-model="newPhotoUrl"
                      class="form-control"
                      placeholder="或貼上外部圖片網址 (https://...)..."
                    />
                    <input
                      type="text"
                      v-model="newPhotoDesc"
                      class="form-control d-none d-lg-block"
                      placeholder="照片描述說明 (選填)..."
                      style="max-width: 240px;"
                    />
                    <button
                      type="button"
                      class="btn btn-outline-primary"
                      :disabled="!newPhotoUrl.trim() || addingPhotoUrl"
                      @click="addPhotoByUrl"
                    >
                      <span v-if="addingPhotoUrl" class="spinner-border spinner-border-sm me-1"></span>
                      <span>加入相片</span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- 上傳進度提示 -->
              <div v-if="uploadingBatch" class="mt-3">
                <div class="progress" style="height: 6px;">
                  <div class="progress-bar progress-bar-striped progress-bar-animated bg-success" style="width: 100%;"></div>
                </div>
                <div class="small text-muted mt-1 text-center">正在為您上傳並優化照片，請稍候...</div>
              </div>
            </div>

            <!-- 照片載入中 -->
            <div v-if="loadingPhotos" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">載入相片中...</span>
              </div>
              <p class="mt-2 text-muted">正在載入相簿照片...</p>
            </div>

            <!-- 無照片空狀態 -->
            <div v-else-if="activeAlbumPhotos.length === 0" class="text-center py-5 bg-white border rounded-3 text-muted">
              <i class="bi bi-images fs-1 opacity-25"></i>
              <p class="mt-3 mb-2 fw-bold text-dark">此相簿目前還沒有任何相片</p>
              <p class="small text-muted mb-3">您可以點擊上方「批量上傳相片」選取多張照片，或貼上圖片連結</p>
              <button
                type="button"
                class="btn btn-primary btn-sm"
                @click="$refs.batchFileInput.click()"
              >
                <i class="bi bi-cloud-arrow-up me-1"></i>立刻選取相片上傳
              </button>
            </div>

            <!-- 照片列表網格 -->
            <div v-else class="row g-3">
              <div
                v-for="photo in activeAlbumPhotos"
                :key="photo.id"
                class="col-xxl-3 col-lg-4 col-sm-6"
              >
                <div class="card h-100 border shadow-sm photo-item-card overflow-hidden">
                  <!-- 照片縮圖 -->
                  <div class="position-relative photo-thumb-wrap">
                    <img
                      :src="photo.image_url"
                      class="w-100 photo-thumb-img"
                      :alt="photo.description || '活動花絮相片'"
                      loading="lazy"
                    />

                    <!-- 封面標籤 -->
                    <span
                      v-if="photo.image_url === activeAlbum?.cover_image"
                      class="badge bg-warning text-dark position-absolute top-0 start-0 m-2 shadow-sm fw-bold"
                    >
                      <i class="bi bi-star-fill me-1"></i>目前封面
                    </span>

                    <!-- 設為封面快捷按鈕 (若非封面) -->
                    <button
                      v-else
                      type="button"
                      class="btn btn-sm btn-dark bg-opacity-75 text-white position-absolute top-0 start-0 m-2 border-0 shadow-sm set-cover-btn"
                      @click="setAsAlbumCover(photo)"
                      title="將此相片設為相簿封面"
                    >
                      <i class="bi bi-star me-1"></i>設為封面
                    </button>

                    <!-- 刪除照片按鈕 -->
                    <button
                      type="button"
                      class="btn btn-sm btn-danger position-absolute top-0 end-0 m-2 shadow-sm rounded-circle p-1 d-flex align-items-center justify-content-center"
                      style="width: 28px; height: 28px;"
                      @click="deletePhoto(photo)"
                      title="刪除此相片"
                    >
                      <i class="bi bi-trash-fill small"></i>
                    </button>
                  </div>

                  <!-- 圖說編輯區 -->
                  <div class="card-body p-2 bg-light">
                    <div class="input-group input-group-sm">
                      <input
                        type="text"
                        v-model="photo.description"
                        class="form-control bg-white"
                        placeholder="點此輸入照片圖說..."
                        @blur="savePhotoDescription(photo)"
                        @keyup.enter="savePhotoDescription(photo)"
                      />
                      <button
                        class="btn btn-outline-secondary"
                        type="button"
                        @click="savePhotoDescription(photo)"
                        title="儲存圖說"
                      >
                        <i class="bi bi-check2"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer bg-light">
            <span class="text-muted small me-auto">
              <i class="bi bi-info-circle me-1"></i>提示：輸入照片圖說後按 Enter 或移開即可自動儲存。
            </span>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" @click="closePhotosModal">
              完成關閉
            </button>
          </div>
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
  name: 'GalleryManagement',
  data() {
    return {
      albums: [],
      loading: true,
      error: null,
      searchQuery: '',
      filterStatus: 'all',

      // 相簿編輯 Modal
      albumInfoModalInstance: null,
      submittingAlbum: false,
      uploadingCover: false,
      editingAlbum: {},
      albumForm: {
        title: '',
        description: '',
        cover_image: '',
        event_date: new Date().toISOString().substring(0, 10),
        sort_order: 0,
        is_published: true
      },

      // 相簿相片管理 Modal
      photosModalInstance: null,
      activeAlbum: null,
      activeAlbumPhotos: [],
      loadingPhotos: false,
      uploadingBatch: false,
      addingPhotoUrl: false,
      newPhotoUrl: '',
      newPhotoDesc: ''
    };
  },
  computed: {
    filteredAlbums() {
      return this.albums.filter(album => {
        // 狀態過濾
        if (this.filterStatus === 'published' && !album.is_published) return false;
        if (this.filterStatus === 'unpublished' && album.is_published) return false;

        // 關鍵字搜尋
        const q = this.searchQuery.trim().toLowerCase();
        if (!q) return true;

        const titleMatch = album.title && album.title.toLowerCase().includes(q);
        const descMatch = album.description && album.description.toLowerCase().includes(q);
        const dateMatch = album.event_date && String(album.event_date).toLowerCase().includes(q);
        return titleMatch || descMatch || dateMatch;
      });
    },
    totalPhotosCount() {
      return this.albums.reduce((acc, curr) => acc + (curr.photo_count || 0), 0);
    }
  },
  mounted() {
    if (this.$refs.albumInfoModalRef) {
      this.albumInfoModalInstance = new Modal(this.$refs.albumInfoModalRef);
    }
    if (this.$refs.photosModalRef) {
      this.photosModalInstance = new Modal(this.$refs.photosModalRef);
    }
    this.fetchAlbums();
  },
  beforeUnmount() {
    if (this.albumInfoModalInstance) this.albumInfoModalInstance.dispose();
    if (this.photosModalInstance) this.photosModalInstance.dispose();
  },
  methods: {
    async fetchAlbums() {
      this.loading = true;
      this.error = null;
      try {
        const res = await api.get('/gallery/albums?admin=1');
        this.albums = res.albums || [];
      } catch (err) {
        this.error = err.message || '無法取得相簿列表，請確認伺服器連線狀態。';
      } finally {
        this.loading = false;
      }
    },

    openCreateAlbumModal() {
      this.editingAlbum = {};
      this.albumForm = {
        title: '',
        description: '',
        cover_image: '',
        event_date: new Date().toISOString().substring(0, 10),
        sort_order: (this.albums.length + 1),
        is_published: true
      };
      this.albumInfoModalInstance?.show();
    },

    openEditAlbumModal(album) {
      this.editingAlbum = { ...album };
      this.albumForm = {
        title: album.title || '',
        description: album.description || '',
        cover_image: album.cover_image || '',
        event_date: album.event_date || new Date().toISOString().substring(0, 10),
        sort_order: album.sort_order ?? 0,
        is_published: Boolean(album.is_published)
      };
      this.albumInfoModalInstance?.show();
    },

    async handleCoverUpload(e) {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!file.type.startsWith('image/')) {
        showToast('請選取有效的圖片檔案 (JPG, PNG, WEBP)！', 'error');
        return;
      }
      this.uploadingCover = true;
      try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await api.post('/upload/gallery-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        if (res.image_url) {
          this.albumForm.cover_image = res.image_url;
          showToast('封面照片上傳成功！', 'success');
        }
      } catch (err) {
        showToast(err.message || '圖片上傳失敗', 'error');
      } finally {
        this.uploadingCover = false;
        if (e.target) e.target.value = '';
      }
    },

    async submitAlbumForm() {
      if (!this.albumForm.title.trim()) {
        showToast('請填寫相簿名稱！', 'warning');
        return;
      }
      this.submittingAlbum = true;
      try {
        if (this.editingAlbum.id) {
          await api.put(`/gallery/albums/${this.editingAlbum.id}`, this.albumForm);
          showToast('相簿資料已更新！', 'success');
        } else {
          await api.post('/gallery/albums', this.albumForm);
          showToast('新相簿已成功建立！', 'success');
        }
        this.albumInfoModalInstance?.hide();
        await this.fetchAlbums();
      } catch (err) {
        showToast(err.message || '儲存相簿失敗', 'error');
      } finally {
        this.submittingAlbum = false;
      }
    },

    async toggleAlbumPublish(album) {
      const newState = !album.is_published;
      try {
        await api.put(`/gallery/albums/${album.id}`, { is_published: newState });
        album.is_published = newState;
        showToast(newState ? `「${album.title}」已於官網發布` : `「${album.title}」已隱藏`, 'info');
      } catch (err) {
        showToast('更新發布狀態失敗', 'error');
      }
    },

    async deleteAlbum(album) {
      const ok = await showConfirm(
        `確定要刪除相簿「${album.title}」嗎？相簿內的所有相片與記錄將一併刪除，此動作無法復原！`,
        '刪除活動相簿'
      );
      if (!ok) return;

      try {
        await api.delete(`/gallery/albums/${album.id}`);
        showToast('相簿已成功刪除！', 'success');
        await this.fetchAlbums();
      } catch (err) {
        showToast(err.message || '刪除失敗', 'error');
      }
    },

    // ==============================================
    // 相簿照片管理
    // ==============================================
    async openPhotosModal(album) {
      this.activeAlbum = album;
      this.activeAlbumPhotos = [];
      this.newPhotoUrl = '';
      this.newPhotoDesc = '';
      this.photosModalInstance?.show();
      await this.fetchAlbumPhotos(album.id);
    },

    async fetchAlbumPhotos(albumId) {
      this.loadingPhotos = true;
      try {
        const res = await api.get(`/gallery/albums/${albumId}`);
        if (res.album) {
          this.activeAlbum = res.album;
          this.activeAlbumPhotos = res.album.photos || [];
        }
      } catch (err) {
        showToast('無法取得相片清單', 'error');
      } finally {
        this.loadingPhotos = false;
      }
    },

    closePhotosModal() {
      this.fetchAlbums();
    },

    async handleBatchUpload(e) {
      const files = e.target.files;
      if (!files || files.length === 0) return;

      this.uploadingBatch = true;
      try {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
          formData.append('files', files[i]);
        }

        // 1. 上傳圖檔取得 URLs
        const uploadRes = await api.post('/upload/gallery-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        const urls = uploadRes.image_urls || (uploadRes.image_url ? [uploadRes.image_url] : []);
        if (urls.length === 0) {
          throw new Error('未能取得已上傳之圖片網址');
        }

        // 2. 批量寫入相簿資料庫
        await api.post(`/gallery/albums/${this.activeAlbum.id}/photos`, {
          image_urls: urls
        });

        showToast(`成功上傳並新增 ${urls.length} 張相片！`, 'success');
        await this.fetchAlbumPhotos(this.activeAlbum.id);
      } catch (err) {
        showToast(err.message || '照片批量上傳失敗', 'error');
      } finally {
        this.uploadingBatch = false;
        if (e.target) e.target.value = '';
      }
    },

    async addPhotoByUrl() {
      const url = this.newPhotoUrl.trim();
      if (!url) return;

      this.addingPhotoUrl = true;
      try {
        await api.post(`/gallery/albums/${this.activeAlbum.id}/photos`, {
          image_url: url,
          description: this.newPhotoDesc.trim()
        });
        showToast('相片已成功加入相簿！', 'success');
        this.newPhotoUrl = '';
        this.newPhotoDesc = '';
        await this.fetchAlbumPhotos(this.activeAlbum.id);
      } catch (err) {
        showToast(err.message || '加入相片失敗', 'error');
      } finally {
        this.addingPhotoUrl = false;
      }
    },

    async savePhotoDescription(photo) {
      try {
        await api.put(`/gallery/photos/${photo.id}`, {
          description: photo.description
        });
        showToast('圖說已儲存', 'success');
      } catch (err) {
        showToast('圖說儲存失敗', 'error');
      }
    },

    async setAsAlbumCover(photo) {
      try {
        await api.put(`/gallery/albums/${this.activeAlbum.id}/cover`, {
          cover_image: photo.image_url
        });
        this.activeAlbum.cover_image = photo.image_url;
        showToast('已成功設定為相簿封面！', 'success');
      } catch (err) {
        showToast('設定封面失敗', 'error');
      }
    },

    async deletePhoto(photo) {
      const ok = await showConfirm('確定要刪除這張相片嗎？', '刪除相片');
      if (!ok) return;

      try {
        await api.delete(`/gallery/photos/${photo.id}`);
        showToast('相片已刪除', 'success');
        await this.fetchAlbumPhotos(this.activeAlbum.id);
      } catch (err) {
        showToast('刪除相片失敗', 'error');
      }
    }
  }
};
</script>

<style scoped>
.gallery-management {
  padding: 10px;
}

.album-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border-radius: 12px;
}

.album-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08) !important;
}

.album-cover-wrap {
  height: 200px;
  background-color: #f8f9fa;
  cursor: pointer;
  overflow: hidden;
}

.album-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.album-cover-wrap:hover .album-cover-img {
  transform: scale(1.04);
}

.album-cover-placeholder {
  width: 100%;
  height: 100%;
}

.album-desc {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.6rem;
}

.photo-item-card {
  border-radius: 8px;
  transition: transform 0.15s ease;
}

.photo-item-card:hover {
  transform: translateY(-2px);
}

.photo-thumb-wrap {
  height: 170px;
  background-color: #000;
  overflow: hidden;
}

.photo-thumb-img {
  height: 100%;
  object-fit: cover;
}

.set-cover-btn {
  opacity: 0.85;
  transition: opacity 0.2s ease;
}

.set-cover-btn:hover {
  opacity: 1;
}
</style>

