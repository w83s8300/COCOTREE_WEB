# Vue Views 檔案手動移動指南

## 🎯 目標

將 `src/views/` 目錄下的檔案按功能分類移動到子資料夾中，提高程式碼組織性。

## 📁 移動清單

### 1. 管理功能檔案 → `management/`

**已創建目錄：** `src/views/management/`

**需要移動的檔案：**
- `Students.vue` → `management/Students.vue`
- `Teachers.vue` → `management/Teachers.vue`
- `Courses.vue` → `management/Courses.vue`
- `Rooms.vue` → `management/Rooms.vue`
- `Styles.vue` → `management/Styles.vue`
- `Schedules.vue` → `management/Schedules.vue`
- `EnrollmentAdmin.vue` → `management/EnrollmentAdmin.vue`
- ✅ `Admin.vue` → `management/Admin.vue` (已完成)

### 2. 表單檔案 → `forms/`

**已創建目錄：** `src/views/forms/`

**需要移動的檔案：**
- `AddStudent.vue` → `forms/AddStudent.vue`
- `AddTeacher.vue` → `forms/AddTeacher.vue`
- `AddCourse.vue` → `forms/AddCourse.vue`
- `AddRoom.vue` → `forms/AddRoom.vue`
- `AddStyle.vue` → `forms/AddStyle.vue`
- `AddSchedule.vue` → `forms/AddSchedule.vue`

### 3. 公開頁面 → `public/`

**已創建目錄：** `src/views/public/`

**需要移動的檔案：**
- `Home.vue` → `public/Home.vue`
- `About.vue` → `public/About.vue`
- `Contact.vue` → `public/Contact.vue`
- `Gallery.vue` → `public/Gallery.vue`
- `History.vue` → `public/History.vue`
- `Faq.vue` → `public/Faq.vue`
- `Pricing.vue` → `public/Pricing.vue`
- `Venue.vue` → `public/Venue.vue`
- `Instructors.vue` → `public/Instructors.vue`

### 4. 學生功能 → `student/`

**已創建目錄：** `src/views/student/`

**需要移動的檔案：**
- `Schedule.vue` → `student/Schedule.vue`

## 📋 手動移動步驟

### 方法 1：使用 Windows 檔案總管
1. 開啟 `c:\Docker_dance-studio-main\dance-studio-website\src\views\`
2. 選取要移動的檔案（例如 `Students.vue`）
3. 剪下檔案 (Ctrl+X)
4. 進入對應的子資料夾（例如 `management`）
5. 貼上檔案 (Ctrl+V)

### 方法 2：使用命令列
```powershell
cd "c:\Docker_dance-studio-main\dance-studio-website\src\views"

# 移動管理檔案
move "Students.vue" "management\"
move "Teachers.vue" "management\"
move "Courses.vue" "management\"
move "Rooms.vue" "management\"
move "Styles.vue" "management\"
move "Schedules.vue" "management\"
move "EnrollmentAdmin.vue" "management\"

# 移動表單檔案
move "AddStudent.vue" "forms\"
move "AddTeacher.vue" "forms\"
move "AddCourse.vue" "forms\"
move "AddRoom.vue" "forms\"
move "AddStyle.vue" "forms\"
move "AddSchedule.vue" "forms\"

# 移動公開頁面
move "Home.vue" "public\"
move "About.vue" "public\"
move "Contact.vue" "public\"
move "Gallery.vue" "public\"
move "History.vue" "public\"
move "Faq.vue" "public\"
move "Pricing.vue" "public\"
move "Venue.vue" "public\"
move "Instructors.vue" "public\"

# 移動學生功能
move "Schedule.vue" "student\"
```

## 🔧 配置更新

### 1. 更新路由配置

將 `src/router/index_modular.js` 重命名為 `src/router/index.js`，或者複製內容到現有的 `index.js` 中。

### 2. 更新組件導入路徑

**需要更新的檔案：**

- `management/Students.vue` 中的導入：
  ```javascript
  // 將
  import AddStudent from './AddStudent.vue';
  // 改為
  import AddStudent from '../forms/AddStudent.vue';
  ```

- `management/Teachers.vue` 中的導入：
  ```javascript
  // 將
  import AddTeacher from './AddTeacher.vue';
  // 改為
  import AddTeacher from '../forms/AddTeacher.vue';
  ```

- 其他管理頁面的類似導入也需要相應更新

## ✅ 檢查清單

移動完成後，請檢查以下項目：

- [ ] 所有檔案都移動到正確的資料夾
- [ ] 路由配置已更新
- [ ] 組件導入路徑已修正
- [ ] 重建前端容器測試
- [ ] 所有頁面能正常存取
- [ ] 管理功能正常工作
- [ ] 表單功能正常工作

## 🚀 測試步驟

1. **移動檔案後重建容器：**
   ```bash
   cd c:\Docker_dance-studio-main
   docker-compose up --build -d dance-studio-website
   ```

2. **測試主要功能：**
   - 存取首頁：`http://localhost:3000/`
   - 存取管理頁面：`http://localhost:3000/admin`
   - 測試學生列表：`http://localhost:3000/admin/students`
   - 測試新增學生：點擊新增學生按鈕

3. **檢查控制台錯誤：**
   - 開啟瀏覽器開發者工具
   - 查看是否有模組載入錯誤

## 📝 備註

- 移動檔案前建議先備份整個專案
- 如果遇到錯誤，可以先移動部分檔案測試
- 所有模組化後的 API 功能不受影響
- 檔案移動完成後，整個專案結構將更加清晰易維護
