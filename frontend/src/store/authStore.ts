import { create } from 'zustand';
import { User, Organization } from '../types';

interface AuthState {
  token: string | null;
  user: User | null;
  currentOrg: Organization | null;
  organizations: Organization[];
  setAuth: (token: string, user: User) => void;
  setCurrentOrg: (org: Organization) => void;
  setOrganizations: (orgs: Organization[]) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null,
  currentOrg: localStorage.getItem('currentOrg') ? JSON.parse(localStorage.getItem('currentOrg')!) : null,
  organizations: [],
  setAuth: (token, user) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ token, user });
  },
  setCurrentOrg: (org) => {
    localStorage.setItem('currentOrg', JSON.stringify(org));
    set({ currentOrg: org });
  },
  setOrganizations: (orgs) => set({ organizations: orgs }),
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('currentOrg');
    set({ token: null, user: null, currentOrg: null, organizations: [] });
  },
}));
