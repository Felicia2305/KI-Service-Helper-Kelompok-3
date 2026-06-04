import type { ReactNode } from 'react';
import { X } from 'lucide-react';
import { Button } from './Button';

export const Modal = ({ title, open, onClose, children }: { title: string; open: boolean; onClose: () => void; children: ReactNode }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/75 p-4 backdrop-blur-sm">
      <div className="w-full max-w-2xl rounded-xl border border-slate-800 bg-slate-950 p-6 shadow-2xl shadow-black/40">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="font-serif text-2xl text-slate-50">{title}</h2>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Tutup modal">
            <X size={16} />
          </Button>
        </div>
        {children}
      </div>
    </div>
  );
};
