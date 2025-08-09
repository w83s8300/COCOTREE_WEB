# 檔案移動腳本
$viewsPath = "c:\Docker_dance-studio-main\dance-studio-website\src\views"

# 檢查檔案是否存在
$studentsFile = Join-Path $viewsPath "Students.vue"
$managementDir = Join-Path $viewsPath "management"
$targetFile = Join-Path $managementDir "Students.vue"

if (Test-Path $studentsFile) {
    Write-Host "找到 Students.vue"
    
    # 讀取檔案內容
    $content = Get-Content $studentsFile -Raw -Encoding UTF8
    Write-Host "已讀取檔案內容，大小: $($content.Length) 字元"
    
    # 寫入新位置
    Set-Content -Path $targetFile -Value $content -Encoding UTF8
    Write-Host "已寫入 management/Students.vue"
    
    # 刪除原檔案
    Remove-Item $studentsFile
    Write-Host "已刪除原檔案"
    
    Write-Host "Students.vue 移動完成！"
} else {
    Write-Host "找不到 Students.vue 檔案"
}

# 檢查結果
Write-Host "`n檢查結果:"
Write-Host "原位置存在: $(Test-Path $studentsFile)"
Write-Host "新位置存在: $(Test-Path $targetFile)"
