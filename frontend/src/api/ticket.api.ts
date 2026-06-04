import { api } from './axiosInstance';
import type { IntegrityResult, ServiceType, Ticket } from '../types';

export const ticketApi = {
  async listMine(): Promise<Ticket[]> {
    const { data } = await api.get('/api/tickets/my');
    return data;
  },

  async listAll(status?: string): Promise<Ticket[]> {
    const { data } = await api.get('/api/tickets', { params: status && status !== 'all' ? { status } : {} });
    return data;
  },

  async get(ticketId: string): Promise<Ticket> {
    const { data } = await api.get(`/api/tickets/${ticketId}`);
    return data;
  },

  async create(payload: { serviceTypeId: string; purpose: string; notes?: string; file?: File | null }): Promise<Ticket> {
    const form = new FormData();
    form.append('service_type_id', payload.serviceTypeId);
    form.append('purpose', payload.purpose);
    if (payload.notes) form.append('notes', payload.notes);
    if (payload.file) form.append('file', payload.file);
    const { data } = await api.post('/api/tickets', form);
    return data;
  },

  async claim(ticketId: string): Promise<Ticket> {
    const { data } = await api.post(`/api/tickets/${ticketId}/claim`);
    return data;
  },

  async claimNext(): Promise<Ticket> {
    const { data } = await api.post('/api/tickets/claim');
    return data;
  },

  async approve(ticketId: string, notes?: string): Promise<Ticket> {
    const { data } = await api.patch(`/api/tickets/${ticketId}/approve`, { notes });
    return data;
  },

  async reject(ticketId: string, notes: string): Promise<Ticket> {
    const { data } = await api.patch(`/api/tickets/${ticketId}/reject`, { notes });
    return data;
  },

  async complete(ticketId: string, file?: File | null, notes?: string): Promise<Ticket> {
    const form = new FormData();
    if (file) form.append('file', file);
    if (notes) form.append('notes', notes);
    const { data } = await api.patch(`/api/tickets/${ticketId}/complete`, form);
    return data;
  },

  async download(ticketId: string, type: 'syarat' | 'hasil'): Promise<void> {
    const endpoint = type === 'syarat' ? `/api/tickets/${ticketId}/download-syarat` : `/api/tickets/${ticketId}/download`;
    const response = await api.get(endpoint, { responseType: 'blob' });
    const contentDisposition = response.headers['content-disposition'] as string | undefined;
    const filename = contentDisposition?.match(/filename="?([^"]+)"?/)?.[1] ?? `ticket-${ticketId}-${type}`;
    const url = URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  },

  async verify(ticketId: string): Promise<IntegrityResult> {
    const { data } = await api.get(`/api/tickets/${ticketId}/verify-integrity`);
    return data;
  },

  async services(): Promise<ServiceType[]> {
    const { data } = await api.get('/api/services');
    return data;
  },
};
