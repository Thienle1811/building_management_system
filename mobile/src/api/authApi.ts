// src/api/authApi.ts
import axiosClient from './axiosClient';

const authApi = {
  login: (username: string, password: string) => {
    // Gửi user/pass lên server để lấy Token
    return axiosClient.post('token/', {
      username,
      password,
    });
  },
};

export default authApi;