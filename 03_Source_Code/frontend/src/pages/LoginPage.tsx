import { useState, type FormEvent } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { BookOpenCheck, ShieldCheck } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Toast } from '../components/ui/Toast';
import { useAuth } from '../hooks/useAuth';

export const LoginPage = () => {
  const { booting, login, isAuthenticated, statusMsg } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  if (!booting && isAuthenticated) return <Navigate to="/dashboard" replace />;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!email.includes('@') || password.length < 8) return;
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="grid min-h-screen place-items-center bg-[radial-gradient(circle_at_top_left,#0f2f2b_0,#020617_34rem)] px-5 py-10 text-white">
      <div className="w-full max-w-5xl">
        <div className="grid overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/80 shadow-2xl shadow-black/40 lg:grid-cols-[1fr_420px]">
          <section className="hidden border-r border-slate-800 p-10 lg:block">
            <div className="flex items-center gap-3">
              <div className="grid h-11 w-11 place-items-center rounded-xl bg-emerald-400 text-slate-950"><ShieldCheck size={22} /></div>
              <div>
                <p className="font-serif text-3xl leading-none">IPB Academic Service Helper</p>
                <p className="mt-1 text-sm text-slate-500">Service Center Terpercaya</p>
              </div>
            </div>
            <div className="mt-24 max-w-lg">
              <p className="mb-3 inline-flex rounded-full border border-emerald-300/20 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-200">Secure service portal</p>
              <h1 className="font-serif text-5xl leading-tight text-slate-50">Layanan akademik dengan validasi keamanan end-to-end.</h1>
              <p className="mt-5 text-base leading-7 text-slate-400">Login untuk mengajukan tiket, memantau status, memproses antrean staff, dan memverifikasi digital signature.</p>
            </div>
          </section>
          <Card className="rounded-none border-0 bg-transparent">
            <CardContent className="p-8 sm:p-10">
              <div className="mb-8">
                <BookOpenCheck className="mb-4 text-emerald-300" size={28} />
                <h2 className="font-serif text-3xl text-slate-50">Masuk</h2>
                <p className="mt-2 text-sm text-slate-500">Gunakan email IPB dan password akun layanan.</p>
              </div>
              <form className="space-y-5" onSubmit={(event) => void submit(event)} autoComplete="off">
                <Input label="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="off" />
                <Input label="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required autoComplete="off" />
                <Button className="w-full" disabled={loading || booting}>{loading ? 'Memverifikasi...' : 'Login'}</Button>
              </form>
              <div className="mt-5 space-y-4">
                <Toast message={statusMsg} tone="red" />
                <p className="text-center text-sm text-slate-400">Belum punya akun? <Link className="font-medium text-emerald-300 hover:text-emerald-200" to="/register">Register</Link></p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
};
