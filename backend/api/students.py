"""
學生管理 API
"""
from flask_restful import Resource, request
from flask import jsonify
import mysql.connector
from .database import get_db_connection

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
                INSERT INTO students (name, email, phone, age, gender, remaining_classes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            student_data = (
                data.get('name'),
                data.get('email'),
                data.get('phone'),
                data.get('age'),
                data.get('gender'),
                data.get('remaining_classes', 0)
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
            
            for field in ['name', 'email', 'phone', 'age', 'gender', 'remaining_classes']:
                if field in data:
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
