"""
課程管理 API
"""
from flask_restful import Resource, request
from flask import jsonify
import mysql.connector
from .database import get_db_connection

class Courses(Resource):
    def get(self):
        """獲取所有課程列表"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT c.*, s.name as style_name, t.name as teacher_name
                FROM courses c
                LEFT JOIN styles s ON c.style_id = s.id
                LEFT JOIN teachers t ON c.teacher_id = t.id
                ORDER BY c.name
            """
            cursor.execute(query)
            courses = cursor.fetchall()
            
            return {'courses': courses}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取課程列表錯誤: {err}")
            return {'error': '獲取課程列表失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def post(self):
        """新增課程"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return {'error': '課程名稱為必填欄位'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO courses (name, description, level, style_id, duration_minutes, max_students, price, teacher_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            course_data = (
                data.get('name'),
                data.get('description'),
                data.get('level'),
                data.get('style_id'),
                data.get('duration_minutes', 60),
                data.get('max_students', 15),
                data.get('price'),
                data.get('teacher_id')
            )
            
            cursor.execute(insert_query, course_data)
            connection.commit()
            course_id = cursor.lastrowid
            
            return {
                'message': '課程新增成功',
                'course_id': course_id
            }, 201
            
        except mysql.connector.Error as err:
            print(f"新增課程錯誤: {err}")
            return {'error': '新增課程失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class Course(Resource):
    def get(self, course_id):
        """獲取單一課程資料"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT c.*, s.name as style_name, t.name as teacher_name
                FROM courses c
                LEFT JOIN styles s ON c.style_id = s.id
                LEFT JOIN teachers t ON c.teacher_id = t.id
                WHERE c.id = %s
            """
            cursor.execute(query, (course_id,))
            course = cursor.fetchone()
            
            if not course:
                return {'error': '找不到該課程'}, 404
                
            return {'course': course}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取課程資料錯誤: {err}")
            return {'error': '獲取課程資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def put(self, course_id):
        """更新課程資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '請提供要更新的資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查課程是否存在
            cursor.execute("SELECT id FROM courses WHERE id = %s", (course_id,))
            if not cursor.fetchone():
                return {'error': '找不到該課程'}, 404
            
            # 建立更新查詢
            update_fields = []
            update_values = []
            
            for field in ['name', 'description', 'level', 'style_id', 'duration_minutes', 'max_students', 'price', 'teacher_id']:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])
            
            if not update_fields:
                return {'error': '沒有提供有效的更新欄位'}, 400
            
            update_values.append(course_id)
            update_query = f"UPDATE courses SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(update_query, update_values)
            connection.commit()
            
            return {'message': '課程資料更新成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"更新課程資料錯誤: {err}")
            return {'error': '更新課程資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def delete(self, course_id):
        """刪除課程"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查課程是否存在
            cursor.execute("SELECT id FROM courses WHERE id = %s", (course_id,))
            if not cursor.fetchone():
                return {'error': '找不到該課程'}, 404
            
            # 檢查是否有相關的排程
            cursor.execute("SELECT COUNT(*) FROM schedules WHERE course_id = %s", (course_id,))
            schedule_count = cursor.fetchone()[0]
            
            if schedule_count > 0:
                return {'error': '該課程有相關排程，無法刪除'}, 400
            
            cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
            connection.commit()
            
            return {'message': '課程刪除成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"刪除課程錯誤: {err}")
            return {'error': '刪除課程失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
