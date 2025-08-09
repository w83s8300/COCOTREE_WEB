"""
報名管理 API
"""
from flask_restful import Resource, request
from flask import jsonify
import mysql.connector
from datetime import datetime, date
from .database import get_db_connection

class Enrollment(Resource):
    def post(self):
        """報名課程"""
        try:
            data = request.get_json()
            
            required_fields = ['student_name', 'schedule_id']
            for field in required_fields:
                if field not in data:
                    return {'error': f'{field} 為必填欄位'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查學生餘額
            cursor.execute("SELECT remaining_classes FROM students WHERE name = %s", (data['student_name'],))
            result = cursor.fetchone()
            
            if not result:
                return {'error': '找不到學生資料'}, 404
            
            remaining_classes = result[0] or 0
            deducted_classes = data.get('deducted_classes', 1)
            
            if remaining_classes < deducted_classes:
                return {'error': f'餘額不足，剩餘堂數：{remaining_classes}'}, 400
            
            # 檢查是否已經報名
            cursor.execute("""
                SELECT id FROM enrollments 
                WHERE student_name = %s AND schedule_id = %s AND status = '已報名'
            """, (data['student_name'], data['schedule_id']))
            
            if cursor.fetchone():
                return {'error': '已經報名過此課程'}, 400
            
            # 新增報名記錄
            insert_query = """
                INSERT INTO enrollments (student_name, schedule_id, enrollment_date, status, deducted_classes)
                VALUES (%s, %s, %s, %s, %s)
            """
            enrollment_data = (
                data['student_name'],
                data['schedule_id'],
                data.get('enrollment_date', date.today()),
                '已報名',
                deducted_classes
            )
            
            cursor.execute(insert_query, enrollment_data)
            
            # 扣除學生餘額
            cursor.execute("""
                UPDATE students 
                SET remaining_classes = remaining_classes - %s 
                WHERE name = %s
            """, (deducted_classes, data['student_name']))
            
            # 更新排程的當前學生數
            cursor.execute("""
                UPDATE schedules 
                SET current_students = current_students + 1 
                WHERE id = %s
            """, (data['schedule_id'],))
            
            connection.commit()
            enrollment_id = cursor.lastrowid
            
            return {
                'message': '報名成功',
                'enrollment_id': enrollment_id,
                'deducted_classes': deducted_classes
            }, 201
            
        except mysql.connector.Error as err:
            print(f"報名錯誤: {err}")
            return {'error': '報名失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class ScheduleEnrollments(Resource):
    def get(self, schedule_id):
        """獲取特定排程的所有報名記錄"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT e.*, s.course_id, c.name as course_name
                FROM enrollments e
                LEFT JOIN schedules s ON e.schedule_id = s.id
                LEFT JOIN courses c ON s.course_id = c.id
                WHERE e.schedule_id = %s
                ORDER BY e.enrollment_date DESC
            """
            cursor.execute(query, (schedule_id,))
            enrollments = cursor.fetchall()
            
            return {'enrollments': enrollments}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取報名記錄錯誤: {err}")
            return {'error': '獲取報名記錄失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class EnrollmentDetail(Resource):
    def get(self, enrollment_id):
        """獲取報名詳情"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT e.*, s.course_id, c.name as course_name, s.start_time, s.end_time, s.day_of_week
                FROM enrollments e
                LEFT JOIN schedules s ON e.schedule_id = s.id
                LEFT JOIN courses c ON s.course_id = c.id
                WHERE e.id = %s
            """
            cursor.execute(query, (enrollment_id,))
            enrollment = cursor.fetchone()
            
            if not enrollment:
                return {'error': '找不到報名記錄'}, 404
                
            return {'enrollment': enrollment}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取報名詳情錯誤: {err}")
            return {'error': '獲取報名詳情失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def put(self, enrollment_id):
        """更新報名狀態（主要用於取消報名）"""
        try:
            data = request.get_json()
            
            if not data or 'status' not in data:
                return {'error': '請提供要更新的狀態'}, 400
            
            new_status = data['status']
            if new_status not in ['已報名', '已取消', '已完成']:
                return {'error': '無效的狀態值'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 獲取當前報名資訊
            cursor.execute("""
                SELECT student_name, schedule_id, status, deducted_classes
                FROM enrollments 
                WHERE id = %s
            """, (enrollment_id,))
            
            enrollment = cursor.fetchone()
            if not enrollment:
                return {'error': '找不到報名記錄'}, 404
            
            student_name, schedule_id, current_status, deducted_classes = enrollment
            
            # 如果是從已報名改為已取消，需要恢復學生餘額
            if current_status == '已報名' and new_status == '已取消':
                cursor.execute("""
                    UPDATE students 
                    SET remaining_classes = remaining_classes + %s 
                    WHERE name = %s
                """, (deducted_classes, student_name))
                
                print(f"取消報名：學生 {student_name} 回復 {deducted_classes} 堂課")
            
            # 更新報名狀態
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
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def delete(self, enrollment_id):
        """刪除報名記錄"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 獲取報名資訊以便恢復餘額
            cursor.execute("""
                SELECT student_name, status, deducted_classes
                FROM enrollments 
                WHERE id = %s
            """, (enrollment_id,))
            
            enrollment = cursor.fetchone()
            if not enrollment:
                return {'error': '找不到報名記錄'}, 404
            
            student_name, status, deducted_classes = enrollment
            
            # 如果是已報名狀態，需要恢復學生餘額
            if status == '已報名':
                cursor.execute("""
                    UPDATE students 
                    SET remaining_classes = remaining_classes + %s 
                    WHERE name = %s
                """, (deducted_classes, student_name))
            
            # 刪除報名記錄
            cursor.execute("DELETE FROM enrollments WHERE id = %s", (enrollment_id,))
            connection.commit()
            
            return {'message': '報名記錄刪除成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"刪除報名記錄錯誤: {err}")
            return {'error': '刪除報名記錄失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}
