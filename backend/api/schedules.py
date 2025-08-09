"""
課程排程管理 API
"""
from flask_restful import Resource, request
from flask import jsonify
import mysql.connector
from datetime import datetime, date
from .database import get_db_connection

class CourseSchedules(Resource):
    def get(self):
        """獲取所有課程排程"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT s.*, c.name as course_name, t.name as teacher_name, r.name as room_name
                FROM schedules s
                LEFT JOIN courses c ON s.course_id = c.id
                LEFT JOIN teachers t ON s.teacher_id = t.id
                LEFT JOIN rooms r ON s.room_id = r.id
                ORDER BY s.day_of_week, s.start_time
            """
            cursor.execute(query)
            schedules = cursor.fetchall()
            
            # 轉換日期時間格式
            for schedule in schedules:
                if schedule['start_time']:
                    schedule['start_time'] = schedule['start_time'].strftime('%H:%M:%S')
                if schedule['end_time']:
                    schedule['end_time'] = schedule['end_time'].strftime('%H:%M:%S')
            
            return {'schedules': schedules}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取排程列表錯誤: {err}")
            return {'error': '獲取排程列表失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def post(self):
        """新增課程排程"""
        try:
            data = request.get_json()
            
            required_fields = ['course_id', 'teacher_id', 'day_of_week', 'start_time', 'end_time']
            for field in required_fields:
                if field not in data:
                    return {'error': f'{field} 為必填欄位'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO schedules (course_id, teacher_id, room_id, start_time, end_time, day_of_week, max_students, current_students)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            schedule_data = (
                data.get('course_id'),
                data.get('teacher_id'),
                data.get('room_id'),
                data.get('start_time'),
                data.get('end_time'),
                data.get('day_of_week'),
                data.get('max_students', 15),
                data.get('current_students', 0)
            )
            
            cursor.execute(insert_query, schedule_data)
            connection.commit()
            schedule_id = cursor.lastrowid
            
            return {
                'message': '排程新增成功',
                'schedule_id': schedule_id
            }, 201
            
        except mysql.connector.Error as err:
            print(f"新增排程錯誤: {err}")
            return {'error': '新增排程失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class CourseSchedule(Resource):
    def get(self, schedule_id):
        """獲取單一排程資料"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT s.*, c.name as course_name, t.name as teacher_name, r.name as room_name
                FROM schedules s
                LEFT JOIN courses c ON s.course_id = c.id
                LEFT JOIN teachers t ON s.teacher_id = t.id
                LEFT JOIN rooms r ON s.room_id = r.id
                WHERE s.id = %s
            """
            cursor.execute(query, (schedule_id,))
            schedule = cursor.fetchone()
            
            if not schedule:
                return {'error': '找不到該排程'}, 404
            
            # 轉換日期時間格式
            if schedule['start_time']:
                schedule['start_time'] = schedule['start_time'].strftime('%H:%M:%S')
            if schedule['end_time']:
                schedule['end_time'] = schedule['end_time'].strftime('%H:%M:%S')
                
            return {'schedule': schedule}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取排程資料錯誤: {err}")
            return {'error': '獲取排程資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def put(self, schedule_id):
        """更新排程資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '請提供要更新的資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查排程是否存在
            cursor.execute("SELECT id FROM schedules WHERE id = %s", (schedule_id,))
            if not cursor.fetchone():
                return {'error': '找不到該排程'}, 404
            
            # 建立更新查詢
            update_fields = []
            update_values = []
            
            for field in ['course_id', 'teacher_id', 'room_id', 'start_time', 'end_time', 'day_of_week', 'max_students', 'current_students']:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])
            
            if not update_fields:
                return {'error': '沒有提供有效的更新欄位'}, 400
            
            update_values.append(schedule_id)
            update_query = f"UPDATE schedules SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(update_query, update_values)
            connection.commit()
            
            return {'message': '排程資料更新成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"更新排程資料錯誤: {err}")
            return {'error': '更新排程資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def delete(self, schedule_id):
        """刪除排程"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查排程是否存在
            cursor.execute("SELECT id FROM schedules WHERE id = %s", (schedule_id,))
            if not cursor.fetchone():
                return {'error': '找不到該排程'}, 404
            
            # 檢查是否有相關的報名記錄
            cursor.execute("SELECT COUNT(*) FROM enrollments WHERE schedule_id = %s", (schedule_id,))
            enrollment_count = cursor.fetchone()[0]
            
            if enrollment_count > 0:
                return {'error': '該排程有報名記錄，無法刪除'}, 400
            
            cursor.execute("DELETE FROM schedules WHERE id = %s", (schedule_id,))
            connection.commit()
            
            return {'message': '排程刪除成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"刪除排程錯誤: {err}")
            return {'error': '刪除排程失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
