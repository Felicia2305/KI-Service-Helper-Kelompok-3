import type { InputHTMLAttributes, TextareaHTMLAttributes } from 'react';
import { cn } from '../../lib/cn';

type FieldProps = {
  label: string;
  error?: string;
};

export const Input = ({ label, error, className = '', ...props }: FieldProps & InputHTMLAttributes<HTMLInputElement>) => (
  <label className="block space-y-2 text-left">
    <span className="text-sm font-medium text-slate-200">{label}</span>
    <input
      className={cn('h-10 w-full rounded-md border border-slate-700 bg-slate-950 px-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-emerald-300 focus:ring-1 focus:ring-emerald-300', className)}
      {...props}
    />
    {error ? <span className="text-xs text-red-300">{error}</span> : null}
  </label>
);

export const Textarea = ({ label, error, className = '', ...props }: FieldProps & TextareaHTMLAttributes<HTMLTextAreaElement>) => (
  <label className="block space-y-2 text-left">
    <span className="text-sm font-medium text-slate-200">{label}</span>
    <textarea
      className={cn('min-h-28 w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-emerald-300 focus:ring-1 focus:ring-emerald-300', className)}
      {...props}
    />
    {error ? <span className="text-xs text-red-300">{error}</span> : null}
  </label>
);
