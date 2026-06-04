import { ClipboardCheck, RefreshCw } from 'lucide-react';
import { ticketApi } from '../api/ticket.api';
import { TicketCard } from '../components/tickets/TicketCard';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import { Toast } from '../components/ui/Toast';
import { useState } from 'react';
import { useTickets } from '../hooks/useTickets';

export const AdminPage = () => {
  const { tickets, loading, reload } = useTickets();
  const [message, setMessage] = useState('');
  const pending = tickets.filter((ticket) => ticket.status === 'pending');
  const claimed = tickets.filter((ticket) => ticket.status === 'claimed');

  const claimNext = async () => {
    const ticket = await ticketApi.claimNext();
    setMessage(`Tiket ${ticket.id.slice(0, 8)} berhasil diklaim.`);
    await reload();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-slate-500">Staff console</p>
          <h2 className="font-serif text-3xl text-white md:text-4xl">Queue operasional</h2>
          <p className="mt-2 text-sm text-slate-400">Fokus ke tiket yang menunggu claim dan tiket yang sedang diproses.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => void reload()}><RefreshCw size={16} /> Refresh</Button>
          <Button onClick={() => void claimNext()}><ClipboardCheck size={16} /> Claim berikutnya</Button>
        </div>
      </div>

      <Toast message={message} />

      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardContent><p className="text-sm text-slate-500">Pending</p><p className="mt-2 text-3xl font-semibold text-white">{pending.length}</p></CardContent></Card>
        <Card><CardContent><p className="text-sm text-slate-500">Claimed</p><p className="mt-2 text-3xl font-semibold text-white">{claimed.length}</p></CardContent></Card>
        <Card><CardContent><p className="text-sm text-slate-500">Total queue</p><p className="mt-2 text-3xl font-semibold text-white">{tickets.length}</p></CardContent></Card>
      </div>

      <Card>
        <CardHeader>
          <h3 className="font-serif text-2xl text-white">Tiket membutuhkan aksi</h3>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {loading ? <><Skeleton className="h-52" /><Skeleton className="h-52" /></> : tickets.filter((ticket) => ['pending', 'claimed', 'approved'].includes(ticket.status)).map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} staff onClaim={(id) => void ticketApi.claim(id).then(() => reload())} />
            ))}
          </div>
          {!loading && tickets.length === 0 ? <EmptyState title="Queue kosong" description="Belum ada tiket yang perlu diproses." /> : null}
        </CardContent>
      </Card>
    </div>
  );
};
