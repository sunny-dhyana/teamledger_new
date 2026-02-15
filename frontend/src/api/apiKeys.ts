import api from '../utils/api';
import { APIKey, ApiResponse } from '../types';

export const apiKeysApi = {
  create: async (name: string, scopes: string[]) => {
    const response = await api.post<ApiResponse<APIKey>>('/api-keys/', {
      name,
      scopes,
    });
    return response.data;
  },

  list: async () => {
    const response = await api.get<ApiResponse<APIKey[]>>('/api-keys/');
    return response.data;
  },

  revoke: async (keyId: string) => {
    const response = await api.delete<ApiResponse<APIKey>>(`/api-keys/${keyId}`);
    return response.data;
  },
};
