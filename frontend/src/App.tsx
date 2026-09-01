import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Alerts } from './pages/Alerts';
import AlertDetail from './pages/AlertDetail';
import { Incidents } from './pages/Incidents';
import { IncidentDetail } from './pages/IncidentDetail';
import { Playbooks } from './pages/Playbooks';
import { Simulation } from './pages/Simulation';
import { ThreatIntel } from './pages/ThreatIntel';
import Assets from './pages/Assets';
import AuditLogs from './pages/AuditLogs';
import Cases from './pages/Cases';
import Reports from './pages/Reports';

const ProtectedRoute: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-dark-900">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-gray-400 mt-4 font-mono text-sm">INITIALIZING SOAR SYSTEMS...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex flex-col h-screen bg-dark-900 text-gray-200">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 bg-dark-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/alerts/:id" element={<AlertDetail />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/incidents/:id" element={<IncidentDetail />} />
            <Route path="/playbooks" element={<Playbooks />} />
            <Route path="/simulation" element={<Simulation />} />
            <Route path="/threat-intel" element={<ThreatIntel />} />
            <Route path="/assets" element={<Assets />} />
            <Route path="/cases" element={<Cases />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/audit" element={<AuditLogs />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
