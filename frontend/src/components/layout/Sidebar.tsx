import { ClipboardList, LayoutDashboard, LogOut, ShieldCheck, Users } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { useAuth } from '../../hooks/useAuth';

export const Sidebar = () => {
  const { user, logout } = useAuth();
  const staff = user?.role !== 'mahasiswa';
  const links = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/tickets', label: staff ? 'Semua Tiket' : 'Tiket Saya', icon: ClipboardList },
    ...(staff ? [{ href: '/admin', label: 'Staff Console', icon: Users }] : []),
  ];

  return (
    <aside className="sticky top-0 hidden h-screen w-72 border-r border-slate-800 bg-slate-950/90 p-5 backdrop-blur lg:block">
      <div className="mb-10 flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-950/30">
          <ShieldCheck size={20} />
        </div>
        <div>
          <p className="font-serif text-2xl leading-none text-white">KI · IPB</p>
          <p className="mt-1 text-xs text-slate-500">Academic Service Helper</p>
        </div>
      </div>

      <nav className="space-y-1">
        {links.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.href}
              to={item.href}
              className={({ isActive }) => `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition ${isActive ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-400 hover:bg-slate-900 hover:text-white'}`}
            >
              <Icon size={18} />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      <div className="absolute bottom-5 left-5 right-5 space-y-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div>
          <p className="truncate text-sm font-semibold text-white">{user?.nama}</p>
          <p className="truncate text-xs text-slate-500">{user?.email}</p>
        </div>
        <Badge tone={staff ? 'blue' : 'green'}>{user?.role}</Badge>
        <Button variant="outline" className="w-full" onClick={() => void logout()}>
          <LogOut size={16} /> Logout
        </Button>
      </div>
    </aside>
  );
};
