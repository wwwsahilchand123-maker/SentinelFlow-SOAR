import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, Clock, CheckCircle, XCircle } from 'lucide-react';
import { auditService } from '../services/api';
import { AuditLog } from '../types';
import { formatDateTime } from '../utils/date';

const formatDate = (d?: string) => formatDateTime(d);

export default function AuditLogs() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('');

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await auditService.getLogs(
        actionFilter ? { action: actionFilter } : undefined
      );
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = logs.filter(l =>
    l.action.toLowerCase().includes(search.toLowerCase()) ||
    l.resource.toLowerCase().includes(search.toLowerCase()) ||
    (l.resource_id && l.resource_id.includes(search))
  );

  const resultIcon = (result: string) => {
    return result === 'success'
      ? <CheckCircle className="w-4 h-4 text-emerald-400" />
      : <XCircle className="w-4 h-4 text-red-400" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">SOC Audit Logs</h1>
          <p className="text-sm text-gray-400">Complete audit trail of all SOC operations</p>
        </div>
        <button onClick={fetchLogs} className="p-2 rounded-xl hover:bg-gray-800 text-gray-400 hover:text-white transition-colors">
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      <div className="flex items-center space-x-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search actions, resources..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-800 border border-gray-700 rounded-xl text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
          />
        </div>
        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="bg-dark-800 border border-gray-700 rounded-xl px-3 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-cyan-500/50"
        >
          <option value="">All Actions</option>
          <option value="LOGIN">Login</option>
          <option value="CREATE">Create</option>
          <option value="UPDATE">Update</option>
          <option value="DELETE">Delete</option>
          <option value="EXECUTE">Execute</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="glass-panel rounded-2xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800 text-left">
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Timestamp</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Action</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Resource</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Resource ID</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Result</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {filtered.map((log) => (
                <tr key={log.id} className="hover:bg-gray-800/30 transition-colors">
                  <td className="px-5 py-3">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-3.5 h-3.5 text-gray-500" />
                      <span className="text-xs text-gray-300 font-mono">{formatDate(log.timestamp)}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-400 border border-cyan-800/40">
                      {log.action}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-300">{log.resource}</td>
                  <td className="px-5 py-3 text-xs text-gray-400 font-mono">{log.resource_id || '—'}</td>
                  <td className="px-5 py-3">
                    <div className="flex items-center space-x-2">
                      {resultIcon(log.result)}
                      <span className="text-xs text-gray-300">{log.result}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3 text-xs text-gray-400 font-mono">{log.ip_address || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <div className="text-center py-12 text-gray-500 text-sm">No audit logs found</div>
          )}
        </div>
      )}
    </div>
  );
}
