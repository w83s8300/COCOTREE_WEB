# 外網 API 訪問配置指南

## 問題描述
當從外網訪問您的舞蹈工作室網站時，前端無法訪問 API，因為瀏覽器會阻止 HTTPS 網站訪問 HTTP API（混合內容安全策略）。

## 解決方案

### 選項 1: 通過 Nginx Proxy Manager 設置 API 代理（推薦）

1. **在 Nginx Proxy Manager 中添加新的代理主機**
   - 域名：`w83s8300.ddns.net`
   - 協議：HTTPS
   - 正向主機：您的內網 IP
   - 正向端口：3001（前端端口）

2. **添加 API 代理路徑**
   在 Nginx Proxy Manager 中，為同一個域名添加一個位置規則：
   - 位置：`/api`
   - 代理傳遞到：`http://YOUR_INTERNAL_IP:8001/api`
   
   或者創建一個單獨的子域名：
   - 域名：`api.w83s8300.ddns.net`
   - 正向主機：您的內網 IP
   - 正向端口：8001

### 選項 2: 修改 Docker Compose 配置

在 docker-compose.yml 中添加 Nginx 反向代理：

```yaml
services:
  # ... 其他服務

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl  # SSL 證書目錄
    depends_on:
      - backend
      - dance-studio-website
    networks:
      - app-network
```

### 選項 3: 使用環境變數配置

在 docker-compose.yml 的前端服務中添加環境變數：

```yaml
dance-studio-website:
  build:
    context: ./dance-studio-website
  environment:
    - API_BASE_URL=https://w83s8300.ddns.net/api
  # ... 其他配置
```

## 當前實施的動態 API 配置

我已經為您創建了動態 API 配置系統：

### 1. API 配置文件 (`src/utils/api.js`)
- 自動檢測訪問環境（本地 vs 外網）
- 根據協議（HTTP/HTTPS）動態設置 API 基礎 URL
- 提供預定義的 API 端點

### 2. 配置邏輯
```javascript
// 本地開發：http://localhost:8001
// 外網 HTTP：http://w83s8300.ddns.net:8001  
// 外網 HTTPS：https://w83s8300.ddns.net/api
```

## 下一步操作

1. **設置 Nginx 代理**（推薦選項 1）
   - 在 Nginx Proxy Manager 中為 `/api` 路徑設置代理到 `http://YOUR_INTERNAL_IP:8001/api`

2. **重新構建前端容器**
   ```bash
   cd c:\Docker_dance-studio-main
   docker-compose up --build dance-studio-website
   ```

3. **測試 API 訪問**
   - 本地訪問：http://localhost:3001
   - 外網訪問：https://w83s8300.ddns.net

## 驗證步驟

1. 打開瀏覽器開發者工具（F12）
2. 查看 Console 輸出，應該會看到 API 配置信息
3. 查看 Network 標籤，確認 API 請求使用正確的 URL
4. 測試各種功能（老師列表、學生列表等）

## 故障排除

如果外網仍無法訪問 API：

1. 確認 Nginx Proxy Manager 中的代理設置
2. 檢查防火牆設置，確保 8001 端口開放
3. 查看瀏覽器 Console 是否有 CORS 錯誤
4. 確認 SSL 證書配置正確

## 聯絡支援

如果遇到問題，請提供：
- 瀏覽器 Console 錯誤信息
- Network 標籤中的失敗請求詳情
- Nginx Proxy Manager 配置截圖
