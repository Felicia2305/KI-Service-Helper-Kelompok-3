import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Toast } from '../components/ui/Toast';
import { useAuth } from '../hooks/useAuth';
import type { Role } from '../types';

export const RegisterPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ nama: '', nim_nip: '', email: '', password: '', confirm: '', role: 'mahasiswa' as Role });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const strong = form.password.length >= 12 && /[A-Z]/.test(form.password) && /\d/.test(form.password);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    if (form.password !== form.confirm) {
      setError('Konfirmasi password tidak cocok.');
      return;
    }
    try {
      await register({ nama: form.nama, nim_nip: form.nim_nip, email: form.email, password: form.password, role: form.role });
      setMessage('Registrasi berhasil. Silakan login.');
      window.setTimeout(() => navigate('/login'), 900);
    } catch {
      setError('Registrasi gagal. Pastikan email IPB belum terdaftar.');
    }
  };

  return (
    <main className="grid min-h-screen place-items-center bg-[radial-gradient(circle_at_top_left,#0f2f2b_0,#020617_34rem)] px-5 py-10 text-white">
      <Card className="w-full max-w-xl">
        <CardContent className="p-8 sm:p-10">
          <h1 className="font-serif text-3xl text-slate-50">Buat akun layanan</h1>
          <p className="mt-2 text-sm text-slate-500">Pilih role sesuai kebutuhan demo atau operasional.</p>
          <form className="mt-8 space-y-5" onSubmit={(event) => void submit(event)} autoComplete="off">
            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Nama" value={form.nama} onChange={(event) => setForm({ ...form, nama: event.target.value })} required autoComplete="off" />
              <Input label="NIM / NIP" value={form.nim_nip} onChange={(event) => setForm({ ...form, nim_nip: event.target.value })} required autoComplete="off" />
            </div>
            <Input label="Email IPB" type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required autoComplete="off" />
            <label className="block space-y-2">
              <span className="text-sm font-medium text-slate-200">Role</span>
              <select className="h-10 w-full rounded-md border border-slate-700 bg-slate-950 px-3 text-sm text-slate-100" value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value as Role })}>
                <option value="mahasiswa">Mahasiswa</option>
                <option value="staff_departemen">Staff Departemen</option>
                <option value="staff_fakultas">Staff Fakultas</option>
                <option value="staff_ipb">Staff IPB</option>
              </select>
            </label>
            <Input label="Password" type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} minLength={8} required autoComplete="off" />
            <div className="h-2 rounded-full bg-slate-800"><div className={`h-2 rounded-full transition-all ${strong ? 'w-full bg-emerald-400' : 'w-1/2 bg-blue-400'}`} /></div>
            <Input label="Konfirmasi password" type="password" value={form.confirm} onChange={(event) => setForm({ ...form, confirm: event.target.value })} minLength={8} required autoComplete="off" />
            <Button className="w-full">Register</Button>
          </form>
          <div className="mt-5 space-y-4">
            <Toast message={message} />
            <Toast message={error} tone="red" />
            <p className="text-center text-sm text-slate-400">Sudah punya akun? <Link className="font-medium text-emerald-300 hover:text-emerald-200" to="/login">Login</Link></p>
          </div>
        </CardContent>
      </Card>
    </main>
  );
};
