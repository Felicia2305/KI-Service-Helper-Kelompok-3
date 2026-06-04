import { Menu, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../ui/Button';

export const Topbar = () => {
  const { user, logout } = useAuth();
  return (
    <header className="sticky top-0 z-20 flex items-center justify-between border-b border-slate-800 bg-slate-950/80 px-4 py-3 backdrop-blur lg:px-8">
      <div className="flex items-center gap-3">
        <Menu className="text-slate-400 lg:hidden" size={20} />
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Secure academic portal</p>
          <h1 className="font-serif text-xl text-white sm:text-2xl">IPB Academic Service Helper</h1>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Link className="rounded-md px-3 py-2 text-sm text-slate-300 hover:bg-slate-900 lg:hidden" to="/dashboard">Dashboard</Link>
        <Link className="rounded-md px-3 py-2 text-sm text-slate-300 hover:bg-slate-900 lg:hidden" to="/tickets">Tiket</Link>
        <div className="hidden items-center gap-2 rounded-full border border-emerald-300/20 bg-emerald-400/10 px-3 py-2 text-xs text-emerald-200 sm:flex">
          <ShieldCheck size={15} />
          {user?.role}
        </div>
        <Button variant="ghost" size="sm" className="lg:hidden" onClick={() => void logout()}>Logout</Button>
      </div>
    </header>
  );
};
