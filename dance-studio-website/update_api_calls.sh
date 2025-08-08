#!/bin/bash

# 批量更新所有 Vue 文件中的 API 調用
# 這個腳本會將硬編碼的 localhost:8001 替換為動態 API 配置

echo "正在更新 Vue 文件中的 API 調用..."

# 要處理的文件列表
files=(
  "src/views/Teachers.vue"
  "src/views/Students.vue"
  "src/views/Styles.vue"
  "src/views/Rooms.vue"
  "src/views/Courses.vue"
  "src/views/AddTeacher.vue"
  "src/views/AddStudent.vue"
  "src/views/AddCourse.vue"
  "src/views/AddRoom.vue"
  "src/views/AddStyle.vue"
  "src/views/AddSchedule.vue"
)

# 對每個文件進行處理
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "處理文件: $file"
    
    # 1. 添加 API import（如果不存在）
    if ! grep -q "import.*utils/api" "$file"; then
      # 查找 import 區域並添加
      sed -i '/import.*from.*axios/a import { API_ENDPOINTS, buildApiUrl } from '\''@/utils/api.js'\'';' "$file"
    fi
    
    # 2. 替換常見的 API 端點
    sed -i 's|http://localhost:8001/api/teachers|API_ENDPOINTS.TEACHERS|g' "$file"
    sed -i 's|http://localhost:8001/api/students|API_ENDPOINTS.STUDENTS|g' "$file"
    sed -i 's|http://localhost:8001/api/styles|API_ENDPOINTS.STYLES|g' "$file"
    sed -i 's|http://localhost:8001/api/rooms|API_ENDPOINTS.ROOMS|g' "$file"
    sed -i 's|http://localhost:8001/api/courses|API_ENDPOINTS.COURSES|g' "$file"
    sed -i 's|http://localhost:8001/api/schedules|API_ENDPOINTS.SCHEDULES|g' "$file"
    
    # 3. 替換動態 API 調用（帶 ID 的）
    sed -i 's|`http://localhost:8001/api/teachers/${|`${API_ENDPOINTS.TEACHERS}/${|g' "$file"
    sed -i 's|`http://localhost:8001/api/students/${|`${API_ENDPOINTS.STUDENTS}/${|g' "$file"
    sed -i 's|`http://localhost:8001/api/styles/${|`${API_ENDPOINTS.STYLES}/${|g' "$file"
    sed -i 's|`http://localhost:8001/api/rooms/${|`${API_ENDPOINTS.ROOMS}/${|g' "$file"
    sed -i 's|`http://localhost:8001/api/courses/${|`${API_ENDPOINTS.COURSES}/${|g' "$file"
    sed -i 's|`http://localhost:8001/api/schedules/${|`${API_ENDPOINTS.SCHEDULES}/${|g' "$file"
    
    echo "✓ 完成: $file"
  else
    echo "✗ 文件不存在: $file"
  fi
done

echo "所有文件更新完成！"
