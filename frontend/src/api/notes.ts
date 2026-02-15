import api from '../utils/api';
import { Note, ApiResponse } from '../types';

export const notesApi = {
  create: async (projectId: string, title: string, content: string) => {
    const response = await api.post<ApiResponse<Note>>(
      `/notes/?project_id=${projectId}`,
      { title, content }
    );
    return response.data;
  },

  list: async (projectId: string) => {
    const response = await api.get<ApiResponse<Note[]>>(`/notes/?project_id=${projectId}`);
    return response.data;
  },

  get: async (projectId: string, noteId: string) => {
    const response = await api.get<ApiResponse<Note>>(
      `/notes/${noteId}?project_id=${projectId}`
    );
    return response.data;
  },

  update: async (projectId: string, noteId: string, data: { title?: string; content?: string }) => {
    const response = await api.put<ApiResponse<Note>>(
      `/notes/${noteId}?project_id=${projectId}`,
      data
    );
    return response.data;
  },

  generateShareLink: async (projectId: string, noteId: string, accessLevel: 'view' | 'edit' = 'view') => {
    const response = await api.post<ApiResponse<{ share_url: string; share_token: string; access_level: string }>>(
      `/notes/${noteId}/share?project_id=${projectId}&access_level=${accessLevel}`
    );
    return response.data;
  },

  revokeShareLink: async (projectId: string, noteId: string) => {
    const response = await api.delete<ApiResponse<{ message: string }>>(
      `/notes/${noteId}/share?project_id=${projectId}`
    );
    return response.data;
  },

  getSharedNote: async (shareToken: string) => {
    const response = await api.get<ApiResponse<Note>>(`/notes/shared/${shareToken}`);
    return response.data;
  },

  updateSharedNote: async (shareToken: string, content: string) => {
    const response = await api.put<ApiResponse<Note>>(
      `/notes/shared/${shareToken}`,
      { content }
    );
    return response.data;
  },
};
