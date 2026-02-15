import api from '../utils/api';
import { User, ApiResponse } from '../types';

export const authApi = {
  register: async (email: string, password: string, full_name: string) => {
    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);
    formData.append('full_name', full_name);

    const response = await api.post<ApiResponse<User>>('/auth/register', {
      email,
      password,
      full_name
    });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post<ApiResponse<{ access_token: string; token_type: string }>>(
      '/auth/login',
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    return response.data;
  },
};
