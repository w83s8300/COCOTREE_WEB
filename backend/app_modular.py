"""
舞蹈工作室管理系統 - 主應用文件
模組化架構，分離不同功能的 API
"""
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

# 導入資料庫初始化
from api.database import init_database_tables

# 導入各功能模組
from api.students import Students, Student
from api.teachers import Teachers, Teacher
from api.courses import Courses, Course
from api.schedules import CourseSchedules, CourseSchedule
from api.styles import Styles, Style
from api.rooms import Rooms, Room
from api.enrollments import (
    HelloWorld, Enrollment, ScheduleEnrollments, 
    EnrollmentDetail
)

# 創建 Flask 應用
app = Flask(__name__)
CORS(app)  # 允許跨域請求
api = Api(app)

# 註冊 API 路由
def register_routes():
    """註冊所有 API 路由"""
    
    # 基本路由
    api.add_resource(HelloWorld, '/')
    
    # 學生管理 API
    api.add_resource(Students, '/api/students')
    api.add_resource(Student, '/api/students/<int:student_id>')
    
    # 老師管理 API
    api.add_resource(Teachers, '/api/teachers')
    api.add_resource(Teacher, '/api/teachers/<int:teacher_id>')
    
    # 課程管理 API
    api.add_resource(Courses, '/api/courses')
    api.add_resource(Course, '/api/courses/<int:course_id>')
    
    # 排程管理 API
    api.add_resource(CourseSchedules, '/api/schedules')
    api.add_resource(CourseSchedule, '/api/schedules/<int:schedule_id>')
    
    # 風格管理 API
    api.add_resource(Styles, '/api/styles')
    api.add_resource(Style, '/api/styles/<int:style_id>')
    
    # 教室管理 API
    api.add_resource(Rooms, '/api/rooms')
    api.add_resource(Room, '/api/rooms/<int:room_id>')
    
    # 報名管理 API
    api.add_resource(Enrollment, '/api/enrollment')
    api.add_resource(ScheduleEnrollments, '/api/schedules/<int:schedule_id>/enrollments')
    api.add_resource(EnrollmentDetail, '/api/enrollments/<int:enrollment_id>')

# 註冊所有路由
register_routes()

if __name__ == '__main__':
    # 初始化資料庫表格
    print("=== 舞蹈工作室管理系統啟動 ===")
    print("正在初始化資料庫...")
    init_database_tables()
    
    print("正在註冊 API 路由...")
    print("✓ 學生管理 API")
    print("✓ 老師管理 API") 
    print("✓ 課程管理 API")
    print("✓ 排程管理 API")
    print("✓ 風格管理 API")
    print("✓ 教室管理 API")
    print("✓ 報名管理 API")
    
    print("伺服器啟動於 http://0.0.0.0:8001")
    print("================================")
    
    app.run(debug=True, host='0.0.0.0', port=8001)
