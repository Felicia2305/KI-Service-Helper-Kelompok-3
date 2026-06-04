import type { ReactNode } from 'react';
import { cn } from '../../lib/cn';

export const Card = ({ children, className = '' }: { children: ReactNode; className?: string }) => (
  <section className={cn('rounded-xl border border-slate-800 bg-slate-950/80 shadow-sm shadow-black/20', className)}>
    {children}
  </section>
);

export const CardHeader = ({ children, className = '' }: { children: ReactNode; className?: string }) => (
  <div className={cn('border-b border-slate-800 px-5 py-4', className)}>{children}</div>
);

export const CardContent = ({ children, className = '' }: { children: ReactNode; className?: string }) => (
  <div className={cn('p-5', className)}>{children}</div>
);
