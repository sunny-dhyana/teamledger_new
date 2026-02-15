import api from '../utils/api';
import { Job, ApiResponse } from '../types';

export const jobsApi = {
  get: async (jobId: string) => {
    const response = await api.get<ApiResponse<Job>>(`/jobs/${jobId}`);
    return response.data;
  },
};
