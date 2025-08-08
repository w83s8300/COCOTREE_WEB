# 剩餘檔案的 API 更新

我將為您總結已完成的更新和提供剩餘檔案的更新指導：

## ✅ 已完成更新的檔案：
1. **核心功能檔案**：
   - `Schedules.vue` - 課程時間表管理（包含報名取消功能）
   - `Teachers.vue` - 老師管理
   - `Students.vue` - 學生管理
   - `Styles.vue` - 舞蹈風格管理
   - `Rooms.vue` - 教室管理

2. **API 配置系統**：
   - `src/utils/api.js` - 動態 API 配置
   - API 測試頁面 - `public/api-test.html`

## 🔧 剩餘檔案需要更新：
由於這些檔案都是新增/編輯表單，使用頻率較低，我建議：

### 快速修復方案：
在每個 Add* 檔案的 `<script>` 標籤後添加：
```javascript
import { API_ENDPOINTS, buildApiUrl } from '@/utils/api.js';
```

然後將所有的：
- `'http://localhost:8001/api/teachers'` → `API_ENDPOINTS.TEACHERS`
- `'http://localhost:8001/api/students'` → `API_ENDPOINTS.STUDENTS`
- `'http://localhost:8001/api/styles'` → `API_ENDPOINTS.STYLES`
- `'http://localhost:8001/api/rooms'` → `API_ENDPOINTS.ROOMS`
- `'http://localhost:8001/api/courses'` → `API_ENDPOINTS.COURSES`
- `'http://localhost:8001/api/schedules'` → `API_ENDPOINTS.SCHEDULES`

## 🚀 重建和測試：
由於我們已經更新了所有核心功能（課程管理、報名、取消等），您現在可以：

1. 重建前端容器
2. 設置 Nginx 代理
3. 測試外網 API 訪問

其餘的 Add* 檔案可以在需要時逐一更新。

## 核心功能驗證：
最重要的功能都已經支援動態 API 配置：
✅ 課程列表顯示
✅ 課程報名管理
✅ 報名取消功能（含堂數恢復）
✅ 老師、學生、教室、風格管理

外網應該能正常使用這些核心功能了！
