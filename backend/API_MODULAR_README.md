# 舞蹈工作室管理系統 - 模組化架構

## 📁 專案結構

```
backend/
├── app.py                 # 原始單一檔案 (保留作為備份)
├── app_modular.py         # 新的模組化主應用
├── api/                   # API 模組目錄
│   ├── __init__.py        # 模組初始化
│   ├── database.py        # 資料庫連接和配置
│   ├── students.py        # 學生管理 API
│   ├── teachers.py        # 老師管理 API
│   ├── courses.py         # 課程管理 API
│   ├── schedules.py       # 排程管理 API
│   ├── styles.py          # 風格管理 API
│   ├── rooms.py           # 教室管理 API
│   └── enrollments.py     # 報名管理 API
├── requirements.txt       # Python 套件依賴
└── Dockerfile            # Docker 容器配置
```

## 🔧 模組說明

### 1. 資料庫模組 (`api/database.py`)
- 資料庫連接配置
- 連接重試機制
- 資料庫表格初始化
- 共用資料庫工具函數

### 2. 學生管理 (`api/students.py`)
- `Students` - 獲取學生列表、新增學生
- `Student` - 單一學生的查詢、更新、刪除

### 3. 老師管理 (`api/teachers.py`)
- `Teachers` - 獲取老師列表、新增老師
- `Teacher` - 單一老師的查詢、更新、刪除

### 4. 課程管理 (`api/courses.py`)
- `Courses` - 獲取課程列表、新增課程
- `Course` - 單一課程的查詢、更新、刪除

### 5. 排程管理 (`api/schedules.py`)
- `CourseSchedules` - 獲取排程列表、新增排程
- `CourseSchedule` - 單一排程的查詢、更新、刪除

### 6. 風格管理 (`api/styles.py`)
- `Styles` - 獲取風格列表、新增風格
- `Style` - 單一風格的查詢、更新、刪除

### 7. 教室管理 (`api/rooms.py`)
- `Rooms` - 獲取教室列表、新增教室
- `Room` - 單一教室的查詢、更新、刪除

### 8. 報名管理 (`api/enrollments.py`)
- `Enrollment` - 課程報名
- `ScheduleEnrollments` - 特定排程的報名記錄
- `EnrollmentDetail` - 報名詳情、狀態更新、刪除

## 🚀 使用方式

### 方式一：使用新的模組化版本 (推薦)
1. 修改 `Dockerfile` 中的啟動命令：
   ```dockerfile
   CMD ["python", "app_modular.py"]
   ```

2. 重建容器：
   ```bash
   docker-compose up --build backend
   ```

### 方式二：保持原有版本
- 繼續使用 `app.py`，無需任何更改

## 📋 API 端點

所有 API 端點保持不變，只是代碼結構更加模組化：

### 學生管理
- `GET /api/students` - 獲取學生列表
- `POST /api/students` - 新增學生
- `GET /api/students/{id}` - 獲取單一學生
- `PUT /api/students/{id}` - 更新學生
- `DELETE /api/students/{id}` - 刪除學生

### 老師管理
- `GET /api/teachers` - 獲取老師列表
- `POST /api/teachers` - 新增老師
- `GET /api/teachers/{id}` - 獲取單一老師
- `PUT /api/teachers/{id}` - 更新老師
- `DELETE /api/teachers/{id}` - 刪除老師

### 課程管理
- `GET /api/courses` - 獲取課程列表
- `POST /api/courses` - 新增課程
- `GET /api/courses/{id}` - 獲取單一課程
- `PUT /api/courses/{id}` - 更新課程
- `DELETE /api/courses/{id}` - 刪除課程

### 排程管理
- `GET /api/schedules` - 獲取排程列表
- `POST /api/schedules` - 新增排程
- `GET /api/schedules/{id}` - 獲取單一排程
- `PUT /api/schedules/{id}` - 更新排程
- `DELETE /api/schedules/{id}` - 刪除排程

### 風格管理
- `GET /api/styles` - 獲取風格列表
- `POST /api/styles` - 新增風格
- `GET /api/styles/{id}` - 獲取單一風格
- `PUT /api/styles/{id}` - 更新風格
- `DELETE /api/styles/{id}` - 刪除風格

### 教室管理
- `GET /api/rooms` - 獲取教室列表
- `POST /api/rooms` - 新增教室
- `GET /api/rooms/{id}` - 獲取單一教室
- `PUT /api/rooms/{id}` - 更新教室
- `DELETE /api/rooms/{id}` - 刪除教室

### 報名管理
- `POST /api/enrollment` - 課程報名
- `GET /api/schedules/{id}/enrollments` - 獲取排程報名記錄
- `GET /api/enrollments/{id}` - 獲取報名詳情
- `PUT /api/enrollments/{id}` - 更新報名狀態
- `DELETE /api/enrollments/{id}` - 刪除報名記錄

## ✅ 模組化的優點

1. **程式碼組織清晰**：每個功能模組獨立，易於理解和維護
2. **可擴展性好**：新增功能時只需新增對應模組
3. **錯誤隔離**：單一模組的問題不會影響其他功能
4. **團隊協作**：不同開發者可以負責不同模組
5. **測試友好**：可以針對單一模組進行單元測試
6. **重用性強**：模組可以在其他專案中重用

## 🔄 遷移建議

1. **測試新版本**：先在開發環境測試模組化版本
2. **逐步遷移**：確認功能正常後再部署到生產環境
3. **保留備份**：原始 `app.py` 保留作為備份
4. **文檔更新**：更新部署文檔和開發指南

## 📝 開發指南

### 新增功能模組
1. 在 `api/` 目錄下創建新的 `.py` 文件
2. 定義相關的 Resource 類別
3. 在 `app_modular.py` 中導入並註冊路由

### 資料庫操作
- 使用 `from api.database import get_db_connection`
- 遵循現有的錯誤處理模式
- 記得在 finally 區塊中關閉連接

### 錯誤處理
- 統一的錯誤回應格式
- 適當的 HTTP 狀態碼
- 詳細的錯誤日誌記錄
