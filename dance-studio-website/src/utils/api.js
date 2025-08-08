// API 配置 - 動態檢測環境並設置正確的 API 基礎 URL
const getApiBaseUrl = () => {
  // 如果是本地開發環境
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8001/api';
  }
  
  // 如果是外網訪問，使用相同的 protocol 和 hostname，但端口改為 8001
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  
  // 如果是 HTTPS，需要通過代理訪問 API（假設您已設置 Nginx 代理）
  if (protocol === 'https:') {
    return `${protocol}//${hostname}/api`;
  }
  
  // 如果是 HTTP，直接使用 8001 端口
  return `${protocol}//${hostname}:8001/api`;
};

export const API_BASE_URL = getApiBaseUrl();

// 常用的 API 端點
export const API_ENDPOINTS = {
  TEACHERS: `${API_BASE_URL}/teachers`,
  STUDENTS: `${API_BASE_URL}/students`,
  STYLES: `${API_BASE_URL}/styles`,
  ROOMS: `${API_BASE_URL}/rooms`,
  COURSES: `${API_BASE_URL}/courses`,
  SCHEDULES: `${API_BASE_URL}/schedules`,
  ENROLLMENTS: `${API_BASE_URL}/enrollments`
};

// 工具函數：構建完整的 API URL
export const buildApiUrl = (endpoint) => {
  // 移除開頭的 /api 如果存在，因為 API_BASE_URL 已經包含了
  const cleanEndpoint = endpoint.replace(/^\/api/, '');
  if (cleanEndpoint.startsWith('/')) {
    return `${API_BASE_URL}${cleanEndpoint}`;
  }
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

console.log('API 配置:', {
  hostname: window.location.hostname,
  protocol: window.location.protocol,
  apiBaseUrl: API_BASE_URL
});
