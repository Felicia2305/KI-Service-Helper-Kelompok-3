import client from './client';

export interface User {
  id: string;
  email: string;
  nama: string;
  nim_nip: string;
  role: string;
  is_active: boolean;
}

export const authApi = {
  async login(email: string, password: string): Promise<{ token: string; user: User }> {
    const form = new URLSearchParams({ username: email, password });
    const { data } = await client.post('/api/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    const { data: user } = await client.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    return { token: data.access_token, user };
  },

  async me(): Promise<User> {
    const { data } = await client.get('/api/auth/me');
    return data;
  },
};
