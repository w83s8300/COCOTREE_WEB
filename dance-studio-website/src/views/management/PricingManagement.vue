<template>
  <div class="pricing-management">
    <!-- 頂部頁頭 -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
      <div>
        <h2 class="fw-bold mb-1">
          <i class="bi bi-tags-fill text-primary me-2"></i>課程價目表與購課管理
        </h2>
        <p class="text-muted small mb-0">管理學員線上買課訂單審核、前台價目方案、學員上課須知與工作室轉帳帳號</p>
      </div>
      <div class="d-flex gap-2">
        <a
          href="/pricing"
          target="_blank"
          rel="noopener noreferrer"
          class="btn btn-outline-primary d-flex align-items-center gap-1 shadow-sm"
        >
          <i class="bi bi-box-arrow-up-right"></i>
          <span>查看前台價目表</span>
        </a>
        <button
          v-if="activeTab === 'plans'"
          @click="openCreateModal"
          class="btn btn-success d-flex align-items-center gap-1 shadow-sm"
        >
          <i class="bi bi-plus-lg"></i>
          <span>新增方案</span>
        </button>
      </div>
    </div>

    <!-- 頁面標籤導覽 (Tabs) -->
    <ul class="nav nav-pills mb-4 bg-light p-2 rounded-3 border">
      <li class="nav-item">
        <button
          class="nav-link py-2 px-3 fw-bold position-relative"
          :class="{ active: activeTab === 'orders' }"
          @click="switchTab('orders')"
        >
          <i class="bi bi-receipt me-1"></i>
          購課訂單審核
          <span v-if="pendingOrdersCount > 0" class="badge rounded-pill bg-danger ms-1">
            {{ pendingOrdersCount }}
          </span>
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link py-2 px-3 fw-bold"
          :class="{ active: activeTab === 'plans' }"
          @click="switchTab('plans')"
        >
          <i class="bi bi-collection-fill me-1"></i>
          價目方案列表 ({{ plans.length }})
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link py-2 px-3 fw-bold"
          :class="{ active: activeTab === 'notice' }"
          @click="switchTab('notice')"
        >
          <i class="bi bi-info-circle-fill me-1"></i>
          上課須知設定
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link py-2 px-3 fw-bold position-relative"
          :class="{ active: activeTab === 'bank' }"
          @click="switchTab('bank')"
        >
          <i class="bi bi-bank me-1"></i>
          轉帳帳號設定
          <span v-if="isAdmin" class="badge bg-primary-subtle text-primary border border-primary-subtle ms-1 small">管理員專用</span>
          <span v-else class="badge bg-secondary-subtle text-secondary border border-secondary-subtle ms-1 small">唯讀</span>
        </button>
      </li>
    </ul>

    <!-- 載入中狀態 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">載入中...</span>
      </div>
      <p class="mt-2 text-muted">正在載入資料...</p>
    </div>

    <!-- 錯誤訊息狀態 -->
    <div v-else-if="error" class="alert alert-danger d-flex justify-content-between align-items-center shadow-sm" role="alert">
      <div>
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        <span>{{ error }}</span>
      </div>
      <button @click="refreshCurrentTab" class="btn btn-outline-danger btn-sm">重新整理</button>
    </div>

    <!-- ==================== Tab 1: 購課訂單審核 ==================== -->
    <div v-else-if="activeTab === 'orders'">
      <!-- 搜尋與篩選列 -->
      <div class="card border-0 shadow-sm mb-3">
        <div class="card-body p-3">
          <div class="row g-2 align-items-center">
            <!-- 狀態篩選 -->
            <div class="col-md-auto">
              <div class="btn-group btn-group-sm" role="group">
                <button
                  type="button"
                  class="btn"
                  :class="orderStatusFilter === 'all' ? 'btn-primary' : 'btn-outline-secondary'"
                  @click="setOrderStatusFilter('all')"
                >
                  全部 ({{ orders.length }})
                </button>
                <button
                  type="button"
                  class="btn position-relative"
                  :class="orderStatusFilter === 'pending' ? 'btn-warning text-dark fw-bold' : 'btn-outline-warning text-dark'"
                  @click="setOrderStatusFilter('pending')"
                >
                  待確認
                  <span v-if="pendingOrdersCount > 0" class="badge rounded-pill bg-danger ms-1">
                    {{ pendingOrdersCount }}
                  </span>
                </button>
                <button
                  type="button"
                  class="btn"
                  :class="orderStatusFilter === 'confirmed' ? 'btn-success' : 'btn-outline-success'"
                  @click="setOrderStatusFilter('confirmed')"
                >
                  已確認入帳
                </button>
                <button
                  type="button"
                  class="btn"
                  :class="orderStatusFilter === 'rejected' ? 'btn-danger' : 'btn-outline-danger'"
                  @click="setOrderStatusFilter('rejected')"
                >
                  已駁回
                </button>
              </div>
            </div>

            <!-- 關鍵字搜尋 -->
            <div class="col-md-4 ms-auto">
              <div class="input-group input-group-sm">
                <span class="input-group-text bg-white text-muted"><i class="bi bi-search"></i></span>
                <input
                  type="text"
                  v-model.trim="orderSearchKeyword"
                  class="form-control"
                  placeholder="搜尋單號、姓名、電話、後5碼..."
                  @keyup.enter="fetchOrders"
                />
                <button class="btn btn-outline-secondary" type="button" @click="fetchOrders">搜尋</button>
              </div>
            </div>

            <!-- 重新整理 -->
            <div class="col-md-auto">
              <button class="btn btn-outline-secondary btn-sm" @click="fetchOrders" title="重新整理訂單">
                <i class="bi bi-arrow-clockwise me-1"></i>重新整理
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 無資料提示 -->
      <div v-if="filteredOrders.length === 0" class="text-center py-5 bg-white rounded-3 shadow-sm border">
        <i class="bi bi-inbox fs-1 text-muted opacity-50"></i>
        <p class="mt-2 mb-0 text-muted">查無符合條件的購課訂單</p>
      </div>

      <!-- 訂單列表表格 -->
      <div v-else class="card border-0 shadow-sm overflow-hidden">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col" style="width: 170px;">訂單編號 / 時間</th>
                <th scope="col" style="width: 150px;">學員資訊</th>
                <th scope="col" style="width: 170px;">購買方案 / 金額</th>
                <th scope="col" style="width: 140px;" class="text-center">銀行後 5 碼</th>
                <th scope="col" style="width: 120px;" class="text-center">訂單狀態</th>
                <th scope="col">備註說明</th>
                <th scope="col" style="width: 170px;" class="text-center">審核操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in filteredOrders" :key="order.id" :class="{ 'table-warning-subtle': order.status === 'pending' }">
                <!-- 訂單編號與時間 -->
                <td>
                  <div class="fw-bold font-monospace text-dark">{{ order.order_no }}</div>
                  <small class="text-muted">{{ formatDateTime(order.created_at) }}</small>
                </td>

                <!-- 學員資訊 -->
                <td>
                  <div class="fw-bold fs-6 text-dark">{{ order.student_name }}</div>
                  <small class="text-muted font-monospace"><i class="bi bi-telephone me-1"></i>{{ order.student_phone }}</small>
                  <div v-if="order.student_membership_expiry" class="mt-1">
                    <span class="badge bg-light text-dark border font-monospace" style="font-size: 0.68rem;">
                      年費至: {{ order.student_membership_expiry.split('T')[0] }}
                    </span>
                  </div>
                </td>

                <!-- 方案與金額 -->
                <td>
                  <div class="fw-bold text-dark">{{ order.plan_title }}</div>
                  <div class="d-flex align-items-center gap-1 flex-wrap">
                    <span class="badge bg-primary-subtle text-primary border font-monospace">{{ order.price }}</span>
                    <span v-if="order.plan_type === 'membership_fee'" class="badge border" style="background-color: #fef3c7; color: #b45309; border-color: #fcd34d !important;">
                      <i class="bi bi-award me-1"></i>會員年費 ({{ order.validity_days || 365 }}天)
                    </span>
                    <span v-else-if="order.plan_type === 'monthly_pass'" class="badge border" style="background-color: #f3e8ff; color: #7e22ce; border-color: #d8b4fe !important;">
                      <i class="bi bi-calendar-check me-1"></i>月費 ({{ order.validity_days || 30 }}天)
                    </span>
                    <span v-if="order.requires_membership" class="badge bg-warning-subtle text-dark border border-warning" title="此方案限年費會員購買">
                      <i class="bi bi-shield-lock-fill text-warning me-1"></i>限年費會員
                    </span>
                    <span v-if="order.classes_count && (order.plan_type !== 'monthly_pass' || order.classes_count > 0)" class="badge bg-success-subtle text-success border">
                      +{{ order.classes_count }} 堂
                    </span>
                  </div>
                </td>

                <!-- 銀行後 5 碼 (醒目顯示) -->
                <td class="text-center">
                  <span class="badge bg-white text-dark border shadow-sm font-monospace fs-6 px-2 py-1">
                    <i class="bi bi-credit-card-2-front text-primary me-1"></i>{{ order.bank_last_5 }}
                  </span>
                </td>

                <!-- 訂單狀態 -->
                <td class="text-center">
                  <span class="badge" :class="getOrderStatusBadgeClass(order.status)">
                    {{ formatOrderStatus(order.status) }}
                  </span>
                  <div v-if="order.confirmed_at" class="small text-muted mt-1" style="font-size: 0.75rem;">
                    {{ formatDateTime(order.confirmed_at) }}
                  </div>
                </td>

                <!-- 備註說明 -->
                <td>
                  <div v-if="order.notes" class="small text-muted mb-1">
                    <span class="text-secondary fw-bold">學員：</span>{{ order.notes }}
                  </div>
                  <div v-if="order.admin_notes" class="small p-1 px-2 bg-light rounded text-dark border">
                    <span class="text-primary fw-bold">審核備註：</span>{{ order.admin_notes }}
                  </div>
                  <span v-if="!order.notes && !order.admin_notes" class="text-muted small">-</span>
                </td>

                <!-- 操作按鈕 -->
                <td class="text-center">
                  <!-- 待確認訂單：確認入帳 / 駁回 -->
                  <div v-if="order.status === 'pending'" class="btn-group btn-group-sm">
                    <button
                      class="btn btn-success text-nowrap d-flex align-items-center gap-1"
                      @click="openConfirmModal(order)"
                      title="確認入帳並自動加堂"
                    >
                      <i class="bi bi-check-lg"></i>
                      <span>確認入帳</span>
                    </button>
                    <button
                      class="btn btn-outline-danger"
                      @click="openRejectModal(order)"
                      title="駁回訂單"
                    >
                      <i class="bi bi-x-lg"></i>
                      <span>駁回</span>
                    </button>
                  </div>

                  <!-- 已審核完成：查看或刪除 -->
                  <div v-else class="d-flex align-items-center justify-content-center gap-1">
                    <small class="text-muted me-1" v-if="order.confirmed_by_name">
                      審核人: {{ order.confirmed_by_name }}
                    </small>
                    <button
                      class="btn btn-outline-secondary btn-sm p-1 px-2"
                      @click="handleDeleteOrder(order)"
                      title="刪除紀錄"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ==================== Tab 2: 價目方案管理 ==================== -->
    <div v-else-if="activeTab === 'plans'">
      <!-- 無資料提示 -->
      <div v-if="plans.length === 0" class="text-center py-5 bg-white rounded-3 shadow-sm border">
        <i class="bi bi-inbox fs-1 text-muted opacity-50"></i>
        <p class="mt-2 mb-3 text-muted">目前尚無任何價目方案</p>
        <button @click="openCreateModal" class="btn btn-primary btn-sm">
          <i class="bi bi-plus-lg me-1"></i>立即新增第一個方案
        </button>
      </div>

      <!-- 方案列表表格 -->
      <div v-else class="card border-0 shadow-sm overflow-hidden">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col" style="width: 70px;" class="text-center">排序</th>
                <th scope="col" style="width: 200px;">方案名稱</th>
                <th scope="col" style="width: 180px;">價格 / 單位</th>
                <th scope="col" style="width: 150px;" class="text-center">方案類型 / 內容</th>
                <th scope="col" style="width: 130px;" class="text-center">熱門推薦</th>
                <th scope="col" style="width: 110px;" class="text-center">前台狀態</th>
                <th scope="col" style="width: 150px;" class="text-center">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="plan in plans" :key="plan.id" :class="{ 'table-secondary opacity-75': !plan.is_active }">
                <!-- 排序 -->
                <td class="text-center">
                  <span class="badge bg-light text-dark border font-monospace">{{ plan.sort_order }}</span>
                </td>
                <!-- 方案名稱 -->
                <td>
                  <div class="fw-bold fs-6 text-dark">{{ plan.title }}</div>
                  <small v-if="plan.subtitle" class="text-muted d-block">{{ plan.subtitle }}</small>
                </td>
                <!-- 價格與單位 -->
                <td>
                  <div class="d-flex align-items-baseline gap-1">
                    <span v-if="plan.original_price" class="text-muted text-decoration-line-through small me-1">
                      {{ plan.original_price }}
                    </span>
                    <span class="fw-bold text-primary fs-5">{{ plan.price }}</span>
                  </div>
                  <div class="small text-muted">{{ plan.unit }}</div>
                </td>
                <!-- 方案類型 / 內容 -->
                <td class="text-center">
                  <span v-if="plan.plan_type === 'membership_fee'" class="badge border fs-6 font-monospace" style="background-color: #fef3c7; color: #b45309; border-color: #fcd34d !important;">
                    <i class="bi bi-award me-1"></i>會員年費 ({{ plan.validity_days || 365 }}天)
                  </span>
                  <span v-else-if="plan.plan_type === 'monthly_pass'" class="badge border fs-6 font-monospace" style="background-color: #f3e8ff; color: #7e22ce; border-color: #d8b4fe !important;">
                    <i class="bi bi-calendar-check me-1"></i>月費 ({{ plan.validity_days || 30 }}天)
                  </span>
                  <span v-else class="badge bg-success-subtle text-success border fs-6 font-monospace">
                    <i class="bi bi-ticket-perforated me-1"></i>{{ plan.classes_count || 1 }} 堂
                  </span>
                  <div class="mt-1" v-if="plan.plan_type !== 'membership_fee'">
                    <span v-if="plan.requires_membership" class="badge bg-warning-subtle text-dark border border-warning" title="僅限具備有效會員年費之學員購買">
                      <i class="bi bi-shield-lock-fill text-warning me-1"></i>限年費會員
                    </span>
                    <span v-else class="badge bg-light text-muted border" title="所有學員皆可購買">
                      一般學員可購
                    </span>
                  </div>
                  <div v-if="(plan.plan_type === 'monthly_pass' || plan.plan_type === 'membership_fee') && plan.classes_count > 0" class="small text-muted mt-1">
                    +{{ plan.classes_count }} 堂贈課
                  </div>
                </td>
                <!-- 熱門推薦 Toggle -->
                <td class="text-center">
                  <button
                    @click="togglePopular(plan)"
                    class="btn btn-sm"
                    :class="plan.is_popular ? 'btn-warning text-dark fw-bold' : 'btn-outline-secondary'"
                    :title="plan.is_popular ? '點擊取消熱門推薦' : '點擊設為熱門推薦'"
                  >
                    <i :class="plan.is_popular ? 'bi bi-star-fill me-1' : 'bi bi-star me-1'"></i>
                    {{ plan.is_popular ? '熱門推薦' : '一般方案' }}
                  </button>
                </td>
                <!-- 上架狀態 Toggle -->
                <td class="text-center">
                  <button
                    @click="toggleActive(plan)"
                    class="btn btn-sm"
                    :class="plan.is_active ? 'btn-success-subtle text-success border border-success' : 'btn-secondary-subtle text-secondary border border-secondary'"
                    :title="plan.is_active ? '點擊下架隱藏' : '點擊上架顯示'"
                  >
                    <i :class="plan.is_active ? 'bi bi-eye-fill me-1' : 'bi bi-eye-slash-fill me-1'"></i>
                    {{ plan.is_active ? '上架中' : '已下架' }}
                  </button>
                </td>
                <!-- 操作按鈕 -->
                <td class="text-center">
                  <div class="btn-group btn-group-sm">
                    <button @click="openEditModal(plan)" class="btn btn-outline-primary" title="編輯方案">
                      <i class="bi bi-pencil-square me-1"></i>編輯
                    </button>
                    <button @click="handleDelete(plan)" class="btn btn-outline-danger" title="刪除方案">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ==================== Tab 3: 上課須知設定 ==================== -->
    <div v-else-if="activeTab === 'notice'" class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white py-3 border-bottom">
            <h5 class="fw-bold mb-0 text-dark">
              <i class="bi bi-pencil-square text-primary me-2"></i>學員報名與上課須知內容編輯
            </h5>
          </div>
          <div class="card-body p-4">
            <div class="mb-3">
              <label class="form-label fw-bold">區塊標題 <span class="text-danger">*</span></label>
              <input
                type="text"
                v-model="noticeForm.title"
                class="form-control"
                placeholder="例如：學員報名與上課須知"
              />
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold">
                須知條列內容
                <small class="text-muted fw-normal">（請以換行分隔，每一行代表一條獨立的注意事項）</small>
              </label>
              <textarea
                v-model="noticeForm.content"
                rows="8"
                class="form-control font-monospace"
                placeholder="請輸入每一條須知，每行一條..."
              ></textarea>
            </div>

            <!-- 即時預覽效果 -->
            <div class="mb-4 p-3 bg-light rounded-3 border">
              <h6 class="fw-bold text-muted mb-2">
                <i class="bi bi-eye me-1"></i>前台呈現預覽：
              </h6>
              <h5 class="fw-bold mb-3 text-dark">{{ noticeForm.title || '（無標題）' }}</h5>
              <ul class="lh-lg mb-0 text-secondary" v-if="parsedNoticeItems.length > 0">
                <li v-for="(item, idx) in parsedNoticeItems" :key="idx">{{ item }}</li>
              </ul>
              <div v-else class="text-muted small">尚未輸入內容</div>
            </div>

            <div class="d-flex justify-content-end">
              <button
                @click="saveNoticeSettings"
                class="btn btn-primary px-4 py-2 d-flex align-items-center gap-2"
                :disabled="savingNotice"
              >
                <span v-if="savingNotice" class="spinner-border spinner-border-sm" role="status"></span>
                <i v-else class="bi bi-check-lg"></i>
                <span>儲存須知設定</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== Tab 4: 轉帳帳號設定 (僅系統管理員可編輯) ==================== -->
    <div v-else-if="activeTab === 'bank'" class="row justify-content-center">
      <div class="col-lg-10">
        <!-- 權限提示 -->
        <div v-if="!isAdmin" class="alert alert-warning d-flex align-items-center mb-4 shadow-sm border-warning rounded-3" role="alert">
          <i class="bi bi-shield-lock-fill fs-3 me-3 text-warning"></i>
          <div>
            <h6 class="fw-bold mb-1">權限提示（唯讀模式）</h6>
            <div class="small text-secondary">
              您目前的角色為 <strong>{{ adminAuth.roleLabel }}</strong>。依工作室安全規範，<strong>只有「系統管理員（admin）」</strong>具備修改轉帳匯款帳號之權限，其餘人員僅供查閱。
            </div>
          </div>
        </div>
        <div v-else class="alert alert-success-subtle d-flex align-items-center mb-4 shadow-sm border-success-subtle rounded-3" role="alert">
          <i class="bi bi-shield-check fs-3 me-3 text-success"></i>
          <div>
            <h6 class="fw-bold mb-1 text-success">系統管理員專屬權限</h6>
            <div class="small text-secondary">
              您已具備<strong>「系統管理員」</strong>最高權限，在此修改的銀行代碼、帳號與戶名將即時同步至全站前台【學員買課確認彈窗】。
            </div>
          </div>
        </div>

        <div class="row g-4">
          <!-- 左側：設定表單 -->
          <div class="col-lg-7">
            <div class="card border-0 shadow-sm rounded-3">
              <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
                <h5 class="fw-bold mb-0 text-dark">
                  <i class="bi bi-bank text-primary me-2"></i>工作室轉帳匯款帳號設定
                </h5>
                <span v-if="isAdmin" class="badge bg-success">
                  <i class="bi bi-unlock-fill me-1"></i>可編輯
                </span>
                <span v-else class="badge bg-secondary">
                  <i class="bi bi-lock-fill me-1"></i>唯讀鎖定
                </span>
              </div>
              <div class="card-body p-4">
                <form @submit.prevent="saveBankAccount">
                  <div class="row g-3">
                    <div class="col-md-7">
                      <label class="form-label fw-bold">銀行名稱 <span class="text-danger">*</span></label>
                      <input
                        type="text"
                        v-model.trim="bankForm.bank_name"
                        class="form-control"
                        :disabled="!isAdmin || savingBank"
                        placeholder="例如：國泰世華銀行、中國信託"
                        required
                      />
                    </div>
                    <div class="col-md-5">
                      <label class="form-label fw-bold">銀行代碼 <span class="text-danger">*</span></label>
                      <input
                        type="text"
                        v-model.trim="bankForm.bank_code"
                        class="form-control font-monospace"
                        :disabled="!isAdmin || savingBank"
                        placeholder="例如：013、822"
                        required
                      />
                    </div>
                    <div class="col-12">
                      <label class="form-label fw-bold">銀行帳號 <span class="text-danger">*</span></label>
                      <input
                        type="text"
                        v-model.trim="bankForm.bank_account"
                        class="form-control font-monospace fs-5"
                        :disabled="!isAdmin || savingBank"
                        placeholder="例如：012-34-567890-1"
                        required
                      />
                    </div>
                    <div class="col-12">
                      <label class="form-label fw-bold">帳戶戶名 <span class="text-danger">*</span></label>
                      <input
                        type="text"
                        v-model.trim="bankForm.bank_account_name"
                        class="form-control"
                        :disabled="!isAdmin || savingBank"
                        placeholder="例如：Dance Studio 舞蹈工作室"
                        required
                      />
                    </div>
                    <div class="col-12">
                      <label class="form-label fw-bold">匯款附註與學員注意事項說明</label>
                      <textarea
                        v-model.trim="bankForm.bank_notes"
                        rows="3"
                        class="form-control"
                        :disabled="!isAdmin || savingBank"
                        placeholder="例如：請先完成匯款後，於下方填寫您的轉帳帳號後 5 碼，以便工作人員核帳開通堂數。"
                      ></textarea>
                    </div>
                  </div>

                  <div class="mt-4 pt-3 border-top d-flex justify-content-between align-items-center">
                    <div class="text-muted small">
                      <span v-if="isAdmin">* 儲存後立即於前台官網買課流程生效</span>
                      <span v-else class="text-danger">* 您無權修改此設定</span>
                    </div>
                    <button
                      v-if="isAdmin"
                      type="submit"
                      class="btn btn-primary px-4 py-2 fw-bold d-flex align-items-center gap-2 shadow-sm"
                      :disabled="savingBank"
                    >
                      <span v-if="savingBank" class="spinner-border spinner-border-sm" role="status"></span>
                      <i v-else class="bi bi-check-circle-fill"></i>
                      <span>儲存轉帳帳號設定</span>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- 右側：即時前台預覽卡片 -->
          <div class="col-lg-5">
            <div class="card border-0 shadow-sm rounded-3 h-100">
              <div class="card-header bg-white py-3 border-bottom">
                <h6 class="fw-bold mb-0 text-dark">
                  <i class="bi bi-eye-fill text-primary me-2"></i>前台學員買課彈窗即時預覽
                </h6>
              </div>
              <div class="card-body p-4 bg-light d-flex flex-column justify-content-center">
                <div class="p-3 bg-primary-subtle text-primary-emphasis rounded-3 border border-primary-subtle shadow-sm small">
                  <div class="fw-bold mb-1">
                    <i class="bi bi-bank me-1"></i>工作室轉帳匯款帳號資訊：
                  </div>
                  <div class="font-monospace lh-base">
                    銀行：{{ bankForm.bank_name || '（尚未填寫銀行）' }} ({{ bankForm.bank_code || '---' }})<br>
                    帳號：<strong class="text-dark">{{ bankForm.bank_account || '尚未設定' }}</strong><br>
                    戶名：{{ bankForm.bank_account_name || '尚未設定' }}
                  </div>
                  <div v-if="bankForm.bank_notes" class="text-muted mt-2" style="font-size: 0.8rem;">
                    * {{ bankForm.bank_notes }}
                  </div>
                </div>

                <div class="mt-3 text-center text-muted small">
                  <i class="bi bi-info-circle me-1"></i>此卡片為學員於「課程價目表」點選買課時看到的實時效果
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== 方案新增 / 編輯 Modal ==================== -->
    <div
      class="modal fade"
      id="pricingPlanModal"
      tabindex="-1"
      aria-labelledby="pricingPlanModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold" id="pricingPlanModalLabel">
              <i :class="editingId ? 'bi bi-pencil-square text-primary' : 'bi bi-plus-circle-fill text-success'" class="me-2"></i>
              {{ editingId ? '編輯價目方案' : '新增價目方案' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4">
            <form @submit.prevent="handleSubmitPlan">
              <div class="row g-3">
                <!-- 方案計費類型選擇 (買幾堂 / 月票 / 會員年費) -->
                <div class="col-12">
                  <label class="form-label fw-bold d-block mb-2">方案計費類型 <span class="text-danger">*</span></label>
                  <div class="row g-2">
                    <div class="col-md-4">
                      <div
                        class="p-3 border rounded-3 text-center cursor-pointer h-100 transition-all"
                        :class="form.plan_type === 'classes' ? 'border-success bg-success-subtle text-success fw-bold shadow-sm' : 'bg-light text-muted'"
                        style="cursor: pointer;"
                        @click="setPlanType('classes')"
                      >
                        <i class="bi bi-ticket-perforated fs-4 d-block mb-1"></i>
                        <span class="fs-6">買幾堂（堂數制）</span>
                        <div class="small fw-normal text-secondary mt-1">例如：單堂體驗、8堂套票、20堂等</div>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div
                        class="p-3 border rounded-3 text-center cursor-pointer h-100 transition-all"
                        :class="form.plan_type === 'monthly_pass' ? 'border-primary bg-primary-subtle text-primary fw-bold shadow-sm' : 'bg-light text-muted'"
                        style="cursor: pointer;"
                        @click="setPlanType('monthly_pass')"
                      >
                        <i class="bi bi-calendar2-week fs-4 d-block mb-1"></i>
                        <span class="fs-6">月票（效期 / 會員期限）</span>
                        <div class="small fw-normal text-secondary mt-1">例如：月票 30天無限跳、季票 90天等</div>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div
                        class="p-3 border rounded-3 text-center cursor-pointer h-100 transition-all"
                        :class="form.plan_type === 'membership_fee' ? 'border-warning bg-warning-subtle text-dark fw-bold shadow-sm' : 'bg-light text-muted'"
                        style="cursor: pointer;"
                        @click="setPlanType('membership_fee')"
                      >
                        <i class="bi bi-award fs-4 d-block mb-1 text-warning"></i>
                        <span class="fs-6">會員年費（會員資格）</span>
                        <div class="small fw-normal text-secondary mt-1">例如：年度會員費 (365天效期)</div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 方案名稱 -->
                <div class="col-md-6">
                  <label class="form-label fw-bold">方案名稱 <span class="text-danger">*</span></label>
                  <input
                    type="text"
                    v-model="form.title"
                    class="form-control"
                    placeholder="例如：小資方案、熱血方案、尊榮月費"
                    required
                  />
                </div>

                <!-- 副標題 / 適用對象簡述 -->
                <div class="col-md-6">
                  <label class="form-label fw-bold">副標題 / 適用對象簡述</label>
                  <input
                    type="text"
                    v-model="form.subtitle"
                    class="form-control"
                    placeholder="例如：適合規律每週練習者"
                  />
                </div>

                <!-- 方案售價 -->
                <div class="col-md-6">
                  <label class="form-label fw-bold">售價金額 <span class="text-danger">*</span></label>
                  <input
                    type="text"
                    v-model="form.price"
                    class="form-control"
                    placeholder="例如：$3,200 或 $500"
                    required
                  />
                </div>

                <!-- 計費單位 -->
                <div class="col-md-6">
                  <label class="form-label fw-bold">計費單位說明 <span class="text-danger">*</span></label>
                  <input
                    type="text"
                    v-model="form.unit"
                    class="form-control"
                    placeholder="例如：/ 堂、/ 8 堂、/ 月 (無限堂數)"
                    required
                  />
                </div>

                <!-- 若為「買幾堂 (堂數制)」時的專用欄位 -->
                <div v-if="form.plan_type === 'classes'" class="col-12 p-3 bg-light rounded-3 border">
                  <label class="form-label fw-bold text-success">
                    <i class="bi bi-ticket-perforated-fill me-1"></i>包含堂數 (確認入帳時自動增加堂數) <span class="text-danger">*</span>
                  </label>
                  <div class="input-group" style="max-width: 250px;">
                    <input
                      type="number"
                      v-model.number="form.classes_count"
                      min="1"
                      class="form-control font-monospace fs-5"
                      placeholder="8"
                      required
                    />
                    <span class="input-group-text">堂</span>
                  </div>
                  <small class="text-muted d-block mt-1">審核確認入帳時，系統將自動為學員帳戶累加此堂數</small>
                </div>

                <!-- 若為「月票 (效期制)」時的專用欄位 -->
                <div v-else-if="form.plan_type === 'monthly_pass'" class="col-12 p-3 bg-light rounded-3 border">
                  <div class="row g-3">
                    <div class="col-md-7">
                      <label class="form-label fw-bold text-primary">
                        <i class="bi bi-calendar-check-fill me-1"></i>月費有效天數 (自動展延月費到期日) <span class="text-danger">*</span>
                      </label>
                      <div class="input-group mb-2" style="max-width: 250px;">
                        <input
                          type="number"
                          v-model.number="form.validity_days"
                          min="1"
                          class="form-control font-monospace fs-5"
                          placeholder="30"
                          required
                        />
                        <span class="input-group-text">天</span>
                      </div>
                      <div class="d-flex flex-wrap gap-1">
                        <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-2" @click="setValidityDays(30)">1 個月 (30天)</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-2" @click="setValidityDays(60)">2 個月 (60天)</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-2" @click="setValidityDays(90)">季票 (90天)</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-2" @click="setValidityDays(180)">半年 (180天)</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-2" @click="setValidityDays(365)">年票 (365天)</button>
                      </div>
                      <small class="text-muted d-block mt-1">審核通過時，將以學員現有月費到期日（或今日）為基準自動順延</small>
                    </div>

                    <div class="col-md-5">
                      <label class="form-label fw-bold text-secondary">
                        <i class="bi bi-gift-fill me-1"></i>額外贈送堂數 (選填)
                      </label>
                      <div class="input-group" style="max-width: 200px;">
                        <input
                          type="number"
                          v-model.number="form.classes_count"
                          min="0"
                          class="form-control font-monospace fs-5"
                          placeholder="0"
                        />
                        <span class="input-group-text">堂</span>
                      </div>
                      <small class="text-muted d-block mt-1">填 0 代表純月票無限暢跳；填大於 0 代表額外送堂數</small>
                    </div>
                  </div>
                </div>

                <!-- 購買資格限制開關 (會員年費限制) -->
                <div class="col-12" v-if="form.plan_type !== 'membership_fee'">
                  <div class="p-3 bg-warning-subtle rounded-3 border border-warning-subtle">
                    <div class="form-check form-switch mb-1">
                      <input
                        class="form-check-input"
                        type="checkbox"
                        role="switch"
                        id="requiresMembershipSwitch"
                        v-model="form.requires_membership"
                      />
                      <label class="form-check-label fw-bold text-dark" for="requiresMembershipSwitch">
                        <i class="bi bi-shield-lock-fill text-warning me-1"></i>限定「會員年費」有效學員才可購買
                      </label>
                    </div>
                    <small class="text-muted d-block">
                      開啟後，只有已繳交且尚未到期之「會員年費」學員才能在線上選購此方案（例如會員專屬課包、會員專屬月費）；未繳交年費或年費已過期學員將無法購買。
                    </small>
                  </div>
                </div>

                <!-- 若為「會員年費 (年度會員資格)」時的專用欄位 -->
                <div v-else-if="form.plan_type === 'membership_fee'" class="col-12 p-3 bg-light rounded-3 border">
                  <div class="row g-3">
                    <div class="col-md-7">
                      <label class="form-label fw-bold text-dark">
                        <i class="bi bi-award-fill text-warning me-1"></i>會員年費有效天數 (自動展延會員年費到期日) <span class="text-danger">*</span>
                      </label>
                      <div class="input-group mb-2" style="max-width: 250px;">
                        <input
                          type="number"
                          v-model.number="form.validity_days"
                          min="1"
                          class="form-control font-monospace fs-5"
                          placeholder="365"
                          required
                        />
                        <span class="input-group-text">天</span>
                      </div>
                      <div class="d-flex flex-wrap gap-1">
                        <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-2" @click="setValidityDays(365)">1 年 (365天)</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-2" @click="setValidityDays(730)">2 年 (730天)</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary py-0 px-2" @click="setValidityDays(180)">半年 (180天)</button>
                      </div>
                      <small class="text-muted d-block mt-1">審核確認入帳時，系統將自動以此天數順延該學員的<strong>會員年費到期日</strong></small>
                    </div>

                    <div class="col-md-5">
                      <label class="form-label fw-bold text-secondary">
                        <i class="bi bi-gift-fill me-1"></i>入會贈送堂數 (選填)
                      </label>
                      <div class="input-group" style="max-width: 200px;">
                        <input
                          type="number"
                          v-model.number="form.classes_count"
                          min="0"
                          class="form-control font-monospace fs-5"
                          placeholder="0"
                        />
                        <span class="input-group-text">堂</span>
                      </div>
                      <small class="text-muted d-block mt-1">若無贈送堂數請填 0，有贈送則入帳時一併增加</small>
                    </div>
                  </div>
                </div>

                <!-- 原價 (劃線促銷) -->
                <div class="col-md-4">
                  <label class="form-label fw-bold">原價 (選填，供劃線比價)</label>
                  <input
                    type="text"
                    v-model="form.original_price"
                    class="form-control"
                    placeholder="例如：$4,000"
                  />
                </div>

                <!-- 排序權重 -->
                <div class="col-md-4">
                  <label class="form-label fw-bold">排序編號</label>
                  <input
                    type="number"
                    v-model.number="form.sort_order"
                    class="form-control"
                    placeholder="數字越小越靠前"
                  />
                  <small class="text-muted">由小至大排序顯示</small>
                </div>

                <!-- 按鈕文字 -->
                <div class="col-md-4">
                  <label class="form-label fw-bold">按鈕文字</label>
                  <input
                    type="text"
                    v-model="form.button_text"
                    class="form-control"
                    placeholder="預設：買課"
                  />
                </div>

                <!-- 狀態開關 -->
                <div class="col-12">
                  <div class="p-3 bg-light rounded-3 border d-flex gap-4 align-items-center">
                    <div class="form-check form-switch mb-0">
                      <input
                        class="form-check-input"
                        type="checkbox"
                        role="switch"
                        id="isPopularSwitch"
                        v-model="form.is_popular"
                      />
                      <label class="form-check-label fw-bold" for="isPopularSwitch">
                        <i class="bi bi-star-fill text-warning me-1"></i>標記為「熱門推薦」
                      </label>
                    </div>

                    <div class="form-check form-switch mb-0">
                      <input
                        class="form-check-input"
                        type="checkbox"
                        role="switch"
                        id="isActiveSwitch"
                        v-model="form.is_active"
                      />
                      <label class="form-check-label fw-bold" for="isActiveSwitch">
                        <i class="bi bi-eye-fill text-success me-1"></i>立即於官網前台啟用上架
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 按鈕區 -->
              <div class="modal-footer px-0 pb-0 mt-4 border-top">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                <button type="submit" class="btn btn-primary px-4" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
                  <span>{{ editingId ? '儲存變更' : '建立方案' }}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== 訂單確認入帳 Modal ==================== -->
    <div
      class="modal fade"
      id="confirmOrderModal"
      tabindex="-1"
      aria-labelledby="confirmOrderModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content shadow border-0 rounded-3">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title fw-bold" id="confirmOrderModalLabel">
              <i class="bi bi-check-circle-fill me-2"></i>確認入帳審核
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4" v-if="selectedOrder">
            <div class="alert alert-success-subtle border border-success-subtle mb-3 small">
              <i class="bi bi-info-circle-fill me-1"></i>
              確認入帳後，系統將<strong>立即自動為學員增加相應課程堂數</strong>。
            </div>

            <div class="p-3 bg-light rounded-3 border mb-3">
              <div class="d-flex justify-content-between mb-1">
                <span class="text-muted">訂單編號：</span>
                <span class="font-monospace text-dark fw-bold">{{ selectedOrder.order_no }}</span>
              </div>
              <div class="d-flex justify-content-between mb-1">
                <span class="text-muted">購課學員：</span>
                <span class="text-dark fw-bold">{{ selectedOrder.student_name }} ({{ selectedOrder.student_phone }})</span>
              </div>
              <div class="d-flex justify-content-between mb-1">
                <span class="text-muted">購買方案：</span>
                <span class="text-primary fw-bold">
                  {{ selectedOrder.plan_title }} ({{ selectedOrder.price }})
                  <span v-if="selectedOrder.plan_type === 'membership_fee'" class="badge border ms-1" style="background-color: #fef3c7; color: #b45309;">
                    會員年費 ({{ selectedOrder.validity_days || 365 }} 天)
                  </span>
                  <span v-else-if="selectedOrder.plan_type === 'monthly_pass'" class="badge border ms-1" style="background-color: #f3e8ff; color: #7e22ce;">
                    月票 ({{ selectedOrder.validity_days || 30 }} 天)
                  </span>
                  <span v-else class="badge bg-success-subtle text-success ms-1">
                    {{ selectedOrder.classes_count || 1 }} 堂
                  </span>
                </span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">銀行後 5 碼：</span>
                <span class="badge bg-white text-dark border font-monospace fs-6 px-2">{{ selectedOrder.bank_last_5 }}</span>
              </div>
            </div>

            <form @submit.prevent="submitConfirmOrder">
              <!-- 若為月票方案：展延天數輸入 -->
              <div v-if="selectedOrder.plan_type === 'monthly_pass' || selectedOrder.plan_type === 'membership_fee' || selectedOrder.validity_days > 0" class="mb-3 p-3 bg-primary-subtle rounded-3 border border-primary-subtle">
                <label class="form-label fw-bold text-primary mb-1">
                  <i class="bi bi-calendar-check-fill me-1"></i>
                  <span v-if="selectedOrder.plan_type === 'monthly_pass'">展延「月費暢跳」有效期限天數</span>
                  <span v-else-if="selectedOrder.plan_type === 'membership_fee'">展延「會員年費」有效期限天數</span>
                  <span v-else>展延會員有效期限天數</span>
                  <span class="text-danger">*</span>
                </label>
                <div class="input-group mb-1" style="max-width: 220px;">
                  <input
                    type="number"
                    v-model.number="confirmForm.validity_days"
                    min="1"
                    class="form-control font-monospace fs-5"
                    required
                  />
                  <span class="input-group-text">天</span>
                </div>
                <small class="text-muted d-block">
                  <span v-if="selectedOrder.plan_type === 'monthly_pass'">確認後系統將自動將該學員的<strong>月費到期日</strong>順延此天數（期間預約特定課程免扣堂數）。</span>
                  <span v-else-if="selectedOrder.plan_type === 'membership_fee'">確認後系統將自動將該學員的<strong>會員年費到期日</strong>順延此天數。</span>
                  <span v-else>確認後系統將自動將該學員的會員到期日順延此天數。</span>
                </small>
              </div>

              <!-- 若有包含堂數或為堂數方案：加堂輸入 -->
              <div v-if="selectedOrder.plan_type !== 'monthly_pass' || confirmForm.classes_to_add > 0" class="mb-3">
                <label class="form-label fw-bold">
                  <i class="bi bi-ticket-perforated-fill text-success me-1"></i>入帳增加堂數
                </label>
                <div class="input-group" style="max-width: 220px;">
                  <input
                    type="number"
                    v-model.number="confirmForm.classes_to_add"
                    min="0"
                    class="form-control font-monospace fs-5"
                    required
                  />
                  <span class="input-group-text">堂</span>
                </div>
                <small class="text-muted">預設為該方案設定的堂數，如有贈堂亦可在此調整</small>
              </div>

              <div class="mb-3">
                <label class="form-label small fw-bold">審核備註 (選填)</label>
                <input
                  type="text"
                  v-model.trim="confirmForm.admin_notes"
                  class="form-control form-control-sm"
                  placeholder="例如：已核對國泰轉帳入帳無誤"
                />
              </div>

              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">取消</button>
                <button type="submit" class="btn btn-success px-4 fw-bold" :disabled="processingOrder">
                  <span v-if="processingOrder" class="spinner-border spinner-border-sm me-1"></span>
                  <span v-if="selectedOrder.plan_type === 'monthly_pass'">確認入帳並開通月費</span>
                  <span v-else-if="selectedOrder.plan_type === 'membership_fee'">確認入帳並開通會員年費</span>
                  <span v-else>確認入帳並加堂</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== 訂單駁回 Modal ==================== -->
    <div
      class="modal fade"
      id="rejectOrderModal"
      tabindex="-1"
      aria-labelledby="rejectOrderModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content shadow border-0 rounded-3">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title fw-bold" id="rejectOrderModalLabel">
              <i class="bi bi-x-circle-fill me-2"></i>駁回購課訂單
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4" v-if="selectedOrder">
            <p class="text-muted small mb-3">
              駁回後此訂單將標記為駁回狀態，<strong>不會為學員增加堂數</strong>。學員可在會員中心查看駁回原因。
            </p>

            <form @submit.prevent="submitRejectOrder">
              <div class="mb-3">
                <label class="form-label fw-bold">駁回原因說明 <span class="text-danger">*</span></label>
                <textarea
                  v-model.trim="rejectForm.admin_notes"
                  rows="3"
                  class="form-control"
                  placeholder="例如：查無此帳號後5碼匯款資訊、匯款金額不符，請聯繫櫃檯等"
                  required
                ></textarea>
              </div>

              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">取消</button>
                <button type="submit" class="btn btn-danger px-4 fw-bold" :disabled="processingOrder">
                  <span v-if="processingOrder" class="spinner-border spinner-border-sm me-1"></span>
                  <span>確認駁回</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api, { API_ENDPOINTS } from '@/utils/api';
import { useAdminAuth } from '@/utils/adminAuth';
import { Modal } from 'bootstrap';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';

export default {
  name: 'PricingManagement',
  data() {
    return {
      adminAuth: useAdminAuth(),
      activeTab: 'orders', // 'orders' | 'plans' | 'notice' | 'bank'
      loading: false,
      error: null,
      submitting: false,
      savingNotice: false,
      savingBank: false,
      processingOrder: false,

      // 方案管理
      plans: [],
      modalInstance: null,
      editingId: null,
      form: {
        title: '',
        subtitle: '',
        price: '',
        unit: '/ 堂',
        plan_type: 'classes',
        classes_count: 8,
        validity_days: 30,
        original_price: '',
        sort_order: 1,
        is_popular: false,
        requires_membership: false,
        is_active: true,
        button_text: '買課',
        button_link: '/contact'
      },

      // 上課須知
      noticeForm: {
        title: '學員報名與上課須知',
        content: ''
      },

      // 轉帳帳號設定 (系統管理員專屬)
      bankForm: {
        bank_name: '國泰世華銀行',
        bank_code: '013',
        bank_account: '012-34-567890-1',
        bank_account_name: 'Dance Studio 舞蹈工作室',
        bank_notes: '請先完成匯款後，於下方填寫您的轉帳帳號後 5 碼，以便工作人員核帳開通堂數。'
      },

      // 購課訂單
      orders: [],
      pendingOrdersCount: 0,
      orderStatusFilter: 'all',
      orderSearchKeyword: '',
      selectedOrder: null,
      confirmModalInstance: null,
      rejectModalInstance: null,
      confirmForm: {
        classes_to_add: 1,
        validity_days: 0,
        admin_notes: ''
      },
      rejectForm: {
        admin_notes: ''
      }
    };
  },
  computed: {
    isAdmin() {
      return this.adminAuth.currentRole === 'admin';
    },
    parsedNoticeItems() {
      if (!this.noticeForm.content) return [];
      return this.noticeForm.content
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
    },
    filteredOrders() {
      return this.orders.filter(order => {
        if (this.orderStatusFilter !== 'all' && order.status !== this.orderStatusFilter) {
          return false;
        }
        if (this.orderSearchKeyword) {
          const kw = this.orderSearchKeyword.toLowerCase();
          const matchNo = (order.order_no || '').toLowerCase().includes(kw);
          const matchName = (order.student_name || '').toLowerCase().includes(kw);
          const matchPhone = (order.student_phone || '').toLowerCase().includes(kw);
          const matchBank = (order.bank_last_5 || '').toLowerCase().includes(kw);
          const matchPlan = (order.plan_title || '').toLowerCase().includes(kw);
          if (!matchNo && !matchName && !matchPhone && !matchBank && !matchPlan) {
            return false;
          }
        }
        return true;
      });
    }
  },
  mounted() {
    this.initModals();
    this.fetchOrders();
    this.fetchPlansData();
    this.fetchBankInfo();
  },
  beforeUnmount() {
    if (this.modalInstance) this.modalInstance.dispose();
    if (this.confirmModalInstance) this.confirmModalInstance.dispose();
    if (this.rejectModalInstance) this.rejectModalInstance.dispose();
  },
  methods: {
    initModals() {
      const planEl = document.getElementById('pricingPlanModal');
      if (planEl) this.modalInstance = new Modal(planEl);

      const confirmEl = document.getElementById('confirmOrderModal');
      if (confirmEl) this.confirmModalInstance = new Modal(confirmEl);

      const rejectEl = document.getElementById('rejectOrderModal');
      if (rejectEl) this.rejectModalInstance = new Modal(rejectEl);
    },
    switchTab(tab) {
      this.activeTab = tab;
      this.refreshCurrentTab();
    },
    refreshCurrentTab() {
      if (this.activeTab === 'orders') {
        this.fetchOrders();
      } else if (this.activeTab === 'bank') {
        this.fetchBankInfo();
      } else {
        this.fetchPlansData();
      }
    },
    setOrderStatusFilter(status) {
      this.orderStatusFilter = status;
    },

    // ---------------- 購課訂單相關 ----------------
    async fetchOrders() {
      try {
        const res = await api.get(API_ENDPOINTS.PRICING_ORDERS, {
          params: { keyword: this.orderSearchKeyword }
        });
        if (res.success) {
          this.orders = res.orders || [];
          this.pendingOrdersCount = res.pending_count ?? 0;
        }
      } catch (err) {
        console.error('查詢訂單失敗:', err);
      }
    },
    openConfirmModal(order) {
      this.selectedOrder = order;
      this.confirmForm = {
        classes_to_add: order.classes_count ?? (order.plan_type === 'classes' ? 1 : 0),
        validity_days: order.validity_days || (order.plan_type === 'membership_fee' ? 365 : (order.plan_type === 'monthly_pass' ? 30 : 0)),
        admin_notes: ''
      };
      if (this.confirmModalInstance) {
        this.confirmModalInstance.show();
      }
    },
    async submitConfirmOrder() {
      if (!this.selectedOrder) return;
      this.processingOrder = true;
      try {
        const payload = {
          classes_to_add: this.confirmForm.classes_to_add,
          validity_days: this.confirmForm.validity_days,
          admin_notes: this.confirmForm.admin_notes,
          admin_user_id: this.adminAuth.currentUser?.id
        };
        const res = await api.post(`${API_ENDPOINTS.PRICING_ORDERS}/${this.selectedOrder.id}/confirm`, payload);
        if (res.success) {
          showToast(res.message || '入帳確認成功！', 'success');
          if (this.confirmModalInstance) this.confirmModalInstance.hide();
          await this.fetchOrders();
        } else {
          showToast(res.error || '確認入帳失敗', 'error');
        }
      } catch (err) {
        showToast(err.message || '操作失敗', 'error');
      } finally {
        this.processingOrder = false;
      }
    },
    openRejectModal(order) {
      this.selectedOrder = order;
      this.rejectForm = {
        admin_notes: ''
      };
      if (this.rejectModalInstance) {
        this.rejectModalInstance.show();
      }
    },
    async submitRejectOrder() {
      if (!this.selectedOrder) return;
      if (!this.rejectForm.admin_notes.trim()) {
        showToast('請填寫駁回原因', 'warning');
        return;
      }
      this.processingOrder = true;
      try {
        const payload = {
          admin_notes: this.rejectForm.admin_notes.trim(),
          admin_user_id: this.adminAuth.currentUser?.id
        };
        const res = await api.post(`${API_ENDPOINTS.PRICING_ORDERS}/${this.selectedOrder.id}/reject`, payload);
        if (res.success) {
          showToast(res.message || '已駁回訂單', 'info');
          if (this.rejectModalInstance) this.rejectModalInstance.hide();
          await this.fetchOrders();
        } else {
          showToast(res.error || '駁回失敗', 'error');
        }
      } catch (err) {
        showToast(err.message || '操作失敗', 'error');
      } finally {
        this.processingOrder = false;
      }
    },
    async handleDeleteOrder(order) {
      const ok = await showConfirm(`確定要刪除訂單【${order.order_no}】嗎？此動作將無法復原。`, '刪除訂單確認');
      if (!ok) return;

      try {
        await api.delete(`${API_ENDPOINTS.PRICING_ORDERS}/${order.id}`);
        showToast('訂單已刪除', 'success');
        await this.fetchOrders();
      } catch (err) {
        showToast(err.message || '刪除失敗', 'error');
      }
    },
    getOrderStatusBadgeClass(status) {
      switch (status) {
        case 'confirmed':
          return 'bg-success';
        case 'pending':
          return 'bg-warning text-dark fw-bold';
        case 'rejected':
          return 'bg-danger';
        default:
          return 'bg-secondary';
      }
    },
    formatOrderStatus(status) {
      switch (status) {
        case 'confirmed':
          return '已確認入帳';
        case 'pending':
          return '待確認';
        case 'rejected':
          return '已駁回';
        default:
          return status || '待處理';
      }
    },
    formatDateTime(val) {
      if (!val) return '';
      try {
        const d = new Date(val);
        if (isNaN(d.getTime())) return val;
        return d.toLocaleString('zh-TW', { hour12: false });
      } catch (e) {
        return val;
      }
    },

    // ---------------- 方案管理相關 ----------------
    async fetchPlansData() {
      this.loading = true;
      this.error = null;
      try {
        const res = await api.get(API_ENDPOINTS.PRICING, { params: { admin: 1 } });
        if (res.success) {
          this.plans = res.plans || [];
          if (res.notice) {
            this.noticeForm.title = res.notice.title || '學員報名與上課須知';
            this.noticeForm.content = res.notice.content || '';
          }
          if (res.bank_info) {
            this.bankForm = Object.assign({}, this.bankForm, res.bank_info);
          }
        } else {
          this.error = res.error || '載入價目表失敗';
        }
      } catch (err) {
        this.error = err.message || '無法連線至伺服器';
      } finally {
        this.loading = false;
      }
    },
    setPlanType(type) {
      this.form.plan_type = type;
      if (type === 'classes') {
        if (!this.form.unit || this.form.unit.includes('/ 月') || this.form.unit.includes('/ 季')) {
          this.form.unit = '/ 堂';
        }
        if (!this.form.classes_count) this.form.classes_count = 8;
      } else if (type === 'monthly_pass') {
        if (!this.form.unit || this.form.unit.includes('/ 堂')) {
          this.form.unit = '/ 月 (無限堂數)';
        }
        if (!this.form.validity_days) this.form.validity_days = 30;
        if (this.form.classes_count === undefined) this.form.classes_count = 0;
      } else if (type === 'membership_fee') {
        if (!this.form.unit || this.form.unit.includes('/ 堂') || this.form.unit.includes('/ 月')) {
          this.form.unit = '/ 年 (365天)';
        }
        if (!this.form.validity_days) this.form.validity_days = 365;
        if (this.form.classes_count === undefined) this.form.classes_count = 0;
      }
    },
    setValidityDays(days) {
      this.form.validity_days = days;
      if (days === 30) this.form.unit = '/ 月 (無限堂數)';
      else if (days === 60) this.form.unit = '/ 雙月 (無限堂數)';
      else if (days === 90) this.form.unit = '/ 季 (無限堂數)';
      else if (days === 180) this.form.unit = '/ 半年 (無限堂數)';
      else if (days === 365) this.form.unit = '/ 年 (無限堂數)';
    },
    openCreateModal() {
      this.editingId = null;
      this.form = {
        title: '',
        subtitle: '',
        price: '',
        unit: '/ 堂',
        plan_type: 'classes',
        classes_count: 8,
        validity_days: 30,
        original_price: '',
        sort_order: (this.plans.length > 0 ? Math.max(...this.plans.map(p => p.sort_order || 0)) + 1 : 1),
        is_popular: false,
        requires_membership: false,
        is_active: true,
        button_text: '買課',
        button_link: '/contact'
      };
      if (this.modalInstance) this.modalInstance.show();
    },
    openEditModal(plan) {
      this.editingId = plan.id;
      this.form = {
        title: plan.title,
        subtitle: plan.subtitle || '',
        price: plan.price,
        unit: plan.unit,
        plan_type: plan.plan_type || 'classes',
        classes_count: plan.classes_count ?? (plan.plan_type === 'classes' ? 1 : 0),
        validity_days: plan.validity_days || (plan.plan_type === 'membership_fee' ? 365 : (plan.plan_type === 'monthly_pass' ? 30 : 0)),
        original_price: plan.original_price || '',
        sort_order: plan.sort_order ?? 0,
        is_popular: !!plan.is_popular,
        requires_membership: !!plan.requires_membership,
        is_active: !!plan.is_active,
        button_text: plan.button_text || '買課',
        button_link: plan.button_link || '/contact'
      };
      if (this.modalInstance) this.modalInstance.show();
    },
    async handleSubmitPlan() {
      if (!this.form.title.trim()) {
        showToast('請填寫方案名稱', 'warning');
        return;
      }
      if (!this.form.price.trim()) {
        showToast('請填寫方案價格', 'warning');
        return;
      }
      if (!this.form.unit.trim()) {
        showToast('請填寫計費單位', 'warning');
        return;
      }

      this.submitting = true;
      try {
        const payload = {
          title: this.form.title.trim(),
          subtitle: this.form.subtitle.trim(),
          price: this.form.price.trim(),
          unit: this.form.unit.trim(),
          plan_type: this.form.plan_type,
          classes_count: this.form.plan_type === 'classes' ? (this.form.classes_count || 1) : (this.form.classes_count || 0),
          validity_days: this.form.plan_type === 'classes' ? 0 : (this.form.validity_days || (this.form.plan_type === 'membership_fee' ? 365 : 30)),
          original_price: this.form.original_price.trim() || null,
          sort_order: this.form.sort_order,
          is_popular: this.form.is_popular,
          requires_membership: this.form.plan_type === 'membership_fee' ? false : !!this.form.requires_membership,
          is_active: this.form.is_active,
          button_text: this.form.button_text.trim() || '買課',
          button_link: this.form.button_link.trim() || '/contact'
        };

        if (this.editingId) {
          await api.put(`${API_ENDPOINTS.PRICING}/${this.editingId}`, payload);
          showToast('價目方案更新成功！', 'success');
        } else {
          await api.post(API_ENDPOINTS.PRICING, payload);
          showToast('新價目方案已建立！', 'success');
        }

        if (this.modalInstance) this.modalInstance.hide();
        await this.fetchPlansData();
      } catch (err) {
        showToast(err.message || '操作失敗', 'error');
      } finally {
        this.submitting = false;
      }
    },
    async toggleActive(plan) {
      try {
        const res = await api.post(`${API_ENDPOINTS.PRICING}/${plan.id}/toggle-active`);
        plan.is_active = res.is_active;
        showToast(res.message || '狀態更新成功', 'success');
      } catch (err) {
        showToast(err.message || '切換狀態失敗', 'error');
      }
    },
    async togglePopular(plan) {
      try {
        const res = await api.post(`${API_ENDPOINTS.PRICING}/${plan.id}/toggle-popular`);
        plan.is_popular = res.is_popular;
        showToast(res.message || '熱門推薦狀態更新成功', 'success');
      } catch (err) {
        showToast(err.message || '切換失敗', 'error');
      }
    },
    async handleDelete(plan) {
      const ok = await showConfirm(`確定要刪除「${plan.title}」方案嗎？此動作將無法復原。`, '刪除方案確認');
      if (!ok) return;

      try {
        await api.delete(`${API_ENDPOINTS.PRICING}/${plan.id}`);
        showToast('方案已成功刪除', 'success');
        await this.fetchPlansData();
      } catch (err) {
        showToast(err.message || '刪除失敗', 'error');
      }
    },
    async saveNoticeSettings() {
      if (!this.noticeForm.title.trim()) {
        showToast('請填寫上課須知標題', 'warning');
        return;
      }

      this.savingNotice = true;
      try {
        await api.put(`${API_ENDPOINTS.PRICING}/notice`, {
          title: this.noticeForm.title.trim(),
          content: this.noticeForm.content.trim()
        });
        showToast('學員報名與上課須知已成功更新！', 'success');
      } catch (err) {
        showToast(err.message || '儲存失敗', 'error');
      } finally {
        this.savingNotice = false;
      }
    },

    // ---------------- 轉帳帳號相關 (僅系統管理員) ----------------
    async fetchBankInfo() {
      try {
        const res = await api.get(API_ENDPOINTS.PRICING_BANK_ACCOUNT);
        if (res.success && res.bank_info) {
          this.bankForm = Object.assign({}, this.bankForm, res.bank_info);
        }
      } catch (err) {
        console.error('查詢轉帳帳號失敗:', err);
      }
    },
    async saveBankAccount() {
      if (!this.isAdmin) {
        showToast('權限不足！只有「系統管理員（admin）」具備修改轉帳帳號之權限。', 'error');
        return;
      }
      if (!this.bankForm.bank_name.trim()) {
        showToast('請輸入銀行名稱', 'warning');
        return;
      }
      if (!this.bankForm.bank_code.trim()) {
        showToast('請輸入銀行代碼', 'warning');
        return;
      }
      if (!this.bankForm.bank_account.trim()) {
        showToast('請輸入轉帳帳號', 'warning');
        return;
      }
      if (!this.bankForm.bank_account_name.trim()) {
        showToast('請輸入戶名', 'warning');
        return;
      }

      this.savingBank = true;
      try {
        const payload = {
          admin_user_id: this.adminAuth.currentUser?.id,
          bank_name: this.bankForm.bank_name.trim(),
          bank_code: this.bankForm.bank_code.trim(),
          bank_account: this.bankForm.bank_account.trim(),
          bank_account_name: this.bankForm.bank_account_name.trim(),
          bank_notes: (this.bankForm.bank_notes || '').trim()
        };
        const res = await api.put(API_ENDPOINTS.PRICING_BANK_ACCOUNT, payload);
        if (res.success) {
          showToast(res.message || '工作室轉帳匯款帳號已成功更新！', 'success');
          if (res.bank_info) {
            this.bankForm = Object.assign({}, this.bankForm, res.bank_info);
          }
        } else {
          showToast(res.error || '儲存失敗', 'error');
        }
      } catch (err) {
        showToast(err.message || '儲存轉帳帳號失敗', 'error');
      } finally {
        this.savingBank = false;
      }
    }
  }
};
</script>

<style scoped>
.pricing-management {
  max-width: 1250px;
  margin: 0 auto;
}

.table > :not(caption) > * > * {
  padding: 1rem 0.85rem;
}
</style>