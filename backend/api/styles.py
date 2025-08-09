"""
舞蹈風格管理 API
"""
from flask_restful import Resource, request
from flask import jsonify
import mysql.connector
from .database import get_db_connection

class Styles(Resource):
    def get(self):
        """獲取所有風格列表"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM styles ORDER BY name")
            styles = cursor.fetchall()
            
            return {'styles': styles}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取風格列表錯誤: {err}")
            return {'error': '獲取風格列表失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def post(self):
        """新增風格"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return {'error': '風格名稱為必填欄位'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO styles (name, description)
                VALUES (%s, %s)
            """
            style_data = (
                data.get('name'),
                data.get('description')
            )
            
            cursor.execute(insert_query, style_data)
            connection.commit()
            style_id = cursor.lastrowid
            
            return {
                'message': '風格新增成功',
                'style_id': style_id
            }, 201
            
        except mysql.connector.Error as err:
            print(f"新增風格錯誤: {err}")
            return {'error': '新增風格失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class Style(Resource):
    def get(self, style_id):
        """獲取單一風格資料"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM styles WHERE id = %s", (style_id,))
            style = cursor.fetchone()
            
            if not style:
                return {'error': '找不到該風格'}, 404
                
            return {'style': style}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取風格資料錯誤: {err}")
            return {'error': '獲取風格資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def put(self, style_id):
        """更新風格資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '請提供要更新的資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查風格是否存在
            cursor.execute("SELECT id FROM styles WHERE id = %s", (style_id,))
            if not cursor.fetchone():
                return {'error': '找不到該風格'}, 404
            
            # 建立更新查詢
            update_fields = []
            update_values = []
            
            for field in ['name', 'description']:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])
            
            if not update_fields:
                return {'error': '沒有提供有效的更新欄位'}, 400
            
            update_values.append(style_id)
            update_query = f"UPDATE styles SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(update_query, update_values)
            connection.commit()
            
            return {'message': '風格資料更新成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"更新風格資料錯誤: {err}")
            return {'error': '更新風格資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def delete(self, style_id):
        """刪除風格"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查風格是否存在
            cursor.execute("SELECT id FROM styles WHERE id = %s", (style_id,))
            if not cursor.fetchone():
                return {'error': '找不到該風格'}, 404
            
            # 檢查是否有相關的課程
            cursor.execute("SELECT COUNT(*) FROM courses WHERE style_id = %s", (style_id,))
            course_count = cursor.fetchone()[0]
            
            if course_count > 0:
                return {'error': '該風格有相關課程，無法刪除'}, 400
            
            cursor.execute("DELETE FROM styles WHERE id = %s", (style_id,))
            connection.commit()
            
            return {'message': '風格刪除成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"刪除風格錯誤: {err}")
            return {'error': '刪除風格失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
