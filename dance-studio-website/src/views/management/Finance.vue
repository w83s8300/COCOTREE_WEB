<template>
  <div class="finance-management p-2 p-md-3">
    <!-- 頂部頁頭 -->
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
      <div>
        <h2 class="fw-bold mb-1 d-flex align-items-center">
          <i class="bi bi-cash-coin text-success me-2"></i>收支記帳管理
        </h2>
        <p class="text-muted small mb-0">
          即時記錄工作室各項營業收入（學費、單堂體驗、場地租借）與日常開銷（房租、水電、師資薪資、雜支耗材）。
        </p>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <button
          type="button"
          class="btn btn-outline-secondary d-flex align-items-center gap-1 shadow-sm"
          @click="exportCsv"
          :disabled="records.length === 0"
        >
          <i class="bi bi-download"></i>
          <span>匯出收支明細 (CSV)</span>
        </button>
        <button
          type="button"
          class="btn btn-success d-flex align-items-center gap-2 px-3 shadow-sm fw-bold"
          @click="openCreateModal('income')"
        >
          <i class="bi bi-plus-circle-fill fs-5"></i>
          <span>記一筆收支</span>
        </button>
      </div>
    </div>

    <!-- 頂部 4 大財務統計卡片 (KPI Summary) -->
    <div class="row g-3 mb-4">
      <!-- 1. 區間總收入 -->
      <div class="col-sm-6 col-xl-3">
        <div class="card border-0 shadow-sm rounded-4 h-100 overflow-hidden" style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);">
          <div class="card-body p-3 p-md-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="small fw-bold text-success text-uppercase">總收入 (Income)</span>
              <span class="badge bg-success bg-opacity-75 text-white rounded-pill px-2">
                {{ summary.income_count }} 筆
              </span>
            </div>
            <div class="fs-2 fw-bolder text-success mb-1">
              +NT$ {{ formatMoney(summary.total_income) }}
            </div>
            <div class="text-muted small">
              <i class="bi bi-arrow-up-right me-1 text-success"></i>所選區間累積進帳
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 區間總支出 -->
      <div class="col-sm-6 col-xl-3">
        <div class="card border-0 shadow-sm rounded-4 h-100 overflow-hidden" style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);">
          <div class="card-body p-3 p-md-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="small fw-bold text-danger text-uppercase">總支出 (Expense)</span>
              <span class="badge bg-danger bg-opacity-75 text-white rounded-pill px-2">
                {{ summary.expense_count }} 筆
              </span>
            </div>
            <div class="fs-2 fw-bolder text-danger mb-1">
              -NT$ {{ formatMoney(summary.total_expense) }}
            </div>
            <div class="text-muted small">
              <i class="bi bi-arrow-down-right me-1 text-danger"></i>所選區間開銷花費
            </div>
          </div>
        </div>
      </div>

      <!-- 3. 本期淨結餘 -->
      <div class="col-sm-6 col-xl-3">
        <div
          class="card border-0 shadow-sm rounded-4 h-100 overflow-hidden"
          :style="summary.net_profit >= 0
            ? 'background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);'
            : 'background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);'"
        >
          <div class="card-body p-3 p-md-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span
                class="small fw-bold text-uppercase"
                :class="summary.net_profit >= 0 ? 'text-primary' : 'text-danger'"
              >
                淨收益 (Net Profit)
              </span>
              <span
                class="badge rounded-pill px-2 fw-bold"
                :class="summary.net_profit >= 0 ? 'bg-primary text-white' : 'bg-danger text-white'"
              >
                {{ summary.net_profit >= 0 ? '盈餘' : '赤字' }}
              </span>
            </div>
            <div
              class="fs-2 fw-bolder mb-1"
              :class="summary.net_profit >= 0 ? 'text-primary' : 'text-danger'"
            >
              {{ summary.net_profit >= 0 ? '+' : '' }}NT$ {{ formatMoney(summary.net_profit) }}
            </div>
            <div class="text-muted small">
              利潤率：<strong>{{ profitMargin }}%</strong> (收入扣減支出)
            </div>
          </div>
        </div>
      </div>

      <!-- 4. 記帳筆數與收支平衡 -->
      <div class="col-sm-6 col-xl-3">
        <div class="card border-0 shadow-sm rounded-4 h-100 bg-white">
          <div class="card-body p-3 p-md-4 d-flex flex-column justify-content-between">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="small fw-bold text-muted text-uppercase">收支結構比例</span>
              <i class="bi bi-pie-chart-fill text-secondary fs-5"></i>
            </div>
            <div>
              <div class="progress mb-2" style="height: 10px;">
                <div
                  class="progress-bar bg-success"
                  role="progressbar"
                  :style="{ width: incomePercentage + '%' }"
                  :title="'收入 ' + incomePercentage + '%'"
                ></div>
                <div
                  class="progress-bar bg-danger"
                  role="progressbar"
                  :style="{ width: (100 - incomePercentage) + '%' }"
                  :title="'支出 ' + (100 - incomePercentage) + '%'"
                ></div>
              </div>
              <div class="d-flex justify-content-between small text-muted">
                <span><i class="bi bi-circle-fill text-success me-1" style="font-size: 8px;"></i>收入 {{ incomePercentage }}%</span>
                <span><i class="bi bi-circle-fill text-danger me-1" style="font-size: 8px;"></i>支出 {{ 100 - incomePercentage }}%</span>
              </div>
            </div>
            <div class="small text-muted mt-2 border-top pt-2">
              總記帳流水：<strong>{{ records.length }}</strong> 筆
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 收支結構佔比分析 (摺疊面板) -->
    <div class="card border-0 shadow-sm rounded-4 mb-4 overflow-hidden">
      <div
        class="card-header bg-white p-3 d-flex justify-content-between align-items-center"
        style="cursor: pointer;"
        @click="showBreakdown = !showBreakdown"
      >
        <span class="fw-bold d-flex align-items-center">
          <i class="bi bi-bar-chart-steps text-primary me-2"></i>
          分類排行與佔比分析 (錢花在哪裡？哪項最賺錢？)
        </span>
        <i class="bi" :class="showBreakdown ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
      </div>

      <div v-if="showBreakdown" class="card-body p-3 p-md-4 bg-light bg-opacity-50">
        <div class="row g-4">
          <!-- 收入排行 -->
          <div class="col-md-6 border-end-md">
            <h6 class="fw-bold text-success mb-3 d-flex align-items-center">
              <i class="bi bi-arrow-up-circle-fill me-2"></i>收入分類來源排行
            </h6>
            <div v-if="categoriesBreakdown.income.length === 0" class="text-muted small py-3 text-center">
              此期間尚無收入記錄
            </div>
            <div v-else class="d-flex flex-column gap-2">
              <div
                v-for="item in categoriesBreakdown.income"
                :key="item.category"
                class="bg-white p-2 px-3 rounded-3 border-0 shadow-sm"
              >
                <div class="d-flex justify-content-between align-items-center mb-1 small">
                  <span class="fw-bold text-dark">{{ item.category }}</span>
                  <span class="text-success fw-bold">+NT$ {{ formatMoney(item.total) }} ({{ item.percentage }}%)</span>
                </div>
                <div class="progress" style="height: 6px;">
                  <div
                    class="progress-bar bg-success"
                    role="progressbar"
                    :style="{ width: item.percentage + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 支出排行 -->
          <div class="col-md-6">
            <h6 class="fw-bold text-danger mb-3 d-flex align-items-center">
              <i class="bi bi-arrow-down-circle-fill me-2"></i>支出主要開銷排行
            </h6>
            <div v-if="categoriesBreakdown.expense.length === 0" class="text-muted small py-3 text-center">
              此期間尚無支出記錄
            </div>
            <div v-else class="d-flex flex-column gap-2">
              <div
                v-for="item in categoriesBreakdown.expense"
                :key="item.category"
                class="bg-white p-2 px-3 rounded-3 border-0 shadow-sm"
              >
                <div class="d-flex justify-content-between align-items-center mb-1 small">
                  <span class="fw-bold text-dark">{{ item.category }}</span>
                  <span class="text-danger fw-bold">-NT$ {{ formatMoney(item.total) }} ({{ item.percentage }}%)</span>
                </div>
                <div class="progress" style="height: 6px;">
                  <div
                    class="progress-bar bg-danger"
                    role="progressbar"
                    :style="{ width: item.percentage + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 篩選器與搜尋工具列 -->
    <div class="card border-0 shadow-sm rounded-4 mb-4">
      <div class="card-body p-3 p-md-4">
        <!-- 快捷日期按鈕列 -->
        <div class="d-flex flex-wrap align-items-center gap-2 mb-3">
          <span class="small fw-bold text-muted me-1">快捷時間：</span>
          <button
            type="button"
            class="btn btn-sm rounded-pill px-3"
            :class="datePreset === 'this_month' ? 'btn-primary' : 'btn-outline-secondary'"
            @click="applyDatePreset('this_month')"
          >
            本月 ({{ currentMonthLabel }})
          </button>
          <button
            type="button"
            class="btn btn-sm rounded-pill px-3"
            :class="datePreset === 'last_month' ? 'btn-primary' : 'btn-outline-secondary'"
            @click="applyDatePreset('last_month')"
          >
            上個月
          </button>
          <button
            type="button"
            class="btn btn-sm rounded-pill px-3"
            :class="datePreset === 'last_30_days' ? 'btn-primary' : 'btn-outline-secondary'"
            @click="applyDatePreset('last_30_days')"
          >
            近 30 天
          </button>
          <button
            type="button"
            class="btn btn-sm rounded-pill px-3"
            :class="datePreset === 'this_year' ? 'btn-primary' : 'btn-outline-secondary'"
            @click="applyDatePreset('this_year')"
          >
            今年度
          </button>
          <button
            type="button"
            class="btn btn-sm rounded-pill px-3"
            :class="datePreset === 'all' ? 'btn-primary' : 'btn-outline-secondary'"
            @click="applyDatePreset('all')"
          >
            全部歷史
          </button>
          <button
            type="button"
            class="btn btn-sm rounded-pill px-3"
            :class="datePreset === 'custom' ? 'btn-primary' : 'btn-outline-secondary'"
            @click="datePreset = 'custom'"
          >
            自訂區間
          </button>
        </div>

        <!-- 條件篩選組合 -->
        <div class="row g-2 align-items-end">
          <!-- 自訂起訖日期 (若選自訂或需要時) -->
          <div class="col-sm-6 col-md-3" v-if="datePreset === 'custom'">
            <label class="form-label small text-muted mb-1">開始日期</label>
            <input
              type="date"
              v-model="filters.start_date"
              class="form-control form-control-sm"
              @change="fetchRecords"
            />
          </div>
          <div class="col-sm-6 col-md-3" v-if="datePreset === 'custom'">
            <label class="form-label small text-muted mb-1">結束日期</label>
            <input
              type="date"
              v-model="filters.end_date"
              class="form-control form-control-sm"
              @change="fetchRecords"
            />
          </div>

          <!-- 收支類型 -->
          <div class="col-6 col-md-2">
            <label class="form-label small text-muted mb-1">收支類型</label>
            <select v-model="filters.type" class="form-select form-select-sm" @change="fetchRecords">
              <option value="all">全部類型</option>
              <option value="income">僅看收入 💚</option>
              <option value="expense">僅看支出 💔</option>
            </select>
          </div>

          <!-- 分類篩選 -->
          <div class="col-6 col-md-2">
            <label class="form-label small text-muted mb-1">分類類別</label>
            <select v-model="filters.category" class="form-select form-select-sm" @change="fetchRecords">
              <option value="">全部分類</option>
              <optgroup label="—— 收入分類 ——">
                <option v-for="cat in presetCategories.income" :key="'in-' + cat" :value="cat">{{ cat }}</option>
              </optgroup>
              <optgroup label="—— 支出分類 ——">
                <option v-for="cat in presetCategories.expense" :key="'ex-' + cat" :value="cat">{{ cat }}</option>
              </optgroup>
            </select>
          </div>

          <!-- 支付方式 -->
          <div class="col-6 col-md-2">
            <label class="form-label small text-muted mb-1">支付方式</label>
            <select v-model="filters.payment_method" class="form-select form-select-sm" @change="fetchRecords">
              <option value="">全部支付方式</option>
              <option value="現金">現金 (Cash)</option>
              <option value="銀行轉帳">銀行轉帳 / 匯款</option>
              <option value="信用卡">信用卡 (Card)</option>
              <option value="LINE Pay">LINE Pay / 行動支付</option>
              <option value="其他">其他方式</option>
            </select>
          </div>

          <!-- 關鍵字搜尋 -->
          <div class="col-6 col-md-3 flex-grow-1">
            <label class="form-label small text-muted mb-1">關鍵字搜尋</label>
            <div class="input-group input-group-sm">
              <input
                type="text"
                v-model="filters.search"
                class="form-control"
                placeholder="搜尋摘要、備註、經手人..."
                @keyup.enter="fetchRecords"
              />
              <button class="btn btn-outline-secondary" type="button" @click="fetchRecords">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>

          <!-- 重設按鈕 -->
          <div class="col-auto">
            <button
              type="button"
              class="btn btn-link btn-sm text-secondary text-decoration-none"
              @click="resetFilters"
              title="清除所有篩選條件"
            >
              <i class="bi bi-arrow-counterclockwise me-1"></i>重設
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 收支記錄明細列表 -->
    <div class="card border-0 shadow-sm rounded-4 overflow-hidden mb-4">
      <div class="card-header bg-white p-3 d-flex justify-content-between align-items-center">
        <span class="fw-bold d-flex align-items-center">
          <i class="bi bi-card-checklist text-primary me-2"></i>
          收支明細清單
        </span>
        <span class="badge bg-secondary rounded-pill">共 {{ records.length }} 筆記錄</span>
      </div>

      <!-- 載入中狀態 -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入中...</span>
        </div>
        <p class="mt-2 text-muted small">正在計算與讀取收支明細...</p>
      </div>

      <!-- 錯誤狀態 -->
      <div v-else-if="error" class="alert alert-danger m-3 d-flex justify-content-between align-items-center">
        <span><i class="bi bi-exclamation-triangle-fill me-2"></i>{{ error }}</span>
        <button class="btn btn-outline-danger btn-sm" @click="fetchRecords">重新嘗試</button>
      </div>

      <!-- 空資料狀態 -->
      <div v-else-if="records.length === 0" class="text-center py-5 text-muted">
        <i class="bi bi-receipt-cutoff fs-1 text-muted opacity-50 d-block mb-3"></i>
        <h6 class="fw-bold">所選篩選區間內尚無收支記錄</h6>
        <p class="small text-muted mb-3">點擊下方按鈕，立即記錄第一筆工作室收入或營運支出！</p>
        <button type="button" class="btn btn-success btn-sm rounded-pill px-4 shadow-sm fw-bold" @click="openCreateModal('income')">
          <i class="bi bi-plus-lg me-1"></i>立即記一筆
        </button>
      </div>

      <!-- 資料表格 -->
      <div v-else class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light small text-muted text-uppercase">
            <tr>
              <th scope="col" style="width: 110px;">日期</th>
              <th scope="col" style="width: 90px;">類型</th>
              <th scope="col" style="width: 140px;">分類</th>
              <th scope="col">摘要與備註</th>
              <th scope="col" style="width: 120px;">支付方式</th>
              <th scope="col" style="width: 110px;">經手人</th>
              <th scope="col" class="text-end" style="width: 140px;">金額 (NT$)</th>
              <th scope="col" class="text-center" style="width: 110px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in records" :key="item.id">
              <!-- 日期 -->
              <td class="font-monospace small fw-bold text-dark">
                {{ item.record_date }}
              </td>

              <!-- 類型 -->
              <td>
                <span
                  class="badge rounded-pill px-2 py-1"
                  :class="item.type === 'income' ? 'bg-success bg-opacity-10 text-success border border-success-subtle' : 'bg-danger bg-opacity-10 text-danger border border-danger-subtle'"
                >
                  <i class="bi me-1" :class="item.type === 'income' ? 'bi-plus-circle-fill' : 'bi-dash-circle-fill'"></i>
                  {{ item.type === 'income' ? '收入' : '支出' }}
                </span>
              </td>

              <!-- 分類 -->
              <td>
                <span class="badge bg-light text-dark border px-2 py-1 small">
                  {{ item.category }}
                </span>
              </td>

              <!-- 摘要與備註 -->
              <td>
                <div class="fw-bold text-dark">{{ item.description }}</div>
                <div v-if="item.note" class="text-muted small">
                  <i class="bi bi-chat-left-dots text-secondary me-1"></i>{{ item.note }}
                </div>
                <div v-if="item.invoice_number" class="text-secondary small font-monospace">
                  <i class="bi bi-receipt me-1"></i>單號: {{ item.invoice_number }}
                </div>
              </td>

              <!-- 支付方式 -->
              <td class="small">
                <span class="badge bg-secondary bg-opacity-10 text-secondary border">
                  {{ item.payment_method }}
                </span>
              </td>

              <!-- 經手人 -->
              <td class="small text-muted">
                {{ item.handler_name || '-' }}
              </td>

              <!-- 金額 -->
              <td class="text-end font-monospace">
                <span
                  class="fs-6 fw-bold"
                  :class="item.type === 'income' ? 'text-success' : 'text-danger'"
                >
                  {{ item.type === 'income' ? '+' : '-' }}{{ formatMoney(item.amount) }}
                </span>
              </td>

              <!-- 操作按鈕 -->
              <td class="text-center">
                <div class="btn-group btn-group-sm">
                  <button
                    type="button"
                    class="btn btn-outline-primary"
                    @click="openEditModal(item)"
                    title="編輯此筆記錄"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-danger"
                    @click="deleteRecord(item)"
                    title="刪除此筆記錄"
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

    <!-- ==================== 新增 / 編輯收支 Modal ==================== -->
    <div
      class="modal fade"
      id="financeRecordModal"
      tabindex="-1"
      aria-labelledby="financeRecordModalLabel"
      aria-hidden="true"
      ref="financeRecordModal"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow rounded-4 overflow-hidden">
          <!-- Modal 頂部 (依收入/支出動態切換色彩) -->
          <div
            class="modal-header text-white px-4 py-3"
            :class="form.type === 'income' ? 'bg-success' : 'bg-danger'"
          >
            <h5 class="modal-title fw-bold d-flex align-items-center" id="financeRecordModalLabel">
              <i class="bi me-2" :class="editingId ? 'bi-pencil-square' : (form.type === 'income' ? 'bi-wallet2' : 'bi-credit-card')"></i>
              {{ editingId ? '編輯收支記錄' : (form.type === 'income' ? '記一筆收入 (Income)' : '記一筆支出 (Expense)') }}
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>

          <div class="modal-body p-4">
            <form @submit.prevent="submitForm" id="financeForm">
              <!-- 1. 類型選擇 (收入 / 支出 大按鈕切換) -->
              <div class="mb-3">
                <label class="form-label small fw-bold text-muted mb-2">收支類型</label>
                <div class="btn-group w-100 p-1 bg-light rounded-pill border" role="group">
                  <button
                    type="button"
                    class="btn rounded-pill fw-bold"
                    :class="form.type === 'income' ? 'btn-success text-white shadow-sm' : 'btn-light text-muted'"
                    @click="switchType('income')"
                  >
                    <i class="bi bi-plus-circle-fill me-1"></i>收入 (進帳)
                  </button>
                  <button
                    type="button"
                    class="btn rounded-pill fw-bold"
                    :class="form.type === 'expense' ? 'btn-danger text-white shadow-sm' : 'btn-light text-muted'"
                    @click="switchType('expense')"
                  >
                    <i class="bi bi-dash-circle-fill me-1"></i>支出 (開銷)
                  </button>
                </div>
              </div>

              <!-- 2. 金額 (醒目大字體) -->
              <div class="mb-3">
                <label for="recordAmount" class="form-label small fw-bold text-muted">
                  金額 (NT$) <span class="text-danger">*</span>
                </label>
                <div class="input-group input-group-lg">
                  <span class="input-group-text bg-white fw-bold" :class="form.type === 'income' ? 'text-success' : 'text-danger'">
                    {{ form.type === 'income' ? '+' : '-' }}$
                  </span>
                  <input
                    type="number"
                    id="recordAmount"
                    v-model.number="form.amount"
                    class="form-control fw-bold font-monospace"
                    :class="form.type === 'income' ? 'text-success' : 'text-danger'"
                    placeholder="請輸入金額，例如: 3200"
                    min="1"
                    step="1"
                    required
                  />
                </div>
              </div>

              <!-- 3. 收支日期與支付方式 (二合一) -->
              <div class="row g-2 mb-3">
                <div class="col-6">
                  <label for="recordDate" class="form-label small fw-bold text-muted">
                    收支日期 <span class="text-danger">*</span>
                  </label>
                  <input
                    type="date"
                    id="recordDate"
                    v-model="form.record_date"
                    class="form-control"
                    required
                  />
                </div>
                <div class="col-6">
                  <label for="paymentMethod" class="form-label small fw-bold text-muted">支付方式</label>
                  <select id="paymentMethod" v-model="form.payment_method" class="form-select">
                    <option value="現金">現金 (Cash)</option>
                    <option value="銀行轉帳">銀行轉帳 / 匯款</option>
                    <option value="信用卡">信用卡 (Card)</option>
                    <option value="LINE Pay">LINE Pay / 行動支付</option>
                    <option value="其他">其他</option>
                  </select>
                </div>
              </div>

              <!-- 4. 收支分類 -->
              <div class="mb-3">
                <label for="recordCategory" class="form-label small fw-bold text-muted d-flex justify-content-between">
                  <span>分類類別 <span class="text-danger">*</span></span>
                  <span class="small text-muted">點擊下方快捷標籤可一鍵帶入</span>
                </label>
                <input
                  type="text"
                  id="recordCategory"
                  v-model="form.category"
                  class="form-control mb-2"
                  placeholder="請選擇下方標籤或自行輸入分類名稱"
                  required
                />
                <!-- 快捷常用分類標籤 -->
                <div class="d-flex flex-wrap gap-1">
                  <button
                    type="button"
                    v-for="cat in currentPresets"
                    :key="cat"
                    class="btn btn-xs py-1 px-2 rounded-pill small transition-all"
                    :class="form.category === cat ? (form.type === 'income' ? 'btn-success text-white' : 'btn-danger text-white') : 'btn-outline-secondary'"
                    @click="form.category = cat"
                  >
                    {{ cat }}
                  </button>
                </div>
              </div>

              <!-- 5. 摘要說明 -->
              <div class="mb-3">
                <label for="recordDescription" class="form-label small fw-bold text-muted">
                  摘要說明 <span class="text-danger">*</span>
                </label>
                <input
                  type="text"
                  id="recordDescription"
                  v-model="form.description"
                  class="form-control"
                  placeholder="例如: 10月份教室房租、王小明購買20堂包套"
                  maxlength="200"
                  required
                />
              </div>

              <!-- 6. 詳細備註與發票單號 (折疊或選填) -->
              <div class="row g-2 mb-2">
                <div class="col-sm-6">
                  <label for="invoiceNumber" class="form-label small fw-bold text-muted">發票 / 收據號碼 (選填)</label>
                  <input
                    type="text"
                    id="invoiceNumber"
                    v-model="form.invoice_number"
                    class="form-control form-control-sm"
                    placeholder="如: AB-12345678"
                  />
                </div>
                <div class="col-sm-6">
                  <label for="handlerName" class="form-label small fw-bold text-muted">經手人 / 記錄人員</label>
                  <input
                    type="text"
                    id="handlerName"
                    v-model="form.handler_name"
                    class="form-control form-control-sm"
                    placeholder="經手工作人員姓名"
                  />
                </div>
              </div>

              <div class="mb-1">
                <label for="recordNote" class="form-label small fw-bold text-muted">詳細備註 (選填)</label>
                <textarea
                  id="recordNote"
                  v-model="form.note"
                  class="form-control form-control-sm"
                  rows="2"
                  placeholder="補充細節說明 (如: 匯款末5碼、發票已開、設備型號等)..."
                ></textarea>
              </div>
            </form>
          </div>

          <div class="modal-footer bg-light px-4 py-3">
            <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">
              取消
            </button>
            <button
              type="submit"
              form="financeForm"
              class="btn rounded-pill px-4 shadow-sm fw-bold d-flex align-items-center gap-1"
              :class="form.type === 'income' ? 'btn-success' : 'btn-danger'"
              :disabled="submitting"
            >
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-check2-circle fs-5"></i>
              <span>{{ editingId ? '儲存變更' : '確認送出記帳' }}</span>
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
import { useAdminAuth } from '@/utils/adminAuth';
import { showToast } from '@/utils/toast';
import { showConfirm } from '@/utils/dialog';

export default {
  name: 'Finance',
  data() {
    return {
      adminAuth: useAdminAuth(),
      records: [],
      loading: false,
      error: null,
      submitting: false,
      showBreakdown: true,
      modalInstance: null,
      editingId: null,

      // 快速預設分類庫
      presetCategories: {
        income: [
          '學費 / 堂數購買',
          '單堂體驗費',
          '場地租借',
          '舞蹈服飾 / 周邊',
          '商演活動 / 編舞',
          '其他收入'
        ],
        expense: [
          '師資授課薪資',
          '櫃檯 / 行政薪資',
          '教室租金 / 管理費',
          '水電瓦斯網路費',
          '舞蹈設備 / 音響修繕',
          '行銷宣傳 / 廣告費',
          '耗材與日常雜支',
          '其他支出'
        ]
      },

      // 統計數據
      summary: {
        total_income: 0,
        total_expense: 0,
        net_profit: 0,
        income_count: 0,
        expense_count: 0
      },
      categoriesBreakdown: {
        income: [],
        expense: []
      },

      // 日期快捷設定
      datePreset: 'this_month',

      // 查詢篩選條件
      filters: {
        type: 'all',
        category: '',
        payment_method: '',
        search: '',
        start_date: '',
        end_date: ''
      },

      // 彈窗表單
      form: {
        type: 'income',
        category: '學費 / 堂數購買',
        amount: null,
        record_date: '',
        payment_method: '現金',
        description: '',
        note: '',
        invoice_number: '',
        handler_name: ''
      }
    };
  },
  computed: {
    currentMonthLabel() {
      const d = new Date();
      return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}`;
    },
    currentPresets() {
      return this.presetCategories[this.form.type] || [];
    },
    incomePercentage() {
      const total = this.summary.total_income + this.summary.total_expense;
      if (total === 0) return 50;
      return Math.round((this.summary.total_income / total) * 100);
    },
    profitMargin() {
      if (this.summary.total_income === 0) return 0;
      return Math.round((this.summary.net_profit / this.summary.total_income) * 100);
    }
  },
  mounted() {
    if (this.$refs.financeRecordModal) {
      this.modalInstance = new Modal(this.$refs.financeRecordModal);
    }
    // 預設套用「本月」日期區間並讀取
    this.applyDatePreset('this_month');
  },
  beforeUnmount() {
    if (this.modalInstance) {
      this.modalInstance.dispose();
    }
  },
  methods: {
    formatMoney(val) {
      if (val === null || val === undefined || isNaN(val)) return '0';
      return Number(val).toLocaleString('zh-TW', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
    },

    applyDatePreset(preset) {
      this.datePreset = preset;
      const today = new Date();

      if (preset === 'this_month') {
        const y = today.getFullYear();
        const m = today.getMonth();
        const start = new Date(y, m, 1);
        const end = new Date(y, m + 1, 0);
        this.filters.start_date = this.formatDate(start);
        this.filters.end_date = this.formatDate(end);
      } else if (preset === 'last_month') {
        const y = today.getFullYear();
        const m = today.getMonth() - 1;
        const start = new Date(y, m, 1);
        const end = new Date(y, m + 1, 0);
        this.filters.start_date = this.formatDate(start);
        this.filters.end_date = this.formatDate(end);
      } else if (preset === 'last_30_days') {
        const end = new Date();
        const start = new Date();
        start.setDate(today.getDate() - 30);
        this.filters.start_date = this.formatDate(start);
        this.filters.end_date = this.formatDate(end);
      } else if (preset === 'this_year') {
        const y = today.getFullYear();
        this.filters.start_date = `${y}-01-01`;
        this.filters.end_date = `${y}-12-31`;
      } else if (preset === 'all') {
        this.filters.start_date = '';
        this.filters.end_date = '';
      }
      this.fetchRecords();
    },

    formatDate(d) {
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${y}-${m}-${day}`;
    },

    resetFilters() {
      this.filters = {
        type: 'all',
        category: '',
        payment_method: '',
        search: '',
        start_date: '',
        end_date: ''
      };
      this.applyDatePreset('this_month');
    },

    async fetchRecords() {
      this.loading = true;
      this.error = null;
      try {
        const params = {};
        if (this.filters.start_date) params.start_date = this.filters.start_date;
        if (this.filters.end_date) params.end_date = this.filters.end_date;
        if (this.filters.type && this.filters.type !== 'all') params.type = this.filters.type;
        if (this.filters.category) params.category = this.filters.category;
        if (this.filters.payment_method) params.payment_method = this.filters.payment_method;
        if (this.filters.search.trim()) params.search = this.filters.search.trim();

        const res = await api.get('/finance/records', { params });
        if (res && res.success) {
          this.records = res.records || [];
          this.summary = res.summary || {
            total_income: 0,
            total_expense: 0,
            net_profit: 0,
            income_count: 0,
            expense_count: 0
          };
          this.categoriesBreakdown = res.categories_breakdown || { income: [], expense: [] };
        }
      } catch (err) {
        console.error('讀取收支記錄失敗:', err);
        this.error = err.message || '讀取收支記錄失敗，請稍後再試';
      } finally {
        this.loading = false;
      }
    },

    switchType(type) {
      this.form.type = type;
      // 自動切換為該類型的第一個常用分類 (若當前分類非該類型)
      if (this.presetCategories && this.presetCategories[type] && !this.presetCategories[type].includes(this.form.category)) {
        this.form.category = this.presetCategories[type][0];
      }
    },

    openCreateModal(defaultType = 'income') {
      const type = (typeof defaultType === 'string' && (defaultType === 'income' || defaultType === 'expense'))
        ? defaultType
        : 'income';
      this.editingId = null;
      const todayStr = this.formatDate(new Date());
      const currentUserName = this.adminAuth.currentUser?.name || '系統管理員';
      const defaultCategory = (this.presetCategories && this.presetCategories[type] && this.presetCategories[type][0])
        ? this.presetCategories[type][0]
        : '學費 / 堂數購買';

      this.form = {
        type: type,
        category: defaultCategory,
        amount: null,
        record_date: todayStr,
        payment_method: '現金',
        description: '',
        note: '',
        invoice_number: '',
        handler_name: currentUserName
      };
      if (this.modalInstance) {
        this.modalInstance.show();
      }
    },

    openEditModal(item) {
      this.editingId = item.id;
      this.form = {
        type: item.type,
        category: item.category,
        amount: item.amount,
        record_date: item.record_date,
        payment_method: item.payment_method,
        description: item.description,
        note: item.note || '',
        invoice_number: item.invoice_number || '',
        handler_name: item.handler_name || ''
      };
      if (this.modalInstance) {
        this.modalInstance.show();
      }
    },

    async submitForm() {
      if (!this.form.amount || this.form.amount <= 0) {
        showToast('請輸入大於 0 的金額', 'warning');
        return;
      }
      if (!this.form.category.trim()) {
        showToast('請選擇或填寫收支分類', 'warning');
        return;
      }
      if (!this.form.description.trim()) {
        showToast('請填寫摘要說明', 'warning');
        return;
      }

      this.submitting = true;
      try {
        const payload = {
          type: this.form.type,
          category: this.form.category.trim(),
          amount: this.form.amount,
          record_date: this.form.record_date,
          payment_method: this.form.payment_method,
          description: this.form.description.trim(),
          note: this.form.note.trim(),
          invoice_number: this.form.invoice_number.trim(),
          handler_name: this.form.handler_name.trim()
        };

        if (this.editingId) {
          await api.put(`/finance/records/${this.editingId}`, payload);
          showToast('收支記錄已成功更新！', 'success');
        } else {
          await api.post('/finance/records', payload);
          showToast('收支記錄已成功建立！', 'success');
        }

        if (this.modalInstance) {
          this.modalInstance.hide();
        }
        this.fetchRecords();
      } catch (err) {
        showToast(err.message || '儲存收支記錄失敗', 'danger');
      } finally {
        this.submitting = false;
      }
    },

    async deleteRecord(item) {
      const typeLabel = item.type === 'income' ? '收入' : '支出';
      const confirmed = await showConfirm(
        `確定要刪除這筆【${typeLabel}】記錄嗎？\n\n日期：${item.record_date}\n項目：${item.description}\n金額：NT$ ${this.formatMoney(item.amount)}`
      );
      if (!confirmed) return;

      try {
        await api.delete(`/finance/records/${item.id}`);
        showToast('該筆收支記錄已刪除', 'info');
        this.fetchRecords();
      } catch (err) {
        showToast(err.message || '刪除失敗', 'danger');
      }
    },

    exportCsv() {
      if (this.records.length === 0) {
        showToast('目前無資料可供匯出', 'warning');
        return;
      }

      const headers = ['流水號', '日期', '收支類型', '分類', '摘要說明', '金額 (NT$)', '支付方式', '經手人', '發票或單號', '備註'];
      const rows = this.records.map(r => [
        r.id,
        r.record_date,
        r.type === 'income' ? '收入' : '支出',
        `"${(r.category || '').replace(/"/g, '""')}"`,
        `"${(r.description || '').replace(/"/g, '""')}"`,
        r.type === 'income' ? r.amount : -r.amount,
        `"${(r.payment_method || '').replace(/"/g, '""')}"`,
        `"${(r.handler_name || '').replace(/"/g, '""')}"`,
        `"${(r.invoice_number || '').replace(/"/g, '""')}"`,
        `"${(r.note || '').replace(/"/g, '""')}"`
      ]);

      const csvContent = '\uFEFF' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `DanceStudio_收支明細表_${this.formatDate(new Date())}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast('收支明細報表 CSV 匯出完成！', 'success');
    }
  }
};
</script>

<style scoped>
.finance-management {
  max-width: 1400px;
  margin: 0 auto;
}

.border-end-md {
  border-right: 1px solid #dee2e6;
}

@media (max-width: 767.98px) {
  .border-end-md {
    border-right: none;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 1.5rem;
  }
}
</style>

