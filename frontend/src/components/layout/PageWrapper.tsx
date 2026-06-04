import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export const PageWrapper = ({ children }: { children: ReactNode }) => (
  <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,#0f2f2b_0,#020617_34rem)] text-slate-100">
    <div className="flex">
      <Sidebar />
      <div className="min-w-0 flex-1">
        <Topbar />
        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
      </div>
    </div>
  </div>
);
