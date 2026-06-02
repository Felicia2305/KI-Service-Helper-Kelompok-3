import client from './client';
import { mapTicket, STATUS_TO_BACKEND } from './mappers';

export const ticketsApi = {
  async myTickets() {
    const { data } = await client.get('/api/tickets/my');
    return data.map(mapTicket);
  },

  async allTickets(statusFilter?: string) {
    const params: Record<string, string> = {};
    if (statusFilter && statusFilter !== 'semua') {
      params.status = STATUS_TO_BACKEND[statusFilter] ?? statusFilter;
    }
    const { data } = await client.get('/api/tickets', { params });
    return data.map(mapTicket);
  },

  async getById(id: string) {
    const { data } = await client.get(`/api/tickets/${id}`);
    return mapTicket(data);
  },

  async submit(serviceTypeId: string, purpose: string, file: File | null) {
    const form = new FormData();
    form.append('service_type_id', serviceTypeId);
    form.append('purpose', purpose);
    if (file) form.append('file', file);
    const { data } = await client.post('/api/tickets', form);
    return mapTicket(data);
  },

  async claimNext() {
    const { data } = await client.post('/api/tickets/claim');
    return mapTicket(data);
  },

  async claimSpecific(ticketId: string) {
    const { data } = await client.post(`/api/tickets/${ticketId}/claim`);
    return mapTicket(data);
  },

  async approve(ticketId: string, catatanTu?: string) {
    const { data } = await client.patch(`/api/tickets/${ticketId}/approve`, { catatan_tu: catatanTu });
    return mapTicket(data);
  },

  async reject(ticketId: string, catatanTu: string) {
    const { data } = await client.patch(`/api/tickets/${ticketId}/reject`, { catatan_tu: catatanTu });
    return mapTicket(data);
  },

  async complete(ticketId: string, file: File, catatanTu?: string) {
    const form = new FormData();
    form.append('file', file);
    if (catatanTu) form.append('catatan_tu', catatanTu);
    const { data } = await client.patch(`/api/tickets/${ticketId}/complete`, form);
    return mapTicket(data);
  },

  async downloadFile(ticketId: string, type: 'hasil' | 'syarat'): Promise<void> {
    const endpoint = type === 'syarat'
      ? `/api/tickets/${ticketId}/download-syarat`
      : `/api/tickets/${ticketId}/download`;
    const response = await client.get(endpoint, { responseType: 'blob' });
    const contentDisposition: string = response.headers['content-disposition'] ?? '';
    const match = contentDisposition.match(/filename=(.+)/);
    const filename = match?.[1] ?? `berkas-${type}.pdf`;
    const url = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  },
};
