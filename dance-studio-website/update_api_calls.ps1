# PowerShell 腳本：批量更新 Vue 文件中的 API 調用
# 將硬編碼的 localhost:8001 替換為動態 API 配置

Write-Host "正在更新 Vue 文件中的 API 調用..." -ForegroundColor Green

# 要處理的文件列表
$files = @(
    "src\views\Teachers.vue",
    "src\views\Students.vue", 
    "src\views\Styles.vue",
    "src\views\Rooms.vue",
    "src\views\Courses.vue",
    "src\views\AddTeacher.vue",
    "src\views\AddStudent.vue",
    "src\views\AddCourse.vue",
    "src\views\AddRoom.vue",
    "src\views\AddStyle.vue",
    "src\views\AddSchedule.vue"
)

# 對每個文件進行處理
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "處理文件: $file" -ForegroundColor Yellow
        
        $content = Get-Content $file -Raw
        
        # 1. 添加 API import（如果不存在）
        if ($content -notmatch "import.*utils/api") {
            $content = $content -replace "(import.*from.*['\`"]axios['\`"];)", "`$1`nimport { API_ENDPOINTS, buildApiUrl } from '@/utils/api.js';"
        }
        
        # 2. 替換常見的 API 端點
        $content = $content -replace "http://localhost:8001/api/teachers", "API_ENDPOINTS.TEACHERS"
        $content = $content -replace "http://localhost:8001/api/students", "API_ENDPOINTS.STUDENTS"
        $content = $content -replace "http://localhost:8001/api/styles", "API_ENDPOINTS.STYLES"
        $content = $content -replace "http://localhost:8001/api/rooms", "API_ENDPOINTS.ROOMS"
        $content = $content -replace "http://localhost:8001/api/courses", "API_ENDPOINTS.COURSES"
        $content = $content -replace "http://localhost:8001/api/schedules", "API_ENDPOINTS.SCHEDULES"
        
        # 3. 替換動態 API 調用（帶 ID 的）
        $content = $content -replace "``http://localhost:8001/api/teachers/\$\{", "``\$\{API_ENDPOINTS.TEACHERS}/\$\{"
        $content = $content -replace "``http://localhost:8001/api/students/\$\{", "``\$\{API_ENDPOINTS.STUDENTS}/\$\{"
        $content = $content -replace "``http://localhost:8001/api/styles/\$\{", "``\$\{API_ENDPOINTS.STYLES}/\$\{"
        $content = $content -replace "``http://localhost:8001/api/rooms/\$\{", "``\$\{API_ENDPOINTS.ROOMS}/\$\{"
        $content = $content -replace "``http://localhost:8001/api/courses/\$\{", "``\$\{API_ENDPOINTS.COURSES}/\$\{"
        $content = $content -replace "``http://localhost:8001/api/schedules/\$\{", "``\$\{API_ENDPOINTS.SCHEDULES}/\$\{"
        
        # 保存更新後的內容
        Set-Content -Path $file -Value $content -Encoding UTF8
        
        Write-Host "✓ 完成: $file" -ForegroundColor Green
    } else {
        Write-Host "✗ 文件不存在: $file" -ForegroundColor Red
    }
}

Write-Host "所有文件更新完成！" -ForegroundColor Green
