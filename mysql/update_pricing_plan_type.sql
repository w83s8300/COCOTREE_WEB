-- 新增方案類型 (plan_type) 與 月票有效天數 (validity_days)
ALTER TABLE pricing_plans 
ADD COLUMN plan_type VARCHAR(20) NOT NULL DEFAULT 'classes' COMMENT '方案類型: classes (買幾堂) 或 monthly_pass (月票/效期制)' AFTER unit,
ADD COLUMN validity_days INT NOT NULL DEFAULT 0 COMMENT '月票有效天數 (如 30 代表 1 個月)' AFTER classes_count;

-- 訂單表格同步支援方案類型與月票天數
ALTER TABLE pricing_orders 
ADD COLUMN plan_type VARCHAR(20) NOT NULL DEFAULT 'classes' COMMENT '方案類型: classes 或 monthly_pass' AFTER price,
ADD COLUMN validity_days INT NOT NULL DEFAULT 0 COMMENT '月票有效天數' AFTER classes_count;

