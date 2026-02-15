import api from '../utils/api';
import { Organization, ApiResponse } from '../types';

export const organizationsApi = {
  create: async (name: string) => {
    const response = await api.post<ApiResponse<Organization>>('/organizations/', { name });
    return response.data;
  },

  list: async () => {
    const response = await api.get<ApiResponse<Organization[]>>('/organizations/');
    return response.data;
  },

  switch: async (orgId: string) => {
    const response = await api.post<ApiResponse<{ access_token: string; token_type: string }>>(
      `/organizations/${orgId}/switch`
    );
    return response.data;
  },

  generateInvite: async (orgId: string) => {
    const response = await api.post<ApiResponse<{ invite_token: string }>>(
      `/organizations/${orgId}/invite`
    );
    return response.data;
  },

  joinOrganization: async (inviteToken: string) => {
    const response = await api.post<ApiResponse<{ message: string; organization_id: string }>>(
      '/organizations/join',
      { invite_token: inviteToken }
    );
    return response.data;
  },
};
