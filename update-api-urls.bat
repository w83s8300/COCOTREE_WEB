@echo off
echo 開始更新 API URL...

:: 設定要處理的檔案列表
set files=^
src\views\AddTeacher.vue ^
src\views\Courses.vue ^
src\views\Schedules.vue ^
src\views\AddSchedule.vue ^
src\views\AddCourse.vue ^
src\views\Teachers.vue ^
src\views\Styles.vue ^
src\views\Students.vue ^
src\views\Rooms.vue

cd dance-studio-website

for %%f in (%files%) do (
    if exist "%%f" (
        echo 處理檔案: %%f
        
        :: 使用 PowerShell 來處理檔案內容替換
        powershell -Command "(Get-Content '%%f') | ForEach-Object { $_ -replace 'http://localhost:8001', '${API_BASE_URL}' } | Set-Content '%%f'"
        
        echo 完成: %%f
    ) else (
        echo 跳過不存在的檔案: %%f
    )
)

cd ..

echo.
echo API URL 更新完成！
echo.
echo 下一步操作：
echo 1. 在 Nginx Proxy Manager 中配置 API 代理（參考 NGINX_PROXY_MANAGER_CONFIG.md）
echo 2. 重新構建前端容器: docker-compose restart dance-studio-website
echo 3. 測試外網訪問: https://w83s8300.ddns.net/
pause
