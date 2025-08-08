# 外網HTTPS訪問API問題解決方案

## 問題診斷

您遇到的問題是典型的 **Mixed Content** 問題：
- 網站通過 HTTPS (https://w83s8300.ddns.net/) 訪問
- 但前端代碼嘗試調用 HTTP 的本地API (http://localhost:8001)
- 瀏覽器出於安全考慮會阻止 HTTPS 頁面調用 HTTP API

## 解決方案

### 步驟1：在 Nginx Proxy Manager 中設置 API 代理

1. 登入您的 Nginx Proxy Manager 管理界面
2. 找到您的 `w83s8300.ddns.net` 代理配置
3. 點擊編輯，進入 "Advanced" 標籤
4. 在 "Custom Nginx Configuration" 中添加以下配置：

```nginx
# API 代理配置
location /api/ {
    # 替換為您的實際伺服器IP，例如：http://192.168.1.100:8001/api/
    proxy_pass http://您的伺服器IP:8001/api/;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 超時設置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # CORS 設定（允許跨域請求）
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
    
    # 處理 OPTIONS 預檢請求
    if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
        add_header 'Access-Control-Max-Age' 1728000;
        add_header 'Content-Type' 'text/plain; charset=utf-8';
        add_header 'Content-Length' 0;
        return 204;
    }
}
```

**重要：** 請將 `您的伺服器IP` 替換為您實際的伺服器IP地址。

### 步驟2：更新前端代碼（已提供配置文件）

我已經為您創建了 `src/config/api.js` 文件，它會根據訪問環境自動選擇正確的API URL：

- 本地開發：`http://localhost:8001`
- 外網HTTPS：`https://w83s8300.ddns.net/api`

### 步驟3：重新部署前端

```bash
# 重啟前端容器以載入新配置
docker-compose restart dance-studio-website
```

### 步驟4：驗證配置

1. 訪問 https://w83s8300.ddns.net/
2. 按 F12 開啟瀏覽器開發者工具
3. 在 Console 標籤中查看是否有 "API Base URL:" 的輸出
4. 在 Network 標籤中檢查API請求是否成功

## 常見問題排除

### 1. 如何找到伺服器IP？
```bash
# 在您的伺服器上執行
ip addr show
# 或
hostname -I
```

### 2. 如果仍然無法連接
檢查防火牆設置，確保8001端口對內網開放：
```bash
# Ubuntu/Debian
sudo ufw allow 8001

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8001/tcp
sudo firewall-cmd --reload
```

### 3. 使用Docker內部網絡（替代方案）
如果上述方法不行，可以將後端加入nginx-proxy-manager的網絡：

```bash
# 1. 查看nginx-proxy-manager的網絡
docker network ls

# 2. 將後端容器加入該網絡（替換網絡名稱）
docker network connect nginx-proxy-manager-zh_default docker_dance-studio-main-backend-1
```

然後在Nginx配置中使用容器名稱：
```nginx
proxy_pass http://docker_dance-studio-main-backend-1:8001/api/;
```

## 測試命令

配置完成後，您可以直接測試API：
```bash
# 測試API是否可訪問
curl https://w83s8300.ddns.net/api/styles
```

如果返回JSON數據，說明配置成功！
