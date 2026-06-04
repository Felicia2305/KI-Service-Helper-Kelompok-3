import { ArrowRight, CalendarDays, LockKeyhole, UserRound } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Ticket } from '../../types';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { Card, CardContent } from '../ui/Card';

const statusTone = (status: Ticket['status']) => {
  if (status === 'approved' || status === 'completed') return 'green';
  if (status === 'rejected') return 'red';
  if (status === 'claimed') return 'blue';
  return 'amber';
};

export const TicketCard = ({ ticket, onClaim, staff }: { ticket: Ticket; onClaim?: (id: string) => void; staff: boolean }) => (
  <Card className="transition hover:border-slate-700 hover:bg-slate-900/60">
    <CardContent className="space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="truncate text-xs font-medium uppercase tracking-wide text-slate-500">{ticket.service_type.nama}</p>
          <h3 className="mt-2 line-clamp-2 text-base font-semibold leading-6 text-slate-50">{ticket.purpose}</h3>
        </div>
        <Badge tone={statusTone(ticket.status)}>{ticket.status}</Badge>
      </div>
      <div className="grid gap-2 text-xs text-slate-400 sm:grid-cols-2">
        <span className="flex items-center gap-2"><CalendarDays size={14} /> {new Date(ticket.created_at).toLocaleDateString('id-ID')}</span>
        <span className="flex items-center gap-2"><UserRound size={14} /> {staff ? ticket.mahasiswa?.nama : ticket.assigned_staff?.nama || 'Belum diklaim'}</span>
        <span className="flex items-center gap-2 sm:col-span-2"><LockKeyhole size={14} /> Data sensitif tersimpan terenkripsi dan ditandatangani.</span>
      </div>
      <div className="flex items-center justify-end gap-2">
        {staff && ticket.status === 'pending' ? <Button variant="outline" size="sm" onClick={() => onClaim?.(ticket.id)}>Claim</Button> : null}
        <Link to={`/tickets/${ticket.id}`}>
          <Button size="sm"><ArrowRight size={15} /> Detail</Button>
        </Link>
      </div>
    </CardContent>
  </Card>
);
