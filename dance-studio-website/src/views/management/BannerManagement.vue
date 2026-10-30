<template>
  <div class="banner-management">
    <!-- 頁頭資訊列 -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
      <div>
        <h2 class="fw-bold mb-1 d-flex align-items-center">
          <i class="bi bi-card-image text-primary me-2"></i>全站橫幅管理
        </h2>
        <p class="text-muted small mb-0">
          集中設定與管理首頁頂部輪播大圖、以及各分頁（關於我們、師資、課表、價目表等）的頂部宣傳橫幅
        </p>
      </div>
      <div class="d-flex gap-2">
        <a
          href="/"
          target="_blank"
          rel="noopener noreferrer"
          class="btn btn-outline-primary d-flex align-items-center gap-1 shadow-sm"
        >
          <i class="bi bi-box-arrow-up-right"></i>
          <span>前往官網首頁</span>
        </a>
        <button
          v-if="activeTab === 'home'"
          @click="openCreateModal"
          class="btn btn-primary d-flex align-items-center gap-1 shadow-sm"
        >
          <i class="bi bi-plus-lg"></i>
          <span>新增首頁橫幅</span>
        </button>
      </div>
    </div>

    <!-- 頁面標籤導覽 (Tabs) -->
    <ul class="nav nav-pills mb-4 bg-light p-2 rounded-3 border">
      <li class="nav-item">
        <button
          class="nav-link py-2 px-3 fw-bold"
          :class="{ active: activeTab === 'logo' }"
          @click="activeTab = 'logo'"
        >
          <i class="bi bi-badge-ad me-1"></i>
          主導航列 LOGO 設定
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link py-2 px-3 fw-bold"
          :class="{ active: activeTab === 'home' }"
          @click="activeTab = 'home'"
        >
          <i class="bi bi-collection-play me-1"></i>
          首頁輪播大圖 ({{ banners.length }})
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link py-2 px-3 fw-bold"
          :class="{ active: activeTab === 'pages' }"
          @click="activeTab = 'pages'"
        >
          <i class="bi bi-window-sidebar me-1"></i>
          各分頁頂部橫幅 ({{ pageBanners.length }})
        </button>
      </li>
    </ul>

    <!-- ==================== Tab 1: 首頁輪播橫幅 ==================== -->
    <div v-if="activeTab === 'home'">
      <!-- 狀態統計卡片 -->
      <div class="row g-3 mb-4">
        <div class="col-sm-6 col-lg-3">
          <div class="card border-0 shadow-sm h-100 stat-card">
            <div class="card-body p-3 d-flex align-items-center">
              <div class="stat-icon bg-primary-subtle text-primary rounded-3 me-3">
                <i class="bi bi-images fs-4"></i>
              </div>
              <div>
                <div class="text-muted small">總橫幅數</div>
                <div class="fs-4 fw-bold text-dark">{{ banners.length }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-sm-6 col-lg-3">
          <div class="card border-0 shadow-sm h-100 stat-card">
            <div class="card-body p-3 d-flex align-items-center">
              <div class="stat-icon bg-success-subtle text-success rounded-3 me-3">
                <i class="bi bi-check-circle-fill fs-4"></i>
              </div>
              <div>
                <div class="text-muted small">前台公開播放中</div>
                <div class="fs-4 fw-bold text-success">{{ activeBannersCount }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-sm-6 col-lg-3">
          <div class="card border-0 shadow-sm h-100 stat-card">
            <div class="card-body p-3 d-flex align-items-center">
              <div class="stat-icon bg-secondary-subtle text-secondary rounded-3 me-3">
                <i class="bi bi-pause-circle-fill fs-4"></i>
              </div>
              <div>
                <div class="text-muted small">草稿 / 已下架</div>
                <div class="fs-4 fw-bold text-muted">{{ inactiveBannersCount }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-sm-6 col-lg-3">
          <div class="card border-0 shadow-sm h-100 stat-card bg-light">
            <div class="card-body p-3 d-flex align-items-center">
              <div class="stat-icon bg-warning-subtle text-warning rounded-3 me-3">
                <i class="bi bi-lightbulb fs-4"></i>
              </div>
              <div class="small text-muted lh-sm">
                按排序號由小到大順序輪播；若僅有 1 張啟用則以靜態呈現。
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 載入中狀態 -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
        <p class="mt-2 text-muted">正在載入首頁橫幅資料...</p>
      </div>

      <!-- 錯誤狀態 -->
      <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
        <div>
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          <span>{{ error }}</span>
        </div>
        <button @click="fetchBanners" class="btn btn-outline-danger btn-sm">重新嘗試</button>
      </div>

      <!-- 空資料狀態 -->
      <div v-else-if="banners.length === 0" class="text-center py-5 bg-white rounded-3 shadow-sm border">
        <i class="bi bi-card-image fs-1 text-muted opacity-50"></i>
        <h5 class="fw-bold mt-3 mb-1">目前尚無任何首頁橫幅</h5>
        <p class="text-muted small mb-3">點擊上方按鈕建立您的第一張首頁輪播宣傳大圖</p>
        <button @click="openCreateModal" class="btn btn-primary btn-sm px-3 rounded-pill">
          <i class="bi bi-plus-lg me-1"></i>立即新增橫幅
        </button>
      </div>

      <!-- 橫幅清單 -->
      <div v-else class="card border-0 shadow-sm overflow-hidden mb-4">
        <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center border-bottom">
          <div class="fw-bold text-dark">
            <i class="bi bi-list-stars me-1 text-primary"></i>首頁橫幅排程列表 (共 {{ banners.length }} 則)
          </div>
          <button @click="fetchBanners" class="btn btn-sm btn-outline-secondary" title="重新整理">
            <i class="bi bi-arrow-clockwise me-1"></i>重新整理
          </button>
        </div>

        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light text-nowrap">
              <tr>
                <th scope="col" style="width: 70px;" class="text-center">排序</th>
                <th scope="col" style="width: 140px;">背景圖預覽</th>
                <th scope="col" style="min-width: 260px;">標題與徽章標籤</th>
                <th scope="col" style="min-width: 220px;">按鈕導向連結</th>
                <th scope="col" style="width: 100px;" class="text-center">輪播間隔</th>
                <th scope="col" style="width: 110px;" class="text-center">啟用狀態</th>
                <th scope="col" style="width: 160px;" class="text-center">管理操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="banner in banners"
                :key="banner.id"
                :class="{ 'opacity-75 bg-light': !banner.is_active }"
              >
                <!-- 排序 -->
                <td class="text-center">
                  <span class="badge bg-secondary-subtle text-secondary font-monospace px-2 py-1">
                    #{{ banner.sort_order }}
                  </span>
                </td>

                <!-- 背景圖縮圖 -->
                <td>
                  <div class="position-relative banner-thumb-wrap rounded overflow-hidden shadow-sm border">
                    <img
                      :src="banner.image_url"
                      :alt="banner.title"
                      class="banner-thumb object-fit-cover w-100"
                      @error="handleImgError"
                    />
                    <div class="thumb-overlay d-flex align-items-center justify-content-center">
                      <button
                        type="button"
                        class="btn btn-sm btn-light py-0 px-2 rounded-pill shadow-sm"
                        @click="openPreviewModal(banner)"
                        title="放大檢視"
                      >
                        <i class="bi bi-eye"></i>
                      </button>
                    </div>
                  </div>
                </td>

                <!-- 標題、副標題與徽章 -->
                <td>
                  <div class="mb-1" v-if="banner.badge_text">
                    <span class="badge shadow-sm" :class="getBadgeClass(banner.badge_color)">
                      {{ banner.badge_text }}
                    </span>
                  </div>
                  <div class="fw-bold text-dark fs-6">{{ banner.title }}</div>
                  <div v-if="banner.subtitle" class="small text-muted text-truncate mt-1" style="max-width: 380px;">
                    {{ banner.subtitle }}
                  </div>
                </td>

                <!-- 行動按鈕連結 -->
                <td>
                  <!-- 主按鈕 -->
                  <div v-if="banner.primary_button_text" class="d-flex align-items-center gap-1 mb-1">
                    <span class="badge bg-primary-subtle text-primary border border-primary-subtle font-monospace text-truncate" style="max-width: 110px;">
                      {{ banner.primary_button_text }}
                    </span>
                    <i class="bi bi-arrow-right text-muted small"></i>
                    <span class="small text-muted font-monospace text-truncate" style="max-width: 140px;" :title="banner.primary_button_link">
                      {{ banner.primary_button_link || '無連結' }}
                    </span>
                  </div>
                  <!-- 次按鈕 -->
                  <div v-if="banner.secondary_button_text" class="d-flex align-items-center gap-1">
                    <span class="badge bg-light text-dark border font-monospace text-truncate" style="max-width: 110px;">
                      {{ banner.secondary_button_text }}
                    </span>
                    <i class="bi bi-arrow-right text-muted small"></i>
                    <span class="small text-muted font-monospace text-truncate" style="max-width: 140px;" :title="banner.secondary_button_link">
                      {{ banner.secondary_button_link || '無連結' }}
                    </span>
                  </div>
                  <span v-if="!banner.primary_button_text && !banner.secondary_button_text" class="text-muted small">
                    無設定按鈕
                  </span>
                </td>

                <!-- 輪播間隔 -->
                <td class="text-center font-monospace small">
                  {{ ((banner.interval_ms || 5000) / 1000).toFixed(1) }} 秒
                </td>

                <!-- 啟用開關 -->
                <td class="text-center">
                  <div class="form-check form-switch d-inline-block">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      role="switch"
                      :id="'switch-' + banner.id"
                      :checked="banner.is_active"
                      :disabled="togglingId === banner.id"
                      @change="toggleActive(banner)"
                    >
                  </div>
                  <div>
                    <span class="badge" :class="banner.is_active ? 'bg-success' : 'bg-secondary'">
                      {{ banner.is_active ? '公開播放' : '已停用' }}
                    </span>
                  </div>
                </td>

                <!-- 管理操作 -->
                <td class="text-center text-nowrap">
                  <button
                    type="button"
                    class="btn btn-outline-info btn-sm me-1"
                    @click="openPreviewModal(banner)"
                    title="即時模擬預覽"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-primary btn-sm me-1"
                    @click="openEditModal(banner)"
                    title="編輯橫幅內容"
                  >
                    <i class="bi bi-pencil-square"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-danger btn-sm"
                    @click="deleteBanner(banner)"
                    title="刪除此橫幅"
                  >
                    <i class="bi bi-trash3"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ==================== Tab 2: 各分頁頂部橫幅 ==================== -->
    <div v-else-if="activeTab === 'pages'">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="text-muted small">
          設定官網各個子頁面（關於我們、師資、課表、價目表等）頂部的橫幅大圖與標題
        </div>
        <button @click="fetchPageBanners" class="btn btn-sm btn-outline-secondary">
          <i class="bi bi-arrow-clockwise me-1"></i>重新整理
        </button>
      </div>

      <div class="row g-4">
        <div
          v-for="pb in pageBanners"
          :key="pb.page_key"
          class="col-md-6 col-lg-4"
        >
          <div class="card border-0 shadow-sm h-100 rounded-3 overflow-hidden page-banner-card">
            <!-- 橫幅預覽圖與標題 -->
            <div class="position-relative page-banner-thumb-box" style="height: 160px; background-color: #111;">
              <img
                :src="pb.image_url"
                :alt="pb.title"
                class="w-100 h-100 object-fit-cover"
                @error="handleImgError"
              />
              <div class="page-banner-thumb-overlay d-flex flex-column justify-content-center align-items-center text-center p-3">
                <span class="badge bg-warning text-dark mb-1 fw-bold">{{ pb.page_name }}</span>
                <h5 class="text-white fw-bold mb-1 text-shadow">{{ pb.title }}</h5>
                <p v-if="pb.subtitle" class="text-white-50 small mb-0 text-shadow text-truncate" style="max-width: 280px;">
                  {{ pb.subtitle }}
                </p>
              </div>
            </div>

            <div class="card-body p-3 d-flex flex-column justify-content-between">
              <div>
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <span class="fw-bold text-dark fs-6">{{ pb.page_name }}</span>
                  <span class="badge bg-light text-muted font-monospace border">/{{ pb.page_key }}</span>
                </div>
                <div class="small text-muted mb-2 text-truncate" :title="pb.title">
                  <strong>主標題：</strong>{{ pb.title }}
                </div>
                <div class="small text-muted mb-3 text-truncate" :title="pb.subtitle">
                  <strong>副標題：</strong>{{ pb.subtitle || '（無設定）' }}
                </div>
              </div>

              <div class="d-flex gap-2 pt-2 border-top">
                <a
                  :href="'/' + (pb.page_key === 'schedule' ? 'schedule' : pb.page_key)"
                  target="_blank"
                  class="btn btn-outline-secondary btn-sm flex-grow-1 d-flex align-items-center justify-content-center gap-1"
                >
                  <i class="bi bi-box-arrow-up-right"></i>前台檢視
                </a>
                <button
                  type="button"
                  class="btn btn-primary btn-sm flex-grow-1 d-flex align-items-center justify-content-center gap-1 shadow-sm"
                  @click="openEditPageBannerModal(pb)"
                >
                  <i class="bi bi-pencil-square"></i>編輯橫幅
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== Tab 3: 主導航列 LOGO 設定 ==================== -->
    <div v-else-if="activeTab === 'logo'">
      <div class="row justify-content-center">
        <div class="col-lg-9 col-xl-8">
          <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4">
            <div class="card-header bg-dark text-white p-3 p-md-4">
              <h5 class="fw-bold mb-1 d-flex align-items-center">
                <i class="bi bi-badge-ad text-primary me-2"></i>主導航列 (Navbar) LOGO 設定
              </h5>
              <p class="text-white-50 small mb-0">
                自訂前台官網最上方導航列左側的品牌標誌，可自由切換以「文字名稱」或「圖片標誌 (LOGO)」方式呈現。
              </p>
            </div>
            
            <div class="card-body p-4">
              <!-- 1. 呈現方式切換 -->
              <div class="mb-4">
                <label class="form-label fw-bold text-dark d-block mb-3">
                  <i class="bi bi-toggles text-primary me-1"></i>LOGO 呈現方式
                </label>
                <div class="row g-3">
                  <div class="col-sm-6">
                    <div
                      class="card h-100 p-3 border-2 transition-all"
                      :class="logoForm.logo_type === 'text' ? 'border-primary bg-primary-subtle' : 'border-light-subtle bg-light'"
                      @click="logoForm.logo_type = 'text'"
                      style="cursor: pointer;"
                    >
                      <div class="form-check d-flex align-items-center gap-2">
                        <input
                          class="form-check-input mt-0 fs-5"
                          type="radio"
                          id="logoTypeText"
                          value="text"
                          v-model="logoForm.logo_type"
                        />
                        <label class="form-check-label fw-bold text-dark" for="logoTypeText" style="cursor: pointer;">
                          <i class="bi bi-fonts me-1 text-primary"></i>文字名稱 (Text)
                        </label>
                      </div>
                      <p class="text-muted small mt-2 mb-0 ps-4">
                        以文字形式展示工作室/品牌名稱，字體清晰簡約。
                      </p>
                    </div>
                  </div>

                  <div class="col-sm-6">
                    <div
                      class="card h-100 p-3 border-2 transition-all"
                      :class="logoForm.logo_type === 'image' ? 'border-primary bg-primary-subtle' : 'border-light-subtle bg-light'"
                      @click="logoForm.logo_type = 'image'"
                      style="cursor: pointer;"
                    >
                      <div class="form-check d-flex align-items-center gap-2">
                        <input
                          class="form-check-input mt-0 fs-5"
                          type="radio"
                          id="logoTypeImage"
                          value="image"
                          v-model="logoForm.logo_type"
                        />
                        <label class="form-check-label fw-bold text-dark" for="logoTypeImage" style="cursor: pointer;">
                          <i class="bi bi-image me-1 text-primary"></i>圖片 LOGO (Image)
                        </label>
                      </div>
                      <p class="text-muted small mt-2 mb-0 ps-4">
                        上傳或指定工作室專屬圖形標誌、商標圖檔。
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 2. 文字名稱設定 (當選文字時顯示) -->
              <div v-if="logoForm.logo_type === 'text'" class="mb-4">
                <label for="logoText" class="form-label fw-bold text-dark">
                  <i class="bi bi-pencil-square text-primary me-1"></i>品牌文字名稱
                </label>
                <div class="input-group input-group-lg">
                  <span class="input-group-text bg-white"><i class="bi bi-type"></i></span>
                  <input
                    type="text"
                    id="logoText"
                    v-model="logoForm.logo_text"
                    class="form-control"
                    placeholder="例如: Dance Studio 或 椰子樹舞蹈工作室"
                    maxlength="50"
                  />
                </div>
                <div class="form-text mt-1">顯示於前台頂部導航列左側的品牌名稱。</div>
              </div>

              <!-- 3. 圖片 LOGO 設定 (當選圖片時顯示) -->
              <div v-if="logoForm.logo_type === 'image'" class="mb-4">
                <label class="form-label fw-bold text-dark">
                  <i class="bi bi-card-image text-primary me-1"></i>LOGO 圖片上傳 / 網址
                </label>
                
                <div class="card p-3 border bg-light mb-3">
                  <div class="d-flex flex-wrap gap-2 mb-3">
                    <button
                      type="button"
                      class="btn btn-outline-primary btn-sm d-flex align-items-center gap-1 shadow-sm"
                      @click="triggerLogoUpload"
                      :disabled="isUploadingLogo"
                    >
                      <span v-if="isUploadingLogo" class="spinner-border spinner-border-sm"></span>
                      <i v-else class="bi bi-upload"></i>
                      <span>{{ isUploadingLogo ? '上傳中...' : '從本機電腦上傳圖片' }}</span>
                    </button>
                    <input
                      type="file"
                      ref="logoFileInput"
                      class="d-none"
                      accept="image/png,image/jpeg,image/webp,image/svg+xml"
                      @change="handleLogoFileSelect"
                    />
                  </div>

                  <div class="input-group">
                    <span class="input-group-text bg-white">圖片網址</span>
                    <input
                      type="text"
                      v-model="logoForm.logo_image"
                      class="form-control"
                      placeholder="https://... 或點擊上方按鈕上傳"
                    />
                    <button
                      v-if="logoForm.logo_image"
                      class="btn btn-outline-danger"
                      type="button"
                      @click="logoForm.logo_image = ''"
                    >
                      清除
                    </button>
                  </div>
                  <div class="form-text mt-2 small">
                    建議使用透明背景的 <strong>PNG</strong>、<strong>SVG</strong> 或 <strong>WebP</strong> 格式，高度建議為 40px~100px。
                  </div>
                </div>
              </div>

              <!-- 4. 即時效果模擬預覽 (導航列深色模擬區) -->
              <div class="mb-4">
                <label class="form-label fw-bold text-dark mb-2">
                  <i class="bi bi-eye text-primary me-1"></i>前台導航列即時預覽效果
                </label>
                <div class="bg-dark p-3 rounded-3 d-flex align-items-center justify-content-between border shadow-sm">
                  <div class="d-flex align-items-center">
                    <template v-if="logoForm.logo_type === 'image' && logoForm.logo_image">
                      <img
                        :src="logoForm.logo_image"
                        alt="Logo Preview"
                        style="max-height: 40px; width: auto; object-fit: contain;"
                        @error="handleLogoPreviewError"
                      />
                    </template>
                    <template v-else>
                      <span class="text-white fw-bold fs-5 font-monospace">
                        {{ logoForm.logo_text || 'Dance Studio' }}
                      </span>
                    </template>
                  </div>
                  <div class="d-none d-md-flex gap-3 text-white-50 small">
                    <span>首頁</span>
                    <span>關於我們</span>
                    <span>師資介紹</span>
                    <span>課程</span>
                  </div>
                </div>
                <div class="form-text small mt-1">※ 此處模擬在前台導航列深色背景下的實際顯示模樣。</div>
              </div>

              <!-- 5. 網站進場開場動畫圖 (Splash Screen) 設定 -->
              <div class="mb-4 pt-3 border-top">
                <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
                  <label class="form-label fw-bold text-dark mb-0">
                    <i class="bi bi-display text-primary me-1"></i>網頁開場動畫圖 (Splash Screen)
                  </label>
                  <button
                    v-if="logoForm.logo_type === 'image' && logoForm.logo_image"
                    type="button"
                    class="btn btn-outline-secondary btn-sm rounded-pill py-0 px-2 small"
                    @click="logoForm.splash_image = logoForm.logo_image"
                  >
                    <i class="bi bi-arrow-down-up me-1"></i>一鍵帶入上方導航列 LOGO 圖片
                  </button>
                </div>
                <p class="text-muted small mb-3">
                  當訪客剛開啟或重新整理網站時，在黑色背景中呈現的開場圖示（呼吸微縮放過場效果），播放完後會優雅淡出進入首頁。
                </p>

                <div class="card p-3 border bg-light mb-3">
                  <div class="d-flex flex-wrap gap-2 mb-3">
                    <button
                      type="button"
                      class="btn btn-outline-primary btn-sm d-flex align-items-center gap-1 shadow-sm"
                      @click="triggerSplashUpload"
                      :disabled="isUploadingSplash"
                    >
                      <span v-if="isUploadingSplash" class="spinner-border spinner-border-sm"></span>
                      <i v-else class="bi bi-upload"></i>
                      <span>{{ isUploadingSplash ? '上傳中...' : '從本機電腦上傳開場圖' }}</span>
                    </button>
                    <input
                      type="file"
                      ref="splashFileInput"
                      class="d-none"
                      accept="image/png,image/jpeg,image/webp,image/svg+xml,image/gif"
                      @change="handleSplashFileSelect"
                    />
                  </div>

                  <div class="input-group">
                    <span class="input-group-text bg-white">圖片網址</span>
                    <input
                      type="text"
                      v-model="logoForm.splash_image"
                      class="form-control"
                      placeholder="https://... 或點擊上方按鈕上傳開場圖 (支援 GIF/PNG/WebP/JPG)"
                    />
                    <button
                      v-if="logoForm.splash_image"
                      class="btn btn-outline-danger"
                      type="button"
                      @click="logoForm.splash_image = ''"
                    >
                      清除
                    </button>
                  </div>
                  <div class="form-text mt-2 small">
                    建議使用高對比度、深色背景可視之 <strong>PNG (透明背景)</strong>、<strong>GIF (動態圖)</strong> 或 <strong>WebP</strong> 格式。
                  </div>
                </div>

                <!-- 開場動畫黑底模擬預覽 -->
                <div>
                  <label class="form-label small fw-bold text-muted mb-2">
                    <i class="bi bi-play-circle text-primary me-1"></i>開場動畫全螢幕黑底預覽 (縮小比例模擬)
                  </label>
                  <div
                    class="rounded-3 d-flex flex-column align-items-center justify-content-center p-4 border shadow-sm position-relative overflow-hidden"
                    style="background-color: #0d0e12; min-height: 160px;"
                  >
                    <img
                      :src="logoForm.splash_image || (logoForm.logo_type === 'image' && logoForm.logo_image ? logoForm.logo_image : '/favicon.png')"
                      alt="Splash Preview"
                      style="max-width: 130px; max-height: 130px; object-fit: contain; animation: pulse 1.5s infinite alternate;"
                    />
                    <span class="badge bg-dark border border-secondary text-white-50 mt-3 small">
                      {{ logoForm.splash_image ? '使用自訂開場圖' : (logoForm.logo_image ? '使用導航列圖片' : '使用工作室圖示') }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 6. 儲存按鈕 -->
              <div class="d-flex justify-content-end gap-2 pt-3 border-top">
                <button
                  type="button"
                  class="btn btn-primary px-4 py-2 fw-bold d-flex align-items-center gap-2 shadow-sm"
                  @click="saveLogoSettings"
                  :disabled="isSavingLogo"
                >
                  <span v-if="isSavingLogo" class="spinner-border spinner-border-sm"></span>
                  <i v-else class="bi bi-check2-circle fs-5"></i>
                  <span>{{ isSavingLogo ? '儲存中...' : '儲存 LOGO 設定' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== 新增 / 編輯 首頁橫幅 Modal ==================== -->
    <div
      class="modal fade"
      id="bannerModal"
      tabindex="-1"
      aria-labelledby="bannerModalLabel"
      aria-hidden="true"
      ref="bannerModal"
    >
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-dark text-white">
            <h5 class="modal-title fw-bold" id="bannerModalLabel">
              <i class="bi bi-card-image text-warning me-2"></i>
              {{ editingBanner.id ? '編輯首頁橫幅' : '新增首頁橫幅' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>

          <div class="modal-body p-4 custom-modal-body">
            <form id="bannerForm" @submit.prevent="submitForm">
              <!-- 即時視覺預覽區 (動態呈現) -->
              <div class="mb-4">
                <label class="form-label fw-bold small text-muted text-uppercase mb-2">
                  <i class="bi bi-display me-1"></i>即時前台效果預覽
                </label>
                <div class="banner-live-preview rounded-3 overflow-hidden position-relative shadow-sm">
                  <img
                    :src="form.image_url || defaultFallbackImg"
                    alt="預覽大圖"
                    class="live-bg-img w-100"
                    @error="handlePreviewImgError"
                  />
                  <div class="live-overlay"></div>
                  <div class="live-caption p-4 text-start">
                    <span
                      v-if="form.badge_text"
                      class="badge px-3 py-1 rounded-pill fw-bold mb-2 shadow-sm d-inline-block"
                      :class="getBadgeClass(form.badge_color)"
                    >
                      {{ form.badge_text }}
                    </span>
                    <h3 class="fw-bold text-white mb-2 text-shadow">
                      {{ form.title || '（請輸入橫幅主標題）' }}
                    </h3>
                    <p class="text-white-50 small mb-3 text-shadow" style="max-width: 520px;">
                      {{ form.subtitle || '（橫幅副標題或補充說明文字）' }}
                    </p>
                    <div class="d-flex flex-wrap gap-2">
                      <button
                        v-if="form.primary_button_text"
                        type="button"
                        class="btn btn-sm rounded-pill px-3 shadow"
                        :class="getBtnClass(form.primary_button_style)"
                      >
                        {{ form.primary_button_text }}
                      </button>
                      <button
                        v-if="form.secondary_button_text"
                        type="button"
                        class="btn btn-sm rounded-pill px-3"
                        :class="getBtnClass(form.secondary_button_style)"
                      >
                        {{ form.secondary_button_text }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 1. 背景圖片設定 -->
              <div class="card border bg-light mb-3">
                <div class="card-body p-3">
                  <h6 class="fw-bold mb-3 d-flex align-items-center">
                    <i class="bi bi-image text-primary me-2"></i>橫幅大圖背景 <span class="text-danger ms-1">*</span>
                  </h6>

                  <!-- 檔案上傳隱藏 input -->
                  <input
                    type="file"
                    ref="bannerFileInput"
                    class="d-none"
                    accept="image/png, image/jpeg, image/jpg, image/webp, image/gif"
                    @change="handleFileUpload"
                  >

                  <div class="row g-2 mb-2">
                    <div class="col-md-8">
                      <div class="input-group">
                        <span class="input-group-text bg-white"><i class="bi bi-link-45deg"></i></span>
                        <input
                          type="text"
                          v-model="form.image_url"
                          class="form-control"
                          placeholder="輸入圖片網址 (https://... 或 /api/uploads/...)"
                          required
                        >
                      </div>
                    </div>
                    <div class="col-md-4 d-flex gap-2">
                      <button
                        type="button"
                        class="btn btn-primary w-100 d-flex align-items-center justify-content-center gap-1 shadow-sm"
                        @click="$refs.bannerFileInput.click()"
                        :disabled="uploadingImage"
                      >
                        <span v-if="uploadingImage" class="spinner-border spinner-border-sm"></span>
                        <i v-else class="bi bi-cloud-arrow-up"></i>
                        <span>{{ uploadingImage ? '上傳中...' : '本地上傳圖片' }}</span>
                      </button>
                    </div>
                  </div>

                  <!-- 推薦預設圖庫快捷選取 -->
                  <div class="mt-2">
                    <div class="small text-muted mb-1">
                      <i class="bi bi-stars text-warning me-1"></i>快捷套用高畫質精選舞蹈背景圖：
                    </div>
                    <div class="d-flex flex-wrap gap-2">
                      <button
                        type="button"
                        v-for="(preset, pIdx) in presetImages"
                        :key="pIdx"
                        class="btn btn-xs btn-outline-secondary py-1 px-2 rounded-pill small"
                        @click="form.image_url = preset.url"
                      >
                        {{ preset.label }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 2. 標題與標籤徽章 -->
              <div class="card border bg-light mb-3">
                <div class="card-body p-3">
                  <h6 class="fw-bold mb-3 d-flex align-items-center">
                    <i class="bi bi-type-h1 text-primary me-2"></i>標題與醒目徽章
                  </h6>

                  <!-- 徽章文字與顏色 -->
                  <div class="row g-2 mb-3">
                    <div class="col-md-7">
                      <label class="form-label small fw-semibold">亮點徽章文字 (選填)</label>
                      <input
                        type="text"
                        v-model="form.badge_text"
                        class="form-control"
                        placeholder="例如：✨ 啟動你的舞蹈新生活、🔥 2024 春季新課"
                      >
                    </div>
                    <div class="col-md-5">
                      <label class="form-label small fw-semibold">徽章背景配色</label>
                      <select v-model="form.badge_color" class="form-select">
                        <option value="warning">黃色 (Warning) 活力醒目</option>
                        <option value="primary">藍色 (Primary) 專業俐落</option>
                        <option value="success">綠色 (Success) 清新自然</option>
                        <option value="danger">紅色 (Danger) 熱情引人</option>
                        <option value="info">青色 (Info) 明亮活潑</option>
                        <option value="dark">黑色 (Dark) 沉穩質感</option>
                        <option value="secondary">灰色 (Secondary) 簡約低調</option>
                      </select>
                    </div>
                  </div>

                  <!-- 主標題 -->
                  <div class="mb-3">
                    <label class="form-label small fw-semibold">
                      橫幅主標題 <span class="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      v-model="form.title"
                      class="form-control form-control-lg fw-bold"
                      placeholder="例如：釋放你的節奏，舞出你的熱情"
                      required
                    >
                  </div>

                  <!-- 副標題 -->
                  <div>
                    <label class="form-label small fw-semibold">副標題 / 宣傳介紹文字 (選填)</label>
                    <textarea
                      v-model="form.subtitle"
                      class="form-control"
                      rows="2"
                      placeholder="簡要描述活動、特色或吸引人的宣傳語句..."
                    ></textarea>
                  </div>
                </div>
              </div>

              <!-- 3. 行動按鈕 (CTA Buttons) 設定 -->
              <div class="card border bg-light mb-3">
                <div class="card-body p-3">
                  <h6 class="fw-bold mb-3 d-flex align-items-center">
                    <i class="bi bi-cursor-fill text-primary me-2"></i>行動呼籲按鈕 (點擊跳轉)
                  </h6>

                  <!-- 主要按鈕 (Primary Button) -->
                  <div class="p-3 bg-white rounded border mb-3">
                    <div class="fw-bold small text-primary mb-2">
                      <i class="bi bi-1-circle-fill me-1"></i>主要按鈕 (Primary CTA)
                    </div>
                    <div class="row g-2 align-items-center">
                      <div class="col-md-4">
                        <label class="form-label small text-muted mb-1">按鈕文字</label>
                        <input
                          type="text"
                          v-model="form.primary_button_text"
                          class="form-control form-control-sm"
                          placeholder="例如：立即預約課程"
                        >
                      </div>
                      <div class="col-md-4">
                        <label class="form-label small text-muted mb-1">連結網址或路徑</label>
                        <input
                          type="text"
                          v-model="form.primary_button_link"
                          class="form-control form-control-sm"
                          placeholder="例如：/schedule 或外部網址"
                        >
                      </div>
                      <div class="col-md-4">
                        <label class="form-label small text-muted mb-1">按鈕色彩樣式</label>
                        <select v-model="form.primary_button_style" class="form-select form-select-sm">
                          <option value="primary">藍色實心 (btn-primary)</option>
                          <option value="warning">黃色醒目 (btn-warning)</option>
                          <option value="success">綠色活力 (btn-success)</option>
                          <option value="light">白色簡約 (btn-light)</option>
                          <option value="danger">紅色熱烈 (btn-danger)</option>
                          <option value="outline-light">白色邊框 (btn-outline-light)</option>
                        </select>
                      </div>
                    </div>
                    <!-- 快速填寫建議連結 -->
                    <div class="mt-2 d-flex flex-wrap gap-1 align-items-center">
                      <span class="text-muted small me-1">常用路徑：</span>
                      <button
                        type="button"
                        v-for="preset in routePresets"
                        :key="preset.path"
                        class="btn btn-xs btn-outline-secondary py-0 px-2 rounded-pill font-monospace"
                        @click="form.primary_button_link = preset.path"
                      >
                        {{ preset.label }}
                      </button>
                    </div>
                  </div>

                  <!-- 次要按鈕 (Secondary Button) -->
                  <div class="p-3 bg-white rounded border">
                    <div class="fw-bold small text-secondary mb-2">
                      <i class="bi bi-2-circle-fill me-1"></i>次要按鈕 (Secondary CTA，可留空)
                    </div>
                    <div class="row g-2 align-items-center">
                      <div class="col-md-4">
                        <label class="form-label small text-muted mb-1">按鈕文字</label>
                        <input
                          type="text"
                          v-model="form.secondary_button_text"
                          class="form-control form-control-sm"
                          placeholder="例如：認識師資團隊"
                        >
                      </div>
                      <div class="col-md-4">
                        <label class="form-label small text-muted mb-1">連結網址或路徑</label>
                        <input
                          type="text"
                          v-model="form.secondary_button_link"
                          class="form-control form-control-sm"
                          placeholder="例如：/instructors"
                        >
                      </div>
                      <div class="col-md-4">
                        <label class="form-label small text-muted mb-1">按鈕色彩樣式</label>
                        <select v-model="form.secondary_button_style" class="form-select form-select-sm">
                          <option value="outline-light">白色邊框 (btn-outline-light)</option>
                          <option value="light">白色實心 (btn-light)</option>
                          <option value="primary">藍色實心 (btn-primary)</option>
                          <option value="warning">黃色醒目 (btn-warning)</option>
                        </select>
                      </div>
                    </div>
                    <!-- 快速填寫建議連結 -->
                    <div class="mt-2 d-flex flex-wrap gap-1 align-items-center">
                      <span class="text-muted small me-1">常用路徑：</span>
                      <button
                        type="button"
                        v-for="preset in routePresets"
                        :key="preset.path"
                        class="btn btn-xs btn-outline-secondary py-0 px-2 rounded-pill font-monospace"
                        @click="form.secondary_button_link = preset.path"
                      >
                        {{ preset.label }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 4. 輪播播放秒數、排序與啟用開關 -->
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label small fw-semibold">
                    <i class="bi bi-stopwatch me-1 text-primary"></i>播放停留秒數
                  </label>
                  <select v-model.number="form.interval_ms" class="form-select">
                    <option :value="3000">3 秒 (快速換頁)</option>
                    <option :value="4000">4 秒</option>
                    <option :value="5000">5 秒 (預設標準)</option>
                    <option :value="7000">7 秒 (較長閱讀)</option>
                    <option :value="10000">10 秒 (慢速展示)</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label small fw-semibold">
                    <i class="bi bi-sort-numeric-down me-1 text-primary"></i>播放排序順序
                  </label>
                  <input
                    type="number"
                    v-model.number="form.sort_order"
                    class="form-control"
                    placeholder="數字越小越先播放 (例如 1, 2, 3)"
                    min="0"
                  >
                </div>
                <div class="col-md-4 d-flex align-items-center pt-md-4">
                  <div class="form-check form-switch fs-6">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      role="switch"
                      id="modalIsActiveSwitch"
                      v-model="form.is_active"
                    >
                    <label class="form-check-label fw-bold" for="modalIsActiveSwitch">
                      {{ form.is_active ? '立即公開於首頁播放' : '暫存為草稿下架' }}
                    </label>
                  </div>
                </div>
              </div>
            </form>
          </div>

          <!-- Modal 底部操作按鈕 (固定置底) -->
          <div class="modal-footer bg-light px-4 py-3">
            <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">取消</button>
            <button
              type="submit"
              form="bannerForm"
              class="btn btn-primary rounded-pill px-4 shadow-sm"
              :disabled="submitting || uploadingImage"
            >
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-check2-circle me-1"></i>
              {{ editingBanner.id ? '儲存變更' : '建立橫幅' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== 編輯 各分頁頂部橫幅 Modal ==================== -->
    <div
      class="modal fade"
      id="pageBannerModal"
      tabindex="-1"
      aria-hidden="true"
      ref="pageBannerModal"
    >
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content border-0 shadow">
          <div class="modal-header bg-dark text-white">
            <h5 class="modal-title fw-bold">
              <i class="bi bi-window-sidebar text-warning me-2"></i>
              編輯分頁橫幅（{{ editingPageBanner.page_name }}）
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>

          <div class="modal-body p-4 custom-modal-body">
            <form id="editPageBannerForm" @submit.prevent="submitPageBannerForm">
              <!-- 隱藏圖片上傳 -->
              <input
                type="file"
                ref="pageBannerFileInput"
                class="d-none"
                accept="image/*"
                @change="handlePageBannerUpload"
              >

              <!-- 預覽區 -->
              <div class="mb-4">
                <label class="form-label small fw-bold text-muted text-uppercase mb-2">
                  <i class="bi bi-display me-1"></i>即時效果預覽
                </label>
                <div class="preview-box rounded-3 overflow-hidden position-relative shadow-sm" style="height: 180px; background-color: #000;">
                  <img :src="pageBannerForm.image_url || defaultFallbackImg" class="w-100 h-100 object-fit-cover" alt="預覽" @error="handleImgError">
                  <div class="preview-overlay d-flex flex-column justify-content-center align-items-center text-center p-3">
                    <span class="badge bg-warning text-dark mb-1 fw-bold">{{ editingPageBanner.page_name }}</span>
                    <h3 class="text-white fw-bold mb-1 text-shadow">{{ pageBannerForm.title || '（標題）' }}</h3>
                    <p v-if="pageBannerForm.subtitle" class="text-white-50 small mb-0 text-shadow" style="max-width: 480px;">
                      {{ pageBannerForm.subtitle }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- 背景圖片設定 -->
              <div class="card border bg-light mb-3">
                <div class="card-body p-3">
                  <label class="form-label small fw-bold mb-2">
                    <i class="bi bi-image text-primary me-1"></i>橫幅大圖背景 <span class="text-danger">*</span>
                  </label>

                  <div class="input-group mb-2">
                    <span class="input-group-text bg-white"><i class="bi bi-link-45deg"></i></span>
                    <input
                      type="text"
                      v-model="pageBannerForm.image_url"
                      class="form-control"
                      placeholder="圖片網址 (https://... 或本地上傳)"
                      required
                    >
                    <button
                      type="button"
                      class="btn btn-primary d-flex align-items-center gap-1 shadow-sm"
                      @click="$refs.pageBannerFileInput.click()"
                      :disabled="pageBannerUploading"
                    >
                      <span v-if="pageBannerUploading" class="spinner-border spinner-border-sm"></span>
                      <i v-else class="bi bi-cloud-arrow-up"></i>
                      <span>{{ pageBannerUploading ? '上傳中...' : '本地上傳圖片' }}</span>
                    </button>
                  </div>

                  <!-- 推薦預設圖庫快捷選取 -->
                  <div class="mt-2">
                    <span class="small text-muted me-2"><i class="bi bi-stars text-warning me-1"></i>精選高清舞蹈圖：</span>
                    <div class="d-inline-flex flex-wrap gap-1 mt-1">
                      <button
                        type="button"
                        v-for="(preset, pIdx) in presetImages"
                        :key="pIdx"
                        class="btn btn-xs btn-outline-secondary py-0 px-2 rounded-pill font-monospace"
                        @click="pageBannerForm.image_url = preset.url"
                      >
                        {{ preset.label }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 標題與副標題 -->
              <div class="card border bg-light mb-2">
                <div class="card-body p-3">
                  <div class="mb-3">
                    <label class="form-label small fw-bold">
                      橫幅主標題 <span class="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      v-model="pageBannerForm.title"
                      class="form-control form-control-lg fw-bold"
                      placeholder="例如：關於我們 / ABOUT US"
                      required
                    >
                  </div>
                  <div>
                    <label class="form-label small fw-bold">副標題 / 宣傳簡述 (選填)</label>
                    <input
                      type="text"
                      v-model="pageBannerForm.subtitle"
                      class="form-control"
                      placeholder="例如：城市中最具活力的舞蹈綠洲，啟動你的專屬舞台"
                    >
                  </div>
                </div>
              </div>
            </form>
          </div>

          <div class="modal-footer bg-light px-4 py-3 justify-content-between">
            <a
              :href="'/' + (editingPageBanner.page_key === 'schedule' ? 'schedule' : editingPageBanner.page_key)"
              target="_blank"
              class="btn btn-outline-dark btn-sm rounded-pill"
            >
              <i class="bi bi-box-arrow-up-right me-1"></i>開新分頁檢視此前台
            </a>
            <div class="d-flex gap-2">
              <button type="button" class="btn btn-secondary rounded-pill px-3" data-bs-dismiss="modal">取消</button>
              <button
                type="submit"
                form="editPageBannerForm"
                class="btn btn-primary rounded-pill px-4 shadow-sm"
                :disabled="pageBannerSaving || pageBannerUploading"
              >
                <span v-if="pageBannerSaving" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-check2 me-1"></i>儲存變更
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== 前台完整全螢幕模擬預覽 Modal ==================== -->
    <div
      class="modal fade"
      id="previewModal"
      tabindex="-1"
      aria-labelledby="previewModalLabel"
      aria-hidden="true"
      ref="previewModal"
    >
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content border-0 bg-dark text-white shadow-lg overflow-hidden">
          <div class="modal-header border-bottom border-secondary py-2 px-3">
            <h6 class="modal-title fw-bold mb-0">
              <i class="bi bi-laptop me-2 text-warning"></i>首頁輪播視覺效果模擬
            </h6>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-0 position-relative">
            <div class="preview-hero-container position-relative">
              <img
                :src="previewItem.image_url"
                :alt="previewItem.title"
                class="w-100 preview-hero-img object-fit-cover"
                @error="handleImgError"
              />
              <div class="preview-hero-overlay"></div>
              <div class="preview-hero-caption p-4 p-md-5">
                <span
                  v-if="previewItem.badge_text"
                  class="badge px-3 py-2 rounded-pill fw-bold mb-3 shadow-sm d-inline-block"
                  :class="getBadgeClass(previewItem.badge_color)"
                >
                  {{ previewItem.badge_text }}
                </span>
                <h1 class="display-5 fw-bold text-white mb-3 text-shadow">
                  {{ previewItem.title }}
                </h1>
                <p class="lead text-white-50 mb-4 text-shadow" style="max-width: 650px;">
                  {{ previewItem.subtitle }}
                </p>
                <div class="d-flex flex-wrap gap-3">
                  <a
                    v-if="previewItem.primary_button_text"
                    :href="previewItem.primary_button_link || 'javascript:void(0)'"
                    class="btn btn-lg rounded-pill px-4 shadow"
                    :class="getBtnClass(previewItem.primary_button_style)"
                  >
                    {{ previewItem.primary_button_text }}
                  </a>
                  <a
                    v-if="previewItem.secondary_button_text"
                    :href="previewItem.secondary_button_link || 'javascript:void(0)'"
                    class="btn btn-lg rounded-pill px-4"
                    :class="getBtnClass(previewItem.secondary_button_style)"
                  >
                    {{ previewItem.secondary_button_text }}
                  </a>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer border-top border-secondary py-2 px-3 justify-content-between">
            <div class="small text-white-50">
              提示：若有多張橫幅，前台將以輪播方式自動切換（每 {{ ((previewItem.interval_ms || 5000) / 1000).toFixed(1) }} 秒）。
            </div>
            <button type="button" class="btn btn-sm btn-outline-light rounded-pill px-3" data-bs-dismiss="modal">
              關閉預覽
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
  name: 'BannerManagement',
  data() {
    return {
      activeTab: 'logo', // 'logo' | 'home' | 'pages'
      logoForm: {
        logo_type: 'text',
        logo_text: 'Dance Studio',
        logo_image: '',
        splash_image: ''
      },
      isUploadingLogo: false,
      isUploadingSplash: false,
      isSavingLogo: false,
      banners: [],
      pageBanners: [],
      loading: true,
      submitting: false,
      uploadingImage: false,
      togglingId: null,
      error: null,
      bannerModalInstance: null,
      previewModalInstance: null,
      pageBannerModalInstance: null,
      editingBanner: {},
      previewItem: {},
      editingPageBanner: {},
      pageBannerSaving: false,
      pageBannerUploading: false,
      pageBannerForm: {
        title: '',
        subtitle: '',
        image_url: ''
      },
      defaultFallbackImg: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=1920&q=80',
      presetImages: [
        { label: '舞動熱情 (舞台光)', url: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=1920&q=80' },
        { label: '街舞律動 (街頭風)', url: 'https://images.unsplash.com/photo-1547153760-18fc86324498?auto=format&fit=crop&w=1920&q=80' },
        { label: '木質教室 (專業鏡面)', url: 'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=1920&q=80' },
        { label: '爵士抒情 (聚光燈)', url: 'https://images.unsplash.com/photo-1535525153412-5a42439a210d?auto=format&fit=crop&w=1920&q=80' },
        { label: '極簡鏡面 (黑白調)', url: 'https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?auto=format&fit=crop&w=1920&q=80' }
      ],
      routePresets: [
        { label: '預約課表', path: '/schedule' },
        { label: '認識師資', path: '/instructors' },
        { label: '價目收費', path: '/pricing' },
        { label: '場地租借', path: '/venue' },
        { label: '關於我們', path: '/about' },
        { label: '活動花絮', path: '/gallery' },
        { label: '常見問題', path: '/faq' },
        { label: '聯絡諮詢', path: '/contact' }
      ],
      form: {
        title: '',
        subtitle: '',
        badge_text: '',
        badge_color: 'warning',
        image_url: '',
        primary_button_text: '立即預約課程',
        primary_button_link: '/schedule',
        primary_button_style: 'primary',
        secondary_button_text: '認識師資團隊',
        secondary_button_link: '/instructors',
        secondary_button_style: 'outline-light',
        interval_ms: 5000,
        sort_order: 1,
        is_active: true
      }
    };
  },
  computed: {
    activeBannersCount() {
      return this.banners.filter(b => b.is_active).length;
    },
    inactiveBannersCount() {
      return this.banners.filter(b => !b.is_active).length;
    }
  },
  mounted() {
    this.bannerModalInstance = new Modal(this.$refs.bannerModal);
    this.previewModalInstance = new Modal(this.$refs.previewModal);
    if (this.$refs.pageBannerModal) {
      this.pageBannerModalInstance = new Modal(this.$refs.pageBannerModal);
    }
    this.fetchBanners();
    this.fetchPageBanners();
    this.fetchLogoSettings();
  },
  beforeUnmount() {
    if (this.bannerModalInstance) this.bannerModalInstance.dispose();
    if (this.previewModalInstance) this.previewModalInstance.dispose();
    if (this.pageBannerModalInstance) this.pageBannerModalInstance.dispose();
  },
  methods: {
    async fetchLogoSettings() {
      try {
        const res = await api.get('/site-settings/logo');
        if (res && (res.success || res.logo_type)) {
          this.logoForm = {
            logo_type: res.logo_type || 'text',
            logo_text: res.logo_text || 'Dance Studio',
            logo_image: res.logo_image || '',
            splash_image: res.splash_image || ''
          };
        }
      } catch (err) {
        console.error('取得 LOGO 設定失敗:', err);
      }
    },

    triggerLogoUpload() {
      if (this.$refs.logoFileInput) {
        this.$refs.logoFileInput.click();
      }
    },

    async handleLogoFileSelect(e) {
      const file = e.target.files?.[0];
      if (!file) return;

      if (file.size > 5 * 1024 * 1024) {
        showToast('圖片檔案大小不得超過 5MB', 'warning');
        return;
      }

      this.isUploadingLogo = true;
      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await api.post('/upload/logo-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        if (res && res.image_url) {
          this.logoForm.logo_image = res.image_url;
          this.logoForm.logo_type = 'image';
          showToast('LOGO 圖片上傳成功！', 'success');
        }
      } catch (err) {
        showToast(err.message || 'LOGO 圖片上傳失敗', 'danger');
      } finally {
        this.isUploadingLogo = false;
        e.target.value = '';
      }
    },

    triggerSplashUpload() {
      if (this.$refs.splashFileInput) {
        this.$refs.splashFileInput.click();
      }
    },

    async handleSplashFileSelect(e) {
      const file = e.target.files?.[0];
      if (!file) return;

      if (file.size > 5 * 1024 * 1024) {
        showToast('圖片檔案大小不得超過 5MB', 'warning');
        return;
      }

      this.isUploadingSplash = true;
      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await api.post('/upload/splash-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        if (res && res.image_url) {
          this.logoForm.splash_image = res.image_url;
          showToast('開場圖片上傳成功！', 'success');
        }
      } catch (err) {
        showToast(err.message || '開場圖片上傳失敗', 'danger');
      } finally {
        this.isUploadingSplash = false;
        e.target.value = '';
      }
    },

    async saveLogoSettings() {
      if (this.logoForm.logo_type === 'text' && !this.logoForm.logo_text.trim()) {
        showToast('請輸入品牌文字名稱', 'warning');
        return;
      }
      if (this.logoForm.logo_type === 'image' && !this.logoForm.logo_image.trim()) {
        showToast('請上傳或輸入 LOGO 圖片網址', 'warning');
        return;
      }

      this.isSavingLogo = true;
      try {
        const res = await api.put('/site-settings/logo', {
          logo_type: this.logoForm.logo_type,
          logo_text: this.logoForm.logo_text.trim(),
          logo_image: this.logoForm.logo_image.trim(),
          splash_image: (this.logoForm.splash_image || '').trim()
        });
        showToast('主導航列 LOGO 與開場圖設定已成功儲存！', 'success');
        // 廣播給 Navbar 與 App.vue 即時更新
        window.dispatchEvent(new CustomEvent('logo-settings-updated', {
          detail: {
            logo_type: this.logoForm.logo_type,
            logo_text: this.logoForm.logo_text.trim(),
            logo_image: this.logoForm.logo_image.trim(),
            splash_image: (this.logoForm.splash_image || '').trim()
          }
        }));
      } catch (err) {
        showToast(err.message || '儲存設定失敗', 'danger');
      } finally {
        this.isSavingLogo = false;
      }
    },

    handleLogoPreviewError() {
      showToast('LOGO 圖片載入失敗，請確認圖片網址是否正確', 'warning');
    },

    async fetchBanners() {
      this.loading = true;
      this.error = null;
      try {
        const res = await api.get('/banners?admin=1');
        if (res.success && Array.isArray(res.banners)) {
          this.banners = res.banners;
        } else {
          this.banners = [];
        }
      } catch (err) {
        this.error = err.message || '取得橫幅清單失敗，請檢查伺服器連線狀態。';
      } finally {
        this.loading = false;
      }
    },

    async fetchPageBanners() {
      try {
        const res = await api.get('/page-banners');
        if (res.success && Array.isArray(res.banners)) {
          this.pageBanners = res.banners;
        }
      } catch (err) {
        console.error('取得分頁橫幅失敗:', err);
      }
    },

    openCreateModal() {
      this.editingBanner = {};
      const nextOrder = this.banners.length > 0
        ? Math.max(...this.banners.map(b => b.sort_order || 0)) + 1
        : 1;

      this.form = {
        title: '',
        subtitle: '',
        badge_text: '✨ 啟動你的舞蹈新生活',
        badge_color: 'warning',
        image_url: this.presetImages[0].url,
        primary_button_text: '立即預約課程',
        primary_button_link: '/schedule',
        primary_button_style: 'primary',
        secondary_button_text: '認識師資團隊',
        secondary_button_link: '/instructors',
        secondary_button_style: 'outline-light',
        interval_ms: 5000,
        sort_order: nextOrder,
        is_active: true
      };
      this.bannerModalInstance.show();
    },

    openEditModal(banner) {
      this.editingBanner = { ...banner };
      this.form = {
        title: banner.title || '',
        subtitle: banner.subtitle || '',
        badge_text: banner.badge_text || '',
        badge_color: banner.badge_color || 'warning',
        image_url: banner.image_url || '',
        primary_button_text: banner.primary_button_text || '',
        primary_button_link: banner.primary_button_link || '',
        primary_button_style: banner.primary_button_style || 'primary',
        secondary_button_text: banner.secondary_button_text || '',
        secondary_button_link: banner.secondary_button_link || '',
        secondary_button_style: banner.secondary_button_style || 'outline-light',
        interval_ms: banner.interval_ms || 5000,
        sort_order: banner.sort_order ?? 1,
        is_active: Boolean(banner.is_active)
      };
      this.bannerModalInstance.show();
    },

    openPreviewModal(banner) {
      this.previewItem = { ...banner };
      this.previewModalInstance.show();
    },

    openEditPageBannerModal(pb) {
      this.editingPageBanner = { ...pb };
      this.pageBannerForm = {
        title: pb.title || '',
        subtitle: pb.subtitle || '',
        image_url: pb.image_url || ''
      };
      if (!this.pageBannerModalInstance && this.$refs.pageBannerModal) {
        this.pageBannerModalInstance = new Modal(this.$refs.pageBannerModal);
      }
      this.pageBannerModalInstance?.show();
    },

    async handleFileUpload(e) {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!file.type.startsWith('image/')) {
        showToast('請選取有效的圖片檔案 (JPG, PNG, WEBP, GIF)！', 'error');
        return;
      }
      this.uploadingImage = true;
      try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await api.post('/upload/banner-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        if (res.image_url) {
          this.form.image_url = res.image_url;
          showToast('圖片上傳成功！', 'success');
        }
      } catch (err) {
        showToast(err.message || '圖片上傳失敗', 'error');
      } finally {
        this.uploadingImage = false;
        if (e.target) e.target.value = '';
      }
    },

    async handlePageBannerUpload(e) {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!file.type.startsWith('image/')) {
        showToast('請選取有效的圖片檔案！', 'error');
        return;
      }
      this.pageBannerUploading = true;
      try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await api.post('/upload/banner-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        if (res.image_url) {
          this.pageBannerForm.image_url = res.image_url;
          showToast('圖片上傳成功！', 'success');
        }
      } catch (err) {
        showToast(err.message || '圖片上傳失敗', 'error');
      } finally {
        this.pageBannerUploading = false;
        if (e.target) e.target.value = '';
      }
    },

    async submitForm() {
      if (!this.form.title.trim()) {
        showToast('請填寫橫幅主標題！', 'warning');
        return;
      }
      if (!this.form.image_url.trim()) {
        showToast('請設定或上傳橫幅背景大圖！', 'warning');
        return;
      }

      this.submitting = true;
      try {
        if (this.editingBanner.id) {
          await api.put(`/banners/${this.editingBanner.id}`, this.form);
          showToast('橫幅更新成功！', 'success');
        } else {
          await api.post('/banners', this.form);
          showToast('首頁橫幅建立成功！', 'success');
        }
        this.bannerModalInstance.hide();
        await this.fetchBanners();
      } catch (err) {
        showToast(err.message || '儲存失敗', 'error');
      } finally {
        this.submitting = false;
      }
    },

    async submitPageBannerForm() {
      if (!this.pageBannerForm.title.trim()) {
        showToast('請填寫橫幅主標題！', 'warning');
        return;
      }
      if (!this.pageBannerForm.image_url.trim()) {
        showToast('請提供或上傳背景大圖！', 'warning');
        return;
      }

      this.pageBannerSaving = true;
      try {
        await api.put(`/page-banners/${this.editingPageBanner.page_key}`, {
          title: this.pageBannerForm.title,
          subtitle: this.pageBannerForm.subtitle,
          image_url: this.pageBannerForm.image_url,
          page_name: this.editingPageBanner.page_name
        });
        showToast(`已成功更新「${this.editingPageBanner.page_name}」橫幅！`, 'success');
        this.pageBannerModalInstance?.hide();
        await this.fetchPageBanners();
      } catch (err) {
        showToast(err.message || '儲存失敗', 'error');
      } finally {
        this.pageBannerSaving = false;
      }
    },

    async toggleActive(banner) {
      this.togglingId = banner.id;
      try {
        const res = await api.post(`/banners/${banner.id}/toggle`);
        if (res.success) {
          banner.is_active = res.is_active;
          showToast(res.message || '橫幅狀態已切換', 'success');
        }
      } catch (err) {
        showToast(err.message || '狀態切換失敗', 'error');
      } finally {
        this.togglingId = null;
      }
    },

    async deleteBanner(banner) {
      const ok = await showConfirm(
        `確定要刪除橫幅「${banner.title}」嗎？此操作將自首頁移除且無法復原。`,
        '確認刪除橫幅'
      );
      if (!ok) return;

      try {
        await api.delete(`/banners/${banner.id}`);
        showToast('橫幅已成功刪除！', 'success');
        await this.fetchBanners();
      } catch (err) {
        showToast(err.message || '刪除橫幅失敗', 'error');
      }
    },

    getBadgeClass(color) {
      const c = color || 'warning';
      const isLight = ['warning', 'light', 'info'].includes(c);
      return `bg-${c} ${isLight ? 'text-dark' : 'text-white'}`;
    },

    getBtnClass(style) {
      const s = (style || 'primary').trim();
      if (s.startsWith('btn-')) return s;
      if (s.startsWith('outline-')) return `btn-${s}`;
      if (s === 'light' || s === 'warning') return `btn-${s} text-dark fw-bold`;
      return `btn-${s}`;
    },

    handleImgError(e) {
      e.target.src = this.defaultFallbackImg;
    },

    handlePreviewImgError(e) {
      e.target.src = this.defaultFallbackImg;
    }
  }
};
</script>

<style scoped>
.banner-management {
  padding: 10px;
}

.stat-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0,0,0,0.06) !important;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-thumb-wrap {
  width: 120px;
  height: 68px;
  background-color: #000;
}
.banner-thumb {
  height: 100%;
}
.thumb-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  opacity: 0;
  transition: opacity 0.2s ease;
}
.banner-thumb-wrap:hover .thumb-overlay {
  opacity: 1;
}

/* 各分頁橫幅卡片 */
.page-banner-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.page-banner-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important;
}

.page-banner-thumb-box {
  background-color: #1a1a1a;
}
.page-banner-thumb-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.7) 100%);
}

/* Modal Live Preview */
.banner-live-preview {
  position: relative;
  height: 220px;
  background-color: #111;
}
.live-bg-img {
  height: 100%;
  object-fit: cover;
}
.live-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.75) 100%);
}
.live-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 2;
}

/* 預覽區域 */
.preview-box {
  background-color: #111;
}
.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.7) 100%);
}

/* Full Preview Modal Hero */
.preview-hero-container {
  height: 500px;
  background-color: #000;
  overflow: hidden;
}
.preview-hero-img {
  height: 100%;
}
.preview-hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.75) 100%);
  z-index: 1;
}
.preview-hero-caption {
  position: absolute;
  bottom: 10%;
  left: 8%;
  right: 8%;
  z-index: 2;
}

.text-shadow {
  text-shadow: 0 2px 8px rgba(0,0,0,0.6);
}

.btn-xs {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
}

/* 確保彈窗內容可正常平順滾動，Footer 固定在底部 */
.custom-modal-body {
  max-height: calc(85vh - 130px);
  overflow-y: auto !important;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}
.custom-modal-body::-webkit-scrollbar {
  width: 6px;
}
.custom-modal-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}
.custom-modal-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}
.custom-modal-body::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>

