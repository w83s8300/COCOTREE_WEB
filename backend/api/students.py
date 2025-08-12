"""
學生管理 API
"""
from flask_restful import Resource, request
from flask import jsonify
import mysql.connector
from datetime import date, datetime
from .database import get_db_connection

def serialize_dates(obj):
    """序列化日期對象為字符串"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj

def process_student_data(student):
    """處理學生資料，序列化日期字段"""
    if student:
        for key, value in student.items():
            student[key] = serialize_dates(value)
    return student

def process_students_list(students):
    """處理學生列表，序列化所有日期字段"""
    for student in students:
        process_student_data(student)
    return students

class Students(Resource):
    def get(self):
        """獲取所有學生列表"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students ORDER BY name")
            students = cursor.fetchall()
            
            # 處理日期序列化
            students = process_students_list(students)
            
            return {'students': students}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取學生列表錯誤: {err}")
            return {'error': '獲取學生列表失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def post(self):
        """新增學生"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return {'error': '學生姓名為必填欄位'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO students (name, email, phone, age, date_of_birth, emergency_contact, emergency_phone, 
                                    medical_notes, remaining_classes, membership_expiry)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # 處理出生年月日，如果沒有提供則設為 1911-01-01
            date_of_birth = data.get('date_of_birth')
            if not date_of_birth:
                date_of_birth = '1911-01-01'
            
            # 處理會員到期日，如果沒有提供則設為 1911-01-01
            membership_expiry = data.get('membership_expiry')
            if not membership_expiry:
                membership_expiry = '1911-01-01'
            
            student_data = (
                data.get('name'),
                data.get('email'),
                data.get('phone'),
                data.get('age'),
                date_of_birth,
                data.get('emergency_contact'),
                data.get('emergency_phone'),
                data.get('medical_notes'),
                data.get('remaining_classes', 0),
                membership_expiry
            )
            
            cursor.execute(insert_query, student_data)
            connection.commit()
            student_id = cursor.lastrowid
            
            return {
                'message': '學生新增成功',
                'student_id': student_id
            }, 201
            
        except mysql.connector.Error as err:
            print(f"新增學生錯誤: {err}")
            return {'error': '新增學生失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class Student(Resource):
    def get(self, student_id):
        """獲取單一學生資料"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
            student = cursor.fetchone()
            
            if not student:
                return {'error': '找不到該學生'}, 404
            
            # 處理日期序列化
            student = process_student_data(student)
                
            return {'student': student}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取學生資料錯誤: {err}")
            return {'error': '獲取學生資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def put(self, student_id):
        """更新學生資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '請提供要更新的資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查學生是否存在
            cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
            if not cursor.fetchone():
                return {'error': '找不到該學生'}, 404
            
            # 建立更新查詢
            update_fields = []
            update_values = []
            
            for field in ['name', 'email', 'phone', 'age', 'date_of_birth', 'emergency_contact', 'emergency_phone', 'medical_notes', 'remaining_classes', 'membership_expiry']:
                if field in data:
                    # 處理日期欄位的空值
                    if field in ['date_of_birth', 'membership_expiry'] and (not data[field] or data[field] == ''):
                        update_fields.append(f"{field} = %s")
                        update_values.append('1911-01-01')
                    else:
                        update_fields.append(f"{field} = %s")
                        update_values.append(data[field])
            
            if not update_fields:
                return {'error': '沒有提供有效的更新欄位'}, 400
            
            update_values.append(student_id)
            update_query = f"UPDATE students SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(update_query, update_values)
            connection.commit()
            
            return {'message': '學生資料更新成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"更新學生資料錯誤: {err}")
            return {'error': '更新學生資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def delete(self, student_id):
        """刪除學生"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查學生是否存在
            cursor.execute("SELECT id FROM students WHERE id = %s", (student_id,))
            if not cursor.fetchone():
                return {'error': '找不到該學生'}, 404
            
            # 檢查是否有相關的報名記錄
            cursor.execute("SELECT COUNT(*) FROM enrollments WHERE student_name = (SELECT name FROM students WHERE id = %s)", (student_id,))
            enrollment_count = cursor.fetchone()[0]
            
            if enrollment_count > 0:
                return {'error': '該學生有報名記錄，無法刪除'}, 400
            
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            connection.commit()
            
            return {'message': '學生刪除成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"刪除學生錯誤: {err}")
            return {'error': '刪除學生失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
