import api from '../utils/api';
import { Project, Job, ApiResponse } from '../types';

export const projectsApi = {
  create: async (name: string, description: string) => {
    const response = await api.post<ApiResponse<Project>>('/projects/', {
      name,
      description,
    });
    return response.data;
  },

  list: async () => {
    const response = await api.get<ApiResponse<Project[]>>('/projects/');
    return response.data;
  },

  get: async (projectId: string) => {
    const response = await api.get<ApiResponse<Project>>(`/projects/${projectId}`);
    return response.data;
  },

  update: async (projectId: string, data: { name?: string; description?: string; status?: string }) => {
    const response = await api.put<ApiResponse<Project>>(`/projects/${projectId}`, data);
    return response.data;
  },

  export: async (projectId: string) => {
    const response = await api.post<ApiResponse<Job>>(`/projects/${projectId}/export`);
    return response.data;
  },
};
