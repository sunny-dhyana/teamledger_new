export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  organization_id: string;
  name: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: string;
  project_id: string;
  organization_id: string;
  title: string;
  content: string;
  version: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  is_shared?: boolean;
  share_access_level?: 'view' | 'edit';
}

export interface APIKey {
  id: string;
  organization_id: string;
  name: string;
  key_prefix: string;
  scopes: string[];
  is_active: boolean;
  created_at: string;
  expires_at: string | null;
  key?: string; // Only returned on creation
}

export interface Job {
  id: string;
  organization_id: string;
  type: string;
  status: string;
  result_path: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
