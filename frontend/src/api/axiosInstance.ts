import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

let accessToken: string | null = null;
let refreshPromise: Promise<string | null> | null = null;

export const tokenStore = {
  get: () => accessToken,
  set: (token: string | null) => {
    accessToken = token;
  },
};

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true,
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStore.get();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (error.response?.status !== 401 || !original || original._retry || original.url?.includes('/api/auth/refresh')) {
      return Promise.reject(error);
    }

    original._retry = true;
    refreshPromise ??= api.post('/api/auth/refresh').then((res) => {
      const token = res.data.access_token as string;
      tokenStore.set(token);
      return token;
    }).catch(() => {
      tokenStore.set(null);
      window.location.href = '/login';
      return null;
    }).finally(() => {
      refreshPromise = null;
    });

    const newToken = await refreshPromise;
    if (newToken) {
      original.headers.Authorization = `Bearer ${newToken}`;
      return api(original);
    }
    return Promise.reject(error);
  },
);
