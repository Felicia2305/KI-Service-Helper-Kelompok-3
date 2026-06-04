import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '../../lib/cn';

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'icon';
  children: ReactNode;
};

export const Button = ({ variant = 'primary', size = 'md', className = '', children, ...props }: ButtonProps) => {
  const variants = {
    primary: 'bg-emerald-400 text-slate-950 shadow-sm shadow-emerald-950/20 hover:bg-emerald-300',
    secondary: 'bg-blue-400 text-slate-950 shadow-sm shadow-blue-950/20 hover:bg-blue-300',
    outline: 'border border-slate-700 bg-slate-950 text-slate-100 hover:bg-slate-900 hover:text-white',
    ghost: 'text-slate-300 hover:bg-slate-800 hover:text-white',
    danger: 'border border-red-400/25 bg-red-500/10 text-red-200 hover:bg-red-500/20',
  };
  const sizes = {
    sm: 'h-9 rounded-md px-3 text-xs',
    md: 'h-10 rounded-md px-4 text-sm',
    icon: 'h-10 w-10 rounded-md p-0',
  };
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-300 disabled:pointer-events-none disabled:opacity-50',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
};
