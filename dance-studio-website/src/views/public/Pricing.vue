<template>
  <div class="pricing-page">
    <!-- 1. Banner -->
    <PageBanner image="https://picsum.photos/1920/500?random=35" title="課程價目表 / PRICING" />

    <!-- 2. Pricing Cards -->
    <div class="container my-5">
      <!-- 載入中骨架/轉圈 (若尚無資料時顯示) -->
      <div v-if="loading && plans.length === 0" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">載入價目表中...</span>
        </div>
        <p class="mt-2 text-muted">正在載入最新價目方案...</p>
      </div>

      <div v-else class="row justify-content-center">
        <div
          class="col-lg-3 col-md-6 mb-4"
          v-for="plan in plans"
          :key="plan.id || plan.title"
          data-aos="fade-up"
        >
          <div
            class="card text-center h-100 shadow-sm pricing-card"
            :class="{ 'border-primary ring-popular': isPlanPopular(plan) }"
          >
            <div
              class="card-header py-3"
              :class="isPlanPopular(plan) ? 'bg-primary text-white' : 'bg-light'"
            >
              <span v-if="isPlanPopular(plan)" class="badge bg-warning text-dark mb-1 fw-bold">
                <i class="bi bi-star-fill me-1"></i>熱門推薦
              </span>
              <h4 class="my-0 fw-bold">{{ plan.title }}</h4>
              <small v-if="plan.subtitle" class="d-block mt-1 opacity-75 small">
                {{ plan.subtitle }}
              </small>
            </div>
            <div class="card-body d-flex flex-column justify-content-between p-4">
              <div class="pricing-header my-auto py-3">
                <del v-if="plan.original_price" class="text-muted small d-block mb-1">
                  原價 {{ plan.original_price }}
                </del>
                <h2 class="card-title pricing-card-title fw-bold text-primary mb-1">
                  {{ plan.price }}
                </h2>
                <span class="text-muted fs-6">{{ plan.unit }}</span>
                <div v-if="plan.plan_type === 'membership_fee'" class="mt-2">
                  <span class="badge border px-2 py-1" style="background-color: #fef3c7; color: #b45309; border-color: #fcd34d !important;">
                    <i class="bi bi-award me-1"></i>會員年費 ({{ plan.validity_days || 365 }} 天資格)
                  </span>
                  <span v-if="plan.classes_count > 0" class="badge bg-light text-secondary border small ms-1">
                    +{{ plan.classes_count }} 堂贈課
                  </span>
                </div>
                <div v-else-if="plan.plan_type === 'monthly_pass'" class="mt-2">
                  <span class="badge border px-2 py-1" style="background-color: #f3e8ff; color: #7e22ce; border-color: #d8b4fe !important;">
                    <i class="bi bi-calendar-check me-1"></i>月費 ({{ plan.validity_days || 30 }} 天暢跳)
                  </span>
                  <span v-if="plan.classes_count > 0" class="badge bg-light text-secondary border small ms-1">
                    +{{ plan.classes_count }} 堂贈課
                  </span>
                </div>
                <div v-else-if="plan.classes_count" class="mt-2">
                  <span class="badge bg-light text-secondary border small">
                    含 {{ plan.classes_count }} 堂課
                  </span>
                </div>
                <div v-if="plan.requires_membership" class="mt-2">
                  <span class="badge border bg-warning-subtle text-dark border-warning px-2 py-1" style="font-size: 0.78rem;">
                    <i class="bi bi-shield-lock-fill text-warning me-1"></i>限有效年度會員購買
                  </span>
                </div>
              </div>

              <!-- 買課按鈕 -->
              <div class="mt-3">
                <button
                  type="button"
                  class="btn w-100 py-2 fw-bold d-flex align-items-center justify-content-center gap-1"
                  :class="isPlanPopular(plan) ? 'btn-primary shadow-sm' : 'btn-outline-primary'"
                  @click="handleBuyClick(plan)"
                >
                  <i class="bi bi-cart-plus"></i>
                  <span>{{ plan.button_text || '買課' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Important Notes -->
      <div
        v-if="notice.items && notice.items.length > 0"
        class="notes-section mt-5 p-4 bg-light rounded text-start shadow-sm border"
        data-aos="fade-up"
      >
        <h4 class="fw-bold mb-3 text-dark">
          <i class="bi bi-info-circle-fill text-primary me-2"></i>{{ notice.title }}
        </h4>
        <ul class="lh-lg mb-0 text-secondary">
          <li v-for="(item, nIdx) in notice.items" :key="nIdx" class="mb-1">
            {{ item }}
          </li>
        </ul>
      </div>
    </div>

    <!-- 4. 買課確認與銀行後 5 碼輸入 Modal -->
    <div
      class="modal fade"
      id="buyCourseModal"
      tabindex="-1"
      aria-labelledby="buyCourseModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content shadow-lg border-0 rounded-4">
          <div class="modal-header bg-light border-bottom">
            <h5 class="modal-title fw-bold text-dark" id="buyCourseModalLabel">
              <i class="bi bi-bag-check-fill text-primary me-2"></i>確認購買課程方案
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4" v-if="selectedPlan">
            <!-- 方案摘要卡片 -->
            <div class="p-3 bg-light rounded-3 border mb-3">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="text-muted small">選購方案</span>
                <span class="badge bg-primary fs-6">{{ selectedPlan.price }}</span>
              </div>
              <div class="fw-bold fs-5 text-dark">{{ selectedPlan.title }}</div>
              <div class="text-muted small">
                {{ selectedPlan.unit }}
                <span v-if="selectedPlan.plan_type === 'membership_fee'" class="ms-1 fw-bold text-warning">
                  (確認後自動展延「會員年費到期日」+{{ selectedPlan.validity_days || 365 }} 天)
                </span>
                <span v-else-if="selectedPlan.plan_type === 'monthly_pass'" class="ms-1 fw-bold text-primary">
                  (確認後自動展延「月費暢跳到期日」+{{ selectedPlan.validity_days || 30 }} 天，期間免扣堂數)
                </span>
                <span v-else-if="selectedPlan.classes_count" class="ms-1 fw-bold text-success">
                  (確認後自動增加 {{ selectedPlan.classes_count }} 堂課)
                </span>
              </div>
            </div>

            <!-- 學員資訊卡 -->
            <div class="d-flex justify-content-between align-items-center p-2 px-3 bg-white border rounded-3 mb-3 small">
              <div>
                <span class="text-muted me-1">學員：</span>
                <strong class="text-dark">{{ currentStudent?.name }}</strong>
                <span class="text-muted ms-2">({{ currentStudent?.phone }})</span>
              </div>
              <div>
                <span class="text-muted">目前剩餘：</span>
                <strong class="text-primary">{{ currentStudent?.remaining_classes ?? 0 }} 堂</strong>
              </div>
            </div>

            <!-- 年費會員資格檢核警示 -->
            <div v-if="selectedPlan?.requires_membership" class="mb-3">
              <div v-if="hasActiveMembership" class="alert alert-success py-2 px-3 small mb-0 d-flex align-items-center rounded-3 border-success-subtle shadow-sm">
                <i class="bi bi-shield-check fs-5 me-2 text-success"></i>
                <div>
                  <strong class="text-success">會員年費資格檢核通過</strong>：年費有效至 {{ currentStudent?.membership_expiry ? currentStudent.membership_expiry.split('T')[0] : '有效中' }}
                </div>
              </div>
              <div v-else class="alert alert-warning p-3 small mb-0 rounded-3 border-warning shadow-sm">
                <div class="d-flex align-items-start">
                  <i class="bi bi-shield-exclamation fs-3 me-2 text-warning flex-shrink-0"></i>
                  <div>
                    <h6 class="fw-bold mb-1 text-dark">此方案限定「會員年費」有效學員購買</h6>
                    <p class="mb-2 text-secondary">
                      您目前的會員年費狀態為：
                      <strong class="text-danger">{{ currentStudent?.membership_expiry ? `已於 ${currentStudent.membership_expiry.split('T')[0]} 到期` : '尚未開通年費' }}</strong>。
                      本方案為正式年度會員專屬特惠，請先繳交或續約「會員年費」即可下單購買！
                    </p>
                    <button
                      type="button"
                      class="btn btn-warning btn-sm fw-bold d-inline-flex align-items-center gap-1 shadow-sm"
                      @click="switchToMembershipFeePlan"
                    >
                      <i class="bi bi-award-fill"></i>
                      <span>改選購買「會員年費」($1,200/年)</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 匯款轉帳帳號資訊 -->
            <div class="p-3 bg-primary-subtle text-primary-emphasis rounded-3 border border-primary-subtle mb-3 small">
              <div class="fw-bold mb-1">
                <i class="bi bi-bank me-1"></i>工作室轉帳匯款帳號資訊：
              </div>
              <div class="font-monospace lh-base">
                銀行：國泰世華銀行 (013)<br>
                帳號：<strong>012-34-567890-1</strong><br>
                戶名：Dance Studio 舞蹈工作室
              </div>
              <div class="text-muted mt-2" style="font-size: 0.8rem;">
                * 請先完成匯款後，於下方填寫您的轉帳帳號後 5 碼，以便工作人員核帳開通堂數。
              </div>
            </div>

            <!-- 購課表單 -->
            <form @submit.prevent="submitBuyOrder">
              <!-- 銀行後 5 碼 -->
              <div class="mb-3">
                <label class="form-label fw-bold d-flex justify-content-between align-items-center">
                  <span>轉帳銀行後 5 碼 <span class="text-danger">*</span></span>
                  <span v-if="currentStudent?.bank_last_5" class="badge bg-success-subtle text-success small fw-normal">
                    已自動帶入設定
                  </span>
                </label>
                <div class="input-group">
                  <span class="input-group-text bg-light text-muted">
                    <i class="bi bi-credit-card-2-front"></i>
                  </span>
                  <input
                    type="text"
                    v-model.trim="purchaseForm.bank_last_5"
                    class="form-control font-monospace fs-5"
                    placeholder="請輸入轉帳帳號後 5 碼 (例如：88990)"
                    maxlength="10"
                    required
                  />
                </div>
                <small class="text-muted">供工作室對帳確認您的匯款款項</small>
              </div>

              <!-- 記住此銀行後 5 碼 -->
              <div class="form-check mb-3">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="saveBankInfoCheck"
                  v-model="purchaseForm.save_bank_info"
                />
                <label class="form-check-label small text-secondary" for="saveBankInfoCheck">
                  同步將此帳號設為我的常用銀行後 5 碼（下次買課自動帶入）
                </label>
              </div>

              <!-- 備註 -->
              <div class="mb-3">
                <label class="form-label small fw-bold">買課備註說明 (選填)</label>
                <input
                  type="text"
                  v-model.trim="purchaseForm.notes"
                  class="form-control form-control-sm"
                  placeholder="例如：已於 10/26 晚上轉帳、轉帳戶名等"
                />
              </div>

              <div class="d-grid gap-2 mt-4">
                <button
                  type="submit"
                  class="btn py-2 fw-bold d-flex align-items-center justify-content-center gap-2 shadow-sm"
                  :class="isMembershipRestricted ? 'btn-secondary opacity-75' : 'btn-primary'"
                  :disabled="submittingOrder || isMembershipRestricted"
                >
                  <span v-if="submittingOrder" class="spinner-border spinner-border-sm" role="status"></span>
                  <template v-else-if="isMembershipRestricted">
                    <i class="bi bi-shield-lock-fill"></i>
                    <span>限定有效會員年費資格</span>
                  </template>
                  <template v-else>
                    <i class="bi bi-send-check-fill"></i>
                    <span>確認送出購課訂單</span>
                  </template>
                </button>
                <button type="button" class="btn btn-light btn-sm text-muted" data-bs-dismiss="modal">
                  取消
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
import PageBanner from '@/components/PageBanner.vue';
import api, { API_ENDPOINTS } from '@/utils/api';
import { useStudentAuth } from '@/utils/auth';
import { showToast } from '@/utils/toast';
import { Modal } from 'bootstrap';

export default {
  name: 'Pricing',
  components: {
    PageBanner
  },
  data() {
    return {
      auth: useStudentAuth(),
      loading: false,
      plans: [
        {
          id: 1,
          title: '單堂體驗',
          subtitle: '適合初次體驗的學員',
          price: '$500',
          unit: '/ 堂',
          classes_count: 1,
          is_popular: false,
          button_text: '買課',
          button_link: '/contact'
        },
        {
          id: 2,
          title: '小資方案',
          subtitle: '適合規律每週練習者',
          price: '$3,200',
          unit: '/ 8 堂 (平均 $400/堂)',
          classes_count: 8,
          is_popular: false,
          button_text: '買課',
          button_link: '/contact'
        },
        {
          id: 3,
          title: '熱血方案',
          subtitle: '適合重度舞蹈愛好者',
          price: '$6,000',
          unit: '/ 20 堂 (平均 $300/堂)',
          classes_count: 20,
          is_popular: true,
          button_text: '買課',
          button_link: '/contact'
        },
        {
          id: 4,
          title: '尊榮月費',
          subtitle: '當月份不限堂數暢快跳',
          price: '$8,000',
          unit: '/ 月 (無限堂數)',
          classes_count: 30,
          is_popular: false,
          button_text: '買課',
          button_link: '/contact'
        }
      ],
      notice: {
        title: '學員報名與上課須知',
        items: [
          '所有常規課程皆需提前於線上系統或向官方 LINE 預約登記。',
          '堂數方案為個人專屬權益，限本人上課使用，不得轉讓或轉售他人。',
          '方案自購買啟用起計，請於各方案指定之有效期限內使用完畢。',
          '若需取消或請假，請最晚於課程開始前 2 小時完成線上取消，以免扣除堂數。',
          '如遇天然災害或政府宣佈停班停課，本工作室常規課程將自動順延。'
        ]
      },

      // 買課狀態
      selectedPlan: null,
      pendingPlan: null,
      modalInstance: null,
      submittingOrder: false,
      purchaseForm: {
        bank_last_5: '',
        notes: '',
        save_bank_info: true
      }
    };
  },
  computed: {
    currentStudent() {
      return this.auth.currentStudent;
    },
    hasActiveMembership() {
      const exp = this.currentStudent?.membership_expiry;
      if (!exp) return false;
      try {
        const d = new Date(exp);
        if (isNaN(d.getTime())) return false;
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return d >= today;
      } catch (e) {
        return false;
      }
    },
    isMembershipRestricted() {
      if (!this.selectedPlan || !this.selectedPlan.requires_membership) return false;
      return !this.hasActiveMembership;
    }
  },
  watch: {
    'auth.isLoggedIn'(isLoggedIn) {
      if (isLoggedIn && this.pendingPlan) {
        const plan = this.pendingPlan;
        this.pendingPlan = null;
        this.$nextTick(() => {
          this.openPurchaseModal(plan);
        });
      }
    }
  },
  mounted() {
    this.initModal();
    this.fetchPricingData();
  },
  beforeUnmount() {
    if (this.modalInstance) {
      this.modalInstance.dispose();
      this.modalInstance = null;
    }
  },
  methods: {
    initModal() {
      const el = document.getElementById('buyCourseModal');
      if (el) {
        this.modalInstance = new Modal(el);
      }
    },
    async fetchPricingData() {
      this.loading = true;
      try {
        const res = await api.get(API_ENDPOINTS.PRICING);
        if (res.success) {
          if (res.plans && res.plans.length > 0) {
            this.plans = res.plans;
          }
          if (res.notice) {
            this.notice.title = res.notice.title || '學員報名與上課須知';
            if (res.notice.items && res.notice.items.length > 0) {
              this.notice.items = res.notice.items;
            }
          }
        }
      } catch (err) {
        console.warn('載入後台價目表失敗，使用預設方案顯示:', err);
      } finally {
        this.loading = false;
      }
    },
    isPlanPopular(plan) {
      return Boolean(plan.is_popular || plan.isPopular);
    },
    handleBuyClick(plan) {
      if (!this.auth.isLoggedIn) {
        this.pendingPlan = plan;
        showToast('請先登入學員帳號以進行買課', 'info');
        this.auth.openLoginModal();
        return;
      }
      this.openPurchaseModal(plan);
    },
    openPurchaseModal(plan) {
      this.selectedPlan = plan;
      // 優先從當前學員資料帶入已儲存之銀行後 5 碼
      this.purchaseForm = {
        bank_last_5: this.currentStudent?.bank_last_5 || '',
        notes: '',
        save_bank_info: true
      };
      if (this.modalInstance) {
        this.modalInstance.show();
      }
    },
    switchToMembershipFeePlan() {
      const memPlan = this.plans.find(p => p.plan_type === 'membership_fee' || (p.title && p.title.includes('年費')));
      if (memPlan) {
        this.openPurchaseModal(memPlan);
        showToast('已為您切換至「會員年費」方案，填寫銀行後 5 碼即可完成下單！', 'success');
      } else {
        showToast('請至價目表選購會員年費方案', 'info');
      }
    },
    async submitBuyOrder() {
      if (this.isMembershipRestricted) {
        showToast('此方案限定「有效會員年費」學員購買，請先開通會員年費', 'warning');
        return;
      }
      if (!this.purchaseForm.bank_last_5.trim()) {
        showToast('請填寫轉帳銀行後 5 碼', 'warning');
        return;
      }

      this.submittingOrder = true;
      try {
        const payload = {
          student_id: this.currentStudent.id,
          plan_id: this.selectedPlan.id,
          bank_last_5: this.purchaseForm.bank_last_5.trim(),
          notes: this.purchaseForm.notes.trim(),
          save_bank_info: this.purchaseForm.save_bank_info
        };

        const res = await api.post(API_ENDPOINTS.PRICING_ORDERS, payload);
        if (res.success) {
          if (this.modalInstance) {
            this.modalInstance.hide();
          }

          // 重新整理學員資料 (同步更新 bank_last_5)
          await this.auth.refreshProfile();

          showToast('購課訂單已成功送出！待工作人員核對匯款後，系統將自動為您入帳並增加堂數。', 'success', 5000);
        } else {
          showToast(res.error || '購課送出失敗', 'error');
        }
      } catch (err) {
        showToast(err.message || '連線失敗，請稍後重試', 'error');
      } finally {
        this.submittingOrder = false;
      }
    }
  }
};
</script>

<style scoped>
.pricing-card {
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  border-radius: 12px;
  overflow: hidden;
  min-height: 280px;
}

.pricing-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12) !important;
}

.ring-popular {
  border-width: 2px !important;
}

.pricing-header {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
</style>
