import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import type { ReactNode } from 'react';
import { PageWrapper } from './components/layout/PageWrapper';
import { useAuth } from './hooks/useAuth';
import { AdminPage } from './pages/AdminPage';
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { TicketDetailPage } from './pages/TicketDetailPage';
import { TicketsPage } from './pages/TicketsPage';

const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  const { booting, isAuthenticated } = useAuth();
  if (booting) {
    return <div className="grid min-h-screen place-items-center bg-slate-950 text-sm text-slate-400">Memuat sesi...</div>;
  }
  return isAuthenticated ? <PageWrapper>{children}</PageWrapper> : <Navigate to="/login" replace />;
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/tickets" element={<ProtectedRoute><TicketsPage /></ProtectedRoute>} />
        <Route path="/tickets/:ticketId" element={<ProtectedRoute><TicketDetailPage /></ProtectedRoute>} />
        <Route path="/admin" element={<ProtectedRoute><AdminPage /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}
