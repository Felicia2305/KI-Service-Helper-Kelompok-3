import { CheckCircle2, Circle, Download, ShieldCheck } from 'lucide-react';
import type { IntegrityResult, Ticket } from '../../types';
import { Button } from '../ui/Button';
import { Card, CardContent, CardHeader } from '../ui/Card';
import { SignatureBadge } from './SignatureBadge';

const steps = ['pending', 'claimed', 'approved', 'completed'];

export const TicketDetail = ({ ticket, result, onVerify, onDownload }: { ticket: Ticket; result?: IntegrityResult; onVerify: () => void; onDownload: (type: 'syarat' | 'hasil') => void }) => (
  <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
    <Card>
      <CardHeader>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{ticket.service_type.nama}</p>
        <h2 className="mt-2 font-serif text-3xl leading-tight text-white">{ticket.purpose}</h2>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <p className="text-sm font-medium text-slate-400">Catatan</p>
          <p className="mt-2 text-sm leading-7 text-slate-300">{ticket.notes || ticket.catatan_tu || 'Belum ada catatan tambahan.'}</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-md border border-slate-800 bg-slate-900/50 p-4">
            <p className="text-xs uppercase text-slate-500">Pemohon</p>
            <p className="mt-1 text-sm font-medium text-slate-100">{ticket.mahasiswa?.nama}</p>
            <p className="text-xs text-slate-500">{ticket.mahasiswa?.nim_nip}</p>
          </div>
          <div className="rounded-md border border-slate-800 bg-slate-900/50 p-4">
            <p className="text-xs uppercase text-slate-500">Staff</p>
            <p className="mt-1 text-sm font-medium text-slate-100">{ticket.assigned_staff?.nama || 'Belum diklaim'}</p>
            <p className="text-xs text-slate-500">{ticket.assigned_staff?.role || '-'}</p>
          </div>
        </div>
      </CardContent>
    </Card>
    <Card>
      <CardHeader>
        <h3 className="font-serif text-xl text-white">Status & integritas</h3>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="space-y-3">
        {steps.map((step) => {
          const active = steps.indexOf(step) <= steps.indexOf(ticket.status);
          return (
            <div key={step} className="flex items-center gap-3 text-sm">
              {active ? <CheckCircle2 className="text-emerald-300" size={18} /> : <Circle className="text-slate-600" size={18} />}
              <span className={active ? 'text-white' : 'text-slate-500'}>{step}</span>
            </div>
          );
        })}
        </div>
        <div className="border-t border-slate-800 pt-5">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-sm text-slate-400">Digital signature</span>
          <SignatureBadge valid={result?.valid} />
        </div>
        <Button className="w-full" onClick={onVerify}><ShieldCheck size={16} /> Verifikasi Integritas Dokumen</Button>
        {result ? <p className="mt-3 text-sm text-slate-300">{result.message}</p> : null}
        </div>
        <div className="space-y-2 border-t border-slate-800 pt-5">
          <Button variant="outline" className="w-full" disabled={!ticket.file_path && !ticket.file_syarat_path} onClick={() => onDownload('syarat')}><Download size={16} /> Download lampiran</Button>
          <Button variant="outline" className="w-full" disabled={!ticket.file_hasil_path} onClick={() => onDownload('hasil')}><Download size={16} /> Download hasil</Button>
        </div>
      </CardContent>
    </Card>
  </div>
);
