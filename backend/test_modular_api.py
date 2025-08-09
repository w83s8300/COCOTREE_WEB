"""
測試模組化 API 的功能
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_api_endpoint(endpoint, method="GET", data=None):
    """測試 API 端點"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"✓ {method} {endpoint} - 狀態碼: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  回應: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return response
    except Exception as e:
        print(f"✗ {method} {endpoint} - 錯誤: {e}")
        return None

def main():
    print("=== 舞蹈工作室模組化 API 測試 ===\n")
    
    # 測試基本端點
    print("1. 測試基本連接")
    test_api_endpoint("/")
    
    print("\n2. 測試學生 API")
    test_api_endpoint("/api/students")
    
    print("\n3. 測試老師 API") 
    test_api_endpoint("/api/teachers")
    
    print("\n4. 測試課程 API")
    test_api_endpoint("/api/courses")
    
    print("\n5. 測試排程 API")
    test_api_endpoint("/api/schedules")
    
    print("\n6. 測試風格 API")
    test_api_endpoint("/api/styles")
    
    print("\n7. 測試教室 API")
    test_api_endpoint("/api/rooms")
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    main()
