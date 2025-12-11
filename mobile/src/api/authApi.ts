import axiosClient from './axiosClient';

const authApi = {
  login: (username: string, password: string) => {
    return axiosClient.post('token/', { username, password });
  },
  
  // Lấy thông tin cá nhân + Xe + Thành viên
  getProfile: () => {
    return axiosClient.get('residents/me/'); 
  },

  // Đổi mật khẩu
  changePassword: (data: any) => {
    return axiosClient.post('residents/change-password/', data);
  }
};

export default authApi;