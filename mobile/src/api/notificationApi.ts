import axiosClient from './axiosClient';
import { Platform } from 'react-native'; // <--- Import quan trọng để lấy hệ điều hành

export interface Notification {
  id: number;
  title: string;
  body: string;
  notification_type: 'FEEDBACK_UPDATE' | 'SYSTEM';
  is_read: boolean;
  created_at: string;
  created_at_display: string;
}

const notificationApi = {
  // 1. Lấy danh sách thông báo
  getAll: () => {
    return axiosClient.get<Notification[]>('notifications/');
  },

  // 2. Đánh dấu tất cả là đã đọc
  markAllRead: () => {
    return axiosClient.post('notifications/mark-all-read/');
  },

  // 3. Đánh dấu 1 tin là đã đọc (khi bấm vào xem)
  markRead: (id: number) => {
    return axiosClient.post(`notifications/${id}/mark-read/`);
  },

  // 4. Đăng ký thiết bị nhận Push Notification (MỚI THÊM)
  registerDevice: (token: string) => {
    return axiosClient.post('notifications/register-device/', {
      expo_push_token: token,
      platform: Platform.OS, // Gửi kèm 'ios' hoặc 'android' để Server biết
    });
  },
};

export default notificationApi;