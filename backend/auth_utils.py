import os
import datetime
import functools
import jwt
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# 優先讀取環境變數 JWT_SECRET，預設值在生產環境應強烈建議從 .env 設置
JWT_SECRET = os.getenv('JWT_SECRET', 'dancestudio-secure-jwt-secret-key-change-in-prod-2026')
JWT_ALGORITHM = 'HS256'

def hash_password(password: str) -> str:
    """使用 pbkdf2/scrypt 生成安全的加鹽密碼雜湊"""
    if not password:
        return ''
    return generate_password_hash(str(password))

def verify_and_upgrade_password(cursor, table_name, user_id, stored_password, input_password, password_col='password') -> bool:
    """
    驗證密碼，若資料庫中仍為舊明文密碼，驗證成功後自動將其升級為雜湊值
    """
    if not stored_password or not input_password:
        return False

    stored_str = str(stored_password)
    input_str = str(input_password)

    # 檢查是否為 Werkzeug 雜湊格式
    if stored_str.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
        return check_password_hash(stored_str, input_str)

    # 舊版明文比對相容
    if stored_str == input_str:
        # 平滑遷移：自動升級為雜湊值
        try:
            new_hash = hash_password(input_str)
            cursor.execute(f"UPDATE {table_name} SET {password_col} = %s WHERE id = %s", (new_hash, user_id))
        except Exception as e:
            print(f"[AUTH] 自動升級密碼雜湊失敗 ({table_name} id={user_id}): {e}")
        return True

    return False

def generate_token(user_id: int, username: str, role: str, expires_in_days: int = 1, extra_claims: dict = None) -> str:
    """簽發 JWT Access Token"""
    now = datetime.datetime.utcnow()
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'iat': now,
        'exp': now + datetime.timedelta(days=expires_in_days)
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def decode_token(token: str) -> dict:
    """解析並驗證 JWT Token"""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

def extract_token_from_request():
    """從請求標頭中提取 Bearer Token"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:].strip()
    return None

def jwt_required(roles=None):
    """
    JWT 認證中介層裝飾器
    - roles: None 表示任何有效登入角色皆可；或指定允許的角色清單，如 ['admin'], ['admin', 'desk']
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            token = extract_token_from_request()
            if not token:
                return {'error': '未提供身分驗證憑證 (Token)，請先登入', 'code': 'UNAUTHORIZED'}, 401

            try:
                payload = decode_token(token)
            except jwt.ExpiredSignatureError:
                return {'error': '登入憑證已過期，請重新登入', 'code': 'TOKEN_EXPIRED'}, 401
            except jwt.InvalidTokenError:
                return {'error': '無效的身分驗證憑證', 'code': 'INVALID_TOKEN'}, 401

            # 檢查角色權限
            if roles:
                user_role = payload.get('role')
                if user_role not in roles and 'admin' not in (user_role or ''):
                    return {'error': '權限不足，您的角色無權執行此操作', 'code': 'FORBIDDEN'}, 403

            # 將認證身分掛載到 request 上供後續函式使用
            request.current_user = payload
            return fn(*args, **kwargs)
        return wrapper
    return decorator
