CREATE TABLE IF NOT EXISTS financial_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('income', 'expense') NOT NULL COMMENT '收支類型',
    category VARCHAR(50) NOT NULL COMMENT '收支分類',
    amount DECIMAL(12, 2) NOT NULL COMMENT '金額',
    record_date DATE NOT NULL COMMENT '收支日期',
    payment_method VARCHAR(50) DEFAULT '現金' COMMENT '支付方式',
    description VARCHAR(255) NOT NULL COMMENT '摘要/說明',
    note TEXT NULL COMMENT '詳細備註',
    handler_name VARCHAR(100) NULL COMMENT '經手人',
    user_id INT NULL COMMENT '建立人員帳號 id',
    invoice_number VARCHAR(100) NULL COMMENT '收據/發票編號',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_record_date (record_date),
    INDEX idx_type (type),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

