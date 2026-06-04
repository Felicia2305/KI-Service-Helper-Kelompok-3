import { Activity, CheckCircle2, Clock, ClipboardList, ShieldCheck, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';
import { useAuth } from '../hooks/useAuth';
import { useTickets } from '../hooks/useTickets';

export const DashboardPage = () => {
  const { user } = useAuth();
  const { tickets, loading } = useTickets();
  const staff = user?.role !== 'mahasiswa';
  const stats = [
    { label: 'Total tiket', value: tickets.length, icon: ClipboardList, tone: 'text-blue-300' },
    { label: 'Pending', value: tickets.filter((ticket) => ticket.status === 'pending').length, icon: Clock, tone: 'text-amber-300' },
    { label: 'Approved', value: tickets.filter((ticket) => ticket.status === 'approved').length, icon: CheckCircle2, tone: 'text-emerald-300' },
    { label: 'Completed', value: tickets.filter((ticket) => ticket.status === 'completed').length, icon: Activity, tone: 'text-slate-300' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <div className="mb-3 flex items-center gap-2">
            <Badge tone={staff ? 'blue' : 'green'}>{user?.role}</Badge>
            <Badge tone="slate">JWT + HttpOnly refresh</Badge>
          </div>
          <h2 className="font-serif text-3xl leading-tight text-white md:text-4xl">Dashboard layanan akademik</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">Pantau status layanan, validasi integritas tiket, dan proses antrean dari satu portal.</p>
        </div>
        <Link to="/tickets">
          <Button><TrendingUp size={16} /> Kelola tiket</Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.label}>
              <CardContent className="p-5">
                <Icon className={item.tone} size={22} />
                <p className="mt-5 text-sm text-slate-500">{item.label}</p>
                <p className="mt-1 text-3xl font-semibold text-white">{loading ? '-' : item.value}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card>
          <CardHeader>
            <h3 className="font-serif text-2xl text-white">Aktivitas terbaru</h3>
          </CardHeader>
          <CardContent className="space-y-3">
            {loading ? <Skeleton className="h-24" /> : tickets.slice(0, 6).map((ticket) => (
              <Link key={ticket.id} to={`/tickets/${ticket.id}`} className="flex items-center justify-between rounded-md border border-slate-800 bg-slate-900/40 px-4 py-3 transition hover:bg-slate-900">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-slate-100">{ticket.service_type.nama}</p>
                  <p className="truncate text-xs text-slate-500">{ticket.purpose}</p>
                </div>
                <Badge tone={ticket.status === 'rejected' ? 'red' : ticket.status === 'pending' ? 'amber' : 'green'}>{ticket.status}</Badge>
              </Link>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="font-serif text-2xl text-white">Keamanan</h3>
          </CardHeader>
          <CardContent className="space-y-4 text-sm text-slate-400">
            {['Access token in-memory', 'Refresh token HttpOnly cookie', 'Fernet encryption at rest', 'RSA digital signature', 'Audit log aktif'].map((item) => (
              <div key={item} className="flex items-center gap-3">
                <ShieldCheck className="text-emerald-300" size={18} />
                <span>{item}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
