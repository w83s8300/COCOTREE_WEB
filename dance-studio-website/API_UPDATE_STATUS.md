# 需要更新的檔案列表（包含 localhost:8001 的 Vue 檔案）

## 已更新完成：
- ✅ Schedules.vue - 課程管理（已更新大部分 API 調用）
- ✅ Teachers.vue - 老師管理（已完全更新）  
- ✅ Students.vue - 學生管理（已完全更新）
- ✅ Styles.vue - 舞蹈風格管理（已完全更新）

## 待更新檔案：
- 🔧 Rooms.vue - 教室管理
- 🔧 Courses.vue - 課程管理  
- 🔧 AddTeacher.vue - 新增/編輯老師
- 🔧 AddStyle.vue - 新增/編輯舞蹈風格
- 🔧 AddStudent.vue - 新增/編輯學生
- 🔧 AddSchedule.vue - 新增/編輯課程時間表
- 🔧 AddRoom.vue - 新增/編輯教室
- 🔧 AddCourse.vue - 新增/編輯課程

## 更新模式：
每個檔案需要：
1. 添加 import { API_ENDPOINTS, buildApiUrl } from '@/utils/api.js';
2. 將 'http://localhost:8001/api/xxx' 替換為 API_ENDPOINTS.XXX
3. 將 `http://localhost:8001/api/xxx/${id}` 替換為 `${API_ENDPOINTS.XXX}/${id}`

## 優先級：
1. **高優先級**：AddSchedule.vue（課程新增功能）
2. **中優先級**：AddTeacher.vue, AddStudent.vue（基本 CRUD）
3. **低優先級**：其他 Add* 檔案
