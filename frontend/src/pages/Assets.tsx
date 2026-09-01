import React, { useState, useEffect } from 'react';
import { Server, Shield, Wifi, WifiOff, Search, RefreshCw } from 'lucide-react';
import { assetService } from '../services/api';
import { SeverityBadge } from '../components/common/Badges';
import { Asset } from '../types';
import { formatDateTime } from '../utils/date';

const formatDate = (d?: string) => formatDateTime(d);

export default function Assets() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchAssets();
  }, [statusFilter]);

  const fetchAssets = async () => {
    try {
      setLoading(true);
      const data = await assetService.getAssets(
        statusFilter ? { status: statusFilter } : undefined
      );
      setAssets(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleIsolate = async (id: number, isolate: boolean) => {
    try {
      await assetService.toggleIsolate(id, isolate);
      fetchAssets();
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = assets.filter(a =>
    a.hostname.toLowerCase().includes(search.toLowerCase()) ||
    a.asset_id.toLowerCase().includes(search.toLowerCase()) ||
    (a.ip_address && a.ip_address.includes(search))
  );

  const statusIcon = (status: string) => {
    switch (status) {
      case 'Online': return <Wifi className="w-4 h-4 text-emerald-400" />;
      case 'Offline': return <WifiOff className="w-4 h-4 text-gray-500" />;
      case 'Quarantined': return <Shield className="w-4 h-4 text-red-400" />;
      default: return <Server className="w-4 h-4 text-amber-400" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Asset Inventory</h1>
          <p className="text-sm text-gray-400">Manage and monitor organizational assets</p>
        </div>
        <button onClick={fetchAssets} className="p-2 rounded-xl hover:bg-gray-800 text-gray-400 hover:text-white transition-colors">
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      <div className="flex items-center space-x-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="Search by hostname, asset ID, or IP..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-800 border border-gray-700 rounded-xl text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-dark-800 border border-gray-700 rounded-xl px-3 py-2.5 text-sm text-gray-200 focus:outline-none focus:border-cyan-500/50"
        >
          <option value="">All Status</option>
          <option value="Online">Online</option>
          <option value="Offline">Offline</option>
          <option value="Quarantined">Quarantined</option>
          <option value="Maintenance">Maintenance</option>
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
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Asset</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">IP Address</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">OS</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Criticality</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Last Seen</th>
                <th className="px-5 py-3 text-xs font-bold text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {filtered.map((asset) => (
                <tr key={asset.id} className="hover:bg-gray-800/30 transition-colors">
                  <td className="px-5 py-3">
                    <div className="flex items-center space-x-3">
                      <Server className="w-4 h-4 text-cyan-400" />
                      <div>
                        <p className="text-sm font-semibold text-white">{asset.hostname}</p>
                        <p className="text-xs text-gray-500 font-mono">{asset.asset_id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-3 text-sm font-mono text-gray-300">{asset.ip_address || '—'}</td>
                  <td className="px-5 py-3 text-sm text-gray-300">{asset.operating_system || '—'}</td>
                  <td className="px-5 py-3"><SeverityBadge severity={asset.criticality} /></td>
                  <td className="px-5 py-3">
                    <div className="flex items-center space-x-2">
                      {statusIcon(asset.status)}
                      <span className="text-sm text-gray-300">{asset.status}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3 text-xs text-gray-400">{formatDate(asset.last_seen)}</td>
                  <td className="px-5 py-3">
                    {asset.status === 'Quarantined' ? (
                      <button
                        onClick={() => handleIsolate(asset.id, false)}
                        className="text-xs px-2 py-1 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 hover:bg-emerald-900 transition-colors"
                      >
                        Release
                      </button>
                    ) : (
                      <button
                        onClick={() => handleIsolate(asset.id, true)}
                        className="text-xs px-2 py-1 rounded bg-red-950 text-red-400 border border-red-800 hover:bg-red-900 transition-colors"
                      >
                        Isolate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <div className="text-center py-12 text-gray-500 text-sm">No assets found</div>
          )}
        </div>
      )}
    </div>
  );
}
