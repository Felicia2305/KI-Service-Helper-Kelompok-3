import { useEffect, useState } from 'react';
import { ArrowLeft, CheckCircle2, Download, Hand, XCircle } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { ticketApi } from '../api/ticket.api';
import { TicketDetail } from '../components/tickets/TicketDetail';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Skeleton } from '../components/ui/Skeleton';
import { Toast } from '../components/ui/Toast';
import { useAuth } from '../hooks/useAuth';
import type { IntegrityResult, Ticket } from '../types';

export const TicketDetailPage = () => {
  const { ticketId = '' } = useParams();
  const { user } = useAuth();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [result, setResult] = useState<IntegrityResult | undefined>();
  const [notes, setNotes] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const staff = user?.role !== 'mahasiswa';

  const load = async () => setTicket(await ticketApi.get(ticketId));

  useEffect(() => {
    void load();
  }, [ticketId]);

  if (!ticket) return <Skeleton className="h-96" />;

  const run = async (action: () => Promise<Ticket>, success: string) => {
    const updated = await action();
    setTicket(updated);
    setMessage(success);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <Link to="/tickets">
          <Button variant="ghost"><ArrowLeft size={16} /> Kembali</Button>
        </Link>
        <Toast message={message} />
      </div>

      <TicketDetail
        ticket={ticket}
        result={result}
        onVerify={() => void ticketApi.verify(ticket.id).then(setResult)}
        onDownload={(type) => void ticketApi.download(ticket.id, type)}
      />

      {staff ? (
        <Card>
          <CardHeader>
            <h3 className="font-serif text-2xl text-white">Aksi staff</h3>
            <p className="mt-1 text-sm text-slate-500">Claim, approve, reject, complete, dan upload hasil opsional.</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input label="Catatan staff" value={notes} onChange={(event) => setNotes(event.target.value)} autoComplete="off" />
            <label className="block space-y-2">
              <span className="text-sm font-medium text-slate-200">File hasil opsional</span>
              <input className="block w-full rounded-md border border-slate-800 bg-slate-950 p-2 text-sm text-slate-400 file:mr-3 file:rounded-md file:border-0 file:bg-slate-800 file:px-3 file:py-2 file:text-sm file:text-slate-100" type="file" accept=".pdf,.jpg,.jpeg,.png,.docx" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
            </label>
            <div className="flex flex-wrap gap-2">
              {ticket.status === 'pending' ? <Button variant="outline" onClick={() => void run(() => ticketApi.claim(ticket.id), 'Tiket berhasil diklaim.')}><Hand size={16} /> Claim</Button> : null}
              {ticket.status === 'claimed' ? <Button onClick={() => void run(() => ticketApi.approve(ticket.id, notes), 'Tiket disetujui.')}><CheckCircle2 size={16} /> Approve</Button> : null}
              {ticket.status === 'claimed' ? <Button variant="danger" onClick={() => void run(() => ticketApi.reject(ticket.id, notes || 'Tidak memenuhi syarat'), 'Tiket ditolak.')}><XCircle size={16} /> Reject</Button> : null}
              {ticket.status === 'approved' || ticket.status === 'claimed' ? <Button variant="secondary" onClick={() => void run(() => ticketApi.complete(ticket.id, file, notes), 'Tiket diselesaikan.')}><Download size={16} /> Complete</Button> : null}
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
};
