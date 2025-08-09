# Vue Views 模組化狀態檢查腳本

$viewsPath = "c:\Docker_dance-studio-main\dance-studio-website\src\views"

Write-Host "=== Vue Views 模組化狀態檢查 ===" -ForegroundColor Green
Write-Host ""

# 檢查資料夾是否存在
$folders = @("management", "forms", "public", "student")
foreach ($folder in $folders) {
    $folderPath = Join-Path $viewsPath $folder
    if (Test-Path $folderPath) {
        Write-Host "✅ 資料夾 $folder/ 存在" -ForegroundColor Green
        $files = Get-ChildItem $folderPath -Filter "*.vue"
        Write-Host "   包含 $($files.Count) 個 Vue 檔案" -ForegroundColor Gray
        foreach ($file in $files) {
            Write-Host "   - $($file.Name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ 資料夾 $folder/ 不存在" -ForegroundColor Red
    }
    Write-Host ""
}

# 檢查根目錄剩餘檔案
Write-Host "📁 根目錄剩餘 Vue 檔案：" -ForegroundColor Yellow
$rootFiles = Get-ChildItem $viewsPath -Filter "*.vue"
if ($rootFiles.Count -gt 0) {
    foreach ($file in $rootFiles) {
        Write-Host "   - $($file.Name)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   沒有剩餘檔案（完全模組化）" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== 檢查完成 ===" -ForegroundColor Green
