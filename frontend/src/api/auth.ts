import apiClient from './client';
import type { UserCreate, UserLogin, UserResponse } from '../types';

export const authApi = {
  register: (data: UserCreate) =>
    apiClient.post<UserResponse>('/auth/register', data),

  login: (data: UserLogin) =>
    apiClient.post<{ message: string; access_token: string; token_type: string }>('/auth/login', data),

  logout: () =>
    apiClient.post<{ message: string }>('/auth/logout'),

  getMe: () =>
    apiClient.get<UserResponse>('/auth/me'),
};

export async function listUsers(): Promise<UserResponse[]> {
  const { data } = await apiClient.get<UserResponse[]>('/users');
  return data;
}
