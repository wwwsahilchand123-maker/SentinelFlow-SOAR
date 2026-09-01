import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, User as UserIcon, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="min-h-screen bg-dark-900 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Cyber Grid Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(#1f2937_1px,transparent_1px)] [background-size:24px_24px] opacity-30"></div>
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md glass-panel bg-dark-800/90 border border-gray-700/80 rounded-3xl p-8 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-cyan-500 to-cyan-300 flex items-center justify-center shadow-xl shadow-cyan-500/25 mb-4">
            <Shield className="w-8 h-8 text-dark-900 stroke-[2.5]" />
          </div>
          <h2 className="text-2xl font-black text-white tracking-wider flex items-center justify-center gap-1.5">
            SENTINEL<span className="text-cyan-400">FLOW</span>
          </h2>
          <p className="text-xs uppercase font-mono tracking-widest text-gray-400 mt-1">Autonomous SOAR Platform</p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-xl bg-red-950/80 border border-red-800 text-red-300 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1.5">
              Username
            </label>
            <div className="relative">
              <UserIcon className="w-4 h-4 text-gray-500 absolute left-3.5 top-3.5" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter SOC username"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-dark-900 border border-gray-700 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-gray-500 absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter credentials"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-dark-900 border border-gray-700 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-cyan-400 text-dark-900 font-bold text-sm hover:from-cyan-400 hover:to-cyan-300 transition-all flex items-center justify-center space-x-2 shadow-lg shadow-cyan-500/20 disabled:opacity-50"
          >
            <span>{loading ? 'Authenticating...' : 'Access Security Console'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Quick Demo Credential Selectors */}
        <div className="mt-8 pt-6 border-t border-gray-800">
          <p className="text-[11px] font-mono text-gray-400 uppercase tracking-wider text-center mb-3">
            Quick-Select Demo Credentials
          </p>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => handleQuickFill('admin', 'admin123')}
              className="px-2.5 py-2 rounded-lg bg-gray-800/80 hover:bg-gray-700/80 border border-gray-700 text-xs text-cyan-300 font-medium transition-colors"
            >
              Admin
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('analyst', 'analyst123')}
              className="px-2.5 py-2 rounded-lg bg-gray-800/80 hover:bg-gray-700/80 border border-gray-700 text-xs text-amber-300 font-medium transition-colors"
            >
              SOC Analyst
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('viewer', 'viewer123')}
              className="px-2.5 py-2 rounded-lg bg-gray-800/80 hover:bg-gray-700/80 border border-gray-700 text-xs text-emerald-300 font-medium transition-colors"
            >
              Auditor
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
