import React, { useState, useEffect } from 'react';
import { Briefcase, Search, RefreshCw, Clock } from 'lucide-react';
import { api } from '../services/api';
import { SeverityBadge, StatusBadge } from '../components/common/Badges';
import { formatDateTime } from '../utils/date';

interface Case {
  id: number;
  case_id: string;
  title: string;
  description?: string;
  priority: string;
  status: string;
  assigned_analyst_id?: number;
  created_at?: string;
  updated_at?: string;
}

const formatDate = (d?: string) => formatDateTime(d);

export default function Cases() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const res = await api.get('/cases');
      setCases(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = cases.filter(c =>
    c.title.toLowerCase().includes(search.toLowerCase()) ||
    c.case_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Case Management</h1>
          <p className="text-sm text-gray-400">Track and manage investigation cases</p>
        </div>
        <button onClick={fetchCases} className="p-2 rounded-xl hover:bg-gray-800 text-gray-400 hover:text-white transition-colors">
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          type="text"
          placeholder="Search cases..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 bg-dark-800 border border-gray-700 rounded-xl text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid gap-4">
          {filtered.map((c) => (
            <div key={c.id} className="glass-panel rounded-2xl p-5 hover:border-cyan-500/30 transition-all cursor-pointer">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 rounded-xl bg-indigo-950/60 border border-indigo-800/40 flex items-center justify-center">
                    <Briefcase className="w-5 h-5 text-indigo-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">{c.title}</h3>
                    <p className="text-xs text-gray-500 font-mono mt-0.5">{c.case_id}</p>
                    {c.description && (
                      <p className="text-xs text-gray-400 mt-2 max-w-xl">{c.description}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <SeverityBadge severity={c.priority} />
                  <StatusBadge status={c.status} />
                </div>
              </div>
              <div className="flex items-center space-x-4 mt-4 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Created: {formatDate(c.created_at)}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Updated: {formatDate(c.updated_at)}</span>
                </div>
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="text-center py-12 text-gray-500 text-sm">No cases found</div>
          )}
        </div>
      )}
    </div>
  );
}
