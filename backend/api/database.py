"""
共用工具模組 - 資料庫連接和配置
"""
import mysql.connector
import time

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
    max_retries = 5
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
                email VARCHAR(100),
                phone VARCHAR(20),
                age INT,
                gender ENUM('男', '女', '其他'),
                remaining_classes INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            # 老師表格
            teachers_table = """
            CREATE TABLE IF NOT EXISTS teachers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                age INT,
                gender ENUM('男', '女', '其他'),
                specialties TEXT,
                experience_years INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            # 風格表格
            styles_table = """
            CREATE TABLE IF NOT EXISTS styles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            # 教室表格
            rooms_table = """
            CREATE TABLE IF NOT EXISTS rooms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                capacity INT DEFAULT 20,
                equipment TEXT,
                description TEXT,
                hourly_rate DECIMAL(10,2),
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            # 課程表格
            courses_table = """
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                level VARCHAR(50),
                style_id INT,
                duration_minutes INT DEFAULT 60,
                max_students INT DEFAULT 15,
                price DECIMAL(10,2),
                teacher_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (style_id) REFERENCES styles(id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            )
            """
            
            # 課程時程表格
            schedules_table = """
            CREATE TABLE IF NOT EXISTS schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_id INT,
                teacher_id INT,
                room_id INT,
                start_time DATETIME,
                end_time DATETIME,
                day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
                max_students INT DEFAULT 15,
                current_students INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(id),
                FOREIGN KEY (room_id) REFERENCES rooms(id)
            )
            """
            
            # 報名表格（包含 deducted_classes 欄位）
            enrollments_table = """
            CREATE TABLE IF NOT EXISTS enrollments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(100) NOT NULL,
                schedule_id INT,
                enrollment_date DATE,
                status ENUM('已報名', '已取消', '已完成') DEFAULT '已報名',
                deducted_classes INT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (schedule_id) REFERENCES schedules(id)
            )
            """
            
            # 執行表格創建
            tables = [
                ("students", students_table),
                ("teachers", teachers_table),
                ("styles", styles_table),
                ("rooms", rooms_table),
                ("courses", courses_table),
                ("schedules", schedules_table),
                ("enrollments", enrollments_table)
            ]
            
            for table_name, table_sql in tables:
                try:
                    cursor.execute(table_sql)
                    print(f"✓ {table_name} 表格創建/確認成功")
                except mysql.connector.Error as table_err:
                    print(f"✗ {table_name} 表格創建失敗: {table_err}")
            
            connection.commit()
            print("資料庫表格初始化完成！")
            
        except mysql.connector.Error as err:
            print(f"資料庫初始化錯誤: {err}")
        finally:
            cursor.close()
            connection.close()
    else:
        print("無法連接到資料庫，跳過表格初始化")
