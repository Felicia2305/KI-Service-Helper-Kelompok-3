import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { authApi } from '../api/auth.api';
import { tokenStore } from '../api/axiosInstance';
import type { User } from '../types';

type RegisterPayload = {
  nama: string;
  email: string;
  password: string;
  nim_nip: string;
  role: User['role'];
};

type AuthContextType = {
  user: User | null;
  token: string | null;
  login: (email: string, pass: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  refreshSession: () => Promise<void>;
  logout: () => Promise<void>;
  statusMsg: string;
  booting: boolean;
  isAuthenticated: boolean;
};

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [statusMsg, setStatusMsg] = useState('');
  const [booting, setBooting] = useState(true);

  const applyToken = useCallback((nextToken: string | null) => {
    tokenStore.set(nextToken);
    setToken(nextToken);
  }, []);

  const login = useCallback(async (email: string, pass: string) => {
    setStatusMsg('Memproses autentikasi...');
    try {
      const { token: nextToken, user: nextUser } = await authApi.login(email, pass);
      applyToken(nextToken);
      setUser(nextUser);
      setStatusMsg('');
    } catch (err) {
      setStatusMsg('Invalid credentials');
      throw err;
    }
  }, [applyToken]);

  const register = useCallback(async (payload: RegisterPayload) => {
    await authApi.register(payload);
  }, []);

  const refreshSession = useCallback(async () => {
    const nextToken = await authApi.refresh();
    applyToken(nextToken);
    const nextUser = await authApi.me();
    setUser(nextUser);
  }, [applyToken]);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // Logout lokal tetap dilakukan jika server tidak tersedia.
    }
    setUser(null);
    applyToken(null);
    window.location.href = '/login';
  }, [applyToken]);

  useEffect(() => {
    void refreshSession().catch(() => undefined).finally(() => setBooting(false));
  }, [refreshSession]);

  useEffect(() => {
    if (!token) return undefined;
    const warning = window.setTimeout(() => {
      const shouldExtend = window.confirm('Sesi Anda akan berakhir dalam 2 menit. Perpanjang?');
      if (shouldExtend) void refreshSession();
    }, Math.max(0, (30 - 2) * 60 * 1000));
    return () => window.clearTimeout(warning);
  }, [refreshSession, token]);

  const value = useMemo(() => ({
    user,
    token,
    login,
    register,
    refreshSession,
    logout,
    statusMsg,
    booting,
    isAuthenticated: Boolean(user && token),
  }), [booting, login, logout, refreshSession, register, statusMsg, token, user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
