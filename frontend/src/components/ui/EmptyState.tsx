import type { ReactNode } from 'react';

export const EmptyState = ({ title, description, action }: { title: string; description: string; action?: ReactNode }) => (
  <div className="rounded-xl border border-dashed border-slate-800 bg-slate-950/60 px-6 py-10 text-center">
    <p className="text-base font-medium text-slate-100">{title}</p>
    <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">{description}</p>
    {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
  </div>
);
