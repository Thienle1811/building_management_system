// src/api/feedbackApi.ts
import axiosClient from './axiosClient';

// Định nghĩa kiểu dữ liệu (Interface) để TypeScript gợi ý code
export interface Feedback {
  id: number;
  code: string;
  title: string;
  description: string;
  status: 'PENDING' | 'PROCESSING' | 'DONE' | 'CANCELLED';
  status_display: string;
  category_name: string;
  created_at: string;
  attachments: { id: number; file_url: string; file_type: string }[];
}

export interface FeedbackCategory {
  id: number;
  name: string;
  code: string;
}

const feedbackApi = {
  // 1. Lấy danh sách phản hồi của tôi
  getMyFeedbacks: () => {
    return axiosClient.get<Feedback[]>('feedback/list/');
  },

  // 2. Lấy danh sách danh mục (để hiện dropdown khi tạo mới)
  getCategories: () => {
    return axiosClient.get<FeedbackCategory[]>('feedback/categories/');
  },

  // 3. Gửi phản hồi mới (Có upload ảnh)
  createFeedback: (title: string, description: string, categoryId: number, images: any[]) => {
    const formData = new FormData();
    
    formData.append('title', title);
    formData.append('description', description);
    formData.append('category', categoryId.toString());

    // Xử lý file đính kèm (React Native FormData)
    images.forEach((img, index) => {
      const file: any = {
        uri: img.uri,
        name: img.fileName || `photo_${index}.jpg`,
        type: img.type || 'image/jpeg',
      };
      formData.append('files', file); // 'files' phải khớp với Serializer ở Backend
    });

    return axiosClient.post('feedback/list/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data', // Quan trọng để upload file
      },
    });
  },
};

export default feedbackApi;