from flask import Flask, request, jsonify, send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime, date, timedelta
import os
import time
import math
import json
import urllib.request
import urllib.parse
import urllib.error

from auth_utils import (
    hash_password,
    verify_and_upgrade_password,
    generate_token,
    jwt_required
)

app = Flask(__name__)
# 限制檔案上傳最大為 16MB，防範 DoS 攻擊
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)  # 允許跨域請求
api = Api(app)

# 上傳檔案存儲目錄
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
AVATARS_FOLDER = os.path.join(UPLOAD_FOLDER, 'avatars')
ROOMS_FOLDER = os.path.join(UPLOAD_FOLDER, 'rooms')
GALLERY_FOLDER = os.path.join(UPLOAD_FOLDER, 'gallery')
os.makedirs(AVATARS_FOLDER, exist_ok=True)
os.makedirs(ROOMS_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)
BANNERS_FOLDER = os.path.join(UPLOAD_FOLDER, 'banners')
os.makedirs(BANNERS_FOLDER, exist_ok=True)

@app.route('/api/uploads/<path:filename>')
def serve_uploaded_file(filename):
    """提供已上傳靜態圖片檔案"""
    return send_from_directory(UPLOAD_FOLDER, filename)

# 資料庫連接配置（優先讀取環境變數）
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'w83s8300'),
    'password': os.getenv('DB_PASSWORD', '!Q83a8300'),
    'database': os.getenv('DB_NAME', 'cocotree_db'),
    'charset': 'utf8mb4',
    'buffered': True
}

def get_db_connection():
    """取得資料庫連接，包含重試機制"""
    max_retries = 15
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            return connection
        except mysql.connector.Error as err:
            print(f"資料庫連接嘗試 {attempt + 1}/{max_retries} 失敗: {err}")
            if attempt < max_retries - 1:
                print(f"等待 {retry_delay} 秒後重試...")
                time.sleep(retry_delay)
            else:
                print("資料庫連接失敗，已達最大重試次數")
                return None

def ensure_pricing_database_tables(cursor):
    """確保 pricing_plans, pricing_orders 以及 students 與 courses 的相關欄位齊備"""
    try:
        # 1. 確保 students 欄位
        cursor.execute("SHOW COLUMNS FROM students LIKE 'membership_expiry'")
        if not cursor.fetchall():
            cursor.execute("SHOW COLUMNS FROM students LIKE 'expiry_date'")
            if cursor.fetchall():
                cursor.execute("ALTER TABLE students ADD COLUMN membership_expiry DATE NULL COMMENT '會員年費到期日' AFTER expiry_date")
                cursor.execute("UPDATE students SET membership_expiry = expiry_date WHERE membership_expiry IS NULL AND expiry_date IS NOT NULL")
            else:
                cursor.execute("ALTER TABLE students ADD COLUMN membership_expiry DATE NULL COMMENT '會員年費到期日'")

        cursor.execute("SHOW COLUMNS FROM students LIKE 'expiry_date'")
        if not cursor.fetchall():
            cursor.execute("ALTER TABLE students ADD COLUMN expiry_date DATE NULL COMMENT '舊版會員到期日相容欄位' AFTER membership_expiry")
            cursor.execute("UPDATE students SET expiry_date = membership_expiry WHERE expiry_date IS NULL AND membership_expiry IS NOT NULL")

        cursor.execute("SHOW COLUMNS FROM students LIKE 'monthly_pass_expiry'")
        if not cursor.fetchall():
            cursor.execute("ALTER TABLE students ADD COLUMN monthly_pass_expiry DATE NULL COMMENT '月費到期日'")

        cursor.execute("SHOW COLUMNS FROM students LIKE 'bank_last_5'")
        if not cursor.fetchall():
            cursor.execute("ALTER TABLE students ADD COLUMN bank_last_5 VARCHAR(10) NULL COMMENT '約定轉帳銀行後5碼'")

        # 2. 確保 pricing_plans 表與欄位
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pricing_plans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            subtitle VARCHAR(100) NULL,
            price VARCHAR(50) NOT NULL,
            unit VARCHAR(100) NOT NULL,
            plan_type VARCHAR(20) NOT NULL DEFAULT 'classes',
            classes_count INT DEFAULT 1,
            validity_days INT NOT NULL DEFAULT 0,
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
        """)

        for col, col_def in [
            ('plan_type', "VARCHAR(20) NOT NULL DEFAULT 'classes'"),
            ('classes_count', "INT DEFAULT 1"),
            ('validity_days', "INT NOT NULL DEFAULT 0"),
            ('requires_membership', "BOOLEAN DEFAULT FALSE COMMENT '是否限有效會員年費學員購買'")
        ]:
            cursor.execute(f"SHOW COLUMNS FROM pricing_plans LIKE '{col}'")
            if not cursor.fetchall():
                cursor.execute(f"ALTER TABLE pricing_plans ADD COLUMN {col} {col_def}")

        # 3. 確保 pricing_orders 表與欄位
        cursor.execute("""
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
            requires_membership BOOLEAN DEFAULT FALSE COMMENT '是否限有效會員年費學員購買',
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
        """)

        for col, col_def in [
            ('plan_type', "VARCHAR(20) NOT NULL DEFAULT 'classes'"),
            ('requires_membership', "BOOLEAN DEFAULT FALSE COMMENT '是否限有效會員年費學員購買'"),
            ('validity_days', "INT NOT NULL DEFAULT 0"),
            ('classes_count', "INT DEFAULT 1")
        ]:
            cursor.execute(f"SHOW COLUMNS FROM pricing_orders LIKE '{col}'")
            if not cursor.fetchall():
                cursor.execute(f"ALTER TABLE pricing_orders ADD COLUMN {col} {col_def}")

    except Exception as err:
        print(f"ensure_pricing_database_tables 警告: {err}")


def init_database_tables():
    """初始化所有資料庫表格，包含重試機制"""
    print("正在初始化資料庫表格...")
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(buffered=True)
            
            # 學生表格
            students_table = """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(20),
                date_of_birth DATE,
                emergency_contact VARCHAR(100),
                emergency_phone VARCHAR(20),
                medical_notes TEXT,
                remaining_classes INT DEFAULT 0 COMMENT '剩餘堂數',
                membership_expiry DATE COMMENT '會員年費到期日',
                monthly_pass_expiry DATE COMMENT '月費到期日',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            # 教室表格
            rooms_table = """
            CREATE TABLE IF NOT EXISTS rooms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                capacity INT DEFAULT 20,
                equipment TEXT,
                description TEXT,
                hourly_rate DECIMAL(10,2),
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            # 老師表格（移除 specialties 欄位）
            teachers_table = """
            CREATE TABLE IF NOT EXISTS teachers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(20),
                bio TEXT,
                hourly_rate DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """

            # 風格表格
            styles_table = """
            CREATE TABLE IF NOT EXISTS styles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                description TEXT
            )
            """

            # 老師-風格關聯表
            teacher_styles_table = """
            CREATE TABLE IF NOT EXISTS teacher_styles (
                teacher_id INT NOT NULL,
                style_id INT NOT NULL,
                PRIMARY KEY (teacher_id, style_id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                FOREIGN KEY (style_id) REFERENCES styles(id) ON DELETE CASCADE
            )
            """
            
            # 課程表格
            courses_table = """
            CREATE TABLE IF NOT EXISTS courses (
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
            )
            """
            
            # 更新課程時間表格
            schedules_table = """
            CREATE TABLE IF NOT EXISTS course_schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_id INT NOT NULL,
                schedule_date DATE NOT NULL,
                day_of_week VARCHAR(20) NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                room_id INT,
                is_active BOOLEAN DEFAULT TRUE,
                allow_enrollment BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL
            )
            """
            
            # 報名表格
            enrollments_table = """
            CREATE TABLE IF NOT EXISTS enrollments (
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
            )
            """

            # 後台管理員/櫃檯/老師帳號表格
            admin_users_table = """
            CREATE TABLE IF NOT EXISTS admin_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(100) NOT NULL,
                role ENUM('admin', 'desk', 'teacher') NOT NULL DEFAULT 'desk',
                phone VARCHAR(20) NULL,
                hourly_rate DECIMAL(10,2) DEFAULT 0.00,
                bank_account VARCHAR(100) NULL,
                teacher_id INT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
            )
            """

            # 員工上下班打卡記錄表格
            staff_attendance_table = """
            CREATE TABLE IF NOT EXISTS staff_attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                clock_in DATETIME NOT NULL,
                effective_clock_in DATETIME NULL,
                clock_out DATETIME NULL,
                effective_clock_out DATETIME NULL,
                work_hours DECIMAL(5,2) DEFAULT 0.00,
                hourly_rate DECIMAL(10,2) DEFAULT 0.00,
                total_pay DECIMAL(10,2) DEFAULT 0.00,
                notes VARCHAR(255) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE
            )
            """
            
            # 授課老師上課下課打卡記錄表格
            teacher_attendance_table = """
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
                FOREIGN KEY (schedule_id) REFERENCES course_schedules(id) ON DELETE SET NULL
            )
            """
            
            # 系統設定表格 (用於打卡 IP 限制等設定)
            system_settings_table = """
            CREATE TABLE IF NOT EXISTS system_settings (
                setting_key VARCHAR(100) PRIMARY KEY,
                setting_value TEXT,
                description VARCHAR(255) NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """

            # 執行表格建立
            cursor.execute(students_table)
            cursor.execute(rooms_table)
            cursor.execute(teachers_table)
            cursor.execute(styles_table)
            cursor.execute(teacher_styles_table)
            cursor.execute(courses_table)
            cursor.execute(schedules_table)
            cursor.execute(enrollments_table)
            cursor.execute(admin_users_table)
            cursor.execute(staff_attendance_table)
            cursor.execute(teacher_attendance_table)
            # 課程價目表表格
            pricing_plans_table = """
            CREATE TABLE IF NOT EXISTS pricing_plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                subtitle VARCHAR(100) NULL,
                price VARCHAR(50) NOT NULL,
                unit VARCHAR(100) NOT NULL,
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
            """
            cursor.execute(pricing_plans_table)
            cursor.execute(system_settings_table)

            # 活動花絮相簿與照片表格
            gallery_albums_table = """
            CREATE TABLE IF NOT EXISTS gallery_albums (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(150) NOT NULL,
                description TEXT NULL,
                cover_image TEXT NULL,
                event_date DATE NULL,
                sort_order INT DEFAULT 0,
                is_published BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            gallery_photos_table = """
            CREATE TABLE IF NOT EXISTS gallery_photos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                album_id INT NOT NULL,
                image_url TEXT NOT NULL,
                description VARCHAR(255) NULL,
                sort_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (album_id) REFERENCES gallery_albums(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(gallery_albums_table)
            cursor.execute(gallery_photos_table)

            # 確保 admin_users password 欄位長度至少 255 以支援密碼雜湊
            try:
                cursor.execute("ALTER TABLE admin_users MODIFY COLUMN password VARCHAR(255) NOT NULL")
            except Exception:
                pass

            # 插入預設管理員、櫃檯、老師帳號（密碼預設經過雜湊加鹽處理）
            cursor.execute("SELECT COUNT(*) FROM admin_users")
            admin_cnt = cursor.fetchone()
            cnt = admin_cnt[0] if isinstance(admin_cnt, tuple) else (admin_cnt.get('COUNT(*)', 0) if isinstance(admin_cnt, dict) else 0)
            if cnt == 0:
                admin_hash = hash_password('admin123')
                desk_hash = hash_password('desk123')
                teacher_hash = hash_password('teacher123')
                seed_admin_users = """
                INSERT IGNORE INTO admin_users (id, username, password, name, role, phone, teacher_id) VALUES
                (1, 'admin', %s, '系統管理員', 'admin', '0911000111', NULL),
                (2, 'counter', %s, '櫃檯客服', 'desk', '0922000222', NULL),
                (3, 'teacher', %s, '張美麗老師', 'teacher', '0933000333', 1)
                """
                cursor.execute(seed_admin_users, (admin_hash, desk_hash, teacher_hash))

            # 插入預設系統設定
            seed_system_settings = """
            INSERT IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
            ('attendance_ip_restriction_enabled', '0', '打卡IP限制開關(0=關閉, 1=開啟)'),
            ('attendance_allowed_ips', '', '允許打卡的IP白名單(逗號或換行分隔)'),
            ('navbar_logo_type', 'text', '主導航列LOGO類型 (text:文字名稱, image:圖片LOGO)'),
            ('navbar_logo_text', 'Dance Studio', '主導航列文字名稱'),
            ('navbar_logo_image', '', '主導航列LOGO圖片網址')
            """
            cursor.execute(seed_system_settings)

            # 插入預設須知設定與預設方案
            seed_pricing_settings = """
            INSERT IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
            ('pricing_notice_title', '學員報名與上課須知', '課程價目表須知標題'),
            ('pricing_notice_content', '所有常規課程皆需提前於線上系統或向官方 LINE 預約登記。\n堂數方案為個人專屬權益，限本人上課使用，不得轉讓或轉售他人。\n方案自購買啟用起計，請於各方案指定之有效期限內使用完畢。\n若需取消或請假，請最晚於課程開始前 2 小時完成線上取消，以免扣除堂數。\n如遇天然災害或政府宣佈停班停課，本工作室常規課程將自動順延。', '課程價目表學員須知內容(每行一項)'),
            ('bank_name', '國泰世華銀行', '工作室匯款銀行名稱'),
            ('bank_code', '013', '工作室匯款銀行代碼'),
            ('bank_account', '012-34-567890-1', '工作室匯款帳號'),
            ('bank_account_name', 'Dance Studio 舞蹈工作室', '工作室匯款戶名'),
            ('bank_notes', '請先完成匯款後，於下方填寫您的轉帳帳號後 5 碼，以便工作人員核帳開通堂數。', '工作室匯款附註與說明')
            """
            cursor.execute(seed_pricing_settings)

            cursor.execute("SELECT COUNT(*) FROM pricing_plans")
            cnt_row = cursor.fetchone()
            if cnt_row and (cnt_row[0] if isinstance(cnt_row, tuple) else cnt_row.get('COUNT(*)', 0)) == 0:
                default_plans = [
                    ('單堂體驗', '適合初次體驗的學員', '$500', '/ 堂', None, False,
                     json.dumps(['適合初次體驗的學員', '可任選一堂常規舞蹈課', '專業教練動作引導', '課後舞風諮詢'], ensure_ascii=False),
                     '買課', '/contact', 1, True),
                    ('小資方案', '適合規律每週練習者', '$3,200', '/ 8 堂 (平均 $400/堂)', None, False,
                     json.dumps(['適合規律每週練習者', '使用期限 2 個月', '全時段常規課程皆適用', '請假彈性保留堂數'], ensure_ascii=False),
                     '買課', '/contact', 2, True),
                    ('熱血方案', '適合重度舞蹈愛好者', '$6,000', '/ 20 堂 (平均 $300/堂)', None, True,
                     json.dumps(['適合重度舞蹈愛好者', '使用期限 4 個月', '全常規課程自由選修', '贈送專屬品牌運動毛巾', '享成果發表報名優先權'], ensure_ascii=False),
                     '買課', '/contact', 3, True),
                    ('尊榮月費', '當月份不限堂數暢快跳', '$8,000', '/ 月 (無限堂數)', None, False,
                     json.dumps(['當月份不限堂數暢快跳', '全常規課程皆可預約', '場地個人租借 8 折特惠', '周邊服飾商品 9 折優惠'], ensure_ascii=False),
                     '買課', '/contact', 4, True)
                ]
                cursor.executemany("""
                    INSERT INTO pricing_plans (title, subtitle, price, unit, original_price, is_popular, features, button_text, button_link, sort_order, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, default_plans)

            # 檢查並插入預設「會員年費」方案 (若不存在)
            cursor.execute("SELECT id FROM pricing_plans WHERE plan_type = 'membership_fee' OR title = '會員年費'")
            if not cursor.fetchone():
                membership_features = json.dumps([
                    '成為正式年度會員',
                    '專屬會員資格有效期限 1 年 (365天)',
                    '享有學員購課與優先報名權益',
                    '專屬會員迎賓禮與活動專屬優惠'
                ], ensure_ascii=False)
                cursor.execute("""
                    INSERT INTO pricing_plans 
                    (title, subtitle, price, unit, plan_type, classes_count, validity_days, original_price, is_popular, requires_membership, features, button_text, button_link, sort_order, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, ('會員年費', '年度專屬會員資格與優惠', '$1,200', '/ 年 (365天)', 'membership_fee', 0, 365, None, 0, 0, membership_features, '買課', '/contact', 5, 1))

            # 檢查並插入預設活動花絮相簿與照片
            cursor.execute("SELECT COUNT(*) FROM gallery_albums")
            gal_cnt_row = cursor.fetchone()
            if gal_cnt_row and (gal_cnt_row[0] if isinstance(gal_cnt_row, tuple) else gal_cnt_row.get('COUNT(*)', 0)) == 0:
                default_albums = [
                    ('2023 年度成果展', '學員們一年努力的成果展示，充滿自信與熱情的舞台時刻。', 'https://picsum.photos/600/400?random=23', '2023-12-15', 1, 1, [
                        ('https://picsum.photos/800/600?random=23', '學員們一年努力的成果展示 - 精彩瞬間1', 1),
                        ('https://picsum.photos/800/600?random=231', '學員們一年努力的成果展示 - 精彩瞬間2', 2),
                        ('https://picsum.photos/800/600?random=232', '學員們一年努力的成果展示 - 精彩瞬間3', 3),
                    ]),
                    ('街舞大賽', '熱血沸騰的街舞對決，舞者齊聚展現極限爆發力！', 'https://picsum.photos/600/400?random=24', '2023-10-20', 2, 1, [
                        ('https://picsum.photos/800/600?random=24', '熱血沸騰的街舞對決 - 選手風采1', 1),
                        ('https://picsum.photos/800/600?random=241', '熱血沸騰的街舞對決 - 選手風采2', 2),
                        ('https://picsum.photos/800/600?random=242', '熱血沸騰的街舞對決 - 選手風采3', 3),
                    ]),
                    ('國際大師工作坊', '與國際知名舞者近距離學習，汲取頂尖舞感與技巧！', 'https://picsum.photos/600/400?random=25', '2023-08-12', 3, 1, [
                        ('https://picsum.photos/800/600?random=25', '與國際知名舞者近距離學習 - 大師授課', 1),
                        ('https://picsum.photos/800/600?random=251', '與國際知名舞者近距離學習 - 互動交流', 2),
                    ]),
                    ('聖誕派對', '充滿歡樂與舞蹈的聖誕節，溫馨同樂夜！', 'https://picsum.photos/600/400?random=26', '2023-12-25', 4, 1, [
                        ('https://picsum.photos/800/600?random=26', '充滿歡樂與舞蹈的聖誕節 - 派對現場', 1),
                        ('https://picsum.photos/800/600?random=261', '充滿歡樂與舞蹈的聖誕節 - 聖誕表演', 2),
                    ]),
                    ('快閃活動', '街頭突擊，展現舞蹈魅力，引爆全場歡呼！', 'https://picsum.photos/600/400?random=27', '2023-06-18', 5, 1, [
                        ('https://picsum.photos/800/600?random=27', '街頭突擊，展現舞蹈魅力 - 街頭快閃', 1),
                        ('https://picsum.photos/800/600?random=271', '街頭突擊，展現舞蹈魅力 - 觀眾互動', 2),
                    ]),
                    ('學員練習日常', '舞者們日復一日的堅持與努力，汗水鑄就的精彩！', 'https://picsum.photos/600/400?random=28', '2023-05-10', 6, 1, [
                        ('https://picsum.photos/800/600?random=28', '舞者們日復一日的堅持與努力 - 練習剪影', 1),
                        ('https://picsum.photos/800/600?random=281', '舞者們日復一日的堅持與努力 - 汗水與堅持', 2),
                    ]),
                ]
                for alb in default_albums:
                    cursor.execute("""
                        INSERT INTO gallery_albums (title, description, cover_image, event_date, sort_order, is_published)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (alb[0], alb[1], alb[2], alb[3], alb[4], alb[5]))
                    alb_id = cursor.lastrowid
                    for p in alb[6]:
                        cursor.execute("""
                            INSERT INTO gallery_photos (album_id, image_url, description, sort_order)
                            VALUES (%s, %s, %s, %s)
                        """, (alb_id, p[0], p[1], p[2]))
            
            # 首頁橫幅 (Hero Banners) 表格
            banners_table = """
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
            """
            cursor.execute(banners_table)

            # 插入預設首頁輪播橫幅 (若表格為空)
            cursor.execute("SELECT COUNT(*) FROM banners")
            banner_cnt_row = cursor.fetchone()
            if banner_cnt_row and (banner_cnt_row[0] if isinstance(banner_cnt_row, tuple) else banner_cnt_row.get('COUNT(*)', 0)) == 0:
                default_banners = [
                    (
                        '釋放你的節奏，舞出你的熱情',
                        '無論是零基礎新手或資深舞者，在 Dance Studio 都能找到最適合你的專屬舞台。',
                        '✨ 啟動你的舞蹈新生活',
                        'warning',
                        'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=1920&q=80',
                        '立即預約課程',
                        '/schedule',
                        'primary',
                        '認識師資團隊',
                        '/instructors',
                        'outline-light',
                        5000,
                        1,
                        1
                    ),
                    (
                        '多元舞風體系 × 專業細膩教學',
                        '流行街舞、K-POP MV、抒情爵士、芭蕾律動，循序漸進拆解每個核心動作。',
                        '👑 頂尖專業名師陣容',
                        'primary',
                        'https://images.unsplash.com/photo-1547153760-18fc86324498?auto=format&fit=crop&w=1920&q=80',
                        '查看本週課表',
                        '/schedule',
                        'warning',
                        '課程收費方案',
                        '/pricing',
                        'outline-light',
                        5000,
                        2,
                        1
                    ),
                    (
                        '高規格減震地板與專業環繞音響',
                        '四大獨立主題練習室，明亮寬敞的空間與貼心休息區，享受最極致的跳舞體驗。',
                        '🏢 專業國際級練習空間',
                        'success',
                        'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=1920&q=80',
                        '參觀場地環境',
                        '/venue',
                        'light',
                        '關於我們',
                        '/about',
                        'outline-light',
                        5000,
                        3,
                        1
                    )
                ]
                cursor.executemany("""
                    INSERT INTO banners (
                        title, subtitle, badge_text, badge_color, image_url,
                        primary_button_text, primary_button_link, primary_button_style,
                        secondary_button_text, secondary_button_link, secondary_button_style,
                        interval_ms, sort_order, is_active
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, default_banners)

            # 各分頁頂部橫幅 (Page Banners) 表格
            page_banners_table = """
            CREATE TABLE IF NOT EXISTS page_banners (
                page_key VARCHAR(50) PRIMARY KEY,
                page_name VARCHAR(100) NOT NULL,
                title VARCHAR(255) NOT NULL,
                subtitle VARCHAR(255) NULL,
                image_url TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(page_banners_table)

            default_page_banners = [
                ('about', '關於我們', '關於我們 / ABOUT US', '致力於為所有舞蹈愛好者提供最專業、多元的學習體驗', 'https://picsum.photos/1920/500?random=9'),
                ('history', '品牌沿革', '品牌沿革 / HISTORY', '見證 Dance Studio 歷年來的里程碑與熱血歷程', 'https://picsum.photos/1920/500?random=8'),
                ('instructors', '師資團隊', '師資團隊 / INSTRUCTORS', '匯聚業界頂尖名師，細膩指導每一步身體律動', 'https://picsum.photos/1920/500?random=14'),
                ('schedule', '課程時間表', '課程時間表 / SCHEDULE', '彈性多元的時段規劃，全方位探索熱門舞風', 'https://picsum.photos/1920/500?random=36'),
                ('pricing', '課程價目表', '課程價目表 / PRICING', '透明彈性的收費方案，滿足不同學習階段需求', 'https://picsum.photos/1920/500?random=35'),
                ('gallery', '活動花絮', '活動花絮 / GALLERY', '回顧學員舞台演出與歡樂練習日常的精彩瞬間', 'https://picsum.photos/1920/500?random=22'),
                ('venue', '場地租借', '場地租借 / VENUE', '專業避震地板、頂級音響設備，打造最佳跳舞空間', 'https://picsum.photos/1920/500?random=29'),
                ('faq', '常見問題', '常見問題 / FAQ', '快速解答學員常見疑問，新手安心踏出第一步', 'https://picsum.photos/1920/500?random=33'),
                ('contact', '聯絡我們', '聯絡我們 / CONTACT', '歡迎預約參觀、諮詢課程或與我們聯繫交流', 'https://picsum.photos/1920/500?random=34')
            ]
            for pb in default_page_banners:
                cursor.execute("""
                    INSERT IGNORE INTO page_banners (page_key, page_name, title, subtitle, image_url)
                    VALUES (%s, %s, %s, %s, %s)
                """, pb)

            # 檢查並添加新欄位 (為了向後兼容)
            try:
                # 檢查 course_schedules 表格是否有 allow_enrollment 欄位
                cursor.execute("SHOW COLUMNS FROM course_schedules LIKE 'allow_enrollment'")
                result = cursor.fetchone()
                
                if not result:
                    # 如果沒有該欄位，則添加它
                    print("正在添加 allow_enrollment 欄位到 course_schedules 表格...")
                    cursor.execute("ALTER TABLE course_schedules ADD COLUMN allow_enrollment BOOLEAN DEFAULT TRUE")
                    print("allow_enrollment 欄位添加成功")
                
                # 檢查 enrollments 表格是否有 deducted_classes 欄位
                cursor.execute("SHOW COLUMNS FROM enrollments LIKE 'deducted_classes'")
                result = cursor.fetchone()
                
                if not result:
                    # 如果沒有該欄位，則添加它
                    print("正在添加 deducted_classes 欄位到 enrollments 表格...")
                    cursor.execute("ALTER TABLE enrollments ADD COLUMN deducted_classes INT DEFAULT 1 AFTER status")
                    print("deducted_classes 欄位添加成功")

                # 檢查 students 表格是否有 password_hash 欄位
                cursor.execute("SHOW COLUMNS FROM students LIKE 'password_hash'")
                result = cursor.fetchone()
                if not result:
                    print("正在添加 password_hash 欄位到 students 表格...")
                    cursor.execute("ALTER TABLE students ADD COLUMN password_hash VARCHAR(255) NULL AFTER phone")
                    print("password_hash 欄位添加成功")

                # 檢查 teachers 表格是否有 bank_account 欄位
                cursor.execute("SHOW COLUMNS FROM teachers LIKE 'bank_account'")
                result = cursor.fetchone()
                if not result:
                    print("正在添加 bank_account 欄位到 teachers 表格...")
                    cursor.execute("ALTER TABLE teachers ADD COLUMN bank_account VARCHAR(100) NULL AFTER hourly_rate")
                    print("bank_account 欄位添加成功")

                # 檢查 courses 表格是否有 low_student_threshold 欄位
                cursor.execute("SHOW COLUMNS FROM courses LIKE 'low_student_threshold'")
                result = cursor.fetchone()
                if not result:
                    print("正在添加 low_student_threshold 與 low_student_salary 欄位到 courses 表格...")
                    cursor.execute("ALTER TABLE courses ADD COLUMN low_student_threshold INT DEFAULT 0 AFTER base_salary, ADD COLUMN low_student_salary DECIMAL(10,2) DEFAULT 0.00 AFTER low_student_threshold")
                    print("low_student_threshold 與 low_student_salary 欄位添加成功")

                # 檢查 admin_users 表格是否有 hourly_rate 與 bank_account 欄位
                cursor.execute("SHOW COLUMNS FROM admin_users LIKE 'hourly_rate'")
                result = cursor.fetchone()
                if not result:
                    print("正在添加 hourly_rate 與 bank_account 欄位到 admin_users 表格...")
                    cursor.execute("ALTER TABLE admin_users ADD COLUMN hourly_rate DECIMAL(10,2) DEFAULT 0.00 AFTER phone, ADD COLUMN bank_account VARCHAR(100) NULL AFTER hourly_rate")
                    print("hourly_rate 與 bank_account 欄位添加成功")

                # 檢查 staff_attendance 表格是否有 effective_clock_in 欄位
                cursor.execute("SHOW COLUMNS FROM staff_attendance LIKE 'effective_clock_in'")
                result = cursor.fetchone()
                if not result:
                    print("正在添加 effective_clock_in 與 effective_clock_out 欄位到 staff_attendance 表格...")
                    cursor.execute("ALTER TABLE staff_attendance ADD COLUMN effective_clock_in DATETIME NULL AFTER clock_in, ADD COLUMN effective_clock_out DATETIME NULL AFTER clock_out")
                    print("effective_clock_in 與 effective_clock_out 欄位添加成功")

                # 檢查 teacher_attendance 表格是否有 course_id 欄位
                cursor.execute("SHOW COLUMNS FROM teacher_attendance LIKE 'course_id'")
                result = cursor.fetchone()
                if not result:
                    print("正在添加 course_id 欄位到 teacher_attendance 表格...")
                    cursor.execute("ALTER TABLE teacher_attendance ADD COLUMN course_id INT NULL AFTER schedule_id")
                    print("course_id 欄位添加成功")

                # 檢查 teachers 表格是否有 avatar_url 欄位
                cursor.execute("SHOW COLUMNS FROM teachers LIKE 'avatar_url'")
                result = cursor.fetchone()
                if not result:
                    print("正在添加 avatar_url 欄位到 teachers 表格...")
                    cursor.execute("ALTER TABLE teachers ADD COLUMN avatar_url TEXT NULL AFTER bank_account")
                    print("avatar_url 欄位添加成功")

                # 檢查 staff_attendance 表格是否有 clock_in_ip 欄位
                cursor.execute("SHOW COLUMNS FROM staff_attendance LIKE 'clock_in_ip'")
                if not cursor.fetchone():
                    print("正在添加 clock_in_ip 與 clock_out_ip 欄位到 staff_attendance 表格...")
                    cursor.execute("ALTER TABLE staff_attendance ADD COLUMN clock_in_ip VARCHAR(50) NULL AFTER clock_out, ADD COLUMN clock_out_ip VARCHAR(50) NULL AFTER clock_in_ip")
                    print("staff_attendance IP 欄位添加成功")

                # 檢查 teacher_attendance 表格是否有 clock_in_ip 欄位
                cursor.execute("SHOW COLUMNS FROM teacher_attendance LIKE 'clock_in_ip'")
                if not cursor.fetchone():
                    print("正在添加 clock_in_ip 與 clock_out_ip 欄位到 teacher_attendance 表格...")
                    cursor.execute("ALTER TABLE teacher_attendance ADD COLUMN clock_in_ip VARCHAR(50) NULL AFTER clock_out, ADD COLUMN clock_out_ip VARCHAR(50) NULL AFTER clock_in_ip")
                    print("teacher_attendance IP 欄位添加成功")

                # 檢查 students 表格是否有 line_user_id 欄位
                cursor.execute("SHOW COLUMNS FROM students LIKE 'line_user_id'")
                if not cursor.fetchone():
                    print("正在添加 line_user_id 等 LINE 關聯欄位到 students 表格...")
                    cursor.execute("ALTER TABLE students ADD COLUMN line_user_id VARCHAR(100) UNIQUE NULL COMMENT 'LINE User ID'")
                    cursor.execute("ALTER TABLE students ADD COLUMN line_display_name VARCHAR(100) NULL COMMENT 'LINE 暱稱'")
                    cursor.execute("ALTER TABLE students ADD COLUMN line_picture_url VARCHAR(255) NULL COMMENT 'LINE 大頭貼'")
                    cursor.execute("ALTER TABLE students ADD COLUMN line_linked_at DATETIME NULL COMMENT 'LINE 關聯時間'")
                    print("students 表格 LINE 欄位添加成功")

                # 檢查 course_schedules 表格是否有 teacher_id 與 is_substitute 欄位
                cursor.execute("SHOW COLUMNS FROM course_schedules LIKE 'teacher_id'")
                if not cursor.fetchone():
                    print("正在添加 teacher_id, is_substitute, substitute_notes 欄位到 course_schedules 表格...")
                    cursor.execute("ALTER TABLE course_schedules ADD COLUMN teacher_id INT NULL AFTER course_id")
                    cursor.execute("ALTER TABLE course_schedules ADD COLUMN is_substitute BOOLEAN DEFAULT FALSE AFTER allow_enrollment")
                    cursor.execute("ALTER TABLE course_schedules ADD COLUMN substitute_notes VARCHAR(255) NULL AFTER is_substitute")
                    try:
                        cursor.execute("ALTER TABLE course_schedules ADD CONSTRAINT fk_cs_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL")
                    except Exception:
                        pass
                    print("course_schedules 代課欄位添加成功")

                # 檢查 teacher_attendance 表格是否有 is_substitute 與 original_teacher_id 欄位
                cursor.execute("SHOW COLUMNS FROM teacher_attendance LIKE 'is_substitute'")
                if not cursor.fetchone():
                    print("正在添加 is_substitute 與 original_teacher_id 欄位到 teacher_attendance 表格...")
                    cursor.execute("ALTER TABLE teacher_attendance ADD COLUMN is_substitute BOOLEAN DEFAULT FALSE AFTER calculated_salary")
                    cursor.execute("ALTER TABLE teacher_attendance ADD COLUMN original_teacher_id INT NULL AFTER is_substitute")
                    print("teacher_attendance 代課欄位添加成功")

                ensure_pricing_database_tables(cursor)

                # 檢查 students 表格是否有 monthly_pass_expiry 欄位 (月費與會員年費分開記錄)
                cursor.execute("SHOW COLUMNS FROM students LIKE 'monthly_pass_expiry'")
                if not cursor.fetchone():
                    print("正在添加 monthly_pass_expiry 欄位到 students 表格...")
                    cursor.execute("ALTER TABLE students ADD COLUMN monthly_pass_expiry DATE NULL COMMENT '月費到期日'")
                    print("monthly_pass_expiry 欄位添加成功")

                # 檢查 courses 表格是否有 allow_monthly_pass 欄位 (是否適用月費暢跳)
                cursor.execute("SHOW COLUMNS FROM courses LIKE 'allow_monthly_pass'")
                if not cursor.fetchone():
                    print("正在添加 allow_monthly_pass 欄位到 courses 表格...")
                    cursor.execute("ALTER TABLE courses ADD COLUMN allow_monthly_pass BOOLEAN DEFAULT TRUE COMMENT '是否支援月費暢跳' AFTER price")
                    print("allow_monthly_pass 欄位添加成功")

                # 檢查 pricing_plans 表格是否有 requires_membership 欄位 (限會員年費才可購買)
                cursor.execute("SHOW COLUMNS FROM pricing_plans LIKE 'requires_membership'")
                if not cursor.fetchone():
                    print("正在添加 requires_membership 欄位到 pricing_plans 表格...")
                    cursor.execute("ALTER TABLE pricing_plans ADD COLUMN requires_membership BOOLEAN DEFAULT FALSE COMMENT '是否限有效會員年費學員購買' AFTER is_popular")
                    print("pricing_plans requires_membership 欄位添加成功")

                # 檢查預設 LINE 設定
                cursor.execute("""
                INSERT IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
                ('line_login_enabled', '1', '是否啟用 LINE 快速登入與帳號關聯 (0=關閉, 1=開啟)'),
                ('line_channel_id', '', 'LINE Login Channel ID'),
                ('line_channel_secret', '', 'LINE Login Channel Secret'),
                ('line_official_id', '', '工作室 LINE 官方帳號 ID'),
                ('line_official_url', '', '工作室 LINE 官方加好友連結')
                """)
                    
            except mysql.connector.Error as err:
                print(f"添加欄位時發生錯誤: {err}")
            
            connection.commit()
            print("所有資料庫表格初始化成功")
            
        except mysql.connector.Error as err:
            print(f"建立表格錯誤: {err}")
        finally:
            cursor.close()
            connection.close()
    else:
        print("無法初始化資料庫表格 - 將在執行時重試")

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class Enrollment(Resource):
    def post(self):
        try:
            data = request.get_json() or {}
            student_name = (data.get('studentName') or data.get('student_name') or '').strip()
            lesson = data.get('lesson') or {}
            schedule_id = data.get('schedule_id')
            
            if not student_name:
                return {'error': '請輸入學生姓名'}, 400
            
            if not lesson and not schedule_id:
                return {'error': '缺少課程資訊'}, 400
            
            # 連接資料庫
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True, buffered=True)
                
                # 先查詢學生是否存在並取得剩餘堂數
                student_query = "SELECT id, name, remaining_classes, monthly_pass_expiry, membership_expiry FROM students WHERE name = %s"
                cursor.execute(student_query, (student_name,))
                student = cursor.fetchone()
                
                if not student:
                    return {'error': f'查無學生「{student_name}」，請至櫃檯辦理會員後再進行報名'}, 400
                
                # 查詢課程的扣堂數和容量檢查
                course_price = 1  # 預設扣除1堂
                course_capacity = 15  # 預設容量
                current_enrollment = 0
                
                course_id = None
                if schedule_id:
                    # 查詢課程價格和課程人數上限及課程資訊
                    price_query = """
                    SELECT c.id as course_id, c.name as course_name, c.price, c.max_students as course_capacity,
                           c.allow_monthly_pass,
                           c.level, s.name as dance_type, COALESCE(sub_t.name, t.name) as teacher_name,
                           cs.schedule_date, cs.day_of_week, cs.start_time, cs.end_time, cs.allow_enrollment,
                           COUNT(e.id) as current_enrollment
                    FROM course_schedules cs 
                    JOIN courses c ON cs.course_id = c.id 
                    LEFT JOIN styles s ON c.style_id = s.id
                    LEFT JOIN teachers t ON c.teacher_id = t.id
                    LEFT JOIN teachers sub_t ON cs.teacher_id = sub_t.id

                LEFT JOIN enrollments e ON cs.id = e.schedule_id AND e.status = 'confirmed'

                WHERE cs.id = %s
                    GROUP BY cs.id, c.id, c.name, c.price, c.max_students, c.allow_monthly_pass, c.level, s.name, t.name, sub_t.name, 
                             cs.schedule_date, cs.day_of_week, cs.start_time, cs.end_time, cs.allow_enrollment
                    """
                    cursor.execute(price_query, (schedule_id,))
                    price_result = cursor.fetchone()
                    if not price_result:
                        return {'error': '查無此課程時間表資料'}, 404

                    # 檢查是否為過去日期（昨天及昨天以前不可預約）
                    sched_date = price_result.get('schedule_date')
                    if sched_date:
                        today_date = datetime.now().date()
                        if isinstance(sched_date, str):
                            sched_date_val = datetime.strptime(sched_date[:10], '%Y-%m-%d').date()
                        else:
                            sched_date_val = sched_date
                        if sched_date_val < today_date:
                            return {'error': '無法預約過去的課程時段（昨天與昨天以前不開放預約）！'}, 400

                    if price_result.get('allow_enrollment') == 0:
                        return {'error': '很抱歉，此課程目前不開放線上預約！'}, 400

                    course_id = price_result.get('course_id')
                    if price_result.get('price'):
                        course_price = int(price_result['price'])
                    if price_result.get('course_capacity'):
                        course_capacity = price_result['course_capacity']
                    current_enrollment = price_result['current_enrollment'] or 0
                    
                    if not lesson.get('name'):
                        lesson['name'] = price_result.get('course_name') or ''
                    if not lesson.get('teacher'):
                        lesson['teacher'] = price_result.get('teacher_name') or ''
                    if not lesson.get('day'):
                        lesson['day'] = price_result.get('day_of_week') or ''
                    if not lesson.get('time') and price_result.get('start_time') and price_result.get('end_time'):
                        lesson['time'] = f"{str(price_result['start_time'])[:5]} - {str(price_result['end_time'])[:5]}"
                    if not lesson.get('level'):
                        lesson['level'] = price_result.get('level') or ''
                    if not lesson.get('type'):
                        lesson['type'] = price_result.get('dance_type') or ''
                
                # 檢查是否重複報名（同一學生在同一課程時段且狀態為 confirmed）
                if schedule_id:
                    check_dup_query = """
                    SELECT id FROM enrollments 
                    WHERE (student_id = %s OR student_name = %s)
                      AND schedule_id = %s 
                      AND status = 'confirmed'
                    """
                    cursor.execute(check_dup_query, (student['id'], student_name, schedule_id))
                    existing = cursor.fetchone()
                    if existing:
                        return {'error': '您已經預約過此時段課程，無法重複報名！'}, 400
                elif lesson.get('name') and lesson.get('time'):
                    check_dup_query = """
                    SELECT id FROM enrollments 
                    WHERE (student_id = %s OR student_name = %s)
                      AND lesson_name = %s
                      AND lesson_day = %s
                      AND lesson_time = %s
                      AND status = 'confirmed'
                    """
                    cursor.execute(check_dup_query, (student['id'], student_name, lesson.get('name'), lesson.get('day'), lesson.get('time')))
                    existing = cursor.fetchone()
                    if existing:
                        return {'error': '您已經預約過此時段課程，無法重複報名！'}, 400

                # 檢查是否已滿額
                if current_enrollment >= course_capacity:
                    return {'error': f'很抱歉，此課程報名人數已滿（{current_enrollment}/{course_capacity}）'}, 400
                
                # 檢查學員是否有有效「月費暢跳」方案資格
                has_valid_monthly_pass = False
                monthly_pass_exp = student.get('monthly_pass_expiry')
                if monthly_pass_exp:
                    if isinstance(monthly_pass_exp, str):
                        try:
                            monthly_pass_exp = datetime.strptime(monthly_pass_exp[:10], '%Y-%m-%d').date()
                        except Exception:
                            monthly_pass_exp = None
                    target_date = sched_date_val if 'sched_date_val' in locals() and sched_date_val else datetime.now().date()
                    if monthly_pass_exp and monthly_pass_exp >= target_date:
                        has_valid_monthly_pass = True

                # 檢查課程是否支援月費暢跳 (預設為 True)
                course_allows_monthly = True
                if schedule_id and 'price_result' in locals() and price_result:
                    raw_allow = price_result.get('allow_monthly_pass')
                    if raw_allow is not None and str(raw_allow) in ('0', 'False', 'false'):
                        course_allows_monthly = False

                is_monthly_pass_booking = has_valid_monthly_pass and course_allows_monthly

                # 剩餘堂數與扣堂判斷
                remaining_classes = student['remaining_classes'] or 0
                if is_monthly_pass_booking:
                    deducted_classes = 0
                    new_remaining_classes = remaining_classes
                else:
                    deducted_classes = course_price
                    if remaining_classes < deducted_classes:
                        return {'error': f'您的剩餘堂數不足（目前剩餘：{remaining_classes}堂，需要：{deducted_classes}堂），請至櫃檯儲值後再進行報名'}, 400
                    new_remaining_classes = remaining_classes - deducted_classes

                
                # 開始事務
                cursor.execute("START TRANSACTION")
                
                # 扣除對應堂數
                if deducted_classes > 0:
    
                    cursor.execute("UPDATE students SET remaining_classes = %s WHERE id = %s", (new_remaining_classes, student['id']))
                # 扣除完成


                
                # 插入報名記錄
                insert_query = """
                INSERT INTO enrollments 
                (student_id, course_id, schedule_id, student_name, lesson_name, lesson_time, lesson_day, 
                 lesson_teacher, lesson_level, lesson_type, deducted_classes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                -- old_values_ignored
                """
                
                values = (
                    student['id'],
                    course_id,
                    schedule_id,
                    student_name,
                    lesson.get('name', ''),
                    lesson.get('time', ''),
                    lesson.get('day', ''),
                    lesson.get('teacher', ''),
                    lesson.get('level', ''),
                    lesson.get('type', ''),
                    deducted_classes  # 記錄扣除的堂數 (若為月費則為 0)
                )
                
                cursor.execute(insert_query, values)
                
                # 提交事務
                connection.commit()
                
                enrollment_id = cursor.lastrowid
                
                print(f"=== 新的課程報名 ===")
                print(f"報名編號: {enrollment_id}")
                print(f"學生姓名: {student_name}")
                print(f"課程名稱: {lesson.get('name')}")
                print(f"上課時間: {lesson.get('day')} {lesson.get('time')}")
                print(f"授課老師: {lesson.get('teacher')}")
                print(f"課程扣堂數: {course_price}")
                print(f"扣除前堂數: {remaining_classes}")
                print(f"扣除後堂數: {new_remaining_classes}")
                print("==================")
                
                return {
                    'success': True,
                    'message': '報名成功！（已套用月費暢跳，免扣堂數）' if is_monthly_pass_booking else '報名成功！',
                    'enrollment': {
                        'id': enrollment_id,
                        'studentName': student_name,
                        'lesson': lesson,
                        'enrollmentTime': datetime.now().isoformat(),
                        'remainingClasses': new_remaining_classes,
                        'usedClasses': deducted_classes,
                        'isMonthlyPass': is_monthly_pass_booking
                    }
                }, 201
                
            except mysql.connector.Error as err:
                import traceback
                traceback.print_exc()
                print(f"資料庫操作錯誤: {err}", flush=True)
                # 回滾事務
                connection.rollback()
                return {'error': f'報名處理失敗 (DB): {err}'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"報名處理錯誤: {str(e)}", flush=True)
            return {'error': f'報名處理失敗: {str(e)}'}, 500
    
    def get(self):
        """取得所有報名記錄"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM enrollments ORDER BY enrollment_time DESC")
                enrollments = cursor.fetchall()
                
                # 轉換 datetime 物件為 ISO 格式字串
                for enrollment in enrollments:
                    if enrollment.get('enrollment_time') and isinstance(enrollment['enrollment_time'], datetime):
                        enrollment['enrollment_time'] = enrollment['enrollment_time'].isoformat()
                
                return {
                    'success': True,
                    'enrollments': enrollments,
                    'total': len(enrollments)
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢錯誤: {err}")
                return {'error': '查詢失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢錯誤: {str(e)}")
            return {'error': '查詢失敗'}, 500

def format_student_info(student):
    """格式化學員資料，過濾敏感密碼雜湊值並序列化日期"""
    if not student:
        return None
    res = dict(student)
    res.pop('password_hash', None)
    if not res.get('membership_expiry') and res.get('expiry_date'):
        res['membership_expiry'] = res['expiry_date']
    for field in ['created_at', 'updated_at', 'line_linked_at']:
        if res.get(field) and isinstance(res[field], datetime):
            res[field] = res[field].isoformat()
    for field in ['membership_expiry', 'monthly_pass_expiry', 'date_of_birth', 'expiry_date']:
        if res.get(field) and isinstance(res[field], date):
            res[field] = res[field].isoformat()
    return res

class Students(Resource):
    def get(self):
        """取得所有學生"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                
                search_name = request.args.get('name')
                
                query = "SELECT * FROM students"
                params = []
                
                if search_name:
                    query += " WHERE name LIKE %s"
                    params.append(f"%{search_name}%")
                    
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                raw_students = cursor.fetchall()
                
                students = [format_student_info(s) for s in raw_students]
                
                return {
                    'success': True,
                    'students': students,
                    'total': len(students)
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢學生錯誤: {err}")
                return {'error': '查詢學生失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢學生錯誤: {str(e)}")
            return {'error': '查詢學生失敗'}, 500
    
    def post(self):
        """新增學生"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return {'error': '缺少必要欄位：姓名'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                insert_query = """
                INSERT INTO students 
                (name, email, phone, date_of_birth, emergency_contact, emergency_phone, bank_last_5, medical_notes, remaining_classes, membership_expiry, monthly_pass_expiry) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data.get('name'),
                    data.get('email'),
                    data.get('phone'),
                    data.get('date_of_birth'),
                    data.get('emergency_contact'),
                    data.get('emergency_phone'),
                    data.get('bank_last_5') or None,
                    data.get('medical_notes'),
                    data.get('remaining_classes', 0),
                    data.get('membership_expiry') or None,
                    data.get('monthly_pass_expiry') or None,
                )
                
                cursor.execute(insert_query, values)
                connection.commit()
                
                student_id = cursor.lastrowid
                
                return {
                    'success': True,
                    'message': '學生新增成功！',
                    'student_id': student_id
                }, 201
                
            except mysql.connector.Error as err:
                print(f"新增學生錯誤: {err}")
                return {'error': '新增學生失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"新增學生錯誤: {str(e)}")
            return {'error': '新增學生失敗'}, 500

class Teachers(Resource):
    def get(self):
        """取得所有老師及其風格"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                
                search_name = request.args.get('name')
                teacher_id = request.args.get('teacher_id')
                
                # 查詢老師 (含後台登入帳號)
                query = """
                SELECT t.*, u.id as user_id, u.username as account_username
                FROM teachers t
                LEFT JOIN admin_users u ON u.teacher_id = t.id AND u.role = 'teacher'
                WHERE 1=1
                """
                params = []
                
                if search_name:
                    query += " AND t.name LIKE %s"
                    params.append(f"%{search_name}%")

                if teacher_id:
                    query += " AND t.id = %s"
                    params.append(teacher_id)

                is_featured = request.args.get('is_featured')
                if is_featured is not None:
                    query += " AND t.is_featured = %s"
                    params.append(1 if str(is_featured).lower() in ['1', 'true'] else 0)
                
                query += " ORDER BY t.is_featured DESC, t.created_at DESC"
                
                cursor.execute(query, params)
                teachers = cursor.fetchall()
                
                # 查詢所有老師的風格
                teacher_ids = [teacher['id'] for teacher in teachers]
                if teacher_ids:
                    style_query = """
                    SELECT ts.teacher_id, s.id as style_id, s.name as style_name
                    FROM teacher_styles ts
                    JOIN styles s ON ts.style_id = s.id
                    WHERE ts.teacher_id IN (%s)
                    """ % ', '.join(['%s'] * len(teacher_ids))
                    
                    cursor.execute(style_query, teacher_ids)
                    styles = cursor.fetchall()
                    
                    # 將風格整理到對應的老師物件中
                    teacher_styles = {teacher_id: [] for teacher_id in teacher_ids}
                    for style in styles:
                        teacher_styles[style['teacher_id']].append({
                            'id': style['style_id'],
                            'name': style['style_name']
                        })
                    
                    # 將風格加入老師物件
                    for teacher in teachers:
                        teacher['styles'] = teacher_styles.get(teacher['id'], [])

                # 轉換 datetime 和 Decimal 物件為 ISO 格式字串
                for teacher in teachers:
                    if teacher.get('hourly_rate'):
                        teacher['hourly_rate'] = str(teacher['hourly_rate'])
                    for field in ['created_at', 'updated_at', 'line_linked_at']:
                        if teacher.get(field) and isinstance(teacher[field], datetime):
                            teacher[field] = teacher[field].isoformat()
                
                return {
                    'success': True,
                    'teachers': teachers,
                    'total': len(teachers)
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢老師錯誤: {err}")
                return {'error': '查詢老師失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢老師錯誤: {str(e)}")
            return {'error': '查詢老師失敗'}, 500
    
    def post(self):
        """新增老師"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return {'error': '缺少必要欄位：姓名'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                # 插入老師基本資料 (包含銀行帳號、大頭貼、主打星與年資)
                insert_teacher_query = """
                INSERT INTO teachers 
                (name, email, phone, experience_years, bio, hourly_rate, bank_account, avatar_url, is_featured) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                -- old_values_ignored
                """
                
                teacher_values = (
                    data.get('name'),
                    data.get('email'),
                    data.get('phone'),
                    data.get('experience_years'),
                    data.get('bio'),
                    data.get('hourly_rate'),
                    data.get('bank_account'),
                    data.get('avatar_url'),
                    1 if data.get('is_featured') else 0
                )
                
                cursor.execute(insert_teacher_query, teacher_values)
                teacher_id = cursor.lastrowid
                
                # 處理老師與風格的關聯
                style_ids = data.get('style_ids', [])
                if style_ids:
                    insert_style_query = """
                    INSERT INTO teacher_styles (teacher_id, style_id)
                    VALUES (%s, %s)
                    """
                    style_values = [(teacher_id, style_id) for style_id in style_ids]
                    cursor.executemany(insert_style_query, style_values)

                # 若有設定帳號與密碼，自動同步建立後台登入帳號
                raw_user = (data.get('account_username') or data.get('username') or '').strip()
                raw_pwd = (data.get('password') or '').strip()
                if raw_user:
                    cursor.execute("SELECT id FROM admin_users WHERE username = %s", (raw_user,))
                    if not cursor.fetchone():
                        cursor.execute("""
                        INSERT INTO admin_users (username, password, name, role, phone, teacher_id)
                        VALUES (%s, %s, %s, 'teacher', %s, %s)
                        """, (raw_user, raw_pwd or 'teacher123', data.get('name'), data.get('phone'), teacher_id))

                connection.commit()
                
                return {
                    'success': True,
                    'message': '老師新增成功！',
                    'teacher_id': teacher_id
                }, 201
                
            except mysql.connector.Error as err:
                print(f"新增老師資料庫錯誤: {err}")
                print(f"錯誤代碼: {err.errno}")
                print(f"SQL狀態: {err.sqlstate}")
                connection.rollback()
                return {'error': f'新增老師失敗: {str(err)}'}, 500
            except Exception as e:
                print(f"新增老師一般錯誤: {str(e)}")
                connection.rollback()
                return {'error': f'新增老師失敗: {str(e)}'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"新增老師外層錯誤: {str(e)}")
            print(f"接收到的資料: {data}")
            return {'error': f'新增老師失敗: {str(e)}'}, 500

class Courses(Resource):
    def get(self):
        """取得所有課程（包含老師資訊）"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT c.*, t.name as teacher_name, t.email as teacher_email, s.name as style_name
                FROM courses c
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN styles s ON c.style_id = s.id
                ORDER BY c.created_at DESC
                """
                cursor.execute(query)
                courses = cursor.fetchall()
                
                # 轉換 Decimal 和 datetime 物件為可 JSON 序列化的格式
                for course in courses:
                    # 將 price 欄位轉為字串
                    if 'price' in course and course['price'] is not None:
                        course['price'] = str(course['price'])
                    for money_col in ['base_salary', 'low_student_salary', 'extra_student_fee', 'salary_cap']:
                        if money_col in course and course[money_col] is not None:
                            course[money_col] = float(course[money_col])
                    for int_col in ['extra_student_threshold', 'low_student_threshold']:
                        if int_col in course and course[int_col] is not None:
                            course[int_col] = int(course[int_col])
                    # 轉換 datetime 物件為 ISO 格式字串
                    for field in ['created_at', 'updated_at', 'line_linked_at']:
                        if course.get(field) and isinstance(course[field], datetime):
                            course[field] = course[field].isoformat()
                
                return {
                    'success': True,
                    'courses': courses,
                    'total': len(courses)
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢課程錯誤: {err}")
                return {'error': f'查詢課程失敗: {err}'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢課程錯誤: {str(e)}")
            return {'error': '查詢課程失敗'}, 500
    
    def post(self):
        """新增課程"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data or 'level' not in data:
                return {'error': '缺少必要欄位：課程名稱、難度級別'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                insert_query = """
                INSERT INTO courses 
                (name, description, level, style_id, duration_minutes, max_students, price, allow_monthly_pass, teacher_id,
                 base_salary, low_student_threshold, low_student_salary, extra_student_threshold, extra_student_fee, salary_cap)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data.get('name'),
                    data.get('description'),
                    data.get('level'),
                    data.get('style_id'),
                    data.get('duration_minutes', 60),
                    data.get('max_students', 15),
                    data.get('price'),
                    1 if data.get('allow_monthly_pass', True) else 0,
                    data.get('teacher_id'),
                    float(data.get('base_salary') or 0),
                    int(data.get('low_student_threshold') or 0),
                    float(data.get('low_student_salary') or 0),
                    int(data.get('extra_student_threshold') or 0),
                    float(data.get('extra_student_fee') or 0),
                    float(data.get('salary_cap') or 0)
                )
                
                cursor.execute(insert_query, values)
                connection.commit()
                
                course_id = cursor.lastrowid
                
                return {
                    'success': True,
                    'message': '課程新增成功！',
                    'course_id': course_id
                }, 201
                
            except mysql.connector.Error as err:
                print(f"新增課程錯誤: {err}")
                return {'error': '新增課程失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"新增課程錯誤: {str(e)}")
            return {'error': '新增課程失敗'}, 500

class CourseSchedules(Resource):
    def get(self):
        """取得所有課程時間表，支援日期範圍過濾"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)

                # 取得查詢參數
                start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')

                # 基本查詢語句，包含報名人數和動態報名狀態
                query = """
                SELECT cs.*, c.name as course_name, c.level, c.price as course_price, c.max_students as course_capacity,
                       c.allow_monthly_pass,
                       c.teacher_id as course_teacher_id,
                       COALESCE(cs.teacher_id, c.teacher_id) as teacher_id,
                       COALESCE(sub_t.name, t.name) as teacher_name,
                       COALESCE(sub_t.avatar_url, t.avatar_url) as teacher_avatar_url,
                       t.id as original_teacher_id,
                       t.name as original_teacher_name,
                       CASE WHEN cs.is_substitute = 1 OR (cs.teacher_id IS NOT NULL AND cs.teacher_id != c.teacher_id) THEN 1 ELSE 0 END as is_substitute,
                       c.base_salary, c.low_student_threshold, c.low_student_salary, c.extra_student_threshold, c.extra_student_fee, c.salary_cap,
                       s.name as style_name, r.name as room_name, 
                       r.capacity as room_capacity,
                       COUNT(e.id) as enrollment_count,
                       CASE 
                           WHEN cs.allow_enrollment = 0 THEN 0
                           WHEN cs.schedule_date < CURRENT_DATE() THEN 0
                           WHEN COUNT(e.id) >= c.max_students THEN 0
                           ELSE 1
                       END as dynamic_allow_enrollment,
                       CASE 
                           WHEN cs.schedule_date < CURRENT_DATE() THEN 1
                           ELSE 0
                       END as is_past
                FROM course_schedules cs
                JOIN courses c ON cs.course_id = c.id
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN styles s ON c.style_id = s.id
                LEFT JOIN rooms r ON cs.room_id = r.id
                LEFT JOIN teachers sub_t ON cs.teacher_id = sub_t.id
                LEFT JOIN enrollments e ON cs.id = e.schedule_id AND e.status = 'confirmed'
                WHERE cs.is_active = TRUE
                """

                # 添加日期範圍過濾條件
                params = []
                if start_date:
                    query += " AND cs.schedule_date >= %s"
                    params.append(start_date)
                if end_date:
                    query += " AND cs.schedule_date <= %s"
                    params.append(end_date)

                query += " GROUP BY cs.id ORDER BY cs.schedule_date, cs.start_time"

                cursor.execute(query, params)
                schedules = cursor.fetchall()

                # 列表時間物件與 Decimal 序列化轉換
                from decimal import Decimal
                for _single_sched in (schedules if 'schedules' in locals() else [schedule]):
                    for _k, _v in list(_single_sched.items()):
                        if isinstance(_v, Decimal):
                            _single_sched[_k] = float(_v)
                        elif isinstance(_v, (datetime, date)):
                            _single_sched[_k] = _v.isoformat()
                        elif isinstance(_v, timedelta):
                            _single_sched[_k] = str(_v)
                for schedule in schedules:
                    if schedule.get('schedule_date'):
                        schedule['schedule_date'] = str(schedule['schedule_date'])
                    schedule['is_past'] = bool(schedule.get('is_past'))
                    if schedule.get('start_time'):
                        schedule['start_time'] = str(schedule['start_time'])
                    if schedule.get('end_time'):
                        schedule['end_time'] = str(schedule['end_time'])
                    if schedule.get('created_at') and isinstance(schedule['created_at'], datetime):
                        schedule['created_at'] = schedule['created_at'].isoformat()
                    # 轉換 Decimal 為 float / int
                    if schedule.get('course_price'):
                        schedule['course_price'] = float(schedule['course_price'])
                    for money_col in ['base_salary', 'low_student_salary', 'extra_student_fee', 'salary_cap']:
                        if schedule.get(money_col) is not None:
                            schedule[money_col] = float(schedule[money_col])
                    for int_col in ['extra_student_threshold', 'low_student_threshold']:
                        if schedule.get(int_col) is not None:
                            schedule[int_col] = int(schedule[int_col])

                return {
                    'success': True,
                    'schedules': schedules,
                    'total': len(schedules)
                }, 200

            except mysql.connector.Error as err:
                print(f"查詢課程時間表錯誤: {err}")
                return {'error': f'查詢課程時間表失敗: {err}'}, 500
            finally:
                cursor.close()
                connection.close()

        except Exception as e:
            print(f"查詢課程時間表錯誤: {str(e)}")
            return {'error': f'查詢課程時間表失敗: {str(e)}'}, 500

    def post(self):
        """新增課程時間表"""
        try:
            data = request.get_json()
            
            required_fields = ['course_id', 'schedule_date', 'start_time', 'end_time']
            if not data or not all(field in data for field in required_fields):
                return {'error': '缺少必要欄位：course_id, schedule_date, start_time, end_time'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                # 從日期推算星期幾
                from datetime import datetime
                date_obj = datetime.strptime(data['schedule_date'], '%Y-%m-%d')
                day_of_week = date_obj.strftime('%A')  # Monday, Tuesday, etc.
                
                insert_query = """
                INSERT INTO course_schedules 
                (course_id, schedule_date, day_of_week, start_time, end_time, room_id, is_active, allow_enrollment, teacher_id, is_substitute)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data.get('course_id'),
                    data.get('schedule_date'),
                    day_of_week,
                    data.get('start_time'),
                    data.get('end_time'),
                    data.get('room_id'),
                    data.get('is_active', True),
                    data.get('allow_enrollment', True),
                    data.get('teacher_id') or None,
                    1 if data.get('is_substitute') else 0
                )
                
                cursor.execute(insert_query, values)
                connection.commit()
                
                schedule_id = cursor.lastrowid
                
                return {
                    'success': True,
                    'message': '課程時間表新增成功！',
                    'schedule_id': schedule_id,
                    'day_of_week': day_of_week
                }, 201
                
            except mysql.connector.Error as err:
                print(f"新增課程時間表錯誤: {err}")
                return {'error': f'新增課程時間表失敗: {err}'}, 500
            except ValueError as e:
                print(f"日期格式錯誤: {e}")
                return {'error': '日期格式錯誤，請使用 YYYY-MM-DD 格式'}, 400
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"新增課程時間表錯誤: {str(e)}")
            return {'error': '新增課程時間表失敗'}, 500

class Student(Resource):
    def get(self, student_id):
        """取得單一學生"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                student = cursor.fetchone()
                
                if not student:
                    return {'error': '學生未找到'}, 404
                
                return {
                    'success': True,
                    'student': format_student_info(student)
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢學生錯誤: {err}")
                return {'error': '查詢學生失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢學生錯誤: {str(e)}")
            return {'error': '查詢學生失敗'}, 500

    def put(self, student_id):
        """更新學生資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '缺少更新資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                # 先確認學生是否存在
                cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
                if not cursor.fetchone():
                    return {'error': '學生未找到'}, 404
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['name', 'email', 'phone', 'date_of_birth', 'emergency_contact', 'emergency_phone', 'medical_notes', 'remaining_classes', 'membership_expiry', 'monthly_pass_expiry', 'bank_last_5', 'line_user_id', 'line_display_name', 'line_picture_url']:
                        if key in ['date_of_birth', 'membership_expiry', 'monthly_pass_expiry'] and (value == '' or value == '1911-01-01'):
                            value = None
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                if not update_fields:
                    return {'error': '沒有可更新的欄位'}, 400
                
                update_query = f"UPDATE students SET {', '.join(update_fields)} WHERE id = %s"
                values.append(student_id)
                
                cursor.execute(update_query, tuple(values))
                connection.commit()
                
                return {
                    'success': True,
                    'message': '學生資料更新成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"更新學生錯誤: {err}")
                return {'error': '更新學生失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"更新學生錯誤: {str(e)}")
            return {'error': '更新學生失敗'}, 500

    def delete(self, student_id):
        """刪除學生"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
                connection.commit()
                
                if cursor.rowcount == 0:
                    return {'error': '學生未找到'}, 404
                
                return {
                    'success': True,
                    'message': '學生刪除成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"刪除學生錯誤: {err}")
                return {'error': '刪除學生失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"刪除學生錯誤: {str(e)}")
            return {'error': '刪除學生失敗'}, 500

class Teacher(Resource):
    def get(self, teacher_id):
        """取得單一老師"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                SELECT t.*, u.id as user_id, u.username as account_username
                FROM teachers t
                LEFT JOIN admin_users u ON u.teacher_id = t.id AND u.role = 'teacher'
                WHERE t.id = %s
                """, (teacher_id,))
                teacher = cursor.fetchone()
                
                if not teacher:
                    return {'error': '老師未找到'}, 404
                
                # 查詢老師的風格
                style_query = """
                SELECT s.id, s.name
                FROM teacher_styles ts
                JOIN styles s ON ts.style_id = s.id
                WHERE ts.teacher_id = %s
                """
                cursor.execute(style_query, (teacher_id,))
                styles = cursor.fetchall()
                teacher['styles'] = styles
                
                # 轉換 datetime 和 Decimal 物件為字串
                if teacher.get('hourly_rate'):
                    teacher['hourly_rate'] = str(teacher['hourly_rate'])
                for field in ['created_at', 'updated_at', 'line_linked_at']:
                    if teacher.get(field) and isinstance(teacher[field], datetime):
                        teacher[field] = teacher[field].isoformat()
                
                return {
                    'success': True,
                    'teacher': teacher
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢老師錯誤: {err}")
                return {'error': '查詢老師失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢老師錯誤: {str(e)}")
            return {'error': '查詢老師失敗'}, 500

    def put(self, teacher_id):
        """更新老師資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '缺少更新資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['name', 'email', 'phone', 'experience_years', 'bio', 'hourly_rate', 'bank_account', 'avatar_url', 'is_featured']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                if update_fields:
                    update_query = f"UPDATE teachers SET {', '.join(update_fields)} WHERE id = %s"
                    update_values = tuple(values) + (teacher_id,)
                    cursor.execute(update_query, update_values)
                
                # 更新老師與風格的關聯
                if 'style_ids' in data:
                    style_ids = data['style_ids']
                    # 先刪除舊的關聯
                    cursor.execute("DELETE FROM teacher_styles WHERE teacher_id = %s", (teacher_id,))
                    # 新增新的關聯
                    if style_ids:
                        insert_style_query = """
                        INSERT INTO teacher_styles (teacher_id, style_id)
                        VALUES (%s, %s)
                        """
                        style_values = [(teacher_id, style_id) for style_id in style_ids]
                        cursor.executemany(insert_style_query, style_values)

                # 更新或建立關聯之登入帳號與密碼
                account_user = (data.get('account_username') or data.get('username') or '').strip()
                account_pwd = (data.get('password') or '').strip()
                if account_user or account_pwd:
                    cursor.execute("SELECT id FROM admin_users WHERE teacher_id = %s", (teacher_id,))
                    u = cursor.fetchone()
                    if u:
                        u_sets = []
                        u_vals = []
                        if account_user:
                            u_sets.append("username = %s")
                            u_vals.append(account_user)
                        if account_pwd:
                            u_sets.append("password = %s")
                            u_vals.append(account_pwd)
                        if u_sets:
                            cursor.execute(f"UPDATE admin_users SET {', '.join(u_sets)} WHERE id = %s", tuple(u_vals) + (u[0],))
                    elif account_user:
                        cursor.execute("""
                        INSERT INTO admin_users (username, password, name, role, phone, teacher_id)
                        VALUES (%s, %s, %s, 'teacher', %s, %s)
                        """, (account_user, account_pwd or 'teacher123', data.get('name') or '老師', data.get('phone'), teacher_id))

                connection.commit()
                
                return {
                    'success': True,
                    'message': '老師資料更新成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"更新老師錯誤: {err}")
                return {'error': '更新老師失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"更新老師錯誤: {str(e)}")
            return {'error': '更新老師失敗'}, 500

    def delete(self, teacher_id):
        """刪除老師"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM teachers WHERE id = %s", (teacher_id,))
                connection.commit()
                
                if cursor.rowcount == 0:
                    return {'error': '老師未找到'}, 404
                
                return {
                    'success': True,
                    'message': '老師刪除成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"刪除老師錯誤: {err}")
                return {'error': '刪除老師失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"刪除老師錯誤: {str(e)}")
            return {'error': '刪除老師失敗'}, 500

class TeacherAccount(Resource):
    def put(self, teacher_id):
        """修改老師登入帳號、密碼與銀行帳號"""
        try:
            data = request.get_json() or {}
            password = (data.get('password') or '').strip()
            username = (data.get('username') or data.get('account_username') or '').strip()
            bank_account = data.get('bank_account')

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT id, name, phone FROM teachers WHERE id = %s", (teacher_id,))
                teacher = cursor.fetchone()
                if not teacher:
                    return {'error': '找不到此老師資料'}, 404

                # 更新銀行帳號 (若有傳)
                if bank_account is not None:
                    cursor.execute("UPDATE teachers SET bank_account = %s WHERE id = %s", (bank_account.strip(), teacher_id))

                # 更新或建立關聯之登入帳號與密碼
                if username or password:
                    cursor.execute("SELECT id, username FROM admin_users WHERE teacher_id = %s", (teacher_id,))
                    existing = cursor.fetchone()

                    if existing:
                        # 若更改帳號，檢查是否與其他帳號重複
                        if username and username != existing['username']:
                            cursor.execute("SELECT id FROM admin_users WHERE username = %s AND id != %s", (username, existing['id']))
                            if cursor.fetchone():
                                return {'error': f'登入帳號「{username}」已被其他員工使用，請自訂其他帳號'}, 400

                        sets = []
                        vals = []
                        if username:
                            sets.append("username = %s")
                            vals.append(username)
                        if password:
                            sets.append("password = %s")
                            vals.append(password)
                        if sets:
                            cursor.execute(f"UPDATE admin_users SET {', '.join(sets)} WHERE id = %s", tuple(vals) + (existing['id'],))
                    else:
                        target_user = username or f"teacher_{teacher_id}"
                        cursor.execute("SELECT id FROM admin_users WHERE username = %s", (target_user,))
                        if cursor.fetchone():
                            return {'error': f'登入帳號「{target_user}」已存在，請自訂其他帳號'}, 400

                        cursor.execute("""
                        INSERT INTO admin_users (username, password, name, role, phone, teacher_id)
                        VALUES (%s, %s, %s, 'teacher', %s, %s)
                        """, (target_user, password or 'teacher123', teacher['name'], teacher['phone'], teacher_id))

                connection.commit()
                return {'success': True, 'message': '老師帳號與資料已成功更新！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'操作失敗: {str(e)}'}, 500

class Course(Resource):
    def get(self, course_id):
        """取得單一課程"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT c.*, t.name as teacher_name, s.name as style_name
                FROM courses c
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN styles s ON c.style_id = s.id
                WHERE c.id = %s
                """
                cursor.execute(query, (course_id,))
                course = cursor.fetchone()
                
                if not course:
                    return {'error': '課程未找到'}, 404
                
                # 轉換 Decimal 和 datetime 物件為可 JSON 序列化的格式
                if 'price' in course and course['price'] is not None:
                    course['price'] = str(course['price'])
                for money_col in ['base_salary', 'low_student_salary', 'extra_student_fee', 'salary_cap']:
                    if money_col in course and course[money_col] is not None:
                        course[money_col] = float(course[money_col])
                for int_col in ['extra_student_threshold', 'low_student_threshold']:
                    if int_col in course and course[int_col] is not None:
                        course[int_col] = int(course[int_col])
                for field in ['created_at', 'updated_at', 'line_linked_at']:
                    if course.get(field) and isinstance(course[field], datetime):
                        course[field] = course[field].isoformat()
                
                return {
                    'success': True,
                    'course': course
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢課程錯誤: {err}")
                return {'error': '查詢課程失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢課程錯誤: {str(e)}")
            return {'error': '查詢課程失敗'}, 500

    def put(self, course_id):
        """更新課程資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '缺少更新資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['name', 'description', 'level', 'style_id', 'duration_minutes', 'max_students', 'price', 'allow_monthly_pass', 'teacher_id',
                               'base_salary', 'low_student_threshold', 'low_student_salary', 'extra_student_threshold', 'extra_student_fee', 'salary_cap']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                if not update_fields:
                    return {'error': '沒有可更新的欄位'}, 400
                
                update_query = f"UPDATE courses SET {', '.join(update_fields)} WHERE id = %s"
                values.append(course_id)
                
                cursor.execute(update_query, tuple(values))
                connection.commit()
                
                if cursor.rowcount == 0:
                    cursor.execute("SELECT id FROM courses WHERE id = %s", (course_id,))
                    if not cursor.fetchone():
                        return {'error': '課程未找到'}, 404
                
                return {
                    'success': True,
                    'message': '課程資料更新成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"更新課程錯誤: {err}")
                return {'error': '更新課程失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"更新課程錯誤: {str(e)}")
            return {'error': '更新課程失敗'}, 500

    def delete(self, course_id):
        """刪除課程"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
                connection.commit()
                
                if cursor.rowcount == 0:
                    return {'error': '課程未找到'}, 404
                
                return {
                    'success': True,
                    'message': '課程刪除成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"刪除課程錯誤: {err}")
                return {'error': '刪除課程失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"刪除課程錯誤: {str(e)}")
            return {'error': '刪除課程失敗'}, 500

api.add_resource(HelloWorld, '/')
api.add_resource(Enrollment, '/api/enrollment', '/api/enrollments')
api.add_resource(Students, '/api/students')
api.add_resource(Student, '/api/students/<int:student_id>') # 新增的學生單一資源
api.add_resource(Teachers, '/api/teachers')
api.add_resource(Teacher, '/api/teachers/<int:teacher_id>')
api.add_resource(Courses, '/api/courses')
api.add_resource(Course, '/api/courses/<int:course_id>')
api.add_resource(CourseSchedules, '/api/schedules')

class CourseSchedule(Resource):
    def get(self, schedule_id):
        """取得單一課程時間表"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT cs.*, c.name as course_name, c.level, c.price as course_price, c.max_students as course_capacity,
                       c.allow_monthly_pass,
                       c.teacher_id as course_teacher_id,
                       COALESCE(cs.teacher_id, c.teacher_id) as teacher_id,
                       COALESCE(sub_t.name, t.name) as teacher_name,
                       COALESCE(sub_t.avatar_url, t.avatar_url) as teacher_avatar_url,
                       t.id as original_teacher_id,
                       t.name as original_teacher_name,
                       CASE WHEN cs.is_substitute = 1 OR (cs.teacher_id IS NOT NULL AND cs.teacher_id != c.teacher_id) THEN 1 ELSE 0 END as is_substitute,
                       c.base_salary, c.low_student_threshold, c.low_student_salary, c.extra_student_threshold, c.extra_student_fee, c.salary_cap,
                       s.name as style_name, 
                       r.name as room_name, 
                       r.capacity as room_capacity
                FROM course_schedules cs
                JOIN courses c ON cs.course_id = c.id
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN styles s ON c.style_id = s.id
                LEFT JOIN rooms r ON cs.room_id = r.id
                LEFT JOIN teachers sub_t ON cs.teacher_id = sub_t.id
                WHERE cs.id = %s
                """
                cursor.execute(query, (schedule_id,))
                schedule = cursor.fetchone()
                
                if not schedule:
                    return {'error': '課程時間表未找到'}, 404
                
                # 列表時間物件與 Decimal 序列化轉換
                from decimal import Decimal
                for _single_sched in (schedules if 'schedules' in locals() else [schedule]):
                    for _k, _v in list(_single_sched.items()):
                        if isinstance(_v, Decimal):
                            _single_sched[_k] = float(_v)
                        elif isinstance(_v, (datetime, date)):
                            _single_sched[_k] = _v.isoformat()
                        elif isinstance(_v, timedelta):
                            _single_sched[_k] = str(_v)
                if schedule.get('schedule_date'):
                    schedule['schedule_date'] = str(schedule['schedule_date'])
                if schedule.get('start_time'):
                    schedule['start_time'] = str(schedule['start_time'])
                if schedule.get('end_time'):
                    schedule['end_time'] = str(schedule['end_time'])
                if schedule.get('created_at') and isinstance(schedule['created_at'], datetime):
                    schedule['created_at'] = schedule['created_at'].isoformat()
                
                return {
                    'success': True,
                    'schedule': schedule
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢課程時間表錯誤: {err}")
                return {'error': '查詢課程時間表失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢課程時間表錯誤: {str(e)}")
            return {'error': '查詢課程時間表失敗'}, 500

    def put(self, schedule_id):
        """更新課程時間表資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '缺少更新資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['course_id', 'schedule_date', 'start_time', 'end_time', 'room_id', 'is_active', 'allow_enrollment', 'teacher_id', 'is_substitute', 'substitute_notes']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                if not update_fields:
                    return {'error': '沒有可更新的欄位'}, 400
                
                # 從日期推算星期幾
                if 'schedule_date' in data:
                    from datetime import datetime
                    date_obj = datetime.strptime(data['schedule_date'], '%Y-%m-%d')
                    day_of_week = date_obj.strftime('%A')
                    update_fields.append("day_of_week = %s")
                    values.append(day_of_week)

                update_query = f"UPDATE course_schedules SET {', '.join(update_fields)} WHERE id = %s"
                values.append(schedule_id)
                
                cursor.execute(update_query, tuple(values))
                connection.commit()
                
                if cursor.rowcount == 0:
                    return {'error': '課程時間表未找到或資料未改變'}, 404
                
                return {
                    'success': True,
                    'message': '課程時間表資料更新成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"更新課程時間表錯誤: {err}")
                return {'error': '更新課程時間表失敗'}, 500
            except ValueError as e:
                print(f"日期格式錯誤: {e}")
                return {'error': '日期格式錯誤，請使用 YYYY-MM-DD 格式'}, 400
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"更新課程時間表錯誤: {str(e)}")
            return {'error': '更新課程時間表失敗'}, 500

    def delete(self, schedule_id):
        """刪除課程時間表"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM course_schedules WHERE id = %s", (schedule_id,))
                connection.commit()
                
                if cursor.rowcount == 0:
                    return {'error': '課程時間表未找到'}, 404
                
                return {
                    'success': True,
                    'message': '課程時間表刪除成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"刪除課程時間表錯誤: {err}")
                return {'error': '刪除課程時間表失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"刪除課程時間表錯誤: {str(e)}")
            return {'error': '刪除課程時間表失敗'}, 500

api.add_resource(CourseSchedule, '/api/schedules/<int:schedule_id>')

class Styles(Resource):
    def get(self):
        """取得所有風格"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM styles ORDER BY id DESC")
                styles = cursor.fetchall()
                
                return {
                    'success': True,
                    'styles': styles,
                    'total': len(styles)
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢風格錯誤: {err}")
                return {'error': '查詢風格失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢風格錯誤: {str(e)}")
            return {'error': '查詢風格失敗'}, 500
    
    def post(self):
        """新增風格"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return {'error': '缺少必要欄位：風格名稱'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                insert_query = """
                INSERT INTO styles (name, description)
                VALUES (%s, %s)
                """
                
                values = (
                    data.get('name'),
                    data.get('description')
                )
                
                cursor.execute(insert_query, values)
                connection.commit()
                
                style_id = cursor.lastrowid
                
                return {
                    'success': True,
                    'message': '風格新增成功！',
                    'style_id': style_id
                }, 201
                
            except mysql.connector.Error as err:
                print(f"新增風格錯誤: {err}")
                return {'error': '新增風格失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"新增風格錯誤: {str(e)}")
            return {'error': '新增風格失敗'}, 500

api.add_resource(Styles, '/api/styles')

class Style(Resource):
    def get(self, style_id):
        """取得單一風格"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM styles WHERE id = %s", (style_id,))
                style = cursor.fetchone()
                
                if not style:
                    return {'error': '風格未找到'}, 404
                
                return {
                    'success': True,
                    'style': style
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢風格錯誤: {err}")
                return {'error': '查詢風格失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢風格錯誤: {str(e)}")
            return {'error': '查詢風格失敗'}, 500

    def put(self, style_id):
        """更新風格資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '缺少更新資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['name', 'description']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                if not update_fields:
                    return {'error': '沒有可更新的欄位'}, 400
                
                update_query = f"UPDATE styles SET {', '.join(update_fields)} WHERE id = %s"
                values.append(style_id)
                
                cursor.execute(update_query, tuple(values))
                connection.commit()
                
                if cursor.rowcount == 0:
                    return {'error': '風格未找到或資料未改變'}, 404
                
                return {
                    'success': True,
                    'message': '風格資料更新成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"更新風格錯誤: {err}")
                return {'error': '更新風格失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"更新風格錯誤: {str(e)}")
            return {'error': '更新風格失敗'}, 500

    def delete(self, style_id):
        """刪除風格"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM styles WHERE id = %s", (style_id,))
                connection.commit()
                
                if cursor.rowcount == 0:
                    return {'error': '風格未找到'}, 404
                
                return {
                    'success': True,
                    'message': '風格刪除成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"刪除風格錯誤: {err}")
                return {'error': '刪除風格失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"刪除風格錯誤: {str(e)}")
            return {'error': '刪除風格失敗'}, 500

api.add_resource(Style, '/api/styles/<int:style_id>')

class Rooms(Resource):
    def get(self):
        """取得所有教室"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '查詢教室失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM rooms ORDER BY id ASC")
                rooms = cursor.fetchall()

                # 轉換 Decimal 物件為字串
                for room in rooms:
                    if room.get('hourly_rate'):
                        room['hourly_rate'] = str(room['hourly_rate'])
                    # 轉換 datetime 物件為 ISO 格式字串
                    for field in ['created_at', 'updated_at', 'line_linked_at']:
                        if room.get(field) and isinstance(room[field], datetime):
                            room[field] = room[field].isoformat()
                
                return {
                    'success': True,
                    'rooms': rooms,
                    'total': len(rooms)
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢教室錯誤: {err}")
                return {'error': '查詢教室失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢教室錯誤: {str(e)}")
            return {'error': '查詢教室失敗'}, 500

    def post(self):
        """新增教室"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return {'error': '缺少必要欄位：教室名稱'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                insert_query = """
                INSERT INTO rooms (name, capacity, equipment, description, image_url, hourly_rate, is_available)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data.get('name'),
                    data.get('capacity'),
                    data.get('equipment'),
                    data.get('description'),
                    data.get('image_url'),
                    data.get('hourly_rate'),
                    data.get('is_available', True)
                )
                
                cursor.execute(insert_query, values)
                connection.commit()
                
                room_id = cursor.lastrowid
                
                return {
                    'success': True,
                    'message': '教室新增成功！',
                    'room_id': room_id
                }, 201
                
            except mysql.connector.Error as err:
                print(f"新增教室錯誤: {err}")
                return {'error': '新增教室失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"新增教室錯誤: {str(e)}")
            return {'error': '新增教室失敗'}, 500

api.add_resource(Rooms, '/api/rooms')

class Room(Resource):
    def get(self, room_id):
        """取得單一教室"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM rooms WHERE id = %s", (room_id,))
                room = cursor.fetchone()
                
                if not room:
                    return {'error': '教室未找到'}, 404
                
                # 轉換 Decimal 與 datetime
                if room.get('hourly_rate') is not None:
                    room['hourly_rate'] = str(room['hourly_rate'])
                for field in ['created_at', 'updated_at', 'line_linked_at']:
                    if room.get(field) and isinstance(room[field], datetime):
                        room[field] = room[field].isoformat()
                
                return {
                    'success': True,
                    'room': room
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢教室錯誤: {err}")
                return {'error': '查詢教室失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢教室錯誤: {str(e)}")
            return {'error': '查詢教室失敗'}, 500

    def put(self, room_id):
        """更新教室資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '缺少更新資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['name', 'capacity', 'equipment', 'description', 'image_url', 'hourly_rate', 'is_available']:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                
                if not update_fields:
                    return {'error': '沒有可更新的欄位'}, 400
                
                update_query = f"UPDATE rooms SET {', '.join(update_fields)} WHERE id = %s"
                values.append(room_id)
                
                cursor.execute(update_query, tuple(values))
                connection.commit()
                
                if cursor.rowcount == 0:
                    return {'error': '教室未找到或資料未改變'}, 404
                
                return {
                    'success': True,
                    'message': '教室資料更新成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"更新教室錯誤: {err}")
                return {'error': '更新教室失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"更新教室錯誤: {str(e)}")
            return {'error': '更新教室失敗'}, 500

    def delete(self, room_id):
        """刪除教室"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM rooms WHERE id = %s", (room_id,))
                connection.commit()
                
                if cursor.rowcount == 0:
                    return {'error': '教室未找到'}, 404
                
                return {
                    'success': True,
                    'message': '教室刪除成功！'
                }, 200
                
            except mysql.connector.Error as err:
                print(f"刪除教室錯誤: {err}")
                return {'error': '刪除教室失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"刪除教室錯誤: {str(e)}")
            return {'error': '刪除教室失敗'}, 500

class ScheduleEnrollments(Resource):
    def get(self, schedule_id):
        """取得特定課程時間表的報名人員列表"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                
                # 查詢課程資訊和報名人員
                query = """
                SELECT 
                    cs.id as schedule_id,
                    c.id as course_id,
                    c.name as course_name,
                    c.price as course_price,
                    c.max_students as course_capacity,
                    c.teacher_id as teacher_id,
                    c.base_salary,
                    c.low_student_threshold,
                    c.low_student_salary,
                    c.extra_student_threshold,
                    c.extra_student_fee,
                    c.salary_cap,
                    cs.schedule_date,
                    cs.start_time,
                    cs.end_time,
                    t.name as teacher_name,
                    r.name as room_name,
                    r.capacity as room_capacity,
                    e.id as enrollment_id,
                    e.student_id,
                    e.student_name,
                    e.deducted_classes,
                    e.enrollment_time,
                    e.status
                FROM course_schedules cs
                JOIN courses c ON cs.course_id = c.id
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN rooms r ON cs.room_id = r.id
                LEFT JOIN enrollments e ON cs.id = e.schedule_id
                LEFT JOIN teachers sub_t ON cs.teacher_id = sub_t.id
                WHERE cs.id = %s AND cs.is_active = TRUE
                ORDER BY e.enrollment_time ASC
                """
                
                cursor.execute(query, (schedule_id,))
                results = cursor.fetchall()
                
                if not results:
                    return {'error': '課程時間表未找到'}, 404
                
                # 處理資料
                schedule_info = None
                enrollments = []
                
                for row in results:
                    if schedule_info is None:
                        schedule_info = {
                            'schedule_id': row['schedule_id'],
                            'course_id': row.get('course_id'),
                            'course_name': row['course_name'],
                            'course_price': float(row['course_price']) if row.get('course_price') is not None else 1.0,
                            'course_capacity': row['course_capacity'],
                            'base_salary': float(row['base_salary'] or 0),
                            'low_student_threshold': int(row['low_student_threshold'] or 0),
                            'low_student_salary': float(row['low_student_salary'] or 0),
                            'extra_student_threshold': int(row['extra_student_threshold'] or 0),
                            'extra_student_fee': float(row['extra_student_fee'] or 0),
                            'salary_cap': float(row['salary_cap'] or 0),
                            'schedule_date': str(row['schedule_date']) if row['schedule_date'] else None,
                            'start_time': str(row['start_time']) if row['start_time'] else None,
                            'end_time': str(row['end_time']) if row['end_time'] else None,
                            'teacher_name': row['teacher_name'],
                            'room_name': row['room_name'],
                            'room_capacity': row['room_capacity']
                        }
                    
                    if row['enrollment_id']:
                        enrollments.append({
                            'enrollment_id': row['enrollment_id'],
                            'student_id': row['student_id'],
                            'student_name': row['student_name'],
                            'deducted_classes': row['deducted_classes'] if row['deducted_classes'] is not None else 1,
                            'enrollment_time': row['enrollment_time'].isoformat() if row['enrollment_time'] else None,
                            'status': row['status']
                        })
                
                return {
                    'success': True,
                    'schedule': schedule_info,
                    'enrollments': enrollments,
                    'total_enrollments': len(enrollments)
                }, 200
                
            except mysql.connector.Error as err:
                print(f"查詢報名人員錯誤: {err}")
                return {'error': '查詢報名人員失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"查詢報名人員錯誤: {str(e)}")
            return {'error': '查詢報名人員失敗'}, 500

    def post(self, schedule_id):
        """後台管理員直接為特定課程時間表新增/登記學生"""
        try:
            data = request.get_json() or {}
            student_id = data.get('student_id')
            student_name = (data.get('student_name') or '').strip()
            deduct_classes = data.get('deduct_classes', True)
            try:
                deducted_classes = int(data.get('deducted_classes', 1))
            except (ValueError, TypeError):
                deducted_classes = 1

            if not deduct_classes:
                deducted_classes = 0
            elif deducted_classes < 0:
                deducted_classes = 0

            if not student_id and not student_name:
                return {'error': '請選擇學員或輸入學員姓名'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)

                # 查詢排程與課程資訊
                schedule_query = """
                SELECT cs.id as schedule_id, cs.course_id, cs.schedule_date, cs.day_of_week, 
                       cs.start_time, cs.end_time,
                       c.name as course_name, c.level, c.price as course_price, 
                       c.max_students as course_capacity,
                       s.name as style_name, t.name as teacher_name
                FROM course_schedules cs
                JOIN courses c ON cs.course_id = c.id
                LEFT JOIN styles s ON c.style_id = s.id
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN teachers sub_t ON cs.teacher_id = sub_t.id
                WHERE cs.id = %s AND cs.is_active = TRUE
                """
                cursor.execute(schedule_query, (schedule_id,))
                schedule_info = cursor.fetchone()
                if not schedule_info:
                    return {'error': '找不到此課程時間表或課程已停用'}, 404

                # 尋找學員資料
                student = None
                if student_id:
                    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                    student = cursor.fetchone()
                elif student_name:
                    cursor.execute("SELECT * FROM students WHERE name = %s LIMIT 1", (student_name,))
                    student = cursor.fetchone()

                if student:
                    student_id = student['id']
                    student_name = student['name']
                    remaining_classes = student.get('remaining_classes') or 0
                else:
                    remaining_classes = 0

                # 檢查若要扣堂數，但沒有學員帳號或堂數不足
                if deducted_classes > 0:
                    if not student:
                        return {'error': f'系統中查無【{student_name}】學員帳號，無法扣除堂數。請選擇現有學員或選擇不扣堂數。'}, 400
                    if remaining_classes < deducted_classes:
                        return {'error': f'學員【{student_name}】剩餘堂數不足！（目前剩餘：{remaining_classes} 堂，欲扣除：{deducted_classes} 堂）'}, 400

                # 檢查是否已重複報名此時段
                check_dup_query = """
                SELECT id FROM enrollments 
                WHERE schedule_id = %s 
                  AND (student_id = %s OR student_name = %s)
                  AND status = 'confirmed'
                """
                cursor.execute(check_dup_query, (schedule_id, student_id, student_name))
                existing = cursor.fetchone()
                if existing:
                    return {'error': f'學員【{student_name}】已經預約過此時段課程，無法重複報名！'}, 400

                # 開始事務
                cursor.execute("START TRANSACTION")

                # 若需扣堂數，扣除學員剩餘堂數
                if deducted_classes > 0 and student_id:
                    cursor.execute(
                        "UPDATE students SET remaining_classes = remaining_classes - %s WHERE id = %s",
                        (deducted_classes, student_id)
                    )

                # 格式化上課時間
                lesson_time = ""
                if schedule_info.get('start_time') and schedule_info.get('end_time'):
                    lesson_time = f"{str(schedule_info['start_time'])[:5]} - {str(schedule_info['end_time'])[:5]}"

                # 插入報名紀錄
                insert_query = """
                INSERT INTO enrollments 
                (student_id, course_id, schedule_id, student_name, lesson_name, lesson_time, lesson_day, 
                 lesson_teacher, lesson_level, lesson_type, deducted_classes, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'confirmed')
                """
                values = (
                    student_id,
                    schedule_info['course_id'],
                    schedule_id,
                    student_name,
                    schedule_info.get('course_name') or '',
                    lesson_time,
                    schedule_info.get('day_of_week') or '',
                    schedule_info.get('teacher_name') or '',
                    schedule_info.get('level') or '',
                    schedule_info.get('style_name') or '',
                    deducted_classes
                )
                cursor.execute(insert_query, values)
                connection.commit()

                return {
                    'success': True,
                    'message': f'成功為【{student_name}】報名此課程！（扣除 {deducted_classes} 堂課）',
                    'enrollment_id': cursor.lastrowid,
                    'student_name': student_name,
                    'deducted_classes': deducted_classes
                }, 201

            except mysql.connector.Error as err:
                connection.rollback()
                print(f"後台新增學員報名資料庫錯誤: {err}")
                return {'error': f'新增學員報名失敗: {err}'}, 500
            finally:
                cursor.close()
                connection.close()

        except Exception as e:
            print(f"後台新增學員報名伺服器錯誤: {str(e)}")
            return {'error': '新增學員報名伺服器錯誤'}, 500

class EnrollmentDetail(Resource):
    def put(self, enrollment_id):
        """更新報名狀態"""
        try:
            data = request.json
            new_status = data.get('status')
            
            if new_status not in ['confirmed', 'pending', 'cancelled']:
                return {'error': '無效的狀態值'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                
                # 檢查報名記錄是否存在
                cursor.execute("SELECT * FROM enrollments WHERE id = %s", (enrollment_id,))
                enrollment = cursor.fetchone()
                
                if not enrollment:
                    return {'error': '報名記錄不存在'}, 404
                
                # 如果是取消報名，需要回復堂數
                if new_status == 'cancelled' and enrollment['status'] != 'cancelled':
                    # 取得學生姓名和當初扣除的堂數
                    student_name = enrollment['student_name']
                    deducted_classes = enrollment.get('deducted_classes', 1)  # 使用記錄的扣除堂數，預設1堂
                    
                    # 回復學生堂數
                    cursor.execute("""
                        UPDATE students 
                        SET remaining_classes = remaining_classes + %s 
                        WHERE name = %s
                    """, (deducted_classes, student_name))
                    
                    print(f"取消報名：學生 {student_name} 回復 {deducted_classes} 堂課")
                
                # 更新報名狀態（不使用updated_at欄位）
                cursor.execute("""
                    UPDATE enrollments 
                    SET status = %s 
                    WHERE id = %s
                """, (new_status, enrollment_id))
                
                connection.commit()
                
                return {
                    'success': True,
                    'message': f'報名狀態已更新為：{new_status}',
                    'enrollment_id': enrollment_id,
                    'new_status': new_status
                }, 200
                
            except mysql.connector.Error as err:
                print(f"更新報名狀態錯誤: {err}")
                connection.rollback()
                return {'error': '更新報名狀態失敗'}, 500
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            print(f"更新報名狀態錯誤: {str(e)}")
            return {'error': '更新報名狀態失敗'}, 500

api.add_resource(Room, '/api/rooms/<int:room_id>')
api.add_resource(ScheduleEnrollments, '/api/schedules/<int:schedule_id>/enrollments')
api.add_resource(EnrollmentDetail, '/api/enrollments/<int:enrollment_id>')

# ==========================================
# 學生登入與會員專區相關 API
# ==========================================

class StudentCheckPhone(Resource):
    def post(self):
        """檢查電話號碼是否存在，並回傳是否為首次登入"""
        try:
            data = request.get_json(silent=True) or {}
            phone = (data.get('phone') or '').strip()
            if not phone:
                return {'error': '請輸入電話號碼'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT id, name, phone, password_hash, remaining_classes FROM students WHERE phone = %s", (phone,))
                student = cursor.fetchone()
                
                if not student:
                    return {
                        'success': False,
                        'exists': False,
                        'message': '查無此電話的學員資料，請確認輸入或洽詢櫃檯'
                    }, 200
                
                is_first_login = not bool(student.get('password_hash'))
                return {
                    'success': True,
                    'exists': True,
                    'is_first_login': is_first_login,
                    'name': student['name']
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"檢查學員電話錯誤: {str(e)}", flush=True)
            return {'error': f'檢查電話失敗: {str(e)}'}, 500

class StudentLogin(Resource):
    def post(self):
        """
        學生登入 API:
        - 首次登入 (password_hash 為空)：無密碼進入設定密碼流程，帶入 new_password 即可設定並完成登入
        - 非首次登入：必須提供正確的 password 進行驗證
        """
        try:
            data = request.get_json() or {}
            phone = (data.get('phone') or '').strip()
            password = data.get('password')
            new_password = data.get('new_password')
            
            if not phone:
                return {'error': '請輸入電話號碼'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM students WHERE phone = %s", (phone,))
                student = cursor.fetchone()
                
                if not student:
                    return {'error': '查無此電話之學生資料，請確認電話是否正確'}, 404
                
                has_password = bool(student.get('password_hash'))
                
                # 首次登入流程（尚未設定密碼）
                if not has_password:
                    if new_password:
                        new_pwd_str = str(new_password).strip()
                        if len(new_pwd_str) < 4:
                            return {'error': '密碼長度至少需 4 個字元'}, 400
                        
                        p_hash = generate_password_hash(new_pwd_str)
                        cursor.execute("UPDATE students SET password_hash = %s WHERE id = %s", (p_hash, student['id']))
                        connection.commit()
                        
                        student['password_hash'] = p_hash
                        student_token = generate_token(student['id'], student.get('phone', ''), 'student', extra_claims={'name': student['name']})
                        return {
                            'success': True,
                            'message': '密碼設定成功，歡迎首次登入！',
                            'is_first_login': True,
                            'token': student_token,
                            'student': format_student_info(student)
                        }, 200
                    else:
                        # 提示前端展示設定密碼介面
                        return {
                            'success': False,
                            'require_set_password': True,
                            'name': student['name'],
                            'message': '首次登入請設定新密碼'
                        }, 200
                
                # 一般登入流程（已設定過密碼）
                if not password:
                    return {'error': '請輸入密碼'}, 400
                
                if not check_password_hash(student['password_hash'], str(password)):
                    return {'error': '密碼不正確，請重新輸入'}, 401
                
                student_token = generate_token(student['id'], student.get('phone', ''), 'student', extra_claims={'name': student['name']})
                return {
                    'success': True,
                    'message': '登入成功！',
                    'is_first_login': False,
                    'token': student_token,
                    'student': format_student_info(student)
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"學員登入錯誤: {str(e)}")
            return {'error': '登入失敗，請稍後再試'}, 500

class StudentChangePassword(Resource):
    def post(self):
        """學員修改密碼 API"""
        try:
            data = request.get_json() or {}
            student_id = data.get('student_id')
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            if not student_id or not old_password or not new_password:
                return {'error': '請填寫所有必要欄位'}, 400
            
            new_pwd_str = str(new_password).strip()
            if len(new_pwd_str) < 4:
                return {'error': '新密碼長度至少需 4 個字元'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT id, password_hash FROM students WHERE id = %s", (student_id,))
                student = cursor.fetchone()
                
                if not student:
                    return {'error': '學員不存在'}, 404
                
                if not student.get('password_hash') or not check_password_hash(student['password_hash'], str(old_password)):
                    return {'error': '舊密碼不正確'}, 400
                
                new_hash = generate_password_hash(new_pwd_str)
                cursor.execute("UPDATE students SET password_hash = %s WHERE id = %s", (new_hash, student_id))
                connection.commit()
                
                return {'success': True, 'message': '密碼修改成功！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"修改密碼錯誤: {str(e)}")
            return {'error': '修改密碼失敗'}, 500

class StudentProfile(Resource):
    def get(self, student_id):
        """取得學員最新資訊 (如剩餘堂數)"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                student = cursor.fetchone()
                
                if not student:
                    return {'error': '學員不存在'}, 404
                
                return {
                    'success': True,
                    'student': format_student_info(student)
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"取得學員資訊錯誤: {str(e)}")
            return {'error': '取得資料失敗'}, 500

class StudentEnrollments(Resource):
    def get(self, student_id):
        """取得特定學員的所有課程預約紀錄"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT e.*,
                       COALESCE(c.name, e.lesson_name) as course_name,
                       COALESCE(t.name, e.lesson_teacher) as teacher_name,
                       COALESCE(e.lesson_time, CONCAT(DATE_FORMAT(cs.start_time, '%H:%i'), ' - ', DATE_FORMAT(cs.end_time, '%H:%i'))) as schedule_time,
                       COALESCE(r.name, 'Dance Studio') as room_name,
                       COALESCE(r.name, 'Dance Studio') as classroom_name,
                       s.name as dance_type,
                       cs.schedule_date, cs.start_time, cs.end_time, cs.day_of_week
                FROM enrollments e
                LEFT JOIN course_schedules cs ON e.schedule_id = cs.id
                LEFT JOIN courses c ON cs.course_id = c.id
                LEFT JOIN styles s ON c.style_id = s.id
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN rooms r ON cs.room_id = r.id
                WHERE e.student_id = %s
                ORDER BY e.enrollment_time DESC
                """
                cursor.execute(query, (student_id,))
                enrollments = cursor.fetchall()
                
                for item in enrollments:
                    # 統一欄位名稱
                    if not item.get('course_name') or item.get('course_name') == '':
                        item['course_name'] = item.get('lesson_name') or '舞蹈課程'
                    if not item.get('teacher_name') or item.get('teacher_name') == '':
                        item['teacher_name'] = item.get('lesson_teacher') or '未指定'
                    if not item.get('classroom_name') or item.get('classroom_name') == '':
                        item['classroom_name'] = item.get('room_name') or 'Dance Studio'
                    if not item.get('schedule_time') or item.get('schedule_time') == '':
                        item['schedule_time'] = item.get('lesson_time') or '依課表'
                    
                    for field in ['enrollment_time']:
                        if item.get(field) and isinstance(item[field], datetime):
                            item[field] = item[field].isoformat()
                    for field in ['schedule_date']:
                        if item.get(field) and isinstance(item[field], date):
                            item[field] = item[field].isoformat()
                    for field in ['start_time', 'end_time']:
                        if item.get(field):
                            item[field] = str(item[field])
                
                return {
                    'success': True,
                    'enrollments': enrollments
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"取得學員預約紀錄錯誤: {str(e)}")
            return {'error': '取得預約紀錄失敗'}, 500

class StudentRegister(Resource):
    def post(self):
        """
        學生會員註冊 API
        """
        try:
            data = request.get_json(silent=True) or {}
            name = (data.get('name') or '').strip()
            phone = (data.get('phone') or '').strip()
            password = data.get('password')
            email = (data.get('email') or '').strip() or None
            date_of_birth = data.get('date_of_birth') or None
            emergency_contact = (data.get('emergency_contact') or '').strip() or None
            emergency_phone = (data.get('emergency_phone') or '').strip() or None
            
            if not name:
                return {'error': '請輸入學員姓名'}, 400
            if not phone:
                return {'error': '請輸入手機電話號碼'}, 400
            if not password or len(str(password).strip()) < 4:
                return {'error': '密碼長度至少需 4 個字元'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            
            try:
                cursor = connection.cursor(dictionary=True, buffered=True)
                
                # 檢查手機號碼是否已被註冊
                cursor.execute("SELECT id, name FROM students WHERE phone = %s", (phone,))
                existing_phone = cursor.fetchone()
                if existing_phone:
                    return {'error': f'此手機號碼已註冊過會員（姓名：{existing_phone["name"]}），請直接登入！'}, 400
                
                # 若有填寫 Email，檢查 Email 是否已被使用
                if email:
                    cursor.execute("SELECT id FROM students WHERE email = %s", (email,))
                    if cursor.fetchone():
                        return {'error': '此電子信箱已被註冊使用，請更換信箱或直接登入！'}, 400
                
                # 加密密碼
                p_hash = generate_password_hash(str(password).strip())
                
                # 預設會員效期一年
                today = datetime.now().date()
                membership_expiry = today + timedelta(days=365)
                
                insert_query = """
                INSERT INTO students 
                (name, phone, email, password_hash, remaining_classes, membership_expiry, date_of_birth, emergency_contact, emergency_phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                -- old_values_ignored
                """
                values = (
                    name,
                    phone,
                    email,
                    p_hash,
                    0,  # 預設新註冊堂數為 0
                    membership_expiry,
                    date_of_birth,
                    emergency_contact,
                    emergency_phone
                )
                cursor.execute(insert_query, values)
                connection.commit()
                
                new_student_id = cursor.lastrowid
                
                cursor.execute("SELECT * FROM students WHERE id = %s", (new_student_id,))
                new_student = cursor.fetchone()
                
                return {
                    'success': True,
                    'message': f'恭喜 {name} 註冊成功，歡迎加入 Dance Studio！已為您自動登入。',
                    'student': format_student_info(new_student)
                }, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'error': f'註冊失敗: {str(e)}'}, 500

api.add_resource(StudentCheckPhone, '/api/student/check-phone')
api.add_resource(StudentLogin, '/api/student/login')
api.add_resource(StudentRegister, '/api/student/register')
api.add_resource(StudentChangePassword, '/api/student/change-password')
api.add_resource(StudentProfile, '/api/student/profile/<int:student_id>')
api.add_resource(StudentEnrollments, '/api/student/<int:student_id>/enrollments')

# ==========================================
# 會員關聯 LINE 與 LINE 快速登入 API
# ==========================================

def get_line_system_settings(cursor):
    """查詢系統設定中的 LINE 相關參數"""
    cursor.execute("""
    SELECT setting_key, setting_value FROM system_settings 
    WHERE setting_key IN ('line_login_enabled', 'line_channel_id', 'line_channel_secret', 'line_official_id', 'line_official_url')
    """)
    rows = cursor.fetchall()
    settings = {
        'line_login_enabled': '1',
        'line_channel_id': '',
        'line_channel_secret': '',
        'line_official_id': '',
        'line_official_url': ''
    }
    for r in rows:
        settings[r['setting_key']] = r['setting_value'] or ''
    return settings

def exchange_line_token(channel_id, channel_secret, code, redirect_uri):
    """向 LINE OAuth Token 端點換取 Access Token"""
    token_url = "https://api.line.me/oauth2/v2.1/token"
    data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': channel_id,
        'client_secret': channel_secret
    }).encode('utf-8')
    req = urllib.request.Request(token_url, data=data, headers={
        'Content-Type': 'application/x-www-form-urlencoded'
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8')), None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        try:
            err_json = json.loads(err_body)
            err_desc = err_json.get('error_description') or err_json.get('error') or str(e)
        except Exception:
            err_desc = err_body or str(e)
        return None, f"LINE 授權 Token 換取失敗: {err_desc}"
    except Exception as e:
        return None, f"連接 LINE 伺服器失敗: {str(e)}"

def get_line_user_profile(access_token):
    """向 LINE Profile API 取得用戶個人資訊"""
    profile_url = "https://api.line.me/v2/profile"
    req = urllib.request.Request(profile_url, headers={
        'Authorization': f'Bearer {access_token}'
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8')), None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        return None, f"取得 LINE 用戶個人資料失敗: {err_body}"
    except Exception as e:
        return None, f"取得 LINE 資料失敗: {str(e)}"

class LinePublicConfigResource(Resource):
    def get(self):
        """前台取得 LINE 相關公開設定 (用於顯示按鈕與好友連結)"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                s = get_line_system_settings(cursor)
                return {
                    'success': True,
                    'enabled': s['line_login_enabled'] == '1',
                    'has_channel_id': bool(s['line_channel_id'].strip()),
                    'channel_id': s['line_channel_id'].strip(),
                    'official_id': s['line_official_id'].strip(),
                    'official_url': s['line_official_url'].strip()
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'取得 LINE 設定失敗: {str(e)}'}, 500

class LineAuthUrlResource(Resource):
    def get(self):
        """產生 LINE OAuth 授權登入 / 綁定跳轉 URL"""
        redirect_uri = request.args.get('redirect_uri')
        state = request.args.get('state') or 'login'
        if not redirect_uri:
            return {'error': '缺少 redirect_uri 參數'}, 400

        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                s = get_line_system_settings(cursor)
                channel_id = s.get('line_channel_id', '').strip()
                if not channel_id:
                    return {
                        'success': False,
                        'configured': False,
                        'message': '系統尚未設定 LINE Login Channel ID，請由管理後台填寫或使用手動/模擬關聯模式'
                    }, 200

                encoded_redirect = urllib.parse.quote(redirect_uri, safe='')
                encoded_state = urllib.parse.quote(state, safe='')
                auth_url = (
                    f"https://access.line.me/oauth2/v2.1/authorize?"
                    f"response_type=code&client_id={channel_id}&redirect_uri={encoded_redirect}&"
                    f"state={encoded_state}&scope=profile%20openid"
                )
                return {
                    'success': True,
                    'configured': True,
                    'auth_url': auth_url
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'產生 LINE 授權網址失敗: {str(e)}'}, 500

class LineCallbackResource(Resource):
    def post(self):
        """
        處理 LINE Login 授權回傳 code:
        - 1. 向 LINE 換取 Token 與 Profile
        - 2. 若為綁定模式 (帶有 student_id 或 state 為 bind:xxx)，將 LINE ID 綁定至該學員
        - 3. 若為登入模式，依 line_user_id 查詢學員；若查無關聯學員，則回傳 need_link 引導綁定
        """
        try:
            data = request.get_json() or {}
            code = (data.get('code') or '').strip()
            redirect_uri = (data.get('redirect_uri') or '').strip()
            state = (data.get('state') or '').strip()
            student_id = data.get('student_id')

            if not code or not redirect_uri:
                return {'error': '缺少必要參數 (code, redirect_uri)'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                settings = get_line_system_settings(cursor)
                channel_id = settings['line_channel_id'].strip()
                channel_secret = settings['line_channel_secret'].strip()

                if not channel_id or not channel_secret:
                    return {'error': '系統尚未完整設定 LINE Login 頻道資訊 (Channel ID / Secret)'}, 400

                # 換取 Token
                token_res, err = exchange_line_token(channel_id, channel_secret, code, redirect_uri)
                if err:
                    return {'error': err}, 400

                access_token = token_res.get('access_token')
                if not access_token:
                    return {'error': '無法取得 LINE Access Token'}, 400

                # 取得 LINE 個人資料
                profile_res, err = get_line_user_profile(access_token)
                if err:
                    return {'error': err}, 400

                line_user_id = profile_res.get('userId')
                line_display_name = profile_res.get('displayName') or 'LINE 會員'
                line_picture_url = profile_res.get('pictureUrl')

                if not line_user_id:
                    return {'error': '未能從 LINE 取得用戶唯一識別碼 (userId)'}, 400

                # 解析 state 判斷是否為綁定模式
                target_student_id = student_id
                if not target_student_id and state.startswith('bind:'):
                    parts = state.split(':')
                    if len(parts) >= 2 and parts[1].isdigit():
                        target_student_id = int(parts[1])

                # 模式 A: 綁定模式 (已登入學員綁定 LINE)
                if target_student_id:
                    # 檢查該 LINE 帳號是否已被其他學員綁定
                    cursor.execute("SELECT id, name FROM students WHERE line_user_id = %s AND id != %s", (line_user_id, target_student_id))
                    conflict = cursor.fetchone()
                    if conflict:
                        return {'error': f'此 LINE 帳號已與學員「{conflict["name"]}」關聯，無法重複關聯！如需變更請先解除原帳號綁定。'}, 400

                    # 執行關聯更新
                    cursor.execute("""
                    UPDATE students 
                    SET line_user_id = %s, line_display_name = %s, line_picture_url = %s, line_linked_at = NOW()
                    WHERE id = %s
                    """, (line_user_id, line_display_name, line_picture_url, target_student_id))
                    connection.commit()

                    cursor.execute("SELECT * FROM students WHERE id = %s", (target_student_id,))
                    updated_student = cursor.fetchone()
                    return {
                        'success': True,
                        'action': 'bound',
                        'message': f'成功關聯 LINE 帳號「{line_display_name}」！',
                        'student': format_student_info(updated_student)
                    }, 200

                # 模式 B: LINE 登入模式
                cursor.execute("SELECT * FROM students WHERE line_user_id = %s", (line_user_id,))
                matched_student = cursor.fetchone()

                if matched_student:
                    # 更新最新 LINE 暱稱與頭貼 (保持同步)
                    cursor.execute("""
                    UPDATE students 
                    SET line_display_name = %s, line_picture_url = %s
                    WHERE id = %s
                    """, (line_display_name, line_picture_url, matched_student['id']))
                    connection.commit()

                    matched_student['line_display_name'] = line_display_name
                    matched_student['line_picture_url'] = line_picture_url

                    return {
                        'success': True,
                        'action': 'login',
                        'message': f'歡迎回來，{matched_student["name"]}！',
                        'student': format_student_info(matched_student)
                    }, 200
                else:
                    # 尚未關聯任何會員帳號，回傳必要資料以引導綁定或註冊
                    return {
                        'success': False,
                        'not_linked': True,
                        'action': 'need_link',
                        'line_user_id': line_user_id,
                        'line_display_name': line_display_name,
                        'line_picture_url': line_picture_url,
                        'message': f'您的 LINE 帳號「{line_display_name}」尚未關聯會員帳號，請綁定既有手機帳號或立即註冊！'
                    }, 200

            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'error': f'LINE 授權處理失敗: {str(e)}'}, 500

class LineDirectBindResource(Resource):
    def post(self):
        """
        學員或管理員直接綁定 LINE 帳號 (支援前端由 LIFF 取得、管理後台手動綁定、或模擬關聯)
        """
        try:
            data = request.get_json() or {}
            student_id = data.get('student_id')
            line_user_id = (data.get('line_user_id') or '').strip()
            line_display_name = (data.get('line_display_name') or '').strip() or 'LINE 用戶'
            line_picture_url = data.get('line_picture_url') or None

            if not student_id:
                return {'error': '缺少 student_id'}, 400
            if not line_user_id:
                return {'error': '請提供欲關聯的 LINE User ID'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                # 確認學員存在
                cursor.execute("SELECT id, name FROM students WHERE id = %s", (student_id,))
                student = cursor.fetchone()
                if not student:
                    return {'error': '找不到此學員資料'}, 404

                # 檢查該 LINE User ID 是否已被其他人綁定
                cursor.execute("SELECT id, name FROM students WHERE line_user_id = %s AND id != %s", (line_user_id, student_id))
                conflict = cursor.fetchone()
                if conflict:
                    return {'error': f'此 LINE 帳號已被學員「{conflict["name"]}」關聯！'}, 400

                cursor.execute("""
                UPDATE students 
                SET line_user_id = %s, line_display_name = %s, line_picture_url = %s, line_linked_at = NOW()
                WHERE id = %s
                """, (line_user_id, line_display_name, line_picture_url, student_id))
                connection.commit()

                cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                updated_student = cursor.fetchone()

                return {
                    'success': True,
                    'message': f'學員【{student["name"]}】已成功關聯 LINE 帳號「{line_display_name}」！',
                    'student': format_student_info(updated_student)
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'綁定 LINE 失敗: {str(e)}'}, 500

class LineDirectUnbindResource(Resource):
    def post(self):
        """解除學員與 LINE 帳號的關聯"""
        try:
            data = request.get_json() or {}
            student_id = data.get('student_id')
            if not student_id:
                return {'error': '缺少 student_id 參數'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT id, name, line_display_name FROM students WHERE id = %s", (student_id,))
                student = cursor.fetchone()
                if not student:
                    return {'error': '找不到此學員資料'}, 404

                cursor.execute("""
                UPDATE students 
                SET line_user_id = NULL, line_display_name = NULL, line_picture_url = NULL, line_linked_at = NULL
                WHERE id = %s
                """, (student_id,))
                connection.commit()

                cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                updated = cursor.fetchone()

                return {
                    'success': True,
                    'message': f'已成功解除學員【{student["name"]}】的 LINE 帳號關聯！',
                    'student': format_student_info(updated)
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'解除 LINE 關聯失敗: {str(e)}'}, 500

class LineLinkPhoneResource(Resource):
    def post(self):
        """
        當用戶使用 LINE 登入但尚未綁定時：
        - 模式 1: 關聯既有手機帳號 (需驗證密碼或首次登入設密碼)
        - 模式 2: 註冊為新會員並直接完成 LINE 關聯
        """
        try:
            data = request.get_json() or {}
            mode = data.get('mode') or 'link'  # 'link' 或 'register'
            line_user_id = (data.get('line_user_id') or '').strip()
            line_display_name = (data.get('line_display_name') or '').strip() or 'LINE 會員'
            line_picture_url = data.get('line_picture_url') or None
            phone = (data.get('phone') or '').strip()

            if not line_user_id:
                return {'error': '缺少 LINE 用戶識別碼'}, 400
            if not phone:
                return {'error': '請輸入手機電話號碼'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)

                # 檢查該 LINE 是否已被他人綁定
                cursor.execute("SELECT id, name FROM students WHERE line_user_id = %s", (line_user_id,))
                conflict = cursor.fetchone()
                if conflict:
                    return {'error': f'此 LINE 帳號已被學員「{conflict["name"]}」關聯！'}, 400

                if mode == 'link':
                    # 關聯現有手機帳號
                    password = data.get('password')
                    cursor.execute("SELECT * FROM students WHERE phone = %s", (phone,))
                    student = cursor.fetchone()
                    if not student:
                        return {'error': '查無此手機號碼的會員資料，請點選「註冊新會員並綁定」！'}, 404

                    if student.get('password_hash'):
                        if not password or not check_password_hash(student['password_hash'], str(password)):
                            return {'error': '密碼錯誤，請重新確認'}, 401
                    else:
                        # 首次登入無密碼，若有傳新密碼則設定
                        if password and len(str(password).strip()) >= 4:
                            p_hash = generate_password_hash(str(password).strip())
                            cursor.execute("UPDATE students SET password_hash = %s WHERE id = %s", (p_hash, student['id']))

                    # 綁定 LINE
                    cursor.execute("""
                    UPDATE students 
                    SET line_user_id = %s, line_display_name = %s, line_picture_url = %s, line_linked_at = NOW()
                    WHERE id = %s
                    """, (line_user_id, line_display_name, line_picture_url, student['id']))
                    connection.commit()

                    cursor.execute("SELECT * FROM students WHERE id = %s", (student['id'],))
                    updated = cursor.fetchone()
                    return {
                        'success': True,
                        'message': f'成功關聯手機號碼與 LINE 帳號！歡迎回來，{updated["name"]}！',
                        'student': format_student_info(updated)
                    }, 200

                elif mode == 'register':
                    # 新註冊並直接綁定 LINE
                    name = (data.get('name') or '').strip() or line_display_name
                    password = data.get('password')
                    email = (data.get('email') or '').strip() or None

                    if not name:
                        return {'error': '請輸入姓名'}, 400
                    if not password or len(str(password).strip()) < 4:
                        return {'error': '密碼至少需 4 個字元'}, 400

                    # 檢查手機是否重複
                    cursor.execute("SELECT id FROM students WHERE phone = %s", (phone,))
                    if cursor.fetchone():
                        return {'error': '此手機號碼已註冊，請選擇「關聯既有手機帳號」登入！'}, 400

                    p_hash = generate_password_hash(str(password).strip())
                    today = datetime.now().date()
                    membership_expiry = today + timedelta(days=365)

                    cursor.execute("""
                    INSERT INTO students 
                    (name, phone, email, password_hash, remaining_classes, membership_expiry, line_user_id, line_display_name, line_picture_url, line_linked_at)
                    VALUES (%s, %s, %s, %s, 0, %s, %s, %s, %s, NOW())
                    """, (name, phone, email, p_hash, membership_expiry, line_user_id, line_display_name, line_picture_url))
                    connection.commit()

                    new_id = cursor.lastrowid
                    cursor.execute("SELECT * FROM students WHERE id = %s", (new_id,))
                    new_student = cursor.fetchone()

                    return {
                        'success': True,
                        'message': f'恭喜 {name} 註冊成功並已綁定 LINE！歡迎加入 Dance Studio！',
                        'student': format_student_info(new_student)
                    }, 201
                else:
                    return {'error': '未知的模式 (mode)'}, 400
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'關聯手機處理失敗: {str(e)}'}, 500

class LineAdminSettingsResource(Resource):
    @jwt_required(['admin'])
    def get(self):
        """後台管理員取得完整 LINE 設定（Channel Secret 遮罩防禦）"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                s = get_line_system_settings(cursor)
                raw_secret = s.get('line_channel_secret', '')
                masked_secret = '••••••••' if raw_secret else ''
                return {
                    'success': True,
                    'settings': {
                        'line_login_enabled': s['line_login_enabled'] == '1',
                        'line_channel_id': s['line_channel_id'],
                        'line_channel_secret': masked_secret,
                        'has_channel_secret': bool(raw_secret),
                        'line_official_id': s['line_official_id'],
                        'line_official_url': s['line_official_url']
                    }
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢 LINE 設定失敗: {str(e)}'}, 500

    @jwt_required(['admin'])
    def post(self):
        """後台管理員更新 LINE 設定"""
        try:
            data = request.get_json() or {}
            enabled = '1' if data.get('line_login_enabled') else '0'
            channel_id = (data.get('line_channel_id') or '').strip()
            channel_secret = (data.get('line_channel_secret') or '').strip()
            official_id = (data.get('line_official_id') or '').strip()
            official_url = (data.get('line_official_url') or '').strip()

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                items = [
                    ('line_login_enabled', enabled, '是否啟用 LINE 快速登入與帳號關聯 (0=關閉, 1=開啟)'),
                    ('line_channel_id', channel_id, 'LINE Login Channel ID'),
                    ('line_official_id', official_id, '工作室 LINE 官方帳號 ID'),
                    ('line_official_url', official_url, '工作室 LINE 官方加好友連結')
                ]
                # 只有當輸入了新 Secret 且非遮罩符號時才更新
                if channel_secret and channel_secret != '••••••••':
                    items.append(('line_channel_secret', channel_secret, 'LINE Login Channel Secret'))

                for k, v, desc in items:
                    cursor.execute("""
                    INSERT INTO system_settings (setting_key, setting_value, description)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                    """, (k, v, desc))

                connection.commit()
                return {'success': True, 'message': 'LINE 整合設定已更新成功！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新 LINE 設定失敗: {str(e)}'}, 500

api.add_resource(LinePublicConfigResource, '/api/line/config')
api.add_resource(LineAuthUrlResource, '/api/line/auth-url')
api.add_resource(LineCallbackResource, '/api/line/callback')
api.add_resource(LineDirectBindResource, '/api/student/line/bind')
api.add_resource(LineDirectUnbindResource, '/api/student/line/unbind')
api.add_resource(LineLinkPhoneResource, '/api/student/line/link-with-phone')
api.add_resource(LineAdminSettingsResource, '/api/admin/settings/line')


# ==========================================
# 後台管理員 / 櫃檯 / 老師 權限與登入 API
# ==========================================
class AdminLogin(Resource):
    def post(self):
        """後台管理員/櫃檯/老師登入"""
        try:
            data = request.get_json() or {}
            username = (data.get('username') or '').strip()
            password = (data.get('password') or '').strip()

            if not username or not password:
                return {'error': '請輸入帳號與密碼'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT u.id, u.username, u.password, u.name, u.role, u.phone, u.hourly_rate, u.bank_account, u.teacher_id,
                       t.name as teacher_name
                FROM admin_users u
                LEFT JOIN teachers t ON u.teacher_id = t.id
                WHERE u.username = %s
                """
                cursor.execute(query, (username,))
                user = cursor.fetchone()

                if not user:
                    return {'error': '帳號或密碼錯誤，請確認後重試'}, 401

                # 密碼驗證（支援平滑遷移：明文密碼驗證通過後自動雜湊加鹽並更新入庫）
                if not verify_and_upgrade_password(cursor, 'admin_users', user['id'], user['password'], password):
                    return {'error': '帳號或密碼錯誤，請確認後重試'}, 401

                connection.commit()

                # 簽發安全 JWT Access Token
                token = generate_token(user['id'], user['username'], user['role'], extra_claims={
                    'name': user['name'],
                    'teacher_id': user.get('teacher_id')
                })

                user_info = {
                    'id': user['id'],
                    'username': user['username'],
                    'name': user['name'],
                    'role': user['role'],
                    'phone': user.get('phone'),
                    'hourly_rate': float(user.get('hourly_rate') or 0),
                    'bank_account': user.get('bank_account'),
                    'teacher_id': user.get('teacher_id'),
                    'teacher_name': user.get('teacher_name')
                }

                return {
                    'success': True,
                    'message': f'歡迎回來，{user["name"]}！',
                    'token': token,
                    'user': user_info
                }, 200
            finally:
                cursor.close()
                connection.close()

        except Exception as e:
            print(f"後台登入錯誤: {str(e)}")
            return {'error': '登入處理發生錯誤'}, 500

class AdminUsers(Resource):
    @jwt_required(['admin'])
    def get(self):
        """取得所有後台管理員/員工清單"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT u.id, u.username, u.name, u.role, u.phone, u.hourly_rate, u.bank_account, u.teacher_id,
                       u.created_at, u.updated_at, t.name as teacher_name
                FROM admin_users u
                LEFT JOIN teachers t ON u.teacher_id = t.id
                ORDER BY u.id ASC
                """
                cursor.execute(query)
                users = cursor.fetchall()
                for u in users:
                    u['hourly_rate'] = float(u.get('hourly_rate') or 0)
                    for field in ['created_at', 'updated_at', 'line_linked_at']:
                        if u.get(field) and isinstance(u[field], datetime):
                            u[field] = u[field].isoformat()

                return {'success': True, 'users': users}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢使用者失敗: {str(e)}'}, 500

    @jwt_required(['admin'])
    def post(self):
        """新增後台管理員/員工"""
        try:
            data = request.get_json() or {}
            username = (data.get('username') or '').strip()
            password = (data.get('password') or '').strip()
            name = (data.get('name') or '').strip()
            role = data.get('role', 'desk')
            phone = (data.get('phone') or '').strip() or None
            hourly_rate = float(data.get('hourly_rate') or 0)
            bank_account = (data.get('bank_account') or '').strip() or None
            teacher_id = data.get('teacher_id') or None

            if not username or not password or not name:
                return {'error': '缺少必要欄位：帳號、密碼、姓名'}, 400

            if role not in ['admin', 'desk', 'teacher']:
                return {'error': '無效的權限角色，必須為 admin、desk 或 teacher'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                # 檢查帳號是否重複
                cursor.execute("SELECT id FROM admin_users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return {'error': f'帳號「{username}」已存在，請使用其他帳號'}, 400

                hashed_password = hash_password(password)
                cursor.execute("""
                INSERT INTO admin_users (username, password, name, role, phone, hourly_rate, bank_account, teacher_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (username, hashed_password, name, role, phone, hourly_rate, bank_account, teacher_id))
                connection.commit()

                return {'success': True, 'message': f'成功建立帳號「{username}」！'}, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'新增使用者失敗: {str(e)}'}, 500

class AdminUser(Resource):
    @jwt_required(['admin', 'desk', 'teacher'])
    def get(self, user_id):
        """取得單一後台員工帳號"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT u.id, u.username, u.name, u.role, u.phone, u.hourly_rate, u.bank_account, u.teacher_id,
                       t.name as teacher_name, u.created_at, u.updated_at
                FROM admin_users u
                LEFT JOIN teachers t ON u.teacher_id = t.id
                WHERE u.id = %s
                """
                cursor.execute(query, (user_id,))
                user = cursor.fetchone()
                if not user:
                    return {'error': '找不到該使用者'}, 404
                user['hourly_rate'] = float(user.get('hourly_rate') or 0)
                for field in ['created_at', 'updated_at', 'line_linked_at']:
                    if user.get(field) and isinstance(user[field], datetime):
                        user[field] = user[field].isoformat()
                return {'success': True, 'user': user}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢使用者失敗: {str(e)}'}, 500

    @jwt_required(['admin', 'desk', 'teacher'])
    def put(self, user_id):
        """編輯後台員工帳號"""
        try:
            data = request.get_json() or {}
            username = (data.get('username') or '').strip()
            password = (data.get('password') or '').strip()
            name = (data.get('name') or '').strip()
            role = data.get('role', 'desk')
            phone = (data.get('phone') or '').strip() or None
            hourly_rate = float(data.get('hourly_rate') or 0)
            bank_account = (data.get('bank_account') or '').strip() or None
            teacher_id = data.get('teacher_id') or None

            if not username or not name:
                return {'error': '缺少必要欄位：帳號、姓名'}, 400

            if role not in ['admin', 'desk', 'teacher']:
                return {'error': '無效的權限角色，必須為 admin、desk 或 teacher'}, 400

            if user_id == 1 and role != 'admin':
                return {'error': '系統最高管理員帳號的角色固定為系統管理員 (admin)'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                # 檢查帳號是否與其他帳號衝突
                cursor.execute("SELECT id FROM admin_users WHERE username = %s AND id != %s", (username, user_id))
                if cursor.fetchone():
                    return {'error': f'帳號「{username}」已被其他使用者使用，請使用其他帳號'}, 400

                if role != 'teacher':
                    teacher_id = None

                if password:
                    hashed_pwd = hash_password(password)
                    update_query = """
                    UPDATE admin_users 
                    SET username = %s, password = %s, name = %s, role = %s, phone = %s, hourly_rate = %s, bank_account = %s, teacher_id = %s
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (username, hashed_pwd, name, role, phone, hourly_rate, bank_account, teacher_id, user_id))
                else:
                    update_query = """
                    UPDATE admin_users 
                    SET username = %s, name = %s, role = %s, phone = %s, hourly_rate = %s, bank_account = %s, teacher_id = %s
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (username, name, role, phone, hourly_rate, bank_account, teacher_id, user_id))

                connection.commit()
                return {'success': True, 'message': f'帳號「{username}」資料已更新！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新使用者失敗: {str(e)}'}, 500

    @jwt_required(['admin'])
    def delete(self, user_id):
        """刪除後台員工帳號"""
        if user_id == 1:
            return {'error': '系統最高管理員帳號無法刪除！'}, 400
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM admin_users WHERE id = %s", (user_id,))
                connection.commit()
                return {'success': True, 'message': '帳號已成功刪除！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'刪除帳號失敗: {str(e)}'}, 500

# ==========================================
# 打卡 IP 白名單防護與設定
# ==========================================
def get_client_ip():
    """獲取客戶端真實 IP (優先取反向代理 Nginx 設定之 X-Real-IP 或遠端連線 IP，防範 X-Forwarded-For 偽造)"""
    x_real_ip = request.headers.get('X-Real-IP')
    if x_real_ip:
        ip = x_real_ip.strip()
        if ip.startswith('::ffff:'):
            ip = ip[7:]
        return ip
    # 若在開發環境或直連，取 remote_addr
    ip = (request.remote_addr or '').strip()
    if ip.startswith('::ffff:'):
        ip = ip[7:]
    return ip

def is_ip_match(client_ip, allowed_ip_pattern):
    """
    比對 client_ip 是否符合 allowed_ip_pattern
    支援精準比對 (IPv4/IPv6)、localhost / 127.0.0.1、以及 CIDR 子網路 (如 192.168.1.0/24)
    """
    import ipaddress
    client_ip = (client_ip or '').strip()
    pattern = (allowed_ip_pattern or '').strip()
    if not pattern:
        return False

    # 本機測試別名互通 (127.0.0.1, ::1, localhost)
    localhost_aliases = {'127.0.0.1', '::1', 'localhost'}
    if client_ip in localhost_aliases and pattern in localhost_aliases:
        return True

    if client_ip == pattern:
        return True

    try:
        if '/' in pattern:
            net = ipaddress.ip_network(pattern, strict=False)
            addr = ipaddress.ip_address(client_ip)
            return addr in net
        else:
            return ipaddress.ip_address(client_ip) == ipaddress.ip_address(pattern)
    except Exception:
        return client_ip.lower() == pattern.lower()

def check_attendance_ip_permission(cursor):
    """
    驗證打卡 IP 是否在白名單內。
    回傳: (allowed: bool, client_ip: str, error_message: str or None)
    """
    client_ip = get_client_ip()
    
    cursor.execute("""
    SELECT setting_key, setting_value FROM system_settings 
    WHERE setting_key IN ('attendance_ip_restriction_enabled', 'attendance_allowed_ips')
    """)
    rows = cursor.fetchall()
    settings = {}
    for r in rows:
        settings[r['setting_key']] = r['setting_value']

    enabled = (settings.get('attendance_ip_restriction_enabled') or '0') == '1'
    if not enabled:
        return True, client_ip, None

    allowed_raw = settings.get('attendance_allowed_ips') or ''
    import re
    allowed_list = [item.strip() for item in re.split(r'[\r\n,;]+', allowed_raw) if item.strip()]

    if not allowed_list:
        return False, client_ip, f'打卡已被拒絕：系統已開啟 IP 限制，但白名單清單尚未設定任何允許的 IP（您當前 IP 為 {client_ip}）。請管理員先將此 IP 加入白名單！'

    for pattern in allowed_list:
        if is_ip_match(client_ip, pattern):
            return True, client_ip, None

    return False, client_ip, f'打卡失敗：您當前的網路 IP [{client_ip}] 不在打卡允許的白名單內。請連接教室官方 Wi-Fi，或聯絡系統管理員！'

class AttendanceIpSettings(Resource):
    def get(self):
        """取得打卡 IP 限制設定與當前請求端 IP"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                SELECT setting_key, setting_value FROM system_settings 
                WHERE setting_key IN ('attendance_ip_restriction_enabled', 'attendance_allowed_ips')
                """)
                rows = cursor.fetchall()
                settings = {
                    'attendance_ip_restriction_enabled': '0',
                    'attendance_allowed_ips': ''
                }
                for r in rows:
                    settings[r['setting_key']] = r['setting_value']

                client_ip = get_client_ip()
                enabled = settings['attendance_ip_restriction_enabled'] == '1'
                allowed_ips = settings['attendance_allowed_ips'] or ''

                return {
                    'success': True,
                    'enabled': enabled,
                    'allowed_ips': allowed_ips,
                    'client_ip': client_ip
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'取得 IP 設定失敗: {str(e)}'}, 500

    @jwt_required(['admin'])
    def post(self):
        """更新打卡 IP 限制開關與白名單清單"""
        try:
            data = request.get_json() or {}
            enabled = bool(data.get('enabled'))
            allowed_ips = (data.get('allowed_ips') or '').strip()

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                enabled_str = '1' if enabled else '0'

                cursor.execute("""
                INSERT INTO system_settings (setting_key, setting_value, description)
                VALUES ('attendance_ip_restriction_enabled', %s, '打卡IP限制開關(0=關閉, 1=開啟)')
                ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                """, (enabled_str,))

                cursor.execute("""
                INSERT INTO system_settings (setting_key, setting_value, description)
                VALUES ('attendance_allowed_ips', %s, '允許打卡的IP白名單(逗號或換行分隔)')
                ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                """, (allowed_ips,))

                connection.commit()
                client_ip = get_client_ip()

                return {
                    'success': True,
                    'message': '打卡 IP 限制設定已成功更新！',
                    'enabled': enabled,
                    'allowed_ips': allowed_ips,
                    'client_ip': client_ip
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'儲存 IP 設定失敗: {str(e)}'}, 500

# ==========================================
# 員工上下班打卡管理 API
# ==========================================
def round_clock_in(dt):
    """
    上班打卡時間進位規則：
    以 30 分鐘為單位，往後進位至下一個半小時整點。
    例如：
    - 08:00:00 -> 08:00
    - 08:00:01 ~ 08:30:00 -> 08:30
    - 08:30:01 ~ 09:00:00 -> 09:00 (如 8:40 算 9:00)
    """
    if dt.minute == 0 and dt.second == 0 and dt.microsecond == 0:
        return dt
    if dt.minute < 30 or (dt.minute == 30 and dt.second == 0 and dt.microsecond == 0):
        return dt.replace(minute=30, second=0, microsecond=0)
    else:
        return (dt + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

def round_clock_out(dt):
    """
    下班打卡時間退位規則：
    以 30 分鐘為單位，往前退位至上一個半小時整點。
    例如：
    - 09:00:00 ~ 09:29:59 -> 09:00
    - 09:30:00 ~ 09:59:59 -> 09:30 (如 9:45 算 9:30)
    """
    if dt.minute < 30:
        return dt.replace(minute=0, second=0, microsecond=0)
    else:
        return dt.replace(minute=30, second=0, microsecond=0)

class StaffAttendanceStatus(Resource):
    def get(self):
        """查詢目前打卡狀態與今日打卡記錄"""
        user_id = request.args.get('user_id')
        if not user_id:
            return {'error': '缺少 user_id 參數'}, 400

        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                SELECT sa.*, u.name as user_name, u.role, u.hourly_rate as current_hourly_rate
                FROM staff_attendance sa
                JOIN admin_users u ON sa.user_id = u.id
                WHERE sa.user_id = %s AND sa.clock_out IS NULL
                ORDER BY sa.id DESC LIMIT 1
                """, (user_id,))
                active_shift = cursor.fetchone()

                if active_shift:
                    if not active_shift.get('effective_clock_in') and active_shift.get('clock_in'):
                        active_shift['effective_clock_in'] = round_clock_in(active_shift['clock_in'])
                    for field in ['clock_in', 'effective_clock_in', 'created_at', 'updated_at']:
                        if active_shift.get(field) and isinstance(active_shift[field], datetime):
                            active_shift[field] = active_shift[field].isoformat()
                    active_shift['hourly_rate'] = float(active_shift.get('hourly_rate') or 0)
                    active_shift['current_hourly_rate'] = float(active_shift.get('current_hourly_rate') or 0)
                    active_shift['work_hours'] = float(active_shift.get('work_hours') or 0)
                    active_shift['total_pay'] = int(math.floor(float(active_shift.get('total_pay') or 0)))

                cursor.execute("""
                SELECT sa.*, u.name as user_name
                FROM staff_attendance sa
                JOIN admin_users u ON sa.user_id = u.id
                WHERE sa.user_id = %s AND DATE(sa.clock_in) = CURRENT_DATE()
                ORDER BY sa.clock_in DESC
                """, (user_id,))
                today_records = cursor.fetchall()

                for r in today_records:
                    if not r.get('effective_clock_in') and r.get('clock_in'):
                        r['effective_clock_in'] = round_clock_in(r['clock_in'])
                    if not r.get('effective_clock_out') and r.get('clock_out'):
                        r['effective_clock_out'] = round_clock_out(r['clock_out'])
                    for field in ['clock_in', 'effective_clock_in', 'clock_out', 'effective_clock_out', 'created_at', 'updated_at']:
                        if r.get(field) and isinstance(r[field], datetime):
                            r[field] = r[field].isoformat()
                    r['hourly_rate'] = float(r.get('hourly_rate') or 0)
                    r['work_hours'] = float(r.get('work_hours') or 0)
                    r['total_pay'] = int(math.floor(float(r.get('total_pay') or 0)))

                return {
                    'success': True,
                    'is_clocked_in': bool(active_shift),
                    'active_shift': active_shift,
                    'today_records': today_records,
                    'substitute_schedules': [],
                    'client_ip': get_client_ip()
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢打卡狀態失敗: {str(e)}'}, 500

class StaffAttendanceClockIn(Resource):
    def post(self):
        """上班打卡"""
        try:
            data = request.get_json() or {}
            user_id = data.get('user_id')
            notes = (data.get('notes') or '').strip() or None

            if not user_id:
                return {'error': '缺少 user_id 欄位'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)

                # 驗證打卡 IP 白名單
                allowed, client_ip, err_msg = check_attendance_ip_permission(cursor)
                if not allowed:
                    return {'error': err_msg, 'client_ip': client_ip}, 403

                cursor.execute("""
                SELECT id, clock_in FROM staff_attendance 
                WHERE user_id = %s AND clock_out IS NULL
                """, (user_id,))
                if cursor.fetchone():
                    return {'error': '您目前已在上班打卡狀態中，請勿重複打卡！'}, 400

                cursor.execute("SELECT name, hourly_rate FROM admin_users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return {'error': '找不到該員工帳號'}, 404

                hourly_rate = float(user.get('hourly_rate') or 0)
                now = datetime.now()
                eff_in = round_clock_in(now)

                cursor.execute("""
                INSERT INTO staff_attendance (user_id, clock_in, effective_clock_in, hourly_rate, notes, clock_in_ip)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, now, eff_in, hourly_rate, notes, client_ip))
                connection.commit()

                return {
                    'success': True,
                    'message': f'{user["name"]}，上班打卡成功！打卡時間 {now.strftime("%H:%M")}（計薪起算：{eff_in.strftime("%H:%M")}），祝您工作順利！',
                    'clock_in': now.isoformat(),
                    'effective_clock_in': eff_in.isoformat(),
                    'clock_in_ip': client_ip
                }, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'上班打卡失敗: {str(e)}'}, 500

class StaffAttendanceClockOut(Resource):
    def post(self):
        """下班打卡"""
        try:
            data = request.get_json() or {}
            user_id = data.get('user_id')
            notes = (data.get('notes') or '').strip() or None

            if not user_id:
                return {'error': '缺少 user_id 欄位'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)

                # 驗證打卡 IP 白名單
                allowed, client_ip, err_msg = check_attendance_ip_permission(cursor)
                if not allowed:
                    return {'error': err_msg, 'client_ip': client_ip}, 403

                cursor.execute("""
                SELECT sa.*, u.name as user_name 
                FROM staff_attendance sa
                JOIN admin_users u ON sa.user_id = u.id
                WHERE sa.user_id = %s AND sa.clock_out IS NULL
                ORDER BY sa.id DESC LIMIT 1
                """, (user_id,))
                active_shift = cursor.fetchone()

                if not active_shift:
                    return {'error': '目前無進行中的上班紀錄，請確認是否已上班打卡'}, 400

                now = datetime.now()
                clock_in = active_shift['clock_in']
                eff_in = active_shift.get('effective_clock_in') or round_clock_in(clock_in)
                eff_out = round_clock_out(now)

                # 以30分鐘為單位計算工時 (0.5小時的倍數)
                diff_seconds = (eff_out - eff_in).total_seconds()
                work_hours = max(0.0, round(diff_seconds / 3600.0, 1))

                hourly_rate = float(active_shift['hourly_rate'] or 0)
                # 不到1元不算1元 (無條件捨去小數點，保留整數元)
                total_pay = int(math.floor(work_hours * hourly_rate))

                cursor.execute("""
                UPDATE staff_attendance 
                SET clock_out = %s, effective_clock_out = %s, work_hours = %s, total_pay = %s, notes = COALESCE(%s, notes), clock_out_ip = %s
                WHERE id = %s
                """, (now, eff_out, work_hours, total_pay, notes, client_ip, active_shift['id']))
                connection.commit()

                eff_in_str = eff_in.strftime("%H:%M")
                eff_out_str = eff_out.strftime("%H:%M")

                return {
                    'success': True,
                    'message': f'{active_shift["user_name"]}，下班打卡成功！計薪區間 {eff_in_str} ~ {eff_out_str}，有效工時 {work_hours} 小時，今日薪資 NT$ {total_pay} 元（不到1元捨去）。辛苦了！',
                    'clock_out': now.isoformat(),
                    'effective_clock_out': eff_out.isoformat(),
                    'work_hours': work_hours,
                    'total_pay': total_pay
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'下班打卡失敗: {str(e)}'}, 500

class StaffAttendanceList(Resource):
    def get(self):
        """查詢上下班打卡歷史清單與統計"""
        user_id = request.args.get('user_id')
        month = request.args.get('month')

        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT sa.*, u.name as user_name, u.username, u.role
                FROM staff_attendance sa
                JOIN admin_users u ON sa.user_id = u.id
                WHERE 1=1
                """
                params = []

                if user_id:
                    query += " AND sa.user_id = %s"
                    params.append(user_id)

                if month:
                    query += " AND DATE_FORMAT(sa.clock_in, '%Y-%m') = %s"
                    params.append(month)

                query += " ORDER BY sa.clock_in DESC"

                cursor.execute(query, tuple(params))
                records = cursor.fetchall()

                total_hours = 0.0
                total_pay = 0
                total_shifts = len(records)

                for r in records:
                    if not r.get('effective_clock_in') and r.get('clock_in'):
                        r['effective_clock_in'] = round_clock_in(r['clock_in'])
                    if not r.get('effective_clock_out') and r.get('clock_out'):
                        r['effective_clock_out'] = round_clock_out(r['clock_out'])
                    for field in ['clock_in', 'effective_clock_in', 'clock_out', 'effective_clock_out', 'created_at', 'updated_at']:
                        if r.get(field) and isinstance(r[field], datetime):
                            r[field] = r[field].isoformat()
                    r['hourly_rate'] = float(r.get('hourly_rate') or 0)
                    r['work_hours'] = float(r.get('work_hours') or 0)
                    r['total_pay'] = int(math.floor(float(r.get('total_pay') or 0)))
                    total_hours += r['work_hours']
                    total_pay += r['total_pay']

                return {
                    'success': True,
                    'records': records,
                    'summary': {
                        'total_shifts': total_shifts,
                        'total_hours': round(total_hours, 1),
                        'total_pay': int(total_pay)
                    }
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢打卡歷史失敗: {str(e)}'}, 500

class StaffAttendanceItem(Resource):
    def put(self, attendance_id):
        """編輯單筆打卡紀錄 (供管理員維護修正時間與薪資)"""
        try:
            data = request.get_json() or {}
            clock_in_str = (data.get('clock_in') or '').strip()
            clock_out_str = (data.get('clock_out') or '').strip()
            hourly_rate = data.get('hourly_rate')
            notes = (data.get('notes') or '').strip() or None

            if not clock_in_str:
                return {'error': '上班打卡時間不可為空'}, 400

            # 解析時間字串，支援 ISO 格式如 '2026-10-18T08:40:00' 或 '2026-10-18 08:40:00'
            try:
                clock_in = datetime.fromisoformat(clock_in_str.replace('Z', ''))
            except Exception:
                return {'error': '上班打卡時間格式錯誤'}, 400

            clock_out = None
            if clock_out_str:
                try:
                    clock_out = datetime.fromisoformat(clock_out_str.replace('Z', ''))
                except Exception:
                    return {'error': '下班打卡時間格式錯誤'}, 400

            if clock_out and clock_out < clock_in:
                return {'error': '下班時間不可早於上班時間'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM staff_attendance WHERE id = %s", (attendance_id,))
                current_record = cursor.fetchone()
                if not current_record:
                    return {'error': '找不到該筆打卡記錄'}, 404

                # 時薪設定
                if hourly_rate is not None and str(hourly_rate).strip() != '':
                    rate = float(hourly_rate)
                else:
                    rate = float(current_record['hourly_rate'] or 0)

                # 套用 30 分鐘進退位規則
                eff_in = round_clock_in(clock_in)
                if clock_out:
                    eff_out = round_clock_out(clock_out)
                    diff_seconds = (eff_out - eff_in).total_seconds()
                    work_hours = max(0.0, round(diff_seconds / 3600.0, 1))
                    total_pay = int(math.floor(work_hours * rate))
                else:
                    eff_out = None
                    work_hours = 0.0
                    total_pay = 0

                cursor.execute("""
                UPDATE staff_attendance
                SET clock_in = %s, effective_clock_in = %s,
                    clock_out = %s, effective_clock_out = %s,
                    work_hours = %s, hourly_rate = %s, total_pay = %s,
                    notes = %s
                WHERE id = %s
                """, (clock_in, eff_in, clock_out, eff_out, work_hours, rate, total_pay, notes, attendance_id))
                connection.commit()

                return {
                    'success': True,
                    'message': '打卡記錄已成功更新！',
                    'record': {
                        'id': attendance_id,
                        'clock_in': clock_in.isoformat(),
                        'effective_clock_in': eff_in.isoformat() if eff_in else None,
                        'clock_out': clock_out.isoformat() if clock_out else None,
                        'effective_clock_out': eff_out.isoformat() if eff_out else None,
                        'work_hours': work_hours,
                        'hourly_rate': rate,
                        'total_pay': total_pay,
                        'notes': notes
                    }
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新打卡記錄失敗: {str(e)}'}, 500

    def delete(self, attendance_id):
        """刪除單筆打卡紀錄 (供管理員維護)"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM staff_attendance WHERE id = %s", (attendance_id,))
                connection.commit()
                return {'success': True, 'message': '打卡記錄已刪除'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'刪除打卡記錄失敗: {str(e)}'}, 500

# ==========================================
# 授課老師上課下課打卡管理 API
# ==========================================
def format_time_delta(td):
    if td is None:
        return ""
    if isinstance(td, timedelta):
        total_seconds = int(td.total_seconds())
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    return str(td)[:5]

def compute_teacher_schedule_salary(cursor, schedule_id, teacher_id=None, duration_minutes=0):
    """計算特定課表時段的老師授課鐘點費 (嚴格依該課堂之師資鐘點費/拆帳規則)"""
    cursor.execute("""
    SELECT cs.*, c.id as course_id, c.name as course_name, c.base_salary, c.low_student_threshold, c.low_student_salary,
           c.extra_student_threshold, c.extra_student_fee, c.salary_cap, c.price
    FROM course_schedules cs
    JOIN courses c ON cs.course_id = c.id
    WHERE cs.id = %s
    """, (schedule_id,))
    sched = cursor.fetchone()
    if not sched:
        return 0, 0, "一般課程"

    cursor.execute("""
    SELECT COUNT(*) as cnt FROM enrollments 
    WHERE schedule_id = %s AND status = 'confirmed'
    """, (schedule_id,))
    enroll_row = cursor.fetchone()
    student_count = enroll_row['cnt'] if enroll_row else 0

    base = float(sched.get('base_salary') or 0)
    low_thresh = int(sched.get('low_student_threshold') or 0)
    low_salary = float(sched.get('low_student_salary') or 0)
    extra_thresh = int(sched.get('extra_student_threshold') or 0)
    extra_fee = float(sched.get('extra_student_fee') or 0)
    cap = float(sched.get('salary_cap') or 0)

    if student_count == 0:
        total = 0
    elif low_thresh > 0 and student_count <= low_thresh:
        total = low_salary
        if cap > 0 and total > cap:
            total = cap
    else:
        extra_students = max(0, student_count - extra_thresh) if extra_thresh > 0 else 0
        total = base + (extra_students * extra_fee)
        if cap > 0 and total > cap:
            total = cap

    final_salary = int(math.floor(total))
    return final_salary, student_count, sched['course_name']

def compute_course_salary(cursor, course_id, student_count=0):
    """計算特定課程的授課鐘點費 (自由授課或補課時，依該課程拆帳規則計費)"""
    cursor.execute("""
    SELECT id, name, base_salary, low_student_threshold, low_student_salary,
           extra_student_threshold, extra_student_fee, salary_cap
    FROM courses
    WHERE id = %s
    """, (course_id,))
    c = cursor.fetchone()
    if not c:
        return 0, 0, "自訂授課"

    base = float(c.get('base_salary') or 0)
    low_thresh = int(c.get('low_student_threshold') or 0)
    low_salary = float(c.get('low_student_salary') or 0)
    extra_thresh = int(c.get('extra_student_threshold') or 0)
    extra_fee = float(c.get('extra_student_fee') or 0)
    cap = float(c.get('salary_cap') or 0)

    if student_count == 0:
        total = base
    elif low_thresh > 0 and student_count <= low_thresh:
        total = low_salary
    else:
        extra_students = max(0, student_count - extra_thresh) if extra_thresh > 0 else 0
        total = base + (extra_students * extra_fee)

    if cap > 0 and total > cap:
        total = cap

    return int(math.floor(total)), student_count, c['name']

class TeacherAttendanceStatus(Resource):
    def get(self):
        """查詢老師當前上課打卡狀態與今日課表、打卡紀錄"""
        user_id = request.args.get('user_id')
        teacher_id = request.args.get('teacher_id')
        if not user_id and not teacher_id:
            return {'error': '缺少 user_id 或 teacher_id 參數'}, 400

        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                
                # 查詢使用者與老師關聯資訊
                if user_id:
                    cursor.execute("""
                    SELECT u.*, t.id as real_teacher_id, t.name as teacher_name, t.bank_account as teacher_bank_account, t.avatar_url as teacher_avatar_url
                    FROM admin_users u
                    LEFT JOIN teachers t ON u.teacher_id = t.id
                    WHERE u.id = %s
                    """, (user_id,))
                else:
                    cursor.execute("""
                    SELECT u.*, t.id as real_teacher_id, t.name as teacher_name, t.bank_account as teacher_bank_account, t.avatar_url as teacher_avatar_url
                    FROM teachers t
                    LEFT JOIN admin_users u ON u.teacher_id = t.id
                    WHERE t.id = %s
                    LIMIT 1
                    """, (teacher_id,))

                user_info = cursor.fetchone()
                if not user_info:
                    return {'error': '找不到對應的帳號或老師資料'}, 404

                t_id = user_info.get('real_teacher_id')
                u_id = user_info.get('id')

                # 查詢正在上課中的打卡紀錄 (clock_out IS NULL)
                active_shift = None
                if u_id:
                    cursor.execute("""
                    SELECT ta.*, u.name as user_name
                    FROM teacher_attendance ta
                    JOIN admin_users u ON ta.user_id = u.id
                    WHERE ta.user_id = %s AND ta.clock_out IS NULL
                    ORDER BY ta.id DESC LIMIT 1
                    """, (u_id,))
                    active_shift = cursor.fetchone()

                if active_shift:
                    for field in ['clock_in', 'created_at', 'updated_at']:
                        if active_shift.get(field) and isinstance(active_shift[field], datetime):
                            active_shift[field] = active_shift[field].isoformat()
                    active_shift['calculated_salary'] = int(math.floor(float(active_shift.get('calculated_salary') or 0)))

                    # 補充目前進行中課程的拆帳規則與預估費用
                    sched_id = active_shift.get('schedule_id')
                    c_info = None
                    if sched_id:
                        cursor.execute("""
                        SELECT c.id as course_id, c.name as course_name, c.base_salary, c.low_student_threshold, 
                               c.low_student_salary, c.extra_student_threshold, c.extra_student_fee, c.salary_cap,
                               (SELECT COUNT(*) FROM enrollments WHERE schedule_id = %s AND status = 'confirmed') as student_count
                        FROM course_schedules cs
                        JOIN courses c ON cs.course_id = c.id
    
                WHERE cs.id = %s
                        """, (sched_id, sched_id))
                        c_info = cursor.fetchone()
                    elif active_shift.get('course_id'):
                        cursor.execute("""
                        SELECT id as course_id, name as course_name, base_salary, low_student_threshold,
                               low_student_salary, extra_student_threshold, extra_student_fee, salary_cap, 0 as student_count
                        FROM courses WHERE id = %s
                        """, (active_shift['course_id'],))
                        c_info = cursor.fetchone()
                    elif active_shift.get('course_name'):
                        cursor.execute("""
                        SELECT id as course_id, name as course_name, base_salary, low_student_threshold,
                               low_student_salary, extra_student_threshold, extra_student_fee, salary_cap, 0 as student_count
                        FROM courses 
                        WHERE name = %s AND (teacher_id = %s OR teacher_id IS NULL)
                        ORDER BY id DESC LIMIT 1
                        """, (active_shift['course_name'], t_id))
                        c_info = cursor.fetchone()

                    if c_info:
                        active_shift['course_id'] = c_info.get('course_id')
                        active_shift['base_salary'] = float(c_info.get('base_salary') or 0)
                        active_shift['low_student_threshold'] = int(c_info.get('low_student_threshold') or 0)
                        active_shift['low_student_salary'] = float(c_info.get('low_student_salary') or 0)
                        active_shift['extra_student_threshold'] = int(c_info.get('extra_student_threshold') or 0)
                        active_shift['extra_student_fee'] = float(c_info.get('extra_student_fee') or 0)
                        active_shift['salary_cap'] = float(c_info.get('salary_cap') or 0)
                        active_shift['student_count'] = int(c_info.get('student_count') or 0)
                        if sched_id:
                            est, _, _ = compute_teacher_schedule_salary(cursor, sched_id, t_id)
                            active_shift['estimated_salary'] = est
                        else:
                            est, _, _ = compute_course_salary(cursor, c_info['course_id'], 0)
                            active_shift['estimated_salary'] = est

                # 查詢今日該老師的所有排程時段
                today_schedules = []
                target_date = request.args.get('date') or datetime.now().strftime('%Y-%m-%d')
                req_sched_id = request.args.get('schedule_id')
                if True:
                    cursor.execute("""
                    SELECT cs.id as schedule_id, cs.schedule_date, cs.start_time, cs.end_time,
                           c.id as course_id, c.name as course_name, c.level, c.base_salary, c.low_student_threshold, c.low_student_salary,
                           c.extra_student_threshold, c.extra_student_fee, c.salary_cap,
                           r.name as room_name,
                           (SELECT COUNT(*) FROM enrollments e WHERE e.schedule_id = cs.id AND e.status = 'confirmed') as student_count
                    FROM course_schedules cs
                    JOIN courses c ON cs.course_id = c.id
                    LEFT JOIN rooms r ON cs.room_id = r.id
                    WHERE cs.is_active = TRUE AND (%s IS NULL OR COALESCE(cs.teacher_id, c.teacher_id) = %s) AND (cs.schedule_date = %s OR cs.schedule_date = CURRENT_DATE())
                    ORDER BY cs.start_time ASC
                    """, (t_id, t_id, target_date))
                    raw_schedules = cursor.fetchall()

                    for s in raw_schedules:
                        if isinstance(s.get('schedule_date'), date):
                            s['schedule_date'] = s['schedule_date'].isoformat()
                        s['start_time_text'] = format_time_delta(s.get('start_time'))
                        s['end_time_text'] = format_time_delta(s.get('end_time'))
                        s['start_time'] = s['start_time_text']
                        s['end_time'] = s['end_time_text']
                        s['time_range'] = f"{s['start_time_text']} - {s['end_time_text']}"
                        s['base_salary'] = float(s.get('base_salary') or 0)
                        s['low_student_threshold'] = int(s.get('low_student_threshold') or 0)
                        s['low_student_salary'] = float(s.get('low_student_salary') or 0)
                        s['extra_student_threshold'] = int(s.get('extra_student_threshold') or 0)
                        s['extra_student_fee'] = float(s.get('extra_student_fee') or 0)
                        s['salary_cap'] = float(s.get('salary_cap') or 0)

                        # 試算預估鐘點費
                        est_salary, _, _ = compute_teacher_schedule_salary(cursor, s['schedule_id'], s.get('teacher_id') or t_id)
                        s['estimated_salary'] = est_salary

                        # 檢查此排程今日是否有打卡記錄
                        cursor.execute("""
                        SELECT id, clock_in, clock_out FROM teacher_attendance
                        WHERE schedule_id = %s AND DATE(clock_in) = CURRENT_DATE()
                        ORDER BY id DESC LIMIT 1
                        """, (s['schedule_id'],))
                        att = cursor.fetchone()
                        if att:
                            if att['clock_out']:
                                s['attendance_status'] = 'completed'
                                s['attendance_text'] = '已下課'
                            else:
                                s['attendance_status'] = 'in_progress'
                                s['attendance_text'] = '上課中'
                        else:
                            s['attendance_status'] = 'pending'
                            s['attendance_text'] = '未上課'

                        today_schedules.append(s)

                # 查詢該老師的所有開設課程 (供無排程或自由授課選擇拆帳規則)
                teacher_courses = []
                target_date = request.args.get('date') or datetime.now().strftime('%Y-%m-%d')
                req_sched_id = request.args.get('schedule_id')
                if True:
                    cursor.execute("""
                    SELECT id, name, level, base_salary, low_student_threshold, low_student_salary,
                           extra_student_threshold, extra_student_fee, salary_cap
                    FROM courses
                    WHERE (%s IS NULL OR teacher_id = %s) AND %s IS NOT NULL
                    ORDER BY name ASC
                    """, (t_id, t_id, target_date))
                    teacher_courses = cursor.fetchall()
                    for tc in teacher_courses:
                        tc['base_salary'] = float(tc.get('base_salary') or 0)
                        tc['low_student_threshold'] = int(tc.get('low_student_threshold') or 0)
                        tc['low_student_salary'] = float(tc.get('low_student_salary') or 0)
                        tc['extra_student_threshold'] = int(tc.get('extra_student_threshold') or 0)
                        tc['extra_student_fee'] = float(tc.get('extra_student_fee') or 0)
                        tc['salary_cap'] = float(tc.get('salary_cap') or 0)

                # 查詢今日其他老師的排程時段 (供現場臨時替他人代課打卡)
                substitute_schedules = []
                target_date = request.args.get('date') or datetime.now().strftime('%Y-%m-%d')
                req_sched_id = request.args.get('schedule_id')
                if True:
                    cursor.execute("""
                    SELECT cs.id as schedule_id, cs.schedule_date, cs.start_time, cs.end_time,
                           c.id as course_id, c.name as course_name, c.level, c.base_salary, c.low_student_threshold, c.low_student_salary,
                           c.extra_student_threshold, c.extra_student_fee, c.salary_cap,
                           r.name as room_name,
                           orig_t.id as original_teacher_id, orig_t.name as original_teacher_name,
                           (SELECT COUNT(*) FROM enrollments e WHERE e.schedule_id = cs.id AND e.status = 'confirmed') as student_count
                    FROM course_schedules cs
                    JOIN courses c ON cs.course_id = c.id
                    LEFT JOIN rooms r ON cs.room_id = r.id
                    LEFT JOIN teachers orig_t ON COALESCE(cs.teacher_id, c.teacher_id) = orig_t.id
                    WHERE cs.is_active = TRUE AND (%s IS NOT NULL AND (COALESCE(cs.teacher_id, c.teacher_id) != %s OR COALESCE(cs.teacher_id, c.teacher_id) IS NULL)) AND (cs.schedule_date = %s OR cs.schedule_date = CURRENT_DATE())
                    ORDER BY cs.start_time ASC
                    """, (t_id, t_id, target_date))
                    raw_subs = cursor.fetchall()
                    for sub in raw_subs:
                        if isinstance(sub.get('schedule_date'), date):
                            sub['schedule_date'] = sub['schedule_date'].isoformat()
                        sub['start_time_text'] = format_time_delta(sub.get('start_time'))
                        sub['end_time_text'] = format_time_delta(sub.get('end_time'))
                        sub['start_time'] = sub['start_time_text']
                        sub['end_time'] = sub['end_time_text']
                        sub['time_range'] = f"{sub['start_time_text']} - {sub['end_time_text']}"
                        sub['base_salary'] = float(sub.get('base_salary') or 0)
                        sub['low_student_threshold'] = int(sub.get('low_student_threshold') or 0)
                        sub['low_student_salary'] = float(sub.get('low_student_salary') or 0)
                        sub['extra_student_threshold'] = int(sub.get('extra_student_threshold') or 0)
                        sub['extra_student_fee'] = float(sub.get('extra_student_fee') or 0)
                        sub['salary_cap'] = float(sub.get('salary_cap') or 0)
                        sub['student_count'] = int(sub.get('student_count') or 0)
                        substitute_schedules.append(sub)

                # 查詢今日已完成或進行中的上課打卡歷史
                today_records = []
                if u_id:
                    cursor.execute("""
                    SELECT ta.*, u.name as user_name
                    FROM teacher_attendance ta
                    JOIN admin_users u ON ta.user_id = u.id
                    WHERE ta.user_id = %s AND DATE(ta.clock_in) = CURRENT_DATE()
                    ORDER BY ta.clock_in DESC
                    """, (u_id,))
                    today_records = cursor.fetchall()
                    for r in today_records:
                        for field in ['clock_in', 'clock_out', 'created_at', 'updated_at']:
                            if r.get(field) and isinstance(r[field], datetime):
                                r[field] = r[field].isoformat()
                        r['calculated_salary'] = int(math.floor(float(r.get('calculated_salary') or 0)))

                return {
                    'success': True,
                    'is_in_class': bool(active_shift),
                    'active_shift': active_shift,
                    'today_schedules': today_schedules,
                    'teacher_courses': teacher_courses,
                    'today_records': today_records,
                    'substitute_schedules': substitute_schedules,
                    'client_ip': get_client_ip(),
                    'teacher_info': {
                        'user_id': u_id,
                        'teacher_id': t_id,
                        'name': user_info.get('name') or user_info.get('teacher_name'),
                        'role': user_info.get('role'),
                        'bank_account': user_info.get('teacher_bank_account') or user_info.get('bank_account'),
                        'avatar_url': user_info.get('teacher_avatar_url')
                    }
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢老師打卡狀態失敗: {str(e)}'}, 500

class TeacherAttendanceClockIn(Resource):
    def post(self):
        """老師上課打卡"""
        try:
            data = request.get_json() or {}
            user_id = data.get('user_id')
            schedule_id = data.get('schedule_id')
            course_id = data.get('course_id')
            course_name = (data.get('course_name') or '').strip()
            notes = (data.get('notes') or '').strip() or None

            if not user_id:
                return {'error': '缺少 user_id 參數'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)

                # 驗證打卡 IP 白名單
                allowed, client_ip, err_msg = check_attendance_ip_permission(cursor)
                if not allowed:
                    return {'error': err_msg, 'client_ip': client_ip}, 403

                cursor.execute("""
                SELECT id FROM teacher_attendance
                WHERE user_id = %s AND clock_out IS NULL
                """, (user_id,))
                if cursor.fetchone():
                    return {'error': '目前已在上課打卡進行中，請先完成上一堂課的下課打卡！'}, 400

                cursor.execute("SELECT * FROM admin_users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return {'error': '找不到該老師帳號'}, 404

                teacher_id = user.get('teacher_id')
                is_substitute = bool(data.get('is_substitute', False))
                original_teacher_id = data.get('original_teacher_id')

                # 若指定了 schedule_id，自動帶出課程 ID 與名稱
                if schedule_id:
                    cursor.execute("""
                    SELECT cs.teacher_id as cs_teacher_id, c.id as course_id, c.name as course_name, c.teacher_id as c_teacher_id FROM course_schedules cs
                    JOIN courses c ON cs.course_id = c.id

                WHERE cs.id = %s
                    """, (schedule_id,))
                    c_row = cursor.fetchone()
                    if c_row:
                        course_id = c_row['course_id']
                        course_name = c_row['course_name']
                        def_teacher = c_row.get('cs_teacher_id') or c_row.get('c_teacher_id')
                        if def_teacher and teacher_id and int(def_teacher) != int(teacher_id):
                            is_substitute = True
                            original_teacher_id = def_teacher
                            cursor.execute("UPDATE course_schedules SET teacher_id = %s, is_substitute = 1, substitute_notes = COALESCE(%s, substitute_notes, '現場即時代課') WHERE id = %s", (teacher_id, notes, schedule_id))
                elif course_id:
                    cursor.execute("SELECT name FROM courses WHERE id = %s", (course_id,))
                    c_row = cursor.fetchone()
                    if c_row:
                        course_name = c_row['name']

                if not course_name:
                    course_name = '一般授課課程'

                now = datetime.now()
                cursor.execute("""
                INSERT INTO teacher_attendance (user_id, teacher_id, schedule_id, course_id, course_name, clock_in, notes, clock_in_ip, is_substitute, original_teacher_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, teacher_id, schedule_id or None, course_id or None, course_name, now, notes, client_ip, 1 if is_substitute else 0, original_teacher_id or None))
                connection.commit()

                return {
                    'success': True,
                    'message': f'{user["name"]}，上課打卡成功！祝您授課順利！',
                    'clock_in': now.isoformat(),
                    'course_name': course_name,
                    'clock_in_ip': client_ip
                }, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'上課打卡失敗: {str(e)}'}, 500

class TeacherAttendanceClockOut(Resource):
    def post(self):
        """老師下課打卡 (依課堂師資鐘點費/拆帳規則結算，非預設時薪)"""
        try:
            data = request.get_json() or {}
            user_id = data.get('user_id')
            notes = (data.get('notes') or '').strip() or None

            if not user_id:
                return {'error': '缺少 user_id 參數'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)

                # 驗證打卡 IP 白名單
                allowed, client_ip, err_msg = check_attendance_ip_permission(cursor)
                if not allowed:
                    return {'error': err_msg, 'client_ip': client_ip}, 403

                cursor.execute("""
                SELECT ta.*, u.name as user_name, u.teacher_id as u_teacher_id
                FROM teacher_attendance ta
                JOIN admin_users u ON ta.user_id = u.id
                WHERE ta.user_id = %s AND ta.clock_out IS NULL
                ORDER BY ta.id DESC LIMIT 1
                """, (user_id,))
                active_shift = cursor.fetchone()

                if not active_shift:
                    return {'error': '目前無進行中的上課紀錄，請確認是否已上課打卡'}, 400

                now = datetime.now()
                clock_in = active_shift['clock_in']
                duration_minutes = max(1, int(round((now - clock_in).total_seconds() / 60)))

                schedule_id = active_shift.get('schedule_id')
                course_id = active_shift.get('course_id')
                teacher_id = active_shift.get('teacher_id') or active_shift.get('u_teacher_id')

                student_count = 0
                salary = 0

                # 嚴格依該課堂之師資鐘點費/拆帳規則計算
                if schedule_id:
                    salary, student_count, c_name = compute_teacher_schedule_salary(cursor, schedule_id, teacher_id, duration_minutes)
                elif course_id:
                    salary, student_count, c_name = compute_course_salary(cursor, course_id, 0)
                else:
                    # 依課程名稱比對老師開設課程之拆帳規則
                    c_name = active_shift.get('course_name') or ''
                    cursor.execute("""
                    SELECT id FROM courses 
                    WHERE name = %s AND (teacher_id = %s OR teacher_id IS NULL)
                    ORDER BY id DESC LIMIT 1
                    """, (c_name, teacher_id))
                    c_match = cursor.fetchone()
                    if c_match:
                        salary, student_count, _ = compute_course_salary(cursor, c_match['id'], 0)
                    else:
                        salary = 0

                cursor.execute("""
                UPDATE teacher_attendance
                SET clock_out = %s, duration_minutes = %s, student_count = %s, calculated_salary = %s,
                    notes = COALESCE(%s, notes), clock_out_ip = %s
                WHERE id = %s
                """, (now, duration_minutes, student_count, salary, notes, client_ip, active_shift['id']))
                connection.commit()

                return {
                    'success': True,
                    'message': f'{active_shift["user_name"]}，下課打卡成功！本堂授課 {duration_minutes} 分鐘，結算課堂鐘點費 NT$ {salary} 元。老師辛苦了！',
                    'clock_out': now.isoformat(),
                    'duration_minutes': duration_minutes,
                    'student_count': student_count,
                    'calculated_salary': salary,
                    'clock_out_ip': client_ip
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'下課打卡失敗: {str(e)}'}, 500

class TeacherAttendanceList(Resource):
    def get(self):
        """查詢老師上課下課打卡歷史紀錄與統計"""
        user_id = request.args.get('user_id')
        teacher_id = request.args.get('teacher_id')
        month = request.args.get('month')

        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT ta.*, u.name as user_name, u.username, t.name as teacher_name, t.bank_account as teacher_bank_account
                FROM teacher_attendance ta
                JOIN admin_users u ON ta.user_id = u.id
                LEFT JOIN teachers t ON ta.teacher_id = t.id
                WHERE 1=1
                """
                params = []

                if user_id:
                    query += " AND ta.user_id = %s"
                    params.append(user_id)

                if teacher_id:
                    query += " AND ta.teacher_id = %s"
                    params.append(teacher_id)

                if month:
                    query += " AND DATE_FORMAT(ta.clock_in, '%Y-%m') = %s"
                    params.append(month)

                query += " ORDER BY ta.clock_in DESC"
                cursor.execute(query, tuple(params))
                records = cursor.fetchall()

                total_classes = len(records)
                total_minutes = 0
                total_salary = 0

                for r in records:
                    for field in ['clock_in', 'clock_out', 'created_at', 'updated_at']:
                        if r.get(field) and isinstance(r[field], datetime):
                            r[field] = r[field].isoformat()
                    r['calculated_salary'] = int(math.floor(float(r.get('calculated_salary') or 0)))
                    r['duration_minutes'] = int(r.get('duration_minutes') or 0)
                    r['student_count'] = int(r.get('student_count') or 0)
                    total_minutes += r['duration_minutes']
                    total_salary += r['calculated_salary']

                total_hours = round(total_minutes / 60.0, 1)

                return {
                    'success': True,
                    'records': records,
                    'summary': {
                        'total_classes': total_classes,
                        'total_minutes': total_minutes,
                        'total_hours': total_hours,
                        'total_salary': total_salary
                    }
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢老師打卡歷史失敗: {str(e)}'}, 500

class TeacherAttendanceItem(Resource):
    def put(self, attendance_id):
        """管理員編輯老師上課下課打卡紀錄"""
        try:
            data = request.get_json() or {}
            clock_in_str = (data.get('clock_in') or '').strip()
            clock_out_str = (data.get('clock_out') or '').strip()
            course_name = (data.get('course_name') or '').strip()
            course_id = data.get('course_id')
            student_count = data.get('student_count')
            calculated_salary = data.get('calculated_salary')
            notes = (data.get('notes') or '').strip() or None

            if not clock_in_str:
                return {'error': '上課時間不可為空'}, 400

            try:
                clock_in = datetime.fromisoformat(clock_in_str.replace('Z', ''))
            except Exception:
                return {'error': '上課時間格式錯誤'}, 400

            clock_out = None
            if clock_out_str:
                try:
                    clock_out = datetime.fromisoformat(clock_out_str.replace('Z', ''))
                except Exception:
                    return {'error': '下課時間格式錯誤'}, 400

            if clock_out and clock_out < clock_in:
                return {'error': '下課時間不可早於上課時間'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500

            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM teacher_attendance WHERE id = %s", (attendance_id,))
                current_record = cursor.fetchone()
                if not current_record:
                    return {'error': '找不到該筆授課打卡記錄'}, 404

                duration_minutes = 0
                if clock_out:
                    duration_minutes = max(1, int(round((clock_out - clock_in).total_seconds() / 60)))

                salary = int(calculated_salary) if calculated_salary is not None else int(float(current_record['calculated_salary'] or 0))
                s_count = int(student_count) if student_count is not None else int(current_record['student_count'] or 0)
                c_name = course_name or current_record['course_name'] or '一般授課課程'
                c_id = course_id if course_id is not None else current_record.get('course_id')

                cursor.execute("""
                UPDATE teacher_attendance
                SET clock_in = %s, clock_out = %s, duration_minutes = %s,
                    course_id = %s, course_name = %s, student_count = %s, calculated_salary = %s,
                    notes = %s
                WHERE id = %s
                """, (clock_in, clock_out, duration_minutes, c_id, c_name, s_count, salary, notes, attendance_id))
                connection.commit()

                return {'success': True, 'message': '授課紀錄已成功更新！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新授課紀錄失敗: {str(e)}'}, 500

    def delete(self, attendance_id):
        """刪除老師打卡紀錄"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM teacher_attendance WHERE id = %s", (attendance_id,))
                connection.commit()
                return {'success': True, 'message': '打卡記錄已刪除'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'刪除打卡記錄失敗: {str(e)}'}, 500

class TeacherAvatarUpload(Resource):
    @jwt_required(['admin', 'desk', 'teacher'])
    def post(self, teacher_id=None):
        """上傳老師大頭貼圖片"""
        try:
            file = request.files.get('file') or request.files.get('avatar') or request.files.get('image')
            avatar_url = None
            
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
                if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    return {'error': '僅支援 JPG, PNG, GIF, WEBP 圖片格式'}, 400
                
                safe_name = f"teacher_{teacher_id or 'new'}_{int(time.time())}.{ext}"
                file_path = os.path.join(AVATARS_FOLDER, safe_name)
                file.save(file_path)
                avatar_url = f"/api/uploads/avatars/{safe_name}"
            else:
                data = request.get_json() or {}
                raw_url = data.get('avatar_url') or data.get('image_url')
                raw_base64 = data.get('image_base64') or data.get('base64')
                
                if raw_url:
                    avatar_url = raw_url.strip()
                elif raw_base64:
                    import base64
                    if ',' in raw_base64:
                        header, base64_data = raw_base64.split(',', 1)
                        if 'png' in header:
                            ext = 'png'
                        elif 'webp' in header:
                            ext = 'webp'
                        else:
                            ext = 'jpg'
                    else:
                        base64_data = raw_base64
                        ext = 'jpg'
                    img_bytes = base64.b64decode(base64_data)
                    safe_name = f"teacher_{teacher_id or 'new'}_{int(time.time())}.{ext}"
                    file_path = os.path.join(AVATARS_FOLDER, safe_name)
                    with open(file_path, 'wb') as f:
                        f.write(img_bytes)
                    avatar_url = f"/api/uploads/avatars/{safe_name}"
                else:
                    return {'error': '未收到上傳檔案或圖片資料'}, 400

            # 若有指定 teacher_id，立即更新 teachers 資料庫
            if teacher_id:
                connection = get_db_connection()
                if connection:
                    try:
                        cursor = connection.cursor(buffered=True)
                        cursor.execute("UPDATE teachers SET avatar_url = %s WHERE id = %s", (avatar_url, teacher_id))
                        connection.commit()
                    finally:
                        cursor.close()
                        connection.close()

            return {
                'success': True,
                'avatar_url': avatar_url,
                'message': '大頭貼上傳成功！'
            }, 200
        except Exception as e:
            return {'error': f'大頭貼上傳失敗: {str(e)}'}, 500

    def delete(self, teacher_id=None):
        """清除老師大頭貼"""
        try:
            if not teacher_id:
                return {'error': '缺少老師 ID'}, 400
            connection = get_db_connection()
            if connection:
                try:
                    cursor = connection.cursor(buffered=True)
                    cursor.execute("UPDATE teachers SET avatar_url = NULL WHERE id = %s", (teacher_id,))
                    connection.commit()
                    return {'success': True, 'message': '大頭貼已成功清除'}
                finally:
                    cursor.close()
                    connection.close()
            return {'error': '資料庫連線失敗'}, 500
        except Exception as e:
            return {'error': f'清除大頭貼失敗: {str(e)}'}, 500

api.add_resource(AdminLogin, '/api/admin/login')
api.add_resource(AdminUsers, '/api/admin/users')
api.add_resource(AdminUser, '/api/admin/users/<int:user_id>')
api.add_resource(TeacherAccount, '/api/teachers/<int:teacher_id>/account')
api.add_resource(TeacherAvatarUpload, '/api/teachers/<int:teacher_id>/avatar', '/api/upload/avatar')
api.add_resource(StaffAttendanceStatus, '/api/admin/attendance/status')
api.add_resource(StaffAttendanceClockIn, '/api/admin/attendance/clock-in')
api.add_resource(StaffAttendanceClockOut, '/api/admin/attendance/clock-out')
api.add_resource(StaffAttendanceList, '/api/admin/attendance')
api.add_resource(StaffAttendanceItem, '/api/admin/attendance/<int:attendance_id>')
api.add_resource(TeacherAttendanceStatus, '/api/admin/teacher-attendance/status')
api.add_resource(TeacherAttendanceClockIn, '/api/admin/teacher-attendance/clock-in')
api.add_resource(TeacherAttendanceClockOut, '/api/admin/teacher-attendance/clock-out')
api.add_resource(TeacherAttendanceList, '/api/admin/teacher-attendance')
api.add_resource(TeacherAttendanceItem, '/api/admin/teacher-attendance/<int:attendance_id>')
class RoomImageUpload(Resource):
    @jwt_required(['admin', 'desk'])
    def post(self, room_id=None):
        """上傳教室/環境照片"""
        try:
            file = request.files.get('file') or request.files.get('image')
            image_url = None
            
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
                if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    return {'error': '僅支援 JPG, PNG, GIF, WEBP 圖片格式'}, 400
                
                safe_name = f"room_{room_id or 'new'}_{int(time.time())}.{ext}"
                file_path = os.path.join(ROOMS_FOLDER, safe_name)
                file.save(file_path)
                image_url = f"/api/uploads/rooms/{safe_name}"
            else:
                data = request.get_json() or {}
                raw_url = data.get('image_url')
                raw_base64 = data.get('image_base64') or data.get('base64')
                
                if raw_url:
                    image_url = raw_url.strip()
                elif raw_base64:
                    import base64
                    if ',' in raw_base64:
                        header, base64_data = raw_base64.split(',', 1)
                        if 'png' in header:
                            ext = 'png'
                        elif 'webp' in header:
                            ext = 'webp'
                        else:
                            ext = 'jpg'
                    else:
                        base64_data = raw_base64
                        ext = 'jpg'
                    img_bytes = base64.b64decode(base64_data)
                    safe_name = f"room_{room_id or 'new'}_{int(time.time())}.{ext}"
                    file_path = os.path.join(ROOMS_FOLDER, safe_name)
                    with open(file_path, 'wb') as f:
                        f.write(img_bytes)
                    image_url = f"/api/uploads/rooms/{safe_name}"
                else:
                    return {'error': '未收到上傳檔案或圖片資料'}, 400

            # 若有指定 room_id，立即更新 rooms 資料庫
            if room_id:
                connection = get_db_connection()
                if connection:
                    try:
                        cursor = connection.cursor(buffered=True)
                        cursor.execute("UPDATE rooms SET image_url = %s WHERE id = %s", (image_url, room_id))
                        connection.commit()
                    finally:
                        cursor.close()
                        connection.close()

            return {
                'success': True,
                'image_url': image_url,
                'message': '教室圖片上傳成功！'
            }, 200
        except Exception as e:
            return {'error': f'教室圖片上傳失敗: {str(e)}'}, 500

    def delete(self, room_id=None):
        """清除教室圖片"""
        try:
            if not room_id:
                return {'error': '缺少教室 ID'}, 400
            connection = get_db_connection()
            if connection:
                try:
                    cursor = connection.cursor(buffered=True)
                    cursor.execute("UPDATE rooms SET image_url = NULL WHERE id = %s", (room_id,))
                    connection.commit()
                    return {'success': True, 'message': '已清除教室圖片'}, 200
                finally:
                    cursor.close()
                    connection.close()
            return {'error': '資料庫連線失敗'}, 500
        except Exception as e:
            return {'error': f'清除教室圖片失敗: {str(e)}'}, 500

api.add_resource(RoomImageUpload, '/api/rooms/<int:room_id>/image', '/api/upload/room-image')
api.add_resource(AttendanceIpSettings, '/api/admin/settings/attendance-ip')

class NewsListResource(Resource):
    def get(self):
        """取得最新消息與活動列表"""
        try:
            category = request.args.get('category')
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連線失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                if category:
                    cursor.execute("SELECT * FROM news WHERE category = %s AND is_published = 1 ORDER BY publish_date DESC, id DESC", (category,))
                else:
                    cursor.execute("SELECT * FROM news WHERE is_published = 1 ORDER BY publish_date DESC, id DESC")
                items = cursor.fetchall()
                for item in items:
                    for field in ['publish_date', 'created_at', 'updated_at']:
                        if item.get(field):
                            item[field] = str(item[field])
                return {'success': True, 'news': items, 'total': len(items)}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢最新消息失敗: {str(e)}'}, 500

    def post(self):
        """新增消息或活動"""
        try:
            data = request.get_json() or {}
            title = data.get('title')
            if not title:
                return {'error': '缺少標題'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連線失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("""
                    INSERT INTO news (title, category, tag, summary, content, image_url, is_published, publish_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_DATE))
                """, (
                    title,
                    data.get('category', 'news'),
                    data.get('tag', '公告'),
                    data.get('summary', ''),
                    data.get('content', ''),
                    data.get('image_url', ''),
                    1 if data.get('is_published', True) else 0,
                    data.get('publish_date')
                ))
                connection.commit()
                news_id = cursor.lastrowid
                return {'success': True, 'id': news_id, 'message': '新增成功'}, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'新增消息失敗: {str(e)}'}, 500

class NewsItemResource(Resource):
    def get(self, news_id):
        """取得單一消息"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連線失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM news WHERE id = %s", (news_id,))
                item = cursor.fetchone()
                if not item:
                    return {'error': '消息未找到'}, 404
                for field in ['publish_date', 'created_at', 'updated_at']:
                    if item.get(field):
                        item[field] = str(item[field])
                return {'success': True, 'news': item}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢消息失敗: {str(e)}'}, 500

    def put(self, news_id):
        """更新消息"""
        try:
            data = request.get_json() or {}
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連線失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                update_fields = []
                values = []
                for field in ['title', 'category', 'tag', 'summary', 'content', 'image_url', 'is_published', 'publish_date']:
                    if field in data:
                        update_fields.append(f"{field} = %s")
                        values.append(data[field])
                if not update_fields:
                    return {'error': '無可更新欄位'}, 400
                values.append(news_id)
                cursor.execute(f"UPDATE news SET {', '.join(update_fields)} WHERE id = %s", tuple(values))
                connection.commit()
                return {'success': True, 'message': '更新成功'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新失敗: {str(e)}'}, 500

    def delete(self, news_id):
        """刪除消息"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連線失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM news WHERE id = %s", (news_id,))
                connection.commit()
                return {'success': True, 'message': '刪除成功'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'刪除失敗: {str(e)}'}, 500

class TeacherFeaturedToggle(Resource):
    def post(self, teacher_id):
        """切換老師是否為本月主打星"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT is_featured FROM teachers WHERE id = %s", (teacher_id,))
                row = cursor.fetchone()
                if not row:
                    return {'error': '找不到該老師'}, 404
                new_state = 0 if row.get('is_featured') else 1
                cursor.execute("UPDATE teachers SET is_featured = %s WHERE id = %s", (new_state, teacher_id))
                connection.commit()
                return {
                    'success': True,
                    'is_featured': bool(new_state),
                    'message': '已設為本月主打星！' if new_state else '已取消本月主打星'
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新主打星狀態失敗: {str(e)}'}, 500

api.add_resource(NewsListResource, '/api/news')
api.add_resource(NewsItemResource, '/api/news/<int:news_id>')
api.add_resource(TeacherFeaturedToggle, '/api/teachers/<int:teacher_id>/toggle-featured')


def parse_plan_features(raw_features):
    """解析 features 欄位，支援 JSON 陣列或換行分隔字串"""
    if not raw_features:
        return []
    if isinstance(raw_features, list):
        return raw_features
    try:
        parsed = json.loads(raw_features)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except Exception:
        pass
    return [line.strip() for line in str(raw_features).split('\n') if line.strip()]

def format_pricing_plan(row):
    """格式化方案資料給前端"""
    if not row:
        return None
    features = parse_plan_features(row.get('features'))
    return {
        'id': row['id'],
        'title': row.get('title', ''),
        'subtitle': row.get('subtitle', ''),
        'price': row.get('price', ''),
        'unit': row.get('unit', ''),
        'plan_type': row.get('plan_type') or 'classes',
        'validity_days': row.get('validity_days') or 0,
        'original_price': row.get('original_price'),
        'classes_count': row.get('classes_count') if row.get('classes_count') is not None else 1,
        'is_popular': bool(row.get('is_popular')),
        'requires_membership': bool(row.get('requires_membership', 0)),
        'features': features,
        'button_text': row.get('button_text') or '買課',
        'button_link': row.get('button_link') or '/contact',
        'sort_order': row.get('sort_order', 0),
        'is_active': bool(row.get('is_active', 1)),
        'created_at': str(row.get('created_at')) if row.get('created_at') else None,
        'updated_at': str(row.get('updated_at')) if row.get('updated_at') else None
    }

class PricingListResource(Resource):
    def get(self):
        """取得價目表方案清單及上課須知 (支援 ?admin=1 取得全部方案)"""
        try:
            is_admin = request.args.get('admin') in ['1', 'true', 'True'] or request.args.get('all') in ['1', 'true', 'True']
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                if is_admin:
                    cursor.execute("SELECT * FROM pricing_plans ORDER BY sort_order ASC, id ASC")
                else:
                    cursor.execute("SELECT * FROM pricing_plans WHERE is_active = 1 ORDER BY sort_order ASC, id ASC")
                rows = cursor.fetchall()
                plans = [format_pricing_plan(r) for r in rows]

                cursor.execute("""
                    SELECT setting_key, setting_value FROM system_settings 
                    WHERE setting_key IN ('pricing_notice_title', 'pricing_notice_content', 'bank_name', 'bank_code', 'bank_account', 'bank_account_name', 'bank_notes')
                """)
                settings_rows = cursor.fetchall()
                settings_dict = {s['setting_key']: s['setting_value'] for s in settings_rows}

                notice_title = settings_dict.get('pricing_notice_title') or '學員報名與上課須知'
                notice_content = settings_dict.get('pricing_notice_content') or ''
                notice_items = [line.strip() for line in notice_content.split('\n') if line.strip()]

                bank_info = {
                    'bank_name': settings_dict.get('bank_name') or '國泰世華銀行',
                    'bank_code': settings_dict.get('bank_code') or '013',
                    'bank_account': settings_dict.get('bank_account') or '012-34-567890-1',
                    'bank_account_name': settings_dict.get('bank_account_name') or 'Dance Studio 舞蹈工作室',
                    'bank_notes': settings_dict.get('bank_notes') if settings_dict.get('bank_notes') is not None else '請先完成匯款後，於下方填寫您的轉帳帳號後 5 碼，以便工作人員核帳開通堂數。'
                }

                return {
                    'success': True,
                    'plans': plans,
                    'total': len(plans),
                    'notice': {
                        'title': notice_title,
                        'content': notice_content,
                        'items': notice_items
                    },
                    'bank_info': bank_info
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢價目表失敗: {str(e)}'}, 500

    def post(self):
        """新增價目方案"""
        try:
            data = request.get_json() or {}
            title = (data.get('title') or '').strip()
            price = (data.get('price') or '').strip()
            unit = (data.get('unit') or '').strip()

            if not title:
                return {'error': '請輸入方案名稱'}, 400
            if not price:
                return {'error': '請輸入方案價格'}, 400
            if not unit:
                return {'error': '請輸入計費單位'}, 400

            features_input = data.get('features')
            if isinstance(features_input, list):
                features_str = json.dumps([str(x).strip() for x in features_input if str(x).strip()], ensure_ascii=False)
            elif isinstance(features_input, str):
                features_list = [l.strip() for l in features_input.split('\n') if l.strip()]
                features_str = json.dumps(features_list, ensure_ascii=False)
            else:
                features_str = json.dumps([], ensure_ascii=False)

            plan_type = (data.get('plan_type') or 'classes').strip()
            validity_days = int(data.get('validity_days', 0) or 0)
            if plan_type == 'membership_fee' and validity_days <= 0:
                validity_days = 365
            elif plan_type == 'monthly_pass' and validity_days <= 0:
                validity_days = 30
            is_popular = 1 if data.get('is_popular') else 0
            requires_membership = 1 if (data.get('requires_membership') and plan_type != 'membership_fee') else 0
            is_active = 1 if data.get('is_active', True) else 0
            sort_order = int(data.get('sort_order', 0) or 0)
            classes_count = int(data.get('classes_count', 0) if data.get('classes_count') is not None else (1 if plan_type == 'classes' else 0))
            subtitle = (data.get('subtitle') or '').strip() or None
            original_price = (data.get('original_price') or '').strip() or None
            button_text = (data.get('button_text') or '').strip() or '買課'
            button_link = (data.get('button_link') or '').strip() or '/contact'

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("""
                    INSERT INTO pricing_plans 
                    (title, subtitle, price, unit, plan_type, classes_count, validity_days, original_price, is_popular, requires_membership, features, button_text, button_link, sort_order, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    title, subtitle, price, unit, plan_type, classes_count, validity_days, original_price, is_popular, requires_membership, features_str,
                    button_text, button_link, sort_order, is_active
                ))
                connection.commit()
                new_id = cursor.lastrowid
                return {'success': True, 'id': new_id, 'message': '新增價目方案成功'}, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'新增方案失敗: {str(e)}'}, 500

class PricingItemResource(Resource):
    def get(self, plan_id):
        """取得單一價目方案"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM pricing_plans WHERE id = %s", (plan_id,))
                row = cursor.fetchone()
                if not row:
                    return {'error': '查無此價目方案'}, 404
                return {'success': True, 'plan': format_pricing_plan(row)}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢方案失敗: {str(e)}'}, 500

    def put(self, plan_id):
        """更新價目方案"""
        try:
            data = request.get_json() or {}
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM pricing_plans WHERE id = %s", (plan_id,))
                existing = cursor.fetchone()
                if not existing:
                    return {'error': '查無此價目方案'}, 404

                update_fields = []
                values = []

                if 'title' in data:
                    update_fields.append("title = %s")
                    values.append(str(data['title']).strip())
                if 'subtitle' in data:
                    update_fields.append("subtitle = %s")
                    values.append(str(data['subtitle']).strip() if data['subtitle'] else None)
                if 'price' in data:
                    update_fields.append("price = %s")
                    values.append(str(data['price']).strip())
                if 'unit' in data:
                    update_fields.append("unit = %s")
                    values.append(str(data['unit']).strip())
                if 'original_price' in data:
                    update_fields.append("original_price = %s")
                    values.append(str(data['original_price']).strip() if data['original_price'] else None)
                if 'plan_type' in data:
                    update_fields.append("plan_type = %s")
                    values.append(str(data['plan_type']).strip() or 'classes')
                if 'validity_days' in data:
                    update_fields.append("validity_days = %s")
                    values.append(int(data['validity_days'] or 0))
                if 'classes_count' in data:
                    update_fields.append("classes_count = %s")
                    values.append(int(data['classes_count'] if data['classes_count'] is not None else 0))
                if 'is_popular' in data:
                    update_fields.append("is_popular = %s")
                    values.append(1 if data['is_popular'] else 0)


                if 'requires_membership' in data:
                    update_fields.append("requires_membership = %s")
                    values.append(1 if data['requires_membership'] else 0)



                if 'button_text' in data:
                    update_fields.append("button_text = %s")
                    values.append(str(data['button_text']).strip() or '買課')
                if 'button_link' in data:
                    update_fields.append("button_link = %s")
                    values.append(str(data['button_link']).strip() or '/contact')
                if 'sort_order' in data:
                    update_fields.append("sort_order = %s")
                    values.append(int(data['sort_order'] or 0))
                if 'is_active' in data:
                    update_fields.append("is_active = %s")
                    values.append(1 if data['is_active'] else 0)
                if 'features' in data:
                    features_input = data['features']
                    if isinstance(features_input, list):
                        features_str = json.dumps([str(x).strip() for x in features_input if str(x).strip()], ensure_ascii=False)
                    elif isinstance(features_input, str):
                        features_list = [l.strip() for l in features_input.split('\n') if l.strip()]
                        features_str = json.dumps(features_list, ensure_ascii=False)
                    else:
                        features_str = json.dumps([], ensure_ascii=False)
                    update_fields.append("features = %s")
                    values.append(features_str)

                if not update_fields:
                    return {'error': '無可更新欄位'}, 400

                values.append(plan_id)
                cursor.execute(f"UPDATE pricing_plans SET {', '.join(update_fields)} WHERE id = %s", tuple(values))
                connection.commit()
                return {'success': True, 'message': '更新方案成功'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新方案失敗: {str(e)}'}, 500

    def delete(self, plan_id):
        """刪除價目方案"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM pricing_plans WHERE id = %s", (plan_id,))
                connection.commit()
                return {'success': True, 'message': '刪除方案成功'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'刪除方案失敗: {str(e)}'}, 500

class PricingNoticeResource(Resource):
    def get(self):
        """取得學員報名與上課須知設定"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT setting_key, setting_value FROM system_settings 
                    WHERE setting_key IN ('pricing_notice_title', 'pricing_notice_content')
                """)
                rows = cursor.fetchall()
                s_dict = {r['setting_key']: r['setting_value'] for r in rows}
                title = s_dict.get('pricing_notice_title') or '學員報名與上課須知'
                content = s_dict.get('pricing_notice_content') or ''
                items = [l.strip() for l in content.split('\n') if l.strip()]
                return {
                    'success': True,
                    'title': title,
                    'content': content,
                    'items': items
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢上課須知失敗: {str(e)}'}, 500

    def put(self):
        """更新學員報名與上課須知設定"""
        try:
            data = request.get_json() or {}
            title = (data.get('title') or '學員報名與上課須知').strip()
            content = (data.get('content') or '').strip()

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("""
                    INSERT INTO system_settings (setting_key, setting_value, description)
                    VALUES ('pricing_notice_title', %s, '課程價目表須知標題')
                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                """, (title,))
                cursor.execute("""
                    INSERT INTO system_settings (setting_key, setting_value, description)
                    VALUES ('pricing_notice_content', %s, '課程價目表學員須知內容(每行一項)')
                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                """, (content,))
                connection.commit()
                return {'success': True, 'message': '上課須知更新成功'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新上課須知失敗: {str(e)}'}, 500

class PricingBankAccountResource(Resource):
    def get(self):
        """取得工作室轉帳匯款帳號資訊"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT setting_key, setting_value FROM system_settings 
                    WHERE setting_key IN ('bank_name', 'bank_code', 'bank_account', 'bank_account_name', 'bank_notes')
                """)
                rows = cursor.fetchall()
                s_dict = {r['setting_key']: r['setting_value'] for r in rows}
                bank_info = {
                    'bank_name': s_dict.get('bank_name') or '國泰世華銀行',
                    'bank_code': s_dict.get('bank_code') or '013',
                    'bank_account': s_dict.get('bank_account') or '012-34-567890-1',
                    'bank_account_name': s_dict.get('bank_account_name') or 'Dance Studio 舞蹈工作室',
                    'bank_notes': s_dict.get('bank_notes') if s_dict.get('bank_notes') is not None else '請先完成匯款後，於下方填寫您的轉帳帳號後 5 碼，以便工作人員核帳開通堂數。'
                }
                return {
                    'success': True,
                    'bank_info': bank_info
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢匯款帳號資訊失敗: {str(e)}'}, 500

    def put(self):
        """更新工作室轉帳匯款帳號資訊 (限定系統管理員 admin 權限)"""
        try:
            data = request.get_json() or {}
            admin_user_id = data.get('admin_user_id')
            if not admin_user_id:
                return {'error': '缺少管理員識別資訊，請先登入系統管理員帳號'}, 401

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                # 驗證操作者是否為 admin
                cursor.execute("SELECT id, name, role FROM admin_users WHERE id = %s", (admin_user_id,))
                user = cursor.fetchone()
                if not user or user.get('role') != 'admin':
                    return {'error': '權限不足！只有「系統管理員（admin）」具備修改工作室轉帳匯款帳號的權限。'}, 403

                bank_name = (data.get('bank_name') or '').strip()
                bank_code = (data.get('bank_code') or '').strip()
                bank_account = (data.get('bank_account') or '').strip()
                bank_account_name = (data.get('bank_account_name') or '').strip()
                bank_notes = (data.get('bank_notes') or '').strip()

                if not bank_name:
                    return {'error': '請輸入銀行名稱'}, 400
                if not bank_code:
                    return {'error': '請輸入銀行代碼'}, 400
                if not bank_account:
                    return {'error': '請輸入轉帳帳號'}, 400
                if not bank_account_name:
                    return {'error': '請輸入戶名'}, 400

                settings_to_update = [
                    ('bank_name', bank_name, '工作室匯款銀行名稱'),
                    ('bank_code', bank_code, '工作室匯款銀行代碼'),
                    ('bank_account', bank_account, '工作室匯款帳號'),
                    ('bank_account_name', bank_account_name, '工作室匯款戶名'),
                    ('bank_notes', bank_notes, '工作室匯款附註與說明')
                ]
                for key, val, desc in settings_to_update:
                    cursor.execute("""
                        INSERT INTO system_settings (setting_key, setting_value, description)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                    """, (key, val, desc))

                connection.commit()
                return {
                    'success': True,
                    'message': '工作室轉帳匯款帳號資訊已成功更新！前台將即時生效。',
                    'bank_info': {
                        'bank_name': bank_name,
                        'bank_code': bank_code,
                        'bank_account': bank_account,
                        'bank_account_name': bank_account_name,
                        'bank_notes': bank_notes
                    }
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新匯款帳號資訊失敗: {str(e)}'}, 500

class PricingToggleActiveResource(Resource):
    def post(self, plan_id):
        """切換方案上架/下架啟用狀態"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT is_active FROM pricing_plans WHERE id = %s", (plan_id,))
                row = cursor.fetchone()
                if not row:
                    return {'error': '查無此價目方案'}, 404
                new_state = 0 if row.get('is_active') else 1
                cursor.execute("UPDATE pricing_plans SET is_active = %s WHERE id = %s", (new_state, plan_id))
                connection.commit()
                return {
                    'success': True,
                    'is_active': bool(new_state),
                    'message': '方案已上架顯示' if new_state else '方案已下架隱藏'
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'切換狀態失敗: {str(e)}'}, 500

class PricingTogglePopularResource(Resource):
    def post(self, plan_id):
        """切換方案是否為熱門推薦"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT is_popular FROM pricing_plans WHERE id = %s", (plan_id,))
                row = cursor.fetchone()
                if not row:
                    return {'error': '查無此價目方案'}, 404
                new_state = 0 if row.get('is_popular') else 1
                cursor.execute("UPDATE pricing_plans SET is_popular = %s WHERE id = %s", (new_state, plan_id))
                connection.commit()
                return {
                    'success': True,
                    'is_popular': bool(new_state),
                    'message': '已標記為熱門推薦' if new_state else '已取消熱門推薦'
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'切換熱門推薦狀態失敗: {str(e)}'}, 500

api.add_resource(PricingListResource, '/api/pricing')
api.add_resource(PricingItemResource, '/api/pricing/<int:plan_id>')
api.add_resource(PricingNoticeResource, '/api/pricing/notice')
api.add_resource(PricingBankAccountResource, '/api/pricing/bank-account')
api.add_resource(PricingToggleActiveResource, '/api/pricing/<int:plan_id>/toggle-active')
api.add_resource(PricingTogglePopularResource, '/api/pricing/<int:plan_id>/toggle-popular')


class StudentBankInfo(Resource):
    def put(self, student_id):
        """會員設定 / 修改約定轉帳銀行後 5 碼"""
        try:
            data = request.get_json() or {}
            bank_last_5 = str(data.get('bank_last_5') or '').strip()
            if bank_last_5 and not bank_last_5.isalnum():
                return {'error': '銀行後 5 碼格式不正確，請輸入英數字'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("UPDATE students SET bank_last_5 = %s WHERE id = %s", (bank_last_5 or None, student_id))
                connection.commit()
                cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                student = cursor.fetchone()
                return {
                    'success': True,
                    'message': '銀行後 5 碼設定已成功儲存！',
                    'bank_last_5': bank_last_5 or None,
                    'student': format_student_info(student)
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'設定失敗: {str(e)}'}, 500

class PricingOrderListResource(Resource):
    def get(self):
        """取得購課訂單列表 (支援依學員、狀態與關鍵字篩選)"""
        try:
            student_id = request.args.get('student_id')
            status = request.args.get('status')
            keyword = request.args.get('keyword')

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)

                ensure_pricing_database_tables(cursor)

                cursor.execute("SELECT COUNT(*) as pending_count FROM pricing_orders WHERE status = 'pending'")
                pending_row = cursor.fetchone()
                pending_count = pending_row['pending_count'] if pending_row else 0

                query = """
                SELECT o.*, u.name as confirmed_by_name, s.membership_expiry as student_membership_expiry, s.monthly_pass_expiry as student_monthly_pass_expiry
                FROM pricing_orders o
                LEFT JOIN admin_users u ON o.confirmed_by = u.id
                LEFT JOIN students s ON o.student_id = s.id
                WHERE 1=1
                """
                params = []

                if student_id:
                    query += " AND o.student_id = %s"
                    params.append(student_id)

                if status and status != 'all':
                    query += " AND o.status = %s"
                    params.append(status)

                if keyword:
                    query += " AND (o.order_no LIKE %s OR o.student_name LIKE %s OR o.student_phone LIKE %s OR o.bank_last_5 LIKE %s)"
                    like_kw = f"%{keyword.strip()}%"
                    params.extend([like_kw, like_kw, like_kw, like_kw])

                query += " ORDER BY o.created_at DESC"

                cursor.execute(query, tuple(params))
                orders = cursor.fetchall()

                for o in orders:
                    for field in ['created_at', 'updated_at', 'confirmed_at', 'student_membership_expiry', 'student_monthly_pass_expiry']:
                        if o.get(field):
                            o[field] = str(o[field])

                return {
                    'success': True,
                    'orders': orders,
                    'total': len(orders),
                    'pending_count': pending_count
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢購課訂單失敗: {str(e)}'}, 500

    def post(self):
        """學員送出買課訂單"""
        try:
            data = request.get_json() or {}
            student_id = data.get('student_id')
            plan_id = data.get('plan_id')
            bank_last_5 = str(data.get('bank_last_5') or '').strip()
            notes = str(data.get('notes') or '').strip()
            save_bank_info = bool(data.get('save_bank_info', True))

            if not student_id:
                return {'error': '請先登入學員帳號'}, 401
            if not plan_id:
                return {'error': '請選擇要購買的課程方案'}, 400
            if not bank_last_5:
                return {'error': '請填寫轉帳銀行後 5 碼'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)

                ensure_pricing_database_tables(cursor)

                cursor.execute("SELECT id, name, phone, bank_last_5, membership_expiry FROM students WHERE id = %s", (student_id,))
                student = cursor.fetchone()
                if not student:
                    return {'error': '找不到該學員帳號，請重新登入'}, 404

                cursor.execute("SELECT * FROM pricing_plans WHERE id = %s", (plan_id,))
                plan = cursor.fetchone()
                if not plan:
                    return {'error': '該課程方案不存在或已下架'}, 404

                requires_membership = 1 if plan.get('requires_membership') else 0
                if requires_membership:
                    today = date.today()
                    mem_exp = student.get('membership_expiry')
                    has_valid_membership = False
                    if mem_exp:
                        if isinstance(mem_exp, str):
                            try:
                                mem_exp = datetime.strptime(mem_exp.split('T')[0], '%Y-%m-%d').date()
                            except Exception:
                                mem_exp = None
                        if mem_exp and mem_exp >= today:
                            has_valid_membership = True
                    if not has_valid_membership:
                        return {'error': '此方案僅限持有效【會員年費】資格之學員購買。您的會員年費尚未開通或已過期，請先購買或續約「會員年費」！'}, 400

                plan_type = plan.get('plan_type') or 'classes'
                classes_count = int(plan.get('classes_count') if plan.get('classes_count') is not None else 0)
                validity_days = int(plan.get('validity_days') or 0)

                now = datetime.now()
                order_no = f"PO{now.strftime('%Y%m%d%H%M%S')}{int(student_id) % 1000:03d}"

                cursor.execute("""
                    INSERT INTO pricing_orders 
                    (order_no, student_id, student_name, student_phone, plan_id, plan_title, price, plan_type, requires_membership, classes_count, validity_days, bank_last_5, status, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s)
                """, (
                    order_no, student['id'], student['name'], student.get('phone') or '',
                    plan['id'], plan['title'], plan['price'], plan_type, requires_membership, classes_count, validity_days, bank_last_5, notes or None
                ))
                order_id = cursor.lastrowid

                if save_bank_info and student.get('bank_last_5') != bank_last_5:
                    cursor.execute("UPDATE students SET bank_last_5 = %s WHERE id = %s", (bank_last_5, student_id))

                connection.commit()

                return {
                    'success': True,
                    'order_id': order_id,
                    'order_no': order_no,
                    'message': '購課訂單已成功送出！待工作人員核對匯款後，系統將自動為您入帳並增加堂數。'
                }, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'購課下單失敗: {str(e)}'}, 500

class PricingOrderItemResource(Resource):
    def get(self, order_id):
        """取得單一購課訂單"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM pricing_orders WHERE id = %s", (order_id,))
                order = cursor.fetchone()
                if not order:
                    return {'error': '查無此訂單'}, 404
                for field in ['created_at', 'updated_at', 'confirmed_at']:
                    if order.get(field):
                        order[field] = str(order[field])
                return {'success': True, 'order': order}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢訂單失敗: {str(e)}'}, 500

    def delete(self, order_id):
        """刪除購課訂單"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM pricing_orders WHERE id = %s", (order_id,))
                connection.commit()
                return {'success': True, 'message': '訂單已成功刪除'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'刪除訂單失敗: {str(e)}'}, 500

class PricingOrderConfirmResource(Resource):
    def post(self, order_id):
        """後台管理員確認入帳 (自動為學員增加相應堂數)"""
        try:
            data = request.get_json() or {}
            admin_notes = str(data.get('admin_notes') or '').strip()
            admin_user_id = data.get('admin_user_id')

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)

                cursor.execute("SELECT * FROM pricing_orders WHERE id = %s FOR UPDATE", (order_id,))
                order = cursor.fetchone()
                if not order:
                    return {'error': '查無此購課訂單'}, 404
                
                if order['status'] == 'confirmed':
                    return {'error': '此訂單先前已確認入帳，不可重複操作'}, 400
                
                student_id = order['student_id']
                cursor.execute("SELECT id, name, remaining_classes, membership_expiry, monthly_pass_expiry FROM students WHERE id = %s FOR UPDATE", (student_id,))
                student = cursor.fetchone()
                if not student:
                    return {'error': '查無對應學員資料'}, 404

                plan_type = order.get('plan_type') or 'classes'
                
                # 堂數處理
                classes_to_add = data.get('classes_to_add')
                if classes_to_add is None:
                    classes_to_add = int(order.get('classes_count', 0) or 0)
                else:
                    classes_to_add = int(classes_to_add)

                # 月票效期天數處理
                validity_days_to_add = data.get('validity_days')
                if validity_days_to_add is None:
                    validity_days_to_add = int(order.get('validity_days', 0) or 0)
                else:
                    validity_days_to_add = int(validity_days_to_add)

                if plan_type == 'monthly_pass' and validity_days_to_add <= 0:
                    validity_days_to_add = 30
                elif plan_type == 'membership_fee' and validity_days_to_add <= 0:
                    validity_days_to_add = 365

                update_msg_parts = []
                today = date.today()

                # 1. 增加堂數 (若大於 0)
                if classes_to_add > 0:
                    cursor.execute("""
                        UPDATE students 
                        SET remaining_classes = COALESCE(remaining_classes, 0) + %s
                        WHERE id = %s
                    """, (classes_to_add, student_id))
                    update_msg_parts.append(f"增加 {classes_to_add} 堂課")

                # 2. 展延會員到期日 (若為月票或設定了有效天數)
                new_expiry_str = None
                if validity_days_to_add > 0:
                    # 月費與會員年費分開記錄
                    if plan_type == 'monthly_pass':
                        current_expiry = student.get('monthly_pass_expiry')
                        expiry_col = 'monthly_pass_expiry'
                        expiry_label = '月費到期日'
                    elif plan_type == 'membership_fee':
                        current_expiry = student.get('membership_expiry')
                        expiry_col = 'membership_expiry'
                        expiry_label = '會員年費到期日'
                    else:
                        current_expiry = student.get('membership_expiry')
                        expiry_col = 'membership_expiry'
                        expiry_label = '會員到期日'
                    if current_expiry:
                        if isinstance(current_expiry, str):
                            try:
                                current_expiry = datetime.strptime(current_expiry.split('T')[0], '%Y-%m-%d').date()
                            except Exception:
                                current_expiry = None

                    if current_expiry and current_expiry >= today:
                        base_date = current_expiry
                    else:
                        base_date = today

                    new_expiry = base_date + timedelta(days=validity_days_to_add)
                    new_expiry_str = str(new_expiry)

                    cursor.execute("""
                        UPDATE students 
                        SET """ + expiry_col + """ = %s
                        WHERE id = %s
                    """, (new_expiry, student_id))
                    update_msg_parts.append(f"{expiry_label}展延至 {new_expiry_str} (+{validity_days_to_add}天)")

                cursor.execute("""
                    UPDATE pricing_orders 
                    SET status = 'confirmed',
                        classes_count = %s,
                        validity_days = %s,
                        confirmed_by = %s,
                        confirmed_at = NOW(),
                        admin_notes = %s
                    WHERE id = %s
                """, (classes_to_add, validity_days_to_add, admin_user_id, admin_notes or None, order_id))

                connection.commit()

                summary_str = "、".join(update_msg_parts) if update_msg_parts else "完成入帳"
                return {
                    'success': True,
                    'message': f"訂單 {order['order_no']} 已確認入帳！已成功為學員【{order['student_name']}】{summary_str}。",
                    'classes_added': classes_to_add,
                    'validity_days_added': validity_days_to_add,
                    'new_membership_expiry': new_expiry_str
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'確認訂單失敗: {str(e)}'}, 500

class PricingOrderRejectResource(Resource):
    def post(self, order_id):
        """後台管理員駁回購課訂單 (不增加堂數)"""
        try:
            data = request.get_json() or {}
            admin_notes = str(data.get('admin_notes') or '').strip()
            admin_user_id = data.get('admin_user_id')

            if not admin_notes:
                return {'error': '請填寫駁回原因'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM pricing_orders WHERE id = %s FOR UPDATE", (order_id,))
                order = cursor.fetchone()
                if not order:
                    return {'error': '查無此購課訂單'}, 404

                if order['status'] == 'confirmed':
                    return {'error': '此訂單已確認入帳，無法駁回'}, 400

                cursor.execute("""
                    UPDATE pricing_orders 
                    SET status = 'rejected',
                        confirmed_by = %s,
                        confirmed_at = NOW(),
                        admin_notes = %s
                    WHERE id = %s
                """, (admin_user_id, admin_notes, order_id))

                connection.commit()
                return {'success': True, 'message': f"訂單 {order['order_no']} 已駁回。"}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'駁回訂單失敗: {str(e)}'}, 500

api.add_resource(StudentBankInfo, '/api/student/<int:student_id>/bank-info')
api.add_resource(PricingOrderListResource, '/api/pricing/orders')
api.add_resource(PricingOrderItemResource, '/api/pricing/orders/<int:order_id>')
api.add_resource(PricingOrderConfirmResource, '/api/pricing/orders/<int:order_id>/confirm')
api.add_resource(PricingOrderRejectResource, '/api/pricing/orders/<int:order_id>/reject')

# ==========================================
# 活動花絮與相簿管理 API
# ==========================================

class GalleryImageUpload(Resource):
    @jwt_required(['admin', 'desk'])
    def post(self):
        """上傳活動花絮圖片 (支援單張或多張上傳，支援檔案或 base64)"""
        try:
            # 1. 支援多檔案上傳
            uploaded_files = request.files.getlist('files')
            if not uploaded_files:
                single_file = request.files.get('file') or request.files.get('image')
                if single_file:
                    uploaded_files = [single_file]

            image_urls = []
            if uploaded_files:
                for file in uploaded_files:
                    if not file or not file.filename:
                        continue
                    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
                    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                        ext = 'jpg'
                    safe_name = f"gallery_{int(time.time()*1000)}_{os.urandom(4).hex()}.{ext}"
                    file_path = os.path.join(GALLERY_FOLDER, safe_name)
                    file.save(file_path)
                    image_urls.append(f"/api/uploads/gallery/{safe_name}")

                if not image_urls:
                    return {'error': '未收到有效的圖片檔案'}, 400

                return {
                    'success': True,
                    'image_url': image_urls[0],
                    'image_urls': image_urls,
                    'count': len(image_urls),
                    'message': f'成功上傳 {len(image_urls)} 張圖片！'
                }, 200

            # 2. 支援 JSON base64 或 raw URL
            data = request.get_json() or {}
            raw_url = data.get('image_url')
            raw_base64 = data.get('image_base64') or data.get('base64')
            if raw_url:
                return {
                    'success': True,
                    'image_url': raw_url.strip(),
                    'image_urls': [raw_url.strip()],
                    'message': '圖片網址已加入！'
                }, 200
            elif raw_base64:
                import base64
                if ',' in raw_base64:
                    header, base64_data = raw_base64.split(',', 1)
                    if 'png' in header:
                        ext = 'png'
                    elif 'webp' in header:
                        ext = 'webp'
                    elif 'gif' in header:
                        ext = 'gif'
                    else:
                        ext = 'jpg'
                else:
                    base64_data = raw_base64
                    ext = 'jpg'
                img_bytes = base64.b64decode(base64_data)
                safe_name = f"gallery_{int(time.time()*1000)}_{os.urandom(4).hex()}.{ext}"
                file_path = os.path.join(GALLERY_FOLDER, safe_name)
                with open(file_path, 'wb') as f:
                    f.write(img_bytes)
                url = f"/api/uploads/gallery/{safe_name}"
                return {
                    'success': True,
                    'image_url': url,
                    'image_urls': [url],
                    'message': '圖片上傳成功！'
                }, 200
            else:
                return {'error': '未收到上傳檔案或圖片資料'}, 400
        except Exception as e:
            return {'error': f'圖片上傳失敗: {str(e)}'}, 500


class GalleryAlbumListResource(Resource):
    def get(self):
        """取得相簿清單 (支援 ?admin=1 取得全部，預設僅取得已發布)"""
        try:
            is_admin = request.args.get('admin') in ['1', 'true', 'True'] or request.args.get('all') in ['1', 'true', 'True']
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                if is_admin:
                    cursor.execute("SELECT * FROM gallery_albums ORDER BY sort_order ASC, event_date DESC, id DESC")
                else:
                    cursor.execute("SELECT * FROM gallery_albums WHERE is_published = 1 ORDER BY sort_order ASC, event_date DESC, id DESC")
                albums = cursor.fetchall()

                # 批次查詢所有相簿之相片
                if albums:
                    album_ids = [a['id'] for a in albums]
                    format_strings = ','.join(['%s'] * len(album_ids))
                    cursor.execute(f"""
                        SELECT id, album_id, image_url, description, sort_order, created_at
                        FROM gallery_photos 
                        WHERE album_id IN ({format_strings})
                        ORDER BY sort_order ASC, id ASC
                    """, tuple(album_ids))
                    all_photos = cursor.fetchall()
                    photos_by_album = {}
                    for p in all_photos:
                        if p['album_id'] not in photos_by_album:
                            photos_by_album[p['album_id']] = []
                        photos_by_album[p['album_id']].append({
                            'id': p['id'],
                            'album_id': p['album_id'],
                            'image_url': p['image_url'],
                            'src': p['image_url'],
                            'description': p['description'] or '',
                            'sort_order': p['sort_order']
                        })
                else:
                    photos_by_album = {}

                formatted_albums = []
                for a in albums:
                    p_list = photos_by_album.get(a['id'], [])
                    cover = a.get('cover_image')
                    if not cover and p_list:
                        cover = p_list[0]['image_url']
                    formatted_albums.append({
                        'id': a['id'],
                        'title': a.get('title', ''),
                        'description': a.get('description') or '',
                        'cover_image': cover or '',
                        'coverImage': cover or '',
                        'event_date': str(a['event_date']) if a.get('event_date') else None,
                        'sort_order': int(a.get('sort_order') or 0),
                        'is_published': bool(a.get('is_published')),
                        'photo_count': len(p_list),
                        'photos': p_list,
                        'images': p_list,
                        'created_at': str(a['created_at']) if a.get('created_at') else None,
                        'updated_at': str(a['updated_at']) if a.get('updated_at') else None
                    })

                return {'success': True, 'albums': formatted_albums, 'total': len(formatted_albums)}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢活動花絮相簿失敗: {str(e)}'}, 500

    def post(self):
        """新增相簿"""
        try:
            data = request.get_json() or {}
            title = (data.get('title') or '').strip()
            if not title:
                return {'error': '請輸入相簿標題'}, 400

            description = (data.get('description') or '').strip()
            cover_image = (data.get('cover_image') or data.get('coverImage') or '').strip()
            event_date = data.get('event_date') or None
            sort_order = int(data.get('sort_order', 0) or 0)
            is_published = 1 if data.get('is_published', True) else 0
            photos = data.get('photos') or []

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("""
                    INSERT INTO gallery_albums (title, description, cover_image, event_date, sort_order, is_published)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (title, description, cover_image or None, event_date, sort_order, is_published))
                album_id = cursor.lastrowid

                # 若有照片資料，批量寫入
                if photos and isinstance(photos, list):
                    for idx, p in enumerate(photos):
                        img_url = p.get('image_url') or p.get('src') if isinstance(p, dict) else str(p)
                        if not img_url:
                            continue
                        desc = p.get('description', '') if isinstance(p, dict) else ''
                        p_order = p.get('sort_order', idx + 1) if isinstance(p, dict) else (idx + 1)
                        cursor.execute("""
                            INSERT INTO gallery_photos (album_id, image_url, description, sort_order)
                            VALUES (%s, %s, %s, %s)
                        """, (album_id, img_url, desc, p_order))
                    if not cover_image and photos:
                        first_url = photos[0].get('image_url') or photos[0].get('src') if isinstance(photos[0], dict) else str(photos[0])
                        if first_url:
                            cursor.execute("UPDATE gallery_albums SET cover_image = %s WHERE id = %s", (first_url, album_id))

                connection.commit()
                return {'success': True, 'id': album_id, 'message': '相簿建立成功！'}, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'新增相簿失敗: {str(e)}'}, 500


class GalleryAlbumDetailResource(Resource):
    def get(self, album_id):
        """取得單一相簿詳情及其所有相片"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM gallery_albums WHERE id = %s", (album_id,))
                album = cursor.fetchone()
                if not album:
                    return {'error': '查無此相簿'}, 404

                cursor.execute("""
                    SELECT id, album_id, image_url, description, sort_order, created_at
                    FROM gallery_photos 
                    WHERE album_id = %s 
                    ORDER BY sort_order ASC, id ASC
                """, (album_id,))
                photos = cursor.fetchall()
                p_list = []
                for p in photos:
                    p_list.append({
                        'id': p['id'],
                        'album_id': p['album_id'],
                        'image_url': p['image_url'],
                        'src': p['image_url'],
                        'description': p['description'] or '',
                        'sort_order': p['sort_order']
                    })

                cover = album.get('cover_image')
                if not cover and p_list:
                    cover = p_list[0]['image_url']

                result = {
                    'id': album['id'],
                    'title': album.get('title', ''),
                    'description': album.get('description') or '',
                    'cover_image': cover or '',
                    'coverImage': cover or '',
                    'event_date': str(album['event_date']) if album.get('event_date') else None,
                    'sort_order': int(album.get('sort_order') or 0),
                    'is_published': bool(album.get('is_published')),
                    'photo_count': len(p_list),
                    'photos': p_list,
                    'images': p_list,
                    'created_at': str(album['created_at']) if album.get('created_at') else None,
                    'updated_at': str(album['updated_at']) if album.get('updated_at') else None
                }
                return {'success': True, 'album': result}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'取得相簿詳情失敗: {str(e)}'}, 500

    def put(self, album_id):
        """更新相簿資訊"""
        try:
            data = request.get_json() or {}
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                update_fields = []
                values = []
                if 'title' in data:
                    title = str(data['title']).strip()
                    if not title:
                        return {'error': '相簿標題不可為空'}, 400
                    update_fields.append("title = %s")
                    values.append(title)
                if 'description' in data:
                    update_fields.append("description = %s")
                    values.append(data['description'])
                if 'cover_image' in data or 'coverImage' in data:
                    cover = data.get('cover_image') if 'cover_image' in data else data.get('coverImage')
                    update_fields.append("cover_image = %s")
                    values.append(cover or None)
                if 'event_date' in data:
                    update_fields.append("event_date = %s")
                    values.append(data['event_date'] or None)
                if 'sort_order' in data:
                    update_fields.append("sort_order = %s")
                    values.append(int(data['sort_order'] or 0))
                if 'is_published' in data:
                    update_fields.append("is_published = %s")
                    values.append(1 if data['is_published'] else 0)

                if not update_fields:
                    return {'error': '無可更新的欄位'}, 400

                values.append(album_id)
                cursor.execute(f"UPDATE gallery_albums SET {', '.join(update_fields)} WHERE id = %s", tuple(values))
                connection.commit()
                return {'success': True, 'message': '相簿資料更新成功！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新相簿失敗: {str(e)}'}, 500

    def delete(self, album_id):
        """刪除相簿 (級聯刪除照片)"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM gallery_albums WHERE id = %s", (album_id,))
                connection.commit()
                return {'success': True, 'message': '相簿已成功刪除！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'刪除相簿失敗: {str(e)}'}, 500


class GalleryAlbumPhotosResource(Resource):
    def post(self, album_id):
        """為特定相簿批量新增照片"""
        try:
            data = request.get_json() or {}
            photos_to_add = []
            if 'photos' in data and isinstance(data['photos'], list):
                photos_to_add = data['photos']
            elif 'image_url' in data:
                photos_to_add = [{
                    'image_url': data['image_url'],
                    'description': data.get('description', ''),
                    'sort_order': data.get('sort_order', 0)
                }]
            elif 'image_urls' in data and isinstance(data['image_urls'], list):
                for url in data['image_urls']:
                    photos_to_add.append({'image_url': url, 'description': '', 'sort_order': 0})

            if not photos_to_add:
                return {'error': '請提供要新增的照片資料'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT id, cover_image FROM gallery_albums WHERE id = %s", (album_id,))
                album = cursor.fetchone()
                if not album:
                    return {'error': '查無此相簿'}, 404

                # 取得目前相簿最大 sort_order
                cursor.execute("SELECT COALESCE(MAX(sort_order), 0) as max_order FROM gallery_photos WHERE album_id = %s", (album_id,))
                max_order = cursor.fetchone()['max_order'] or 0

                inserted_photos = []
                for idx, p in enumerate(photos_to_add):
                    img_url = p.get('image_url') or p.get('src') if isinstance(p, dict) else str(p)
                    if not img_url:
                        continue
                    desc = p.get('description', '') if isinstance(p, dict) else ''
                    p_order = p.get('sort_order') if (isinstance(p, dict) and p.get('sort_order') is not None) else (max_order + idx + 1)
                    cursor.execute("""
                        INSERT INTO gallery_photos (album_id, image_url, description, sort_order)
                        VALUES (%s, %s, %s, %s)
                    """, (album_id, img_url, desc, p_order))
                    new_id = cursor.lastrowid
                    inserted_photos.append({
                        'id': new_id,
                        'album_id': album_id,
                        'image_url': img_url,
                        'src': img_url,
                        'description': desc,
                        'sort_order': p_order
                    })

                # 若相簿尚未設定封面照，自動將第一張上傳的照片設為封面
                if not album.get('cover_image') and inserted_photos:
                    cursor.execute("UPDATE gallery_albums SET cover_image = %s WHERE id = %s", (inserted_photos[0]['image_url'], album_id))

                connection.commit()
                return {
                    'success': True,
                    'message': f'成功新增 {len(inserted_photos)} 張相片！',
                    'count': len(inserted_photos),
                    'photos': inserted_photos
                }, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'新增照片失敗: {str(e)}'}, 500


class GalleryPhotoDetailResource(Resource):
    def put(self, photo_id):
        """更新單張照片資訊 (描述、排序)"""
        try:
            data = request.get_json() or {}
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                update_fields = []
                values = []
                if 'description' in data:
                    update_fields.append("description = %s")
                    values.append(data['description'])
                if 'sort_order' in data:
                    update_fields.append("sort_order = %s")
                    values.append(int(data['sort_order'] or 0))

                if not update_fields:
                    return {'error': '無可更新欄位'}, 400

                values.append(photo_id)
                cursor.execute(f"UPDATE gallery_photos SET {', '.join(update_fields)} WHERE id = %s", tuple(values))
                connection.commit()
                return {'success': True, 'message': '照片資料更新成功！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新照片失敗: {str(e)}'}, 500

    def delete(self, photo_id):
        """刪除單張照片"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM gallery_photos WHERE id = %s", (photo_id,))
                photo = cursor.fetchone()
                if not photo:
                    return {'error': '查無此照片'}, 404

                album_id = photo['album_id']
                photo_url = photo['image_url']

                cursor.execute("DELETE FROM gallery_photos WHERE id = %s", (photo_id,))

                # 檢查若此照片為相簿封面，更換為相簿內其他照片或 NULL
                cursor.execute("SELECT cover_image FROM gallery_albums WHERE id = %s", (album_id,))
                alb = cursor.fetchone()
                if alb and alb.get('cover_image') == photo_url:
                    cursor.execute("SELECT image_url FROM gallery_photos WHERE album_id = %s ORDER BY sort_order ASC, id ASC LIMIT 1", (album_id,))
                    next_photo = cursor.fetchone()
                    new_cover = next_photo['image_url'] if next_photo else None
                    cursor.execute("UPDATE gallery_albums SET cover_image = %s WHERE id = %s", (new_cover, album_id))

                connection.commit()
                return {'success': True, 'message': '照片已成功刪除！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'刪除照片失敗: {str(e)}'}, 500


class GalleryAlbumCoverResource(Resource):
    def put(self, album_id):
        """設定相簿封面照片"""
        try:
            data = request.get_json() or {}
            cover_image = data.get('cover_image') or data.get('coverImage') or data.get('image_url')
            photo_id = data.get('photo_id')

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                if not cover_image and photo_id:
                    cursor.execute("SELECT image_url FROM gallery_photos WHERE id = %s", (photo_id,))
                    p = cursor.fetchone()
                    if p:
                        cover_image = p['image_url']

                if not cover_image:
                    return {'error': '請提供封面圖片網址或照片 ID'}, 400

                cursor.execute("UPDATE gallery_albums SET cover_image = %s WHERE id = %s", (cover_image, album_id))
                connection.commit()
                return {'success': True, 'cover_image': cover_image, 'message': '封面照片已更新！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'設定封面照片失敗: {str(e)}'}, 500

api.add_resource(GalleryImageUpload, '/api/upload/gallery-image', '/api/gallery/upload')
api.add_resource(GalleryAlbumListResource, '/api/gallery/albums')
api.add_resource(GalleryAlbumDetailResource, '/api/gallery/albums/<int:album_id>')
api.add_resource(GalleryAlbumPhotosResource, '/api/gallery/albums/<int:album_id>/photos')
api.add_resource(GalleryPhotoDetailResource, '/api/gallery/photos/<int:photo_id>')
api.add_resource(GalleryAlbumCoverResource, '/api/gallery/albums/<int:album_id>/cover')

class BannerImageUploadResource(Resource):
    @jwt_required(['admin', 'desk'])
    def post(self):
        """上傳首頁橫幅圖片"""
        try:
            file = request.files.get('file') or request.files.get('image')
            image_url = None
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
                if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    return {'error': '僅支援 JPG, PNG, GIF, WEBP 圖片格式'}, 400
                safe_name = f"banner_{int(time.time() * 1000)}_{os.urandom(4).hex()}.{ext}"
                file_path = os.path.join(BANNERS_FOLDER, safe_name)
                file.save(file_path)
                image_url = f"/api/uploads/banners/{safe_name}"
            else:
                data = request.get_json() or {}
                raw_url = data.get('image_url') or data.get('url')
                raw_base64 = data.get('image_base64') or data.get('base64')
                if raw_url:
                    image_url = raw_url.strip()
                elif raw_base64:
                    import base64
                    if ',' in raw_base64:
                        header, base64_data = raw_base64.split(',', 1)
                        if 'png' in header:
                            ext = 'png'
                        elif 'webp' in header:
                            ext = 'webp'
                        elif 'gif' in header:
                            ext = 'gif'
                        else:
                            ext = 'jpg'
                    else:
                        base64_data = raw_base64
                        ext = 'jpg'
                    img_bytes = base64.b64decode(base64_data)
                    safe_name = f"banner_{int(time.time() * 1000)}_{os.urandom(4).hex()}.{ext}"
                    file_path = os.path.join(BANNERS_FOLDER, safe_name)
                    with open(file_path, 'wb') as f:
                        f.write(img_bytes)
                    image_url = f"/api/uploads/banners/{safe_name}"
                else:
                    return {'error': '未收到上傳檔案或圖片資料'}, 400

            return {
                'success': True,
                'image_url': image_url,
                'message': '橫幅圖片上傳成功！'
            }, 200
        except Exception as e:
            return {'error': f'橫幅圖片上傳失敗: {str(e)}'}, 500


class BannerListResource(Resource):
    def get(self):
        """取得首頁橫幅清單 (支援 ?admin=1 或 ?all=1 取得全部，包含已停用)"""
        try:
            is_admin = request.args.get('admin') in ['1', 'true', 'True'] or request.args.get('all') in ['1', 'true', 'True']
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                if is_admin:
                    cursor.execute("SELECT * FROM banners ORDER BY sort_order ASC, id ASC")
                else:
                    cursor.execute("SELECT * FROM banners WHERE is_active = 1 ORDER BY sort_order ASC, id ASC")
                rows = cursor.fetchall()

                banners = []
                for r in rows:
                    banners.append({
                        'id': r['id'],
                        'title': r.get('title') or '',
                        'subtitle': r.get('subtitle') or '',
                        'badge_text': r.get('badge_text') or '',
                        'badge_color': r.get('badge_color') or 'warning',
                        'image_url': r.get('image_url') or '',
                        'primary_button_text': r.get('primary_button_text') or '',
                        'primary_button_link': r.get('primary_button_link') or '',
                        'primary_button_style': r.get('primary_button_style') or 'primary',
                        'secondary_button_text': r.get('secondary_button_text') or '',
                        'secondary_button_link': r.get('secondary_button_link') or '',
                        'secondary_button_style': r.get('secondary_button_style') or 'outline-light',
                        'interval_ms': int(r.get('interval_ms') or 5000),
                        'sort_order': int(r.get('sort_order') or 0),
                        'is_active': bool(r.get('is_active')),
                        'created_at': str(r['created_at']) if r.get('created_at') else None,
                        'updated_at': str(r['updated_at']) if r.get('updated_at') else None
                    })

                return {'success': True, 'banners': banners, 'total': len(banners)}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢首頁橫幅失敗: {str(e)}'}, 500

    def post(self):
        """新增首頁橫幅"""
        try:
            data = request.get_json() or {}
            title = (data.get('title') or '').strip()
            image_url = (data.get('image_url') or '').strip()

            if not title:
                return {'error': '請輸入橫幅主標題'}, 400
            if not image_url:
                return {'error': '請提供或上傳背景圖片'}, 400

            subtitle = (data.get('subtitle') or '').strip()
            badge_text = (data.get('badge_text') or '').strip()
            badge_color = (data.get('badge_color') or 'warning').strip()
            primary_button_text = (data.get('primary_button_text') or '').strip()
            primary_button_link = (data.get('primary_button_link') or '').strip()
            primary_button_style = (data.get('primary_button_style') or 'primary').strip()
            secondary_button_text = (data.get('secondary_button_text') or '').strip()
            secondary_button_link = (data.get('secondary_button_link') or '').strip()
            secondary_button_style = (data.get('secondary_button_style') or 'outline-light').strip()
            interval_ms = int(data.get('interval_ms') or 5000)
            sort_order = int(data.get('sort_order') or 0)
            is_active = 1 if data.get('is_active', True) else 0

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("""
                    INSERT INTO banners (
                        title, subtitle, badge_text, badge_color, image_url,
                        primary_button_text, primary_button_link, primary_button_style,
                        secondary_button_text, secondary_button_link, secondary_button_style,
                        interval_ms, sort_order, is_active
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    title, subtitle or None, badge_text or None, badge_color, image_url,
                    primary_button_text or None, primary_button_link or None, primary_button_style,
                    secondary_button_text or None, secondary_button_link or None, secondary_button_style,
                    interval_ms, sort_order, is_active
                ))
                connection.commit()
                banner_id = cursor.lastrowid
                return {'success': True, 'id': banner_id, 'message': '首頁橫幅新增成功！'}, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'新增橫幅失敗: {str(e)}'}, 500


class BannerDetailResource(Resource):
    def get(self, banner_id):
        """取得單一橫幅資料"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM banners WHERE id = %s", (banner_id,))
                r = cursor.fetchone()
                if not r:
                    return {'error': '找不到此橫幅'}, 404

                banner = {
                    'id': r['id'],
                    'title': r.get('title') or '',
                    'subtitle': r.get('subtitle') or '',
                    'badge_text': r.get('badge_text') or '',
                    'badge_color': r.get('badge_color') or 'warning',
                    'image_url': r.get('image_url') or '',
                    'primary_button_text': r.get('primary_button_text') or '',
                    'primary_button_link': r.get('primary_button_link') or '',
                    'primary_button_style': r.get('primary_button_style') or 'primary',
                    'secondary_button_text': r.get('secondary_button_text') or '',
                    'secondary_button_link': r.get('secondary_button_link') or '',
                    'secondary_button_style': r.get('secondary_button_style') or 'outline-light',
                    'interval_ms': int(r.get('interval_ms') or 5000),
                    'sort_order': int(r.get('sort_order') or 0),
                    'is_active': bool(r.get('is_active')),
                    'created_at': str(r['created_at']) if r.get('created_at') else None,
                    'updated_at': str(r['updated_at']) if r.get('updated_at') else None
                }
                return {'success': True, 'banner': banner}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢橫幅失敗: {str(e)}'}, 500

    def put(self, banner_id):
        """修改橫幅資料"""
        try:
            data = request.get_json() or {}
            title = (data.get('title') or '').strip()
            image_url = (data.get('image_url') or '').strip()

            if not title:
                return {'error': '請輸入橫幅主標題'}, 400
            if not image_url:
                return {'error': '請提供背景圖片'}, 400

            subtitle = (data.get('subtitle') or '').strip()
            badge_text = (data.get('badge_text') or '').strip()
            badge_color = (data.get('badge_color') or 'warning').strip()
            primary_button_text = (data.get('primary_button_text') or '').strip()
            primary_button_link = (data.get('primary_button_link') or '').strip()
            primary_button_style = (data.get('primary_button_style') or 'primary').strip()
            secondary_button_text = (data.get('secondary_button_text') or '').strip()
            secondary_button_link = (data.get('secondary_button_link') or '').strip()
            secondary_button_style = (data.get('secondary_button_style') or 'outline-light').strip()
            interval_ms = int(data.get('interval_ms') or 5000)
            sort_order = int(data.get('sort_order') or 0)
            is_active = 1 if data.get('is_active', True) else 0

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("""
                    UPDATE banners SET
                        title = %s,
                        subtitle = %s,
                        badge_text = %s,
                        badge_color = %s,
                        image_url = %s,
                        primary_button_text = %s,
                        primary_button_link = %s,
                        primary_button_style = %s,
                        secondary_button_text = %s,
                        secondary_button_link = %s,
                        secondary_button_style = %s,
                        interval_ms = %s,
                        sort_order = %s,
                        is_active = %s
                    WHERE id = %s
                """, (
                    title, subtitle or None, badge_text or None, badge_color, image_url,
                    primary_button_text or None, primary_button_link or None, primary_button_style,
                    secondary_button_text or None, secondary_button_link or None, secondary_button_style,
                    interval_ms, sort_order, is_active,
                    banner_id
                ))
                connection.commit()
                return {'success': True, 'message': '橫幅已更新！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新橫幅失敗: {str(e)}'}, 500

    def delete(self, banner_id):
        """刪除橫幅"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("DELETE FROM banners WHERE id = %s", (banner_id,))
                connection.commit()
                return {'success': True, 'message': '橫幅已成功刪除！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'刪除橫幅失敗: {str(e)}'}, 500


class BannerToggleActiveResource(Resource):
    def post(self, banner_id):
        """切換橫幅啟用/停用狀態"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT is_active FROM banners WHERE id = %s", (banner_id,))
                row = cursor.fetchone()
                if not row:
                    return {'error': '查無此橫幅'}, 404
                new_state = 0 if row['is_active'] else 1
                cursor.execute("UPDATE banners SET is_active = %s WHERE id = %s", (new_state, banner_id))
                connection.commit()
                return {
                    'success': True,
                    'is_active': bool(new_state),
                    'message': f"橫幅已{'啟用發布' if new_state else '下架停用'}！"
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'切換橫幅狀態失敗: {str(e)}'}, 500

api.add_resource(BannerImageUploadResource, '/api/upload/banner-image', '/api/banners/upload')
api.add_resource(BannerListResource, '/api/banners')
api.add_resource(BannerDetailResource, '/api/banners/<int:banner_id>')
api.add_resource(BannerToggleActiveResource, '/api/banners/<int:banner_id>/toggle')

class PageBannerListResource(Resource):
    def get(self):
        """取得所有子頁面頂部橫幅設定"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM page_banners ORDER BY page_key ASC")
                rows = cursor.fetchall()

                banners_map = {}
                banners_list = []
                for r in rows:
                    item = {
                        'page_key': r['page_key'],
                        'page_name': r.get('page_name') or r['page_key'],
                        'title': r.get('title') or '',
                        'subtitle': r.get('subtitle') or '',
                        'image_url': r.get('image_url') or '',
                        'updated_at': str(r['updated_at']) if r.get('updated_at') else None
                    }
                    banners_map[r['page_key']] = item
                    banners_list.append(item)

                return {'success': True, 'banners': banners_list, 'banners_map': banners_map, 'total': len(banners_list)}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢各頁橫幅失敗: {str(e)}'}, 500


class PageBannerDetailResource(Resource):
    def get(self, page_key):
        """取得單一子頁面橫幅設定"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM page_banners WHERE page_key = %s", (page_key,))
                r = cursor.fetchone()
                if not r:
                    return {'error': f'找不到頁面 {page_key} 的橫幅設定'}, 404

                banner = {
                    'page_key': r['page_key'],
                    'page_name': r.get('page_name') or r['page_key'],
                    'title': r.get('title') or '',
                    'subtitle': r.get('subtitle') or '',
                    'image_url': r.get('image_url') or '',
                    'updated_at': str(r['updated_at']) if r.get('updated_at') else None
                }
                return {'success': True, 'banner': banner}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢頁面橫幅失敗: {str(e)}'}, 500

    def put(self, page_key):
        """更新單一子頁面橫幅設定 (upsert)"""
        try:
            data = request.get_json() or {}
            title = (data.get('title') or '').strip()
            image_url = (data.get('image_url') or '').strip()
            subtitle = (data.get('subtitle') or '').strip()
            page_name = (data.get('page_name') or page_key).strip()

            if not title:
                return {'error': '請輸入橫幅標題'}, 400
            if not image_url:
                return {'error': '請提供背景圖片網址'}, 400

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("""
                    INSERT INTO page_banners (page_key, page_name, title, subtitle, image_url)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        page_name = VALUES(page_name),
                        title = VALUES(title),
                        subtitle = VALUES(subtitle),
                        image_url = VALUES(image_url)
                """, (page_key, page_name, title, subtitle or None, image_url))
                connection.commit()
                return {'success': True, 'message': '頁面橫幅已更新！'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新頁面橫幅失敗: {str(e)}'}, 500

api.add_resource(PageBannerListResource, '/api/page-banners')
api.add_resource(PageBannerDetailResource, '/api/page-banners/<string:page_key>')

class LogoSettingsResource(Resource):
    def get(self):
        """取得導航列 LOGO 與網站名稱、開場動畫圖設定 (公開 API)"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT setting_key, setting_value FROM system_settings 
                    WHERE setting_key IN ('navbar_logo_type', 'navbar_logo_text', 'navbar_logo_image', 'splash_logo_image')
                """)
                rows = cursor.fetchall()
                settings = {r['setting_key']: r['setting_value'] for r in rows}
                return {
                    'success': True,
                    'logo_type': settings.get('navbar_logo_type', 'text') or 'text',
                    'logo_text': settings.get('navbar_logo_text', 'Dance Studio') or 'Dance Studio',
                    'logo_image': settings.get('navbar_logo_image', '') or '',
                    'splash_image': settings.get('splash_logo_image', '') or ''
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢 LOGO 設定失敗: {str(e)}'}, 500

    @jwt_required(['admin', 'desk'])
    def put(self):
        """更新導航列 LOGO 與網站名稱、開場動畫圖設定 (需管理員或櫃檯權限)"""
        try:
            data = request.get_json() or {}
            logo_type = 'image' if str(data.get('logo_type')).lower() == 'image' else 'text'
            logo_text = (data.get('logo_text') or '').strip() or 'Dance Studio'
            logo_image = (data.get('logo_image') or '').strip()
            splash_image = (data.get('splash_image') or '').strip()

            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor(buffered=True)
                cursor.execute("""
                    INSERT INTO system_settings (setting_key, setting_value, description)
                    VALUES 
                        ('navbar_logo_type', %s, '主導航列LOGO類型 (text:文字名稱, image:圖片LOGO)'),
                        ('navbar_logo_text', %s, '主導航列文字名稱'),
                        ('navbar_logo_image', %s, '主導航列LOGO圖片網址'),
                        ('splash_logo_image', %s, '網站開場進場動畫圖片網址')
                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                """, (logo_type, logo_text, logo_image, splash_image))
                connection.commit()
                return {
                    'success': True,
                    'message': '主導航列 LOGO 與開場圖設定已更新！',
                    'logo_type': logo_type,
                    'logo_text': logo_text,
                    'logo_image': logo_image,
                    'splash_image': splash_image
                }, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'更新 LOGO 設定失敗: {str(e)}'}, 500

class LogoImageUploadResource(BannerImageUploadResource):
    """主導航列 LOGO 與開場動畫圖片上傳"""
    pass

api.add_resource(LogoSettingsResource, '/api/site-settings/logo')
api.add_resource(LogoImageUploadResource, '/api/upload/logo-image', '/api/upload/splash-image')

# 確保在 Gunicorn / 生產環境啟動時自動初始化資料庫表格
try:
    init_database_tables()
except Exception as e:
    print(f"資料庫初始化警示: {e}")

if __name__ == '__main__':
    # 初始化資料庫表格
    init_database_tables()
    flask_debug = os.getenv('FLASK_DEBUG', 'false').lower() in ('true', '1', 't')
    app.run(debug=flask_debug, host='0.0.0.0', port=8001)