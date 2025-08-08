#!/bin/bash

# API URL 更新腳本
# 這個腳本會將所有 Vue 文件中的 localhost:8001 API 調用替換為動態配置

# 要處理的文件列表
files=(
    "src/views/AddTeacher.vue"
    "src/views/Courses.vue"
    "src/views/Schedules.vue"
    "src/views/AddSchedule.vue"
    "src/views/AddCourse.vue"
    "src/views/Teachers.vue"
    "src/views/Styles.vue"
    "src/views/Students.vue"
    "src/views/Rooms.vue"
)

echo "開始更新 API URL..."

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "處理文件: $file"
        
        # 檢查是否已經導入 API_BASE_URL
        if ! grep -q "import.*API_BASE_URL.*from.*@/config/api" "$file"; then
            # 在 <script> 標籤後添加導入語句
            sed -i '/<script>/a import { API_BASE_URL } from '\''@/config/api'\'';' "$file"
        fi
        
        # 替換所有的 localhost:8001 為動態 API URL
        sed -i 's|http://localhost:8001/api|\${API_BASE_URL}/api|g' "$file"
        sed -i "s|'http://localhost:8001/api|\`\${API_BASE_URL}/api|g" "$file"
        sed -i 's|"http://localhost:8001/api|`${API_BASE_URL}/api|g' "$file"
        
        echo "完成: $file"
    else
        echo "跳過不存在的文件: $file"
    fi
done

echo "API URL 更新完成！"
echo ""
echo "下一步操作："
echo "1. 在 Nginx Proxy Manager 中配置 API 代理（參考 NGINX_PROXY_MANAGER_CONFIG.md）"
echo "2. 重新構建前端容器: docker-compose restart dance-studio-website"
echo "3. 測試外網訪問: https://w83s8300.ddns.net/"
