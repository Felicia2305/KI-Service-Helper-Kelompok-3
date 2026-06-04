import { FileUp, LockKeyhole } from 'lucide-react';
import { useState, type FormEvent } from 'react';
import type { ServiceType } from '../../types';
import { Button } from '../ui/Button';
import { Textarea } from '../ui/Input';

export const TicketForm = ({ services, onSubmit }: { services: ServiceType[]; onSubmit: (data: { serviceTypeId: string; purpose: string; notes?: string; file?: File | null }) => Promise<void> }) => {
  const [serviceTypeId, setServiceTypeId] = useState('');
  const [purpose, setPurpose] = useState('');
  const [notes, setNotes] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (purpose.length < 10) return;
    setLoading(true);
    await onSubmit({ serviceTypeId, purpose, notes, file });
    setPurpose('');
    setNotes('');
    setFile(null);
    setLoading(false);
  };

  return (
    <form className="space-y-5" onSubmit={(event) => void submit(event)} autoComplete="off">
      <label className="block space-y-2">
        <span className="text-sm font-medium text-slate-200">Jenis layanan</span>
        <select className="h-10 w-full rounded-md border border-slate-700 bg-slate-950 px-3 text-sm text-slate-100 outline-none focus:border-emerald-300 focus:ring-1 focus:ring-emerald-300" value={serviceTypeId} onChange={(event) => setServiceTypeId(event.target.value)} required>
          <option value="">Pilih layanan</option>
          {services.map((service) => <option key={service.id} value={service.id}>{service.nama}</option>)}
        </select>
      </label>
      <Textarea label="Keperluan" value={purpose} onChange={(event) => setPurpose(event.target.value)} minLength={10} maxLength={2000} required autoComplete="off" />
      <Textarea label="Catatan opsional" value={notes} onChange={(event) => setNotes(event.target.value)} maxLength={2000} autoComplete="off" />
      <label className="block space-y-2">
        <span className="text-sm font-medium text-slate-200">Lampiran opsional</span>
        <div className="flex min-h-24 items-center justify-center rounded-md border border-dashed border-slate-700 bg-slate-950 px-4 py-5 text-center">
          <div>
            <FileUp className="mx-auto mb-2 text-slate-500" size={22} />
            <input className="block w-full text-sm text-slate-400 file:mr-3 file:rounded-md file:border-0 file:bg-slate-800 file:px-3 file:py-2 file:text-sm file:text-slate-100" type="file" accept=".pdf,.jpg,.jpeg,.png,.docx" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
            <p className="mt-2 text-xs text-slate-500">PDF, JPG, PNG, DOCX sampai 5MB. Tidak wajib.</p>
          </div>
        </div>
      </label>
      <p className="flex items-start gap-3 rounded-md border border-emerald-300/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200"><LockKeyhole className="mt-0.5 shrink-0" size={16} /> Data keperluan dan catatan akan dienkripsi sebelum disimpan.</p>
      <Button className="w-full" disabled={loading || purpose.length < 10}>{loading ? 'Mengirim...' : 'Ajukan tiket'}</Button>
    </form>
  );
};
