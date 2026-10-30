#!/bin/bash
set -e

DOMAIN="coconuttreedancestudio.ddns.net"

# 檢查是否有輸入 Email
if [ -z "$1" ]; then
    echo "使用方式: ./setup-ssl.sh 你的Email@example.com"
    exit 1
fi

EMAIL="$1"

echo "=========================================="
echo "正在為 ${DOMAIN} 申請 Let's Encrypt SSL 憑證..."
echo "聯絡 Email: ${EMAIL}"
echo "=========================================="

# 1. 建立憑證與驗證目錄
mkdir -p ./certbot/conf ./certbot/www

# 2. 透過 Certbot 容器驗證網域並下載憑證
docker compose -f docker-compose.prod.yml run --rm --entrypoint certbot certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  --email "${EMAIL}" \
  --agree-tos \
  --no-eff-email \
  -d "${DOMAIN}"

# 3. 將 Nginx 設定切換為 SSL 正式版
echo ">>> 憑證取得成功！切換 Nginx 設定為 HTTPS..."
cp ./dance-studio-website/nginx.ssl.conf ./dance-studio-website/nginx.conf

# 4. 重新載入 Nginx 設定
docker compose -f docker-compose.prod.yml exec dance-studio-website nginx -s reload

echo "=========================================="
echo "🎉 SSL 設定成功！您的網站已啟用 HTTPS："
echo "👉 https://${DOMAIN}"
echo "=========================================="
