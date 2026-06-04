import { api } from './axiosInstance';
import type { Role, User } from '../types';

export const authApi = {
  async login(email: string, password: string): Promise<{ token: string; user: User }> {
    const form = new URLSearchParams({ username: email, password });
    const { data } = await api.post('/api/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    const { data: user } = await api.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    return { token: data.access_token, user };
  },

  async register(payload: { nama: string; email: string; password: string; nim_nip: string; role: Role }): Promise<User> {
    const { data } = await api.post('/api/auth/register', payload);
    return data;
  },

  async refresh(): Promise<string> {
    const { data } = await api.post('/api/auth/refresh');
    return data.access_token;
  },

  async logout(): Promise<void> {
    await api.post('/api/auth/logout');
  },

  async me(): Promise<User> {
    const { data } = await api.get('/api/auth/me');
    return data;
  },
};
