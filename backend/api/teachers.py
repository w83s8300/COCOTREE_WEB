"""
老師管理 API
"""
from flask_restful import Resource, request
from flask import jsonify
import mysql.connector
from .database import get_db_connection

class Teachers(Resource):
    def get(self):
        """獲取所有老師列表"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM teachers ORDER BY name")
            teachers = cursor.fetchall()
            
            return {'teachers': teachers}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取老師列表錯誤: {err}")
            return {'error': '獲取老師列表失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def post(self):
        """新增老師"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return {'error': '老師姓名為必填欄位'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO teachers (name, email, phone, age, gender, specialties, experience_years)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            teacher_data = (
                data.get('name'),
                data.get('email'),
                data.get('phone'),
                data.get('age'),
                data.get('gender'),
                data.get('specialties'),
                data.get('experience_years')
            )
            
            cursor.execute(insert_query, teacher_data)
            connection.commit()
            teacher_id = cursor.lastrowid
            
            return {
                'message': '老師新增成功',
                'teacher_id': teacher_id
            }, 201
            
        except mysql.connector.Error as err:
            print(f"新增老師錯誤: {err}")
            return {'error': '新增老師失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class Teacher(Resource):
    def get(self, teacher_id):
        """獲取單一老師資料"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM teachers WHERE id = %s", (teacher_id,))
            teacher = cursor.fetchone()
            
            if not teacher:
                return {'error': '找不到該老師'}, 404
                
            return {'teacher': teacher}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取老師資料錯誤: {err}")
            return {'error': '獲取老師資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def put(self, teacher_id):
        """更新老師資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '請提供要更新的資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查老師是否存在
            cursor.execute("SELECT id FROM teachers WHERE id = %s", (teacher_id,))
            if not cursor.fetchone():
                return {'error': '找不到該老師'}, 404
            
            # 建立更新查詢
            update_fields = []
            update_values = []
            
            for field in ['name', 'email', 'phone', 'age', 'gender', 'specialties', 'experience_years']:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])
            
            if not update_fields:
                return {'error': '沒有提供有效的更新欄位'}, 400
            
            update_values.append(teacher_id)
            update_query = f"UPDATE teachers SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(update_query, update_values)
            connection.commit()
            
            return {'message': '老師資料更新成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"更新老師資料錯誤: {err}")
            return {'error': '更新老師資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def delete(self, teacher_id):
        """刪除老師"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查老師是否存在
            cursor.execute("SELECT id FROM teachers WHERE id = %s", (teacher_id,))
            if not cursor.fetchone():
                return {'error': '找不到該老師'}, 404
            
            # 檢查是否有相關的課程
            cursor.execute("SELECT COUNT(*) FROM courses WHERE teacher_id = %s", (teacher_id,))
            course_count = cursor.fetchone()[0]
            
            if course_count > 0:
                return {'error': '該老師有相關課程，無法刪除'}, 400
            
            cursor.execute("DELETE FROM teachers WHERE id = %s", (teacher_id,))
            connection.commit()
            
            return {'message': '老師刪除成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"刪除老師錯誤: {err}")
            return {'error': '刪除老師失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
