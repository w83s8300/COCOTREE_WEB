// API 配置文件
const isProduction = window.location.protocol === 'https:';
const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// 根據環境動態設置API基礎URL
export const API_BASE_URL = (() => {
  if (isDevelopment) {
    // 開發環境：使用localhost
    return 'http://localhost:8001';
  } else if (isProduction) {
    // 生產環境（HTTPS）：使用相同域名的/api路徑
    return `${window.location.protocol}//${window.location.host}/api`;
  } else {
    // HTTP生產環境：使用當前域名
    return `http://${window.location.host}/api`;
  }
})();

console.log('API Base URL:', API_BASE_URL);
