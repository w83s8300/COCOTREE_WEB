# Nginx Proxy Manager 配置指南

## 問題說明
當通過HTTPS訪問 https://w83s8300.ddns.net/ 時，前端嘗試調用 http://localhost:8001 的API會被瀏覽器阻擋（Mixed Content問題）。

## 解決方案

### 1. 在 Nginx Proxy Manager 中設置API代理

登入您的 Nginx Proxy Manager 管理界面，為 w83s8300.ddns.net 添加以下自定義配置：

```nginx
# 在 Advanced 頁籤的 Custom Nginx Configuration 中添加：

location /api/ {
    proxy_pass http://您的伺服器IP:8001/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # CORS 設定
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
    
    # 處理 OPTIONS 請求
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

### 2. 替代方案：使用 Docker 內部網絡

如果上述方法不行，可以將後端加入到 nginx-proxy-manager 的 Docker 網絡中：

```bash
# 1. 找到 nginx-proxy-manager 的網絡名稱
docker network ls

# 2. 將後端容器加入該網絡
docker network connect nginx-proxy-manager-zh_default docker_dance-studio-main-backend-1
```

然後在 Nginx Proxy Manager 配置中使用容器名稱：

```nginx
location /api/ {
    proxy_pass http://docker_dance-studio-main-backend-1:8001/api/;
    # ... 其他配置同上
}
```

### 3. 檢查配置是否生效

配置完成後，前端會自動檢測環境並使用正確的API URL：
- 開發環境（localhost）：使用 http://localhost:8001
- 生產環境（HTTPS）：使用 https://w83s8300.ddns.net/api

### 4. 測試方法

在瀏覽器控制台中檢查：
1. 打開 https://w83s8300.ddns.net/
2. 按 F12 開啟開發者工具
3. 在 Console 中查看 "API Base URL:" 的輸出
4. 在 Network 標籤中確認API請求是否成功
