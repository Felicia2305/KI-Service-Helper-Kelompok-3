import type { ReactNode } from 'react';
import { cn } from '../../lib/cn';

export const Badge = ({ children, tone = 'slate', className = '' }: { children: ReactNode; tone?: 'slate' | 'green' | 'blue' | 'red' | 'amber'; className?: string }) => {
  const tones = {
    slate: 'bg-slate-800 text-slate-300 border-slate-700',
    green: 'bg-emerald-400/10 text-emerald-300 border-emerald-300/20',
    blue: 'bg-blue-400/10 text-blue-300 border-blue-300/20',
    red: 'bg-red-400/10 text-red-300 border-red-300/20',
    amber: 'bg-amber-400/10 text-amber-300 border-amber-300/20',
  };
  return <span className={cn('inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-medium', tones[tone], className)}>{children}</span>;
};
