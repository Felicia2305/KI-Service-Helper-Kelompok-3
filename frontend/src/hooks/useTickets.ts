import { useCallback, useEffect, useState } from 'react';
import { ticketApi } from '../api/ticket.api';
import type { ServiceType, Ticket } from '../types';
import { useAuth } from './useAuth';

export const useTickets = () => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [services, setServices] = useState<ServiceType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError('');
    try {
      const staff = user.role !== 'mahasiswa';
      const [ticketData, serviceData] = await Promise.all([
        staff ? ticketApi.listAll() : ticketApi.listMine(),
        ticketApi.services(),
      ]);
      setTickets(ticketData);
      setServices(serviceData);
    } catch {
      setError('Gagal memuat data. Periksa koneksi backend atau akses role.');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    void load();
  }, [load]);

  return { tickets, services, loading, error, reload: load, setTickets };
};
