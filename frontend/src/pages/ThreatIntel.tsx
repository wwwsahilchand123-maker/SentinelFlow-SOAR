import React, { useState, useEffect } from 'react';
import { Globe2, Search, Plus, ShieldCheck, ShieldAlert, RefreshCw, CheckCircle } from 'lucide-react';
import { threatIntelService } from '../services/api';
import { Indicator, IndicatorType, IndicatorReputation } from '../types';
import { ReputationBadge } from '../components/common/Badges';
import { formatDateTime } from '../utils/date';

export const ThreatIntel: React.FC = () => {
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [searchValue, setSearchValue] = useState('');
  const [lookupResult, setLookupResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [lookingUp, setLookingUp] = useState(false);

  const fetchIndicators = async () => {
    try {
      setLoading(true);
      const data = await threatIntelService.getIndicators();
      setIndicators(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIndicators();
  }, []);

  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchValue.trim()) return;
    try {
      setLookingUp(true);
      setLookupResult(null);
      const data = await threatIntelService.lookup(searchValue.trim());
      setLookupResult(data);
      fetchIndicators();
    } catch (err) {
      console.error(err);
    } finally {
      setLookingUp(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            <Globe2 className="w-6 h-6 text-cyan-400" />
            THREAT INTELLIGENCE & IOC ENGINE
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Reputation lookup, IOC correlation, and multi-source enrichment feeds
          </p>
        </div>

        <button
          onClick={fetchIndicators}
          disabled={loading}
          className="px-3.5 py-2 rounded-xl bg-dark-800 border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white transition-all flex items-center space-x-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh IOCs</span>
        </button>
      </div>

      {/* Live Lookup Search Box */}
      <div className="glass-panel p-6 rounded-2xl bg-dark-800 border border-gray-800 space-y-4">
        <div>
          <h3 className="text-sm font-bold text-white">Interactive Indicator (IOC) Lookup</h3>
          <p className="text-xs text-gray-400">Search any IPv4 address, domain, file hash, or email address for real-time reputation analysis</p>
        </div>

        <form onSubmit={handleLookup} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-gray-500 absolute left-3.5 top-3" />
            <input
              type="text"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="e.g. 185.220.101.45, malicious-domain.xyz, or deadbeef1234567890abcdef"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-dark-900 border border-gray-700 text-white font-mono placeholder-gray-500 text-xs focus:outline-none focus:border-cyan-500"
            />
          </div>
          <button
            type="submit"
            disabled={lookingUp}
            className="px-6 py-2.5 rounded-xl bg-cyan-500 text-dark-900 font-bold text-xs hover:bg-cyan-400 transition-colors flex items-center space-x-1.5 shadow-lg shadow-cyan-500/20 disabled:opacity-50"
          >
            <span>{lookingUp ? 'Analyzing...' : 'Analyze IOC'}</span>
          </button>
        </form>

        {lookupResult && (
          <div className="p-4 rounded-xl bg-dark-900 border border-cyan-800/60 mt-4 space-y-3 animate-in fade-in duration-200">
            <div className="flex items-center justify-between">
              <span className="font-mono text-cyan-400 font-bold text-xs">
                Target: {lookupResult.indicator?.value}
              </span>
              <ReputationBadge reputation={lookupResult.indicator?.reputation} />
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div>
                <span className="text-gray-500 block text-[10px] uppercase">Confidence</span>
                <span className="font-mono font-bold text-white">{lookupResult.indicator?.confidence}%</span>
              </div>
              <div>
                <span className="text-gray-500 block text-[10px] uppercase">IOC Type</span>
                <span className="font-mono text-gray-300">{lookupResult.indicator?.indicator_type}</span>
              </div>
              <div>
                <span className="text-gray-500 block text-[10px] uppercase">Source Provider</span>
                <span className="text-gray-300">{lookupResult.indicator?.source || 'Threat Intel Engine'}</span>
              </div>
              <div>
                <span className="text-gray-500 block text-[10px] uppercase">Engine Status</span>
                <span className="text-emerald-400 font-semibold">Active Ingestion</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Indicators Table */}
      <div className="glass-panel rounded-2xl bg-dark-800 border border-gray-800 overflow-hidden shadow-xl">
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 font-mono">
            Tracked Indicators Inventory ({indicators.length})
          </h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[10px] uppercase font-bold text-gray-400 border-b border-gray-800 bg-gray-900/60">
              <tr>
                <th className="py-3 px-4">Indicator Value</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Reputation</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Source</th>
                <th className="py-3 px-4">Tags</th>
                <th className="py-3 px-4">Last Seen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 font-medium">
              {indicators.map((ind) => (
                <tr key={ind.id} className="hover:bg-gray-800/40 transition-colors">
                  <td className="py-3 px-4 font-mono font-bold text-cyan-400">{ind.value}</td>
                  <td className="py-3 px-4 font-mono text-gray-300">{ind.indicator_type}</td>
                  <td className="py-3 px-4">
                    <ReputationBadge reputation={ind.reputation} />
                  </td>
                  <td className="py-3 px-4 font-mono font-bold">
                    <span className={ind.confidence >= 80 ? 'text-red-400' : ind.confidence >= 50 ? 'text-amber-400' : 'text-emerald-400'}>
                      {Math.round(ind.confidence)}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-300">{ind.source || 'Threat Intel Engine'}</td>
                  <td className="py-3 px-4">
                    {ind.tags ? (
                      <div className="flex flex-wrap gap-1">
                        {ind.tags.split(',').map((tag, i) => (
                          <span key={i} className="px-1.5 py-0.5 rounded bg-gray-800 text-[10px] text-gray-300 border border-gray-700">
                            {tag.trim()}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-gray-500">-</span>
                    )}
                  </td>
                  <td className="py-3 px-4 font-mono text-gray-400">
                    {ind.last_seen ? formatDateTime(ind.last_seen) : 'Recent'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
