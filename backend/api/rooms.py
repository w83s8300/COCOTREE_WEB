"""
教室管理 API
"""
from flask_restful import Resource, request
from flask import jsonify
import mysql.connector
from .database import get_db_connection

class Rooms(Resource):
    def get(self):
        """獲取所有教室列表"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM rooms ORDER BY name")
            rooms = cursor.fetchall()
            
            return {'rooms': rooms}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取教室列表錯誤: {err}")
            return {'error': '獲取教室列表失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def post(self):
        """新增教室"""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data:
                return {'error': '教室名稱為必填欄位'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO rooms (name, capacity, equipment, description, hourly_rate, is_available)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            room_data = (
                data.get('name'),
                data.get('capacity', 20),
                data.get('equipment'),
                data.get('description'),
                data.get('hourly_rate'),
                data.get('is_available', True)
            )
            
            cursor.execute(insert_query, room_data)
            connection.commit()
            room_id = cursor.lastrowid
            
            return {
                'message': '教室新增成功',
                'room_id': room_id
            }, 201
            
        except mysql.connector.Error as err:
            print(f"新增教室錯誤: {err}")
            return {'error': '新增教室失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class Room(Resource):
    def get(self, room_id):
        """獲取單一教室資料"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM rooms WHERE id = %s", (room_id,))
            room = cursor.fetchone()
            
            if not room:
                return {'error': '找不到該教室'}, 404
                
            return {'room': room}, 200
            
        except mysql.connector.Error as err:
            print(f"獲取教室資料錯誤: {err}")
            return {'error': '獲取教室資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def put(self, room_id):
        """更新教室資料"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': '請提供要更新的資料'}, 400
            
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查教室是否存在
            cursor.execute("SELECT id FROM rooms WHERE id = %s", (room_id,))
            if not cursor.fetchone():
                return {'error': '找不到該教室'}, 404
            
            # 建立更新查詢
            update_fields = []
            update_values = []
            
            for field in ['name', 'capacity', 'equipment', 'description', 'hourly_rate', 'is_available']:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])
            
            if not update_fields:
                return {'error': '沒有提供有效的更新欄位'}, 400
            
            update_values.append(room_id)
            update_query = f"UPDATE rooms SET {', '.join(update_fields)} WHERE id = %s"
            
            cursor.execute(update_query, update_values)
            connection.commit()
            
            return {'message': '教室資料更新成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"更新教室資料錯誤: {err}")
            return {'error': '更新教室資料失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    def delete(self, room_id):
        """刪除教室"""
        try:
            connection = get_db_connection()
            if not connection:
                return {'error': '資料庫連接失敗'}, 500
                
            cursor = connection.cursor()
            
            # 檢查教室是否存在
            cursor.execute("SELECT id FROM rooms WHERE id = %s", (room_id,))
            if not cursor.fetchone():
                return {'error': '找不到該教室'}, 404
            
            # 檢查是否有相關的排程
            cursor.execute("SELECT COUNT(*) FROM schedules WHERE room_id = %s", (room_id,))
            schedule_count = cursor.fetchone()[0]
            
            if schedule_count > 0:
                return {'error': '該教室有相關排程，無法刪除'}, 400
            
            cursor.execute("DELETE FROM rooms WHERE id = %s", (room_id,))
            connection.commit()
            
            return {'message': '教室刪除成功'}, 200
            
        except mysql.connector.Error as err:
            print(f"刪除教室錯誤: {err}")
            return {'error': '刪除教室失敗'}, 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
