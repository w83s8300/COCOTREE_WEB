# API 修正狀態

## ✅ 已修正的檔案：
- Styles.vue - 完成
- Students.vue - 完成 (import 和主要方法)
- Teachers.vue - 完成 (import 和主要方法)
- Rooms.vue - import 已修正
- Courses.vue - import 已修正

## 📋 仍需修正的檔案：
- Rooms.vue - API 調用方法
- Courses.vue - API 調用方法  
- Schedules.vue - 全部需要修正

## 🔧 需要修正的模式：
1. 將 `axios.get(API_ENDPOINTS.XXX)` 改為 `apiService.get('xxx')`
2. 將 `response.data.xxx` 改為先 `response.json()` 再取 `data.xxx`
3. 移除 `import axios from 'axios'` 和 `import { API_ENDPOINTS, buildApiUrl }`
4. 添加 `import apiService from '@/utils/api'`

## 錯誤修正重點：
- 所有的 API 調用都需要先 `.json()` 才能取得數據
- 端點名稱要使用小寫，如 'students', 'teachers' 等
- 刪除調用同樣需要 `.json()` 處理
