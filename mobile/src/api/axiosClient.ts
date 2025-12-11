// src/api/axiosClient.ts

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// --- CẤU HÌNH ĐỊA CHỈ SERVER ---
// Hãy chọn dòng phù hợp với môi trường của bạn và bỏ comment:

// 1. Cho máy ảo Android (Emulator)
const BASE_URL = 'http://192.168.1.126:8000/api/v1/';

// 2. Cho máy ảo iOS (Simulator)
// const BASE_URL = 'http://127.0.0.1:8000/api/v1/';

// 3. Cho điện thoại thật (Thay XXX bằng IP LAN máy tính của bạn)
// const BASE_URL = 'http://192.168.1.XXX:8000/api/v1/';

const axiosClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Timeout sau 10 giây nếu mạng lag
  timeout: 10000, 
});

// --- INTERCEPTOR REQUEST: Gửi kèm Token ---
// Mỗi khi gọi API, tự động lấy Token từ bộ nhớ và gắn vào Header
axiosClient.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('userToken');
  if (token) {
    // Django yêu cầu format: "Bearer <token>" (hoặc "Token <token>" tùy config, mặc định JWT là Bearer)
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// --- INTERCEPTOR RESPONSE: Xử lý lỗi chung ---
axiosClient.interceptors.response.use(
  (response) => {
    // Trả về dữ liệu sạch (response.data) giúp code gọn hơn
    return response;
  },
  (error) => {
    if (error.response) {
      // Lỗi từ Server trả về (4xx, 5xx)
      console.log('API Error Status:', error.response.status);
      console.log('API Error Data:', error.response.data);
      
      if (error.response.status === 401) {
        // Token hết hạn hoặc không hợp lệ -> Có thể xử lý logout tự động ở đây
        console.log('Token hết hạn, cần đăng nhập lại');
      }
    } else if (error.request) {
      // Lỗi không nhận được phản hồi (Mất mạng, Server sập)
      console.log('Network Error:', error.request);
    } else {
      console.log('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default axiosClient;