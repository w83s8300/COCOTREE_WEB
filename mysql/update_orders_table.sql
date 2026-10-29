-- 1. students 表增加 bank_last_5
ALTER TABLE students ADD COLUMN bank_last_5 VARCHAR(10) NULL COMMENT '銀行帳號後5碼' AFTER emergency_phone;

-- 2. pricing_plans 表增加 classes_count
ALTER TABLE pricing_plans ADD COLUMN classes_count INT DEFAULT 1 COMMENT '方案包含堂數' AFTER unit;

-- 更新現有4個方案的堂數
UPDATE pricing_plans SET classes_count = 1 WHERE id = 1;
UPDATE pricing_plans SET classes_count = 8 WHERE id = 2;
UPDATE pricing_plans SET classes_count = 20 WHERE id = 3;
UPDATE pricing_plans SET classes_count = 30 WHERE id = 4;

-- 3. 建立 pricing_orders 表格
CREATE TABLE IF NOT EXISTS pricing_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(50) UNIQUE NOT NULL,
    student_id INT NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    student_phone VARCHAR(20) NOT NULL,
    plan_id INT NULL,
    plan_title VARCHAR(100) NOT NULL,
    price VARCHAR(50) NOT NULL,
    classes_count INT DEFAULT 1,
    bank_last_5 VARCHAR(10) NOT NULL,
    status ENUM('pending', 'confirmed', 'rejected', 'cancelled') DEFAULT 'pending',
    notes TEXT NULL,
    admin_notes TEXT NULL,
    confirmed_by INT NULL,
    confirmed_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES pricing_plans(id) ON DELETE SET NULL,
    FOREIGN KEY (confirmed_by) REFERENCES admin_users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

