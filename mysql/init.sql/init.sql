SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS course_schedules;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS teacher_styles;
DROP TABLE IF EXISTS styles;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS students;

-- 建立學生表格
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NULL COMMENT '登入密碼雜湊',
    age INT,
    date_of_birth DATE COMMENT '出生年月日',
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(20),
    medical_notes TEXT,
    remaining_classes INT DEFAULT 0 COMMENT '剩餘堂數',
    membership_expiry DATE COMMENT '會員年費到期日',
    expiry_date DATE NULL COMMENT '會員年費到期日 (相容欄位)',
    monthly_pass_expiry DATE COMMENT '月費到期日',
    bank_last_5 VARCHAR(10) NULL COMMENT '約定轉帳銀行後5碼',
    line_user_id VARCHAR(100) UNIQUE NULL COMMENT 'LINE User ID',
    line_display_name VARCHAR(100) NULL COMMENT 'LINE 暱稱',
    line_picture_url VARCHAR(255) NULL COMMENT 'LINE 大頭貼圖片URL',
    line_linked_at DATETIME NULL COMMENT 'LINE 帳號關聯時間',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 建立教室表格
CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    capacity INT DEFAULT 20,
    equipment TEXT,
    description TEXT,
    hourly_rate DECIMAL(10,2),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 建立老師表格
CREATE TABLE teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    experience_years INT,
    bio TEXT,
    hourly_rate DECIMAL(10,2),
    bank_account VARCHAR(100) COMMENT '銀行帳號',
    avatar_url TEXT NULL COMMENT '大頭貼圖片URL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 建立風格表格
CREATE TABLE styles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 建立老師-風格關聯表
CREATE TABLE teacher_styles (
    teacher_id INT NOT NULL,
    style_id INT NOT NULL,
    PRIMARY KEY (teacher_id, style_id),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (style_id) REFERENCES styles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 建立課程表格
CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    level VARCHAR(20) NOT NULL,
    style_id INT,
    duration_minutes INT DEFAULT 60,
    max_students INT DEFAULT 15,
    price DECIMAL(10,2),
    allow_monthly_pass BOOLEAN DEFAULT TRUE COMMENT '是否支援月費暢跳',
    teacher_id INT,
    base_salary DECIMAL(10,2) DEFAULT 0.00,
    low_student_threshold INT DEFAULT 0,
    low_student_salary DECIMAL(10,2) DEFAULT 0.00,
    extra_student_threshold INT DEFAULT 0,
    extra_student_fee DECIMAL(10,2) DEFAULT 0.00,
    salary_cap DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
    FOREIGN KEY (style_id) REFERENCES styles(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 建立課程時間表格
CREATE TABLE course_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    schedule_date DATE NOT NULL, -- 具體日期 (YYYY-MM-DD)
    day_of_week VARCHAR(20) NOT NULL, -- Monday, Tuesday, etc.
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    room_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    allow_enrollment BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 修改現有的報名表格，添加外鍵關聯
CREATE TABLE enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    course_id INT,
    schedule_id INT,
    student_name VARCHAR(100) NOT NULL,
    lesson_name VARCHAR(100) NOT NULL,
    lesson_time VARCHAR(50) NOT NULL,
    lesson_day VARCHAR(20) NOT NULL,
    lesson_teacher VARCHAR(50) NOT NULL,
    lesson_level VARCHAR(20) NOT NULL,
    lesson_type VARCHAR(50) NOT NULL,
    enrollment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'confirmed',
    deducted_classes INT DEFAULT 1,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL,
    FOREIGN KEY (schedule_id) REFERENCES course_schedules(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 插入範例教室資料
INSERT INTO rooms (name, capacity, equipment, description, hourly_rate, is_available) VALUES
('Studio A', 20, 'Sound System, Mirrors, Ballet Barre', '大型練習室，適合芭蕾和現代舞', 500.00, TRUE),
('Studio B', 15, 'Sound System, Mirrors', '中型練習室，適合各種舞蹈類型', 400.00, TRUE),
('Studio C', 25, 'Professional Sound System, LED Lighting, Mirrors', '專業表演練習室，設備齊全', 800.00, TRUE),
('Studio D', 10, 'Basic Sound System, Mirrors', '小型練習室，適合私人課程', 300.00, TRUE);

-- 插入範例風格資料
INSERT INTO styles (name, description) VALUES
('Ballet', '古典芭蕾舞'),
('Jazz', '爵士舞'),
('Hip-Hop', '嘻哈街舞'),
('Contemporary', '現代舞'),
('Modern', '現代舞'),
('Street Dance', '街舞');

-- 插入範例老師資料
INSERT INTO teachers (name, email, phone, experience_years, bio, hourly_rate) VALUES
('張美麗', 'zhang@dancestudio.com', '0912-345-678', 8, '專業芭蕾舞老師，畢業於國立台北藝術大學', 1200.00),
('李強', 'li@dancestudio.com', '0923-456-789', 5, '街舞冠軍，擅長各種流行舞蹈', 1000.00),
('王雅文', 'wang@dancestudio.com', '0934-567-890', 10, '爵士舞專家，具有豐富的表演經驗', 1300.00);

-- 插入老師-風格關聯資料
INSERT INTO teacher_styles (teacher_id, style_id) VALUES
(1, 1), -- 張美麗 - Ballet
(1, 4), -- 張美麗 - Contemporary
(2, 3), -- 李強 - Hip-Hop
(2, 6), -- 李強 - Street Dance
(3, 2), -- 王雅文 - Jazz
(3, 5); -- 王雅文 - Modern

-- 插入範例課程資料
INSERT INTO courses (name, description, level, style_id, duration_minutes, max_students, price, teacher_id) VALUES
('初級芭蕾', '適合零基礎學員的芭蕾課程', 'beginner', 1, 90, 12, 800.00, 1),
('中級芭蕾', '具有基礎的學員進階課程', 'intermediate', 1, 90, 10, 1000.00, 1),
('街舞入門', '流行街舞基礎教學', 'beginner', 3, 60, 15, 600.00, 2),
('爵士舞精修', '爵士舞進階技巧訓練', 'advanced', 2, 75, 8, 1200.00, 3),
('現代舞基礎', '現代舞基本動作與表達', 'beginner', 5, 75, 12, 700.00, 3);

-- 插入範例課程時間表
INSERT INTO course_schedules (course_id, schedule_date, day_of_week, start_time, end_time, room_id) VALUES
(1, '2025-01-06', 'Monday', '18:00:00', '19:30:00', 1),
(1, '2025-01-08', 'Wednesday', '18:00:00', '19:30:00', 1),
(1, '2025-01-13', 'Monday', '18:00:00', '19:30:00', 1),
(1, '2025-01-15', 'Wednesday', '18:00:00', '19:30:00', 1),
(2, '2025-01-07', 'Tuesday', '19:00:00', '20:30:00', 1),
(2, '2025-01-09', 'Thursday', '19:00:00', '20:30:00', 1),
(2, '2025-01-14', 'Tuesday', '19:00:00', '20:30:00', 1),
(2, '2025-01-16', 'Thursday', '19:00:00', '20:30:00', 1),
(3, '2025-01-06', 'Monday', '20:00:00', '21:00:00', 2),
(3, '2025-01-10', 'Friday', '19:00:00', '20:00:00', 2),
(3, '2025-01-13', 'Monday', '20:00:00', '21:00:00', 2),
(3, '2025-01-17', 'Friday', '19:00:00', '20:00:00', 2),
(4, '2025-01-08', 'Wednesday', '20:00:00', '21:15:00', 3),
(4, '2025-01-15', 'Wednesday', '20:00:00', '21:15:00', 3),
(5, '2025-01-11', 'Saturday', '10:00:00', '11:15:00', 1),
(5, '2025-01-18', 'Saturday', '10:00:00', '11:15:00', 1);

-- 建立管理後台帳號表格 (管理員、櫃檯、老師權限)
CREATE TABLE IF NOT EXISTS admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'desk', 'teacher') NOT NULL DEFAULT 'desk',
    phone VARCHAR(20) NULL,
    hourly_rate DECIMAL(10,2) DEFAULT 0.00,
    bank_account VARCHAR(100) NULL COMMENT '銀行帳號',
    teacher_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 插入預設管理員、櫃檯、老師帳號
INSERT IGNORE INTO admin_users (id, username, password, name, role, phone, teacher_id) VALUES
(1, 'admin', 'admin123', '系統管理員', 'admin', '0911000111', NULL),
(2, 'counter', 'desk123', '櫃檯客服', 'desk', '0922000222', NULL),
(3, 'teacher', 'teacher123', '張美麗老師', 'teacher', '0933000333', 1);

-- 建立員工上下班打卡記錄表
CREATE TABLE IF NOT EXISTS staff_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    clock_in DATETIME NOT NULL,
    effective_clock_in DATETIME NULL COMMENT '計薪起算時間(30分進位)',
    clock_out DATETIME NULL,
    effective_clock_out DATETIME NULL COMMENT '計薪截止時間(30分退位)',
    work_hours DECIMAL(5,2) DEFAULT 0.00,
    hourly_rate DECIMAL(10,2) DEFAULT 0.00,
    total_pay DECIMAL(10,2) DEFAULT 0.00,
    notes VARCHAR(255) NULL,
    clock_in_ip VARCHAR(50) NULL COMMENT '上班打卡IP',
    clock_out_ip VARCHAR(50) NULL COMMENT '下班打卡IP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 建立授課老師上課下課打卡記錄表
CREATE TABLE IF NOT EXISTS teacher_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    teacher_id INT NULL,
    schedule_id INT NULL,
    course_id INT NULL,
    course_name VARCHAR(100) NULL,
    clock_in DATETIME NOT NULL,
    clock_out DATETIME NULL,
    duration_minutes INT DEFAULT 0,
    student_count INT DEFAULT 0,
    calculated_salary DECIMAL(10,2) DEFAULT 0.00,
    notes VARCHAR(255) NULL,
    clock_in_ip VARCHAR(50) NULL COMMENT '上課打卡IP',
    clock_out_ip VARCHAR(50) NULL COMMENT '下課打卡IP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
    FOREIGN KEY (schedule_id) REFERENCES course_schedules(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 建立系統通用設定表 (打卡 IP 白名單等)
CREATE TABLE IF NOT EXISTS system_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value TEXT NULL,
    description VARCHAR(255) NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



INSERT IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
('attendance_ip_restriction_enabled', '0', '是否啟用打卡 IP 白名單限制 (0=關閉, 1=開啟)'),
('attendance_allowed_ips', '', '允許打卡的 IP 地址清單 (以逗號或換行分隔)'),
('line_login_enabled', '1', '是否啟用 LINE 快速登入與帳號關聯 (0=關閉, 1=開啟)'),
('line_channel_id', '', 'LINE Login Channel ID (頻道識別碼)'),
('line_channel_secret', '', 'LINE Login Channel Secret (頻道金鑰)'),
('line_official_id', '', '工作室 LINE 官方帳號 ID (例如 @dancestudio)'),
('line_official_url', '', '工作室 LINE 官方加好友連結 (例如 https://line.me/R/ti/p/@dancestudio)');


-- 建立課程價目表表格
CREATE TABLE IF NOT EXISTS pricing_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    subtitle VARCHAR(100) NULL,
    price VARCHAR(50) NOT NULL,
    unit VARCHAR(100) NOT NULL,
    plan_type VARCHAR(20) NOT NULL DEFAULT 'classes' COMMENT '方案類型: classes (買幾堂) 或 monthly_pass (月票/效期制)',
    classes_count INT DEFAULT 1,
    validity_days INT NOT NULL DEFAULT 0 COMMENT '月票有效天數 (如 30 代表 1 個月)',
    original_price VARCHAR(50) NULL,
    is_popular BOOLEAN DEFAULT FALSE,
    requires_membership BOOLEAN DEFAULT FALSE COMMENT '是否限有效會員年費學員購買',
    features TEXT NOT NULL,
    button_text VARCHAR(50) DEFAULT '買課',
    button_link VARCHAR(255) DEFAULT '/contact',
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



INSERT IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
('pricing_notice_title', '學員報名與上課須知', '課程價目表須知標題'),
('bank_name', '國泰世華銀行', '工作室匯款銀行名稱'),
('bank_code', '013', '工作室匯款銀行代碼'),
('bank_account', '012-34-567890-1', '工作室匯款帳號'),
('bank_account_name', 'Dance Studio 舞蹈工作室', '工作室匯款戶名'),
('bank_notes', '請先完成匯款後，於下方填寫您的轉帳帳號後 5 碼，以便工作人員核帳開通堂數。', '工作室匯款附註與說明'),
('pricing_notice_content', '所有常規課程皆需提前於線上系統或向官方 LINE 預約登記。\n堂數方案為個人專屬權益，限本人上課使用，不得轉讓或轉售他人。\n方案自購買啟用起計，請於各方案指定之有效期限內使用完畢。\n若需取消或請假，請最晚於課程開始前 2 小時完成線上取消，以免扣除堂數。\n如遇天然災害或政府宣佈停班停課，本工作室常規課程將自動順延。', '課程價目表學員須知內容(每行一項)');

INSERT INTO pricing_plans (id, title, subtitle, price, unit, original_price, is_popular, features, button_text, button_link, sort_order, is_active)
SELECT 1, '單堂體驗', '適合初次體驗的學員', '$500', '/ 堂', NULL, 0, '["適合初次體驗的學員", "可任選一堂常規舞蹈課", "專業教練動作引導", "課後舞風諮詢"]', '買課', '/contact', 1, 1
WHERE NOT EXISTS (SELECT 1 FROM pricing_plans WHERE id = 1);

INSERT INTO pricing_plans (id, title, subtitle, price, unit, original_price, is_popular, features, button_text, button_link, sort_order, is_active)
SELECT 2, '小資方案', '適合規律每週練習者', '$3,200', '/ 8 堂 (平均 $400/堂)', NULL, 0, '["適合規律每週練習者", "使用期限 2 個月", "全時段常規課程皆適用", "請假彈性保留堂數"]', '買課', '/contact', 2, 1
WHERE NOT EXISTS (SELECT 1 FROM pricing_plans WHERE id = 2);

INSERT INTO pricing_plans (id, title, subtitle, price, unit, original_price, is_popular, features, button_text, button_link, sort_order, is_active)
SELECT 3, '熱血方案', '適合重度舞蹈愛好者', '$6,000', '/ 20 堂 (平均 $300/堂)', NULL, 1, '["適合重度舞蹈愛好者", "使用期限 4 個月", "全常規課程自由選修", "贈送專屬品牌運動毛巾", "享成果發表報名優先權"]', '買課', '/contact', 3, 1
WHERE NOT EXISTS (SELECT 1 FROM pricing_plans WHERE id = 3);

INSERT INTO pricing_plans (id, title, subtitle, price, unit, original_price, is_popular, features, button_text, button_link, sort_order, is_active)
SELECT 4, '尊榮月費', '當月份不限堂數暢快跳', '$8,000', '/ 月 (無限堂數)', NULL, 0, '["當月份不限堂數暢快跳", "全常規課程皆可預約", "場地個人租借 8 折特惠", "周邊服飾商品 9 折優惠"]', '買課', '/contact', 4, 1
WHERE NOT EXISTS (SELECT 1 FROM pricing_plans WHERE id = 4);

INSERT INTO pricing_plans (id, title, subtitle, price, unit, plan_type, classes_count, validity_days, original_price, is_popular, features, button_text, button_link, sort_order, is_active)
SELECT 5, '會員年費', '年度專屬會員資格與優惠', '$1,200', '/ 年 (365天)', 'membership_fee', 0, 365, NULL, 0, '["成為正式年度會員", "專屬會員身份有效期限 1 年 (365天)", "享有購課與報名優惠資格", "專屬會員專屬禮與活動優先權"]', '買課', '/contact', 5, 1
WHERE NOT EXISTS (SELECT 1 FROM pricing_plans WHERE id = 5);


-- 建立購課訂單表格
CREATE TABLE IF NOT EXISTS pricing_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_no VARCHAR(50) UNIQUE NOT NULL,
    student_id INT NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    student_phone VARCHAR(20) NOT NULL,
    plan_id INT NULL,
    plan_title VARCHAR(100) NOT NULL,
    price VARCHAR(50) NOT NULL,
    plan_type VARCHAR(20) NOT NULL DEFAULT 'classes',
    requires_membership BOOLEAN DEFAULT FALSE,
    classes_count INT DEFAULT 1,
    validity_days INT NOT NULL DEFAULT 0,
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



-- 建立首頁橫幅表格
CREATE TABLE IF NOT EXISTS banners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subtitle TEXT NULL,
    badge_text VARCHAR(100) NULL,
    badge_color VARCHAR(50) DEFAULT 'warning',
    image_url TEXT NOT NULL,
    primary_button_text VARCHAR(100) NULL,
    primary_button_link VARCHAR(255) NULL,
    primary_button_style VARCHAR(100) DEFAULT 'primary',
    secondary_button_text VARCHAR(100) NULL,
    secondary_button_link VARCHAR(255) NULL,
    secondary_button_style VARCHAR(100) DEFAULT 'outline-light',
    interval_ms INT DEFAULT 5000,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO banners (id, title, subtitle, badge_text, badge_color, image_url, primary_button_text, primary_button_link, primary_button_style, secondary_button_text, secondary_button_link, secondary_button_style, interval_ms, sort_order, is_active)
SELECT 1, '釋放你的節奏，舞出你的熱情', '無論是零基礎新手或資深舞者，在 Dance Studio 都能找到最適合你的專屬舞台。', '✨ 啟動你的舞蹈新生活', 'warning', 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=1920&q=80', '立即預約課程', '/schedule', 'primary', '認識師資團隊', '/instructors', 'outline-light', 5000, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM banners WHERE id = 1);

INSERT INTO banners (id, title, subtitle, badge_text, badge_color, image_url, primary_button_text, primary_button_link, primary_button_style, secondary_button_text, secondary_button_link, secondary_button_style, interval_ms, sort_order, is_active)
SELECT 2, '多元舞風體系 × 專業細膩教學', '流行街舞、K-POP MV、抒情爵士、芭蕾律動，循序漸進拆解每個核心動作。', '👑 頂尖專業名師陣容', 'primary', 'https://images.unsplash.com/photo-1547153760-18fc86324498?auto=format&fit=crop&w=1920&q=80', '查看本週課表', '/schedule', 'warning', '課程收費方案', '/pricing', 'outline-light', 5000, 2, 1
WHERE NOT EXISTS (SELECT 1 FROM banners WHERE id = 2);

INSERT INTO banners (id, title, subtitle, badge_text, badge_color, image_url, primary_button_text, primary_button_link, primary_button_style, secondary_button_text, secondary_button_link, secondary_button_style, interval_ms, sort_order, is_active)
SELECT 3, '高規格減震地板與專業環繞音響', '四大獨立主題練習室，明亮寬敞的空間與貼心休息區，享受最極致的跳舞體驗。', '🏢 專業國際級練習空間', 'success', 'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=1920&q=80', '參觀場地環境', '/venue', 'light', '關於我們', '/about', 'outline-light', 5000, 3, 1
WHERE NOT EXISTS (SELECT 1 FROM banners WHERE id = 3);

-- 建立各分頁頂部橫幅表格
CREATE TABLE IF NOT EXISTS page_banners (
    page_key VARCHAR(50) PRIMARY KEY,
    page_name VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(255) NULL,
    image_url TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO page_banners (page_key, page_name, title, subtitle, image_url) VALUES
('about', '關於我們', '關於我們 / ABOUT US', '致力於為所有舞蹈愛好者提供最專業、多元的學習體驗', 'https://picsum.photos/1920/500?random=9'),
('history', '品牌沿革', '品牌沿革 / HISTORY', '見證 Dance Studio 歷年來的里程碑與熱血歷程', 'https://picsum.photos/1920/500?random=8'),
('instructors', '師資團隊', '師資團隊 / INSTRUCTORS', '匯聚業界頂尖名師，細膩指導每一步身體律動', 'https://picsum.photos/1920/500?random=14'),
('schedule', '課程時間表', '課程時間表 / SCHEDULE', '彈性多元的時段規劃，全方位探索熱門舞風', 'https://picsum.photos/1920/500?random=36'),
('pricing', '課程價目表', '課程價目表 / PRICING', '透明彈性的收費方案，滿足不同學習階段需求', 'https://picsum.photos/1920/500?random=35'),
('gallery', '活動花絮', '活動花絮 / GALLERY', '回顧學員舞台演出與歡樂練習日常的精彩瞬間', 'https://picsum.photos/1920/500?random=22'),
('venue', '場地租借', '場地租借 / VENUE', '專業避震地板、頂級音響設備，打造最佳跳舞空間', 'https://picsum.photos/1920/500?random=29'),
('faq', '常見問題', '常見問題 / FAQ', '快速解答學員常見疑問，新手安心踏出第一步', 'https://picsum.photos/1920/500?random=33'),
('contact', '聯絡我們', '聯絡我們 / CONTACT', '歡迎預約參觀、諮詢課程或與我們聯繫交流', 'https://picsum.photos/1920/500?random=34')
ON DUPLICATE KEY UPDATE page_name=VALUES(page_name);

-- 建立最新消息與活動公告表格
CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) DEFAULT 'news',
    tag VARCHAR(50) DEFAULT '公告',
    summary TEXT NULL,
    content TEXT NULL,
    image_url TEXT NULL,
    is_published BOOLEAN DEFAULT TRUE,
    publish_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 建立收支記帳表格
CREATE TABLE IF NOT EXISTS financial_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('income', 'expense') NOT NULL COMMENT '收支類型: income收入, expense支出',
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

