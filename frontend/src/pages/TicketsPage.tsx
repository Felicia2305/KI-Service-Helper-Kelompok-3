import { useMemo, useState } from 'react';
import { ClipboardCheck, Plus, RefreshCw } from 'lucide-react';
import { ticketApi } from '../api/ticket.api';
import { TicketCard } from '../components/tickets/TicketCard';
import { TicketForm } from '../components/tickets/TicketForm';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';
import { Modal } from '../components/ui/Modal';
import { Skeleton } from '../components/ui/Skeleton';
import { Toast } from '../components/ui/Toast';
import { useAuth } from '../hooks/useAuth';
import { useTickets } from '../hooks/useTickets';

const filters = ['all', 'pending', 'claimed', 'approved', 'rejected', 'completed'];

export const TicketsPage = () => {
  const { user } = useAuth();
  const { tickets, services, loading, reload } = useTickets();
  const [filter, setFilter] = useState('all');
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const staff = user?.role !== 'mahasiswa';
  const filtered = useMemo(() => tickets.filter((ticket) => filter === 'all' || ticket.status === filter), [filter, tickets]);

  const claimNext = async () => {
    const ticket = await ticketApi.claimNext();
    setMessage(`Tiket ${ticket.id.slice(0, 8)} berhasil diklaim.`);
    await reload();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">{staff ? 'Staff queue' : 'Mahasiswa'}</p>
          <h2 className="font-serif text-3xl text-white md:text-4xl">{staff ? 'Semua tiket layanan' : 'Tiket saya'}</h2>
          <p className="mt-2 text-sm text-slate-400">{staff ? 'Claim antrean, review pengajuan, dan verifikasi integritas tiket.' : 'Ajukan layanan baru dan pantau progresnya.'}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={() => void reload()}><RefreshCw size={16} /> Refresh</Button>
          {staff ? <Button variant="secondary" onClick={() => void claimNext()}><ClipboardCheck size={16} /> Claim berikutnya</Button> : <Button onClick={() => setOpen(true)}><Plus size={16} /> Ajukan Tiket Baru</Button>}
        </div>
      </div>

      <Toast message={message} />

      <Card>
        <CardContent className="flex flex-wrap gap-2">
          {filters.map((item) => (
            <button key={item} className={`rounded-md border px-3 py-2 text-xs font-medium transition ${filter === item ? 'border-emerald-300/40 bg-emerald-400/10 text-emerald-200' : 'border-slate-800 text-slate-400 hover:bg-slate-900'}`} onClick={() => setFilter(item)}>
              {item}
            </button>
          ))}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        {loading ? <><Skeleton className="h-52" /><Skeleton className="h-52" /></> : filtered.map((ticket) => (
          <TicketCard key={ticket.id} ticket={ticket} staff={staff} onClaim={(id) => void ticketApi.claim(id).then(() => reload())} />
        ))}
      </div>

      {!loading && filtered.length === 0 ? (
        <EmptyState
          title="Tidak ada tiket"
          description="Belum ada tiket pada filter ini."
          action={!staff ? <Button onClick={() => setOpen(true)}><Plus size={16} /> Ajukan tiket</Button> : undefined}
        />
      ) : null}

      <Modal title="Ajukan tiket baru" open={open} onClose={() => setOpen(false)}>
        <TicketForm services={services} onSubmit={async (payload) => {
          await ticketApi.create(payload);
          setMessage('Tiket berhasil dibuat.');
          setOpen(false);
          await reload();
        }} />
      </Modal>
    </div>
  );
};
