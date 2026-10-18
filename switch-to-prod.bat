@echo off
chcp 65001 >nul
echo ========================================================
echo       切換到 Dance Studio 正式環境 [Production]
echo ========================================================
echo.
echo [1/3] 正在切換前端為正式模式容器...
docker stop dance-studio-website >nul 2>&1
docker rm dance-studio-website >nul 2>&1

echo.
echo [2/3] 建置並啟動正式模式 [Nginx (Port 3001)]...
docker-compose -f docker-compose.prod.yml up -d --build

if errorlevel 1 goto ERROR

echo.
echo [3/3] 等待前端與 API 服務就緒...
powershell -NoProfile -Command "$s = Get-Date; while (((Get-Date) - $s).TotalSeconds -lt 40) { try { $res = Invoke-WebRequest -Uri 'http://localhost:3001/api/courses' -UseBasicParsing -TimeoutSec 2; if ($res.StatusCode -eq 200) { Write-Host ' [OK]'; exit 0 } } catch {} Write-Host -NoNewline '.'; Start-Sleep -Seconds 1 }; Write-Host ' [逾時]'; exit 1"

if errorlevel 1 goto TIMEOUT_WARN

:SUCCESS
echo.
echo ========================================================
echo  [成功] 正式環境已就緒！
echo  - 前端服務：已打包編譯，高效能 Nginx 託管 [Port 3001]
echo  - 訪問網址：http://localhost:3001/admin/courses
echo ========================================================
goto END

:TIMEOUT_WARN
echo.
echo [提示] 服務啟動花費較長時間，請稍候片刻後重新整理網頁。
echo 訪問網址：http://localhost:3001/admin/courses
goto END

:ERROR
echo.
echo [錯誤] 啟動失敗，請檢查 Docker 服務是否正常運行。

:END
echo.
pause