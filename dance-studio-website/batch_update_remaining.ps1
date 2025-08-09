# 批量更新 Vue 檔案的 API 調用
# 這個腳本會更新所有剩餘的檔案

Write-Host "開始批量更新 Vue 檔案的 API 調用..." -ForegroundColor Green

# 更新函數
function Update-VueFile($filePath) {
    if (-not (Test-Path $filePath)) {
        Write-Host "檔案不存在: $filePath" -ForegroundColor Red
        return
    }

    Write-Host "更新檔案: $filePath" -ForegroundColor Yellow
    
    $content = Get-Content $filePath -Raw
    
    # 檢查是否已經有 API import
    if ($content -notmatch "import.*utils/api") {
        # 在 axios import 後添加 API import
        $content = $content -replace "(import axios from ['\`"]axios['\`"];)", "`$1`nimport { API_ENDPOINTS, buildApiUrl } from '@/utils/api.js';"
        Write-Host "  ✓ 添加了 API import" -ForegroundColor Green
    }
    
    # 記錄更新次數
    $updateCount = 0
    
    # 替換所有 API 調用
    $replacements = @{
        "http://localhost:8001/api/teachers" = "API_ENDPOINTS.TEACHERS"
        "http://localhost:8001/api/students" = "API_ENDPOINTS.STUDENTS"
        "http://localhost:8001/api/styles" = "API_ENDPOINTS.STYLES"
        "http://localhost:8001/api/rooms" = "API_ENDPOINTS.ROOMS"
        "http://localhost:8001/api/courses" = "API_ENDPOINTS.COURSES"
        "http://localhost:8001/api/schedules" = "API_ENDPOINTS.SCHEDULES"
        "http://localhost:8001/api/enrollments" = "API_ENDPOINTS.ENROLLMENTS"
    }
    
    foreach ($old in $replacements.Keys) {
        $new = $replacements[$old]
        if ($content -match [regex]::Escape($old)) {
            $content = $content -replace [regex]::Escape($old), $new
            $updateCount++
        }
    }
    
    # 替換動態 API 調用（帶 ID 的）
    $dynamicReplacements = @{
        "``http://localhost:8001/api/teachers/\$\{" = "``\$\{API_ENDPOINTS.TEACHERS}/\$\{"
        "``http://localhost:8001/api/students/\$\{" = "``\$\{API_ENDPOINTS.STUDENTS}/\$\{"
        "``http://localhost:8001/api/styles/\$\{" = "``\$\{API_ENDPOINTS.STYLES}/\$\{"
        "``http://localhost:8001/api/rooms/\$\{" = "``\$\{API_ENDPOINTS.ROOMS}/\$\{"
        "``http://localhost:8001/api/courses/\$\{" = "``\$\{API_ENDPOINTS.COURSES}/\$\{"
        "``http://localhost:8001/api/schedules/\$\{" = "``\$\{API_ENDPOINTS.SCHEDULES}/\$\{"
    }
    
    foreach ($old in $dynamicReplacements.Keys) {
        $new = $dynamicReplacements[$old]
        if ($content -match [regex]::Escape($old)) {
            $content = $content -replace [regex]::Escape($old), $new
            $updateCount++
        }
    }
    
    # 保存檔案
    Set-Content -Path $filePath -Value $content -Encoding UTF8
    Write-Host "  ✓ 更新了 $updateCount 個 API 調用" -ForegroundColor Green
}

# 要更新的檔案列表
$files = @(
    "src\views\AddStyle.vue",
    "src\views\AddStudent.vue", 
    "src\views\AddSchedule.vue",
    "src\views\AddRoom.vue",
    "src\views\AddCourse.vue"
)

# 更新所有檔案
foreach ($file in $files) {
    Update-VueFile $file
}

Write-Host "`n批量更新完成！" -ForegroundColor Green
Write-Host "請檢查更新結果並重建 Docker 容器。" -ForegroundColor Cyan
