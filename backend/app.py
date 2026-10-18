from flask import Flask, request, jsonify, send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime, date, timedelta
import os
import time
import math

app = Flask(__name__)
CORS(app)  # 允許跨域請求
api = Api(app)

# 上傳檔案存儲目錄
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
AVATARS_FOLDER = os.path.join(UPLOAD_FOLDER, 'avatars')
os.makedirs(AVATARS_FOLDER, exist_ok=True)

@app.route('/api/uploads/<path:filename>')
def serve_uploaded_file(filename):
    """提供已上傳靜態圖片檔案"""
    return send_from_directory(UPLOAD_FOLDER, filename)

# 資料庫連接配置
DB_CONFIG = {
    'host': 'db',  # Docker Compose 中的服務名稱
    'port': 3306,
    'user': 'user',
    'password': 'userpass',
    'database': 'testdb',
    'charset': 'utf8mb4'
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

def init_database_tables():
    """初始化所有資料庫表格，包含重試機制"""
    print("正在初始化資料庫表格...")
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
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
                membership_expiry DATE COMMENT '會員到期日',
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
            cursor.execute(system_settings_table)

            # 插入預設管理員、櫃檯、老師帳號
            seed_admin_users = """
            INSERT IGNORE INTO admin_users (id, username, password, name, role, phone, teacher_id) VALUES
            (1, 'admin', 'admin123', '系統管理員', 'admin', '0911000111', NULL),
            (2, 'counter', 'desk123', '櫃檯客服', 'desk', '0922000222', NULL),
            (3, 'teacher', 'teacher123', '張美麗老師', 'teacher', '0933000333', 1)
            """
            cursor.execute(seed_admin_users)

            # 插入預設系統設定
            seed_system_settings = """
            INSERT IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
            ('attendance_ip_restriction_enabled', '0', '打卡IP限制開關(0=關閉, 1=開啟)'),
            ('attendance_allowed_ips', '', '允許打卡的IP白名單(逗號或換行分隔)')
            """
            cursor.execute(seed_system_settings)
            
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
                student_query = "SELECT id, name, remaining_classes FROM students WHERE name = %s"
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
                           c.level, s.name as dance_type, t.name as teacher_name,
                           cs.schedule_date, cs.day_of_week, cs.start_time, cs.end_time, cs.allow_enrollment,
                           COUNT(e.id) as current_enrollment
                    FROM course_schedules cs 
                    JOIN courses c ON cs.course_id = c.id 
                    LEFT JOIN styles s ON c.style_id = s.id
                    LEFT JOIN teachers t ON c.teacher_id = t.id
                    LEFT JOIN enrollments e ON cs.id = e.schedule_id AND e.status = 'confirmed'
                    WHERE cs.id = %s
                    GROUP BY cs.id, c.id, c.name, c.price, c.max_students, c.level, s.name, t.name, 
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
                
                # 檢查剩餘堂數
                remaining_classes = student['remaining_classes'] or 0
                if remaining_classes < course_price:
                    return {'error': f'您的剩餘堂數不足（目前剩餘：{remaining_classes}堂，需要：{course_price}堂），請至櫃檯儲值後再進行報名'}, 400
                
                # 開始事務
                cursor.execute("START TRANSACTION")
                
                # 扣除對應堂數
                new_remaining_classes = remaining_classes - course_price
                update_query = "UPDATE students SET remaining_classes = %s WHERE id = %s"
                cursor.execute(update_query, (new_remaining_classes, student['id']))
                
                # 插入報名記錄
                insert_query = """
                INSERT INTO enrollments 
                (student_id, course_id, schedule_id, student_name, lesson_name, lesson_time, lesson_day, 
                 lesson_teacher, lesson_level, lesson_type, deducted_classes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    course_price  # 記錄扣除的堂數
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
                    'message': '報名成功！',
                    'enrollment': {
                        'id': enrollment_id,
                        'studentName': student_name,
                        'lesson': lesson,
                        'enrollmentTime': datetime.now().isoformat(),
                        'remainingClasses': new_remaining_classes,
                        'usedClasses': course_price
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
    for field in ['created_at', 'updated_at']:
        if res.get(field) and isinstance(res[field], datetime):
            res[field] = res[field].isoformat()
    for field in ['membership_expiry', 'date_of_birth']:
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
                cursor = connection.cursor()
                
                insert_query = """
                INSERT INTO students 
                (name, email, phone, date_of_birth, emergency_contact, emergency_phone, medical_notes, remaining_classes, membership_expiry)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data.get('name'),
                    data.get('email'),
                    data.get('phone'),
                    data.get('date_of_birth'),
                    data.get('emergency_contact'),
                    data.get('emergency_phone'),
                    data.get('medical_notes'),
                    data.get('remaining_classes', 0),
                    data.get('membership_expiry')
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
                
                query += " ORDER BY t.created_at DESC"
                
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
                    for field in ['created_at', 'updated_at']:
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
                cursor = connection.cursor()
                
                # 插入老師基本資料 (包含銀行帳號、大頭貼)
                insert_teacher_query = """
                INSERT INTO teachers 
                (name, email, phone, bio, hourly_rate, bank_account, avatar_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                teacher_values = (
                    data.get('name'),
                    data.get('email'),
                    data.get('phone'),
                    data.get('bio'),
                    data.get('hourly_rate'),
                    data.get('bank_account'),
                    data.get('avatar_url')
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
                    for field in ['created_at', 'updated_at']:
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
                cursor = connection.cursor()
                
                insert_query = """
                INSERT INTO courses 
                (name, description, level, style_id, duration_minutes, max_students, price, teacher_id,
                 base_salary, low_student_threshold, low_student_salary, extra_student_threshold, extra_student_fee, salary_cap)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data.get('name'),
                    data.get('description'),
                    data.get('level'),
                    data.get('style_id'),
                    data.get('duration_minutes', 60),
                    data.get('max_students', 15),
                    data.get('price'),
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
                       c.teacher_id as teacher_id,
                       c.base_salary, c.low_student_threshold, c.low_student_salary, c.extra_student_threshold, c.extra_student_fee, c.salary_cap,
                       s.name as style_name, t.name as teacher_name, t.avatar_url as teacher_avatar_url, r.name as room_name, 
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

                # 轉換時間物件為字串
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
                cursor = connection.cursor()
                
                # 從日期推算星期幾
                from datetime import datetime
                date_obj = datetime.strptime(data['schedule_date'], '%Y-%m-%d')
                day_of_week = date_obj.strftime('%A')  # Monday, Tuesday, etc.
                
                insert_query = """
                INSERT INTO course_schedules 
                (course_id, schedule_date, day_of_week, start_time, end_time, room_id, is_active, allow_enrollment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data.get('course_id'),
                    data.get('schedule_date'),
                    day_of_week,
                    data.get('start_time'),
                    data.get('end_time'),
                    data.get('room_id'),
                    data.get('is_active', True),
                    data.get('allow_enrollment', True)
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
                cursor = connection.cursor()
                
                # 先確認學生是否存在
                cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
                if not cursor.fetchone():
                    return {'error': '學生未找到'}, 404
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['name', 'email', 'phone', 'date_of_birth', 'emergency_contact', 'emergency_phone', 'medical_notes', 'remaining_classes', 'membership_expiry']:
                        if key in ['date_of_birth', 'membership_expiry'] and (value == '' or value == '1911-01-01'):
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
                cursor = connection.cursor()
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
                for field in ['created_at', 'updated_at']:
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
                cursor = connection.cursor()
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['name', 'email', 'phone', 'bio', 'hourly_rate', 'bank_account', 'avatar_url']:
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
                cursor = connection.cursor()
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
                for field in ['created_at', 'updated_at']:
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
                cursor = connection.cursor()
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['name', 'description', 'level', 'style_id', 'duration_minutes', 'max_students', 'price', 'teacher_id',
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
                cursor = connection.cursor()
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
                       c.teacher_id as teacher_id,
                       c.base_salary, c.low_student_threshold, c.low_student_salary, c.extra_student_threshold, c.extra_student_fee, c.salary_cap,
                       s.name as style_name, 
                       t.name as teacher_name, t.avatar_url as teacher_avatar_url, r.name as room_name, 
                       r.capacity as room_capacity
                FROM course_schedules cs
                JOIN courses c ON cs.course_id = c.id
                LEFT JOIN teachers t ON c.teacher_id = t.id
                LEFT JOIN styles s ON c.style_id = s.id
                LEFT JOIN rooms r ON cs.room_id = r.id
                WHERE cs.id = %s
                """
                cursor.execute(query, (schedule_id,))
                schedule = cursor.fetchone()
                
                if not schedule:
                    return {'error': '課程時間表未找到'}, 404
                
                # 轉換時間物件為字串
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
                cursor = connection.cursor()
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['course_id', 'schedule_date', 'start_time', 'end_time', 'room_id', 'is_active', 'allow_enrollment']:
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
                cursor = connection.cursor()
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
                cursor = connection.cursor()
                
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
                cursor = connection.cursor()
                
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
                cursor = connection.cursor()
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
                cursor.execute("SELECT * FROM rooms ORDER BY id DESC")
                rooms = cursor.fetchall()

                # 轉換 Decimal 物件為字串
                for room in rooms:
                    if room.get('hourly_rate'):
                        room['hourly_rate'] = str(room['hourly_rate'])
                    # 轉換 datetime 物件為 ISO 格式字串
                    for field in ['created_at', 'updated_at']:
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
                cursor = connection.cursor()
                
                insert_query = """
                INSERT INTO rooms (name, capacity, equipment, description, hourly_rate, is_available)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data.get('name'),
                    data.get('capacity'),
                    data.get('equipment'),
                    data.get('description'),
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
                for field in ['created_at', 'updated_at']:
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
                cursor = connection.cursor()
                
                update_fields = []
                values = []
                
                for key, value in data.items():
                    if key in ['name', 'capacity', 'equipment', 'description', 'hourly_rate', 'is_available']:
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
                cursor = connection.cursor()
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
                        return {
                            'success': True,
                            'message': '密碼設定成功，歡迎首次登入！',
                            'is_first_login': True,
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
                
                return {
                    'success': True,
                    'message': '登入成功！',
                    'is_first_login': False,
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
                (name, phone, email, password_hash, remaining_classes, membership_expiry, date_of_birth, emergency_contact, emergency_phone)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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

                if not user or user['password'] != password:
                    return {'error': '帳號或密碼錯誤，請確認後重試'}, 401

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
                    'user': user_info
                }, 200
            finally:
                cursor.close()
                connection.close()

        except Exception as e:
            print(f"後台登入錯誤: {str(e)}")
            return {'error': '登入處理發生錯誤'}, 500

class AdminUsers(Resource):
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
                    for field in ['created_at', 'updated_at']:
                        if u.get(field) and isinstance(u[field], datetime):
                            u[field] = u[field].isoformat()

                return {'success': True, 'users': users}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢使用者失敗: {str(e)}'}, 500

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

                cursor.execute("""
                INSERT INTO admin_users (username, password, name, role, phone, hourly_rate, bank_account, teacher_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (username, password, name, role, phone, hourly_rate, bank_account, teacher_id))
                connection.commit()

                return {'success': True, 'message': f'成功建立帳號「{username}」！'}, 201
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'新增使用者失敗: {str(e)}'}, 500

class AdminUser(Resource):
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
                for field in ['created_at', 'updated_at']:
                    if user.get(field) and isinstance(user[field], datetime):
                        user[field] = user[field].isoformat()
                return {'success': True, 'user': user}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'查詢使用者失敗: {str(e)}'}, 500

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
                    update_query = """
                    UPDATE admin_users 
                    SET username = %s, password = %s, name = %s, role = %s, phone = %s, hourly_rate = %s, bank_account = %s, teacher_id = %s
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (username, password, name, role, phone, hourly_rate, bank_account, teacher_id, user_id))
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

    def delete(self, user_id):
        """刪除後台員工帳號"""
        if user_id == 1:
            return {'error': '系統最高管理員帳號無法刪除！'}, 400
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
            try:
                cursor = connection.cursor()
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
    """獲取客戶端真實 IP (支援反向代理如 Vite、Nginx 轉發之標頭，並正規化 IPv4-mapped IPv6)"""
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
        if ip:
            if ip.startswith('::ffff:'):
                ip = ip[7:]
            return ip
    x_real_ip = request.headers.get('X-Real-IP')
    if x_real_ip:
        ip = x_real_ip.strip()
        if ip.startswith('::ffff:'):
            ip = ip[7:]
        return ip
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
                cursor = connection.cursor()
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
                cursor = connection.cursor()
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
                if t_id:
                    cursor.execute("""
                    SELECT cs.id as schedule_id, cs.schedule_date, cs.start_time, cs.end_time,
                           c.id as course_id, c.name as course_name, c.level, c.base_salary, c.low_student_threshold, c.low_student_salary,
                           c.extra_student_threshold, c.extra_student_fee, c.salary_cap,
                           r.name as room_name,
                           COUNT(CASE WHEN e.status = 'confirmed' THEN 1 END) as student_count
                    FROM course_schedules cs
                    JOIN courses c ON cs.course_id = c.id
                    LEFT JOIN rooms r ON cs.room_id = r.id
                    LEFT JOIN enrollments e ON cs.id = e.schedule_id
                    WHERE c.teacher_id = %s AND cs.schedule_date = CURRENT_DATE()
                    GROUP BY cs.id
                    ORDER BY cs.start_time ASC
                    """, (t_id,))
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
                        est_salary, _, _ = compute_teacher_schedule_salary(cursor, s['schedule_id'], t_id)
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
                if t_id:
                    cursor.execute("""
                    SELECT id, name, level, base_salary, low_student_threshold, low_student_salary,
                           extra_student_threshold, extra_student_fee, salary_cap
                    FROM courses
                    WHERE teacher_id = %s
                    ORDER BY name ASC
                    """, (t_id,))
                    teacher_courses = cursor.fetchall()
                    for tc in teacher_courses:
                        tc['base_salary'] = float(tc.get('base_salary') or 0)
                        tc['low_student_threshold'] = int(tc.get('low_student_threshold') or 0)
                        tc['low_student_salary'] = float(tc.get('low_student_salary') or 0)
                        tc['extra_student_threshold'] = int(tc.get('extra_student_threshold') or 0)
                        tc['extra_student_fee'] = float(tc.get('extra_student_fee') or 0)
                        tc['salary_cap'] = float(tc.get('salary_cap') or 0)

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

                # 若指定了 schedule_id，自動帶出課程 ID 與名稱
                if schedule_id:
                    cursor.execute("""
                    SELECT c.id as course_id, c.name as course_name FROM course_schedules cs
                    JOIN courses c ON cs.course_id = c.id
                    WHERE cs.id = %s
                    """, (schedule_id,))
                    c_row = cursor.fetchone()
                    if c_row:
                        course_id = c_row['course_id']
                        course_name = c_row['course_name']
                elif course_id:
                    cursor.execute("SELECT name FROM courses WHERE id = %s", (course_id,))
                    c_row = cursor.fetchone()
                    if c_row:
                        course_name = c_row['name']

                if not course_name:
                    course_name = '一般授課課程'

                now = datetime.now()
                cursor.execute("""
                INSERT INTO teacher_attendance (user_id, teacher_id, schedule_id, course_id, course_name, clock_in, notes, clock_in_ip)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, teacher_id, schedule_id or None, course_id or None, course_name, now, notes, client_ip))
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
                cursor = connection.cursor()
                cursor.execute("DELETE FROM teacher_attendance WHERE id = %s", (attendance_id,))
                connection.commit()
                return {'success': True, 'message': '打卡記錄已刪除'}, 200
            finally:
                cursor.close()
                connection.close()
        except Exception as e:
            return {'error': f'刪除打卡記錄失敗: {str(e)}'}, 500

class TeacherAvatarUpload(Resource):
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
                        cursor = connection.cursor()
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
                    cursor = connection.cursor()
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
api.add_resource(AttendanceIpSettings, '/api/admin/settings/attendance-ip')

if __name__ == '__main__':
    # 初始化資料庫表格
    init_database_tables()
    app.run(debug=True, host='0.0.0.0', port=8001)