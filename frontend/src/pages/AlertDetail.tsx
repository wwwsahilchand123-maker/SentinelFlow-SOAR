import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ShieldAlert, Clock, Server, User, Globe, Hash } from 'lucide-react';
import { alertService } from '../services/api';
import { SeverityBadge, StatusBadge } from '../components/common/Badges';
import { Alert } from '../types';
import { formatDateTime } from '../utils/date';

const formatDate = (d?: string) => formatDateTime(d);

export default function AlertDetail() {
  const { id } = useParams<{ id: string }>();
  const [alert, setAlert] = useState<Alert | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (id) fetchAlert();
  }, [id]);

  const fetchAlert = async () => {
    try {
      setLoading(true);
      const data = await alertService.getAlert(Number(id));
      setAlert(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!alert) return;
    try {
      setUpdating(true);
      const updated = await alertService.updateAlert(alert.id, { status: newStatus as any });
      setAlert(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!alert) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Alert not found</p>
        <Link to="/alerts" className="text-cyan-400 hover:underline mt-2 inline-block">← Back to Alerts</Link>
      </div>
    );
  }

  const infoItems = [
    { label: 'Alert ID', value: alert.alert_id, icon: Hash },
    { label: 'Source', value: alert.source, icon: Server },
    { label: 'Type', value: alert.alert_type, icon: ShieldAlert },
    { label: 'Category', value: alert.category || '—', icon: ShieldAlert },
    { label: 'Source IP', value: alert.source_ip || '—', icon: Globe },
    { label: 'Destination IP', value: alert.destination_ip || '—', icon: Globe },
    { label: 'Username', value: alert.username || '—', icon: User },
    { label: 'Host', value: alert.host || '—', icon: Server },
    { label: 'Timestamp', value: formatDate(alert.timestamp), icon: Clock },
    { label: 'Created', value: formatDate(alert.created_at), icon: Clock },
    { label: 'Updated', value: formatDate(alert.updated_at), icon: Clock },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/alerts" className="p-2 rounded-xl hover:bg-gray-800 text-gray-400 hover:text-white transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-white">{alert.alert_type}</h1>
            <p className="text-sm text-gray-400 font-mono">{alert.alert_id}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <SeverityBadge severity={alert.severity} />
          <StatusBadge status={alert.status} />
        </div>
      </div>

      {alert.description && (
        <div className="glass-panel rounded-2xl p-5">
          <h3 className="text-sm font-bold text-gray-300 mb-2">Description</h3>
          <p className="text-gray-400 text-sm">{alert.description}</p>
        </div>
      )}

      <div className="glass-panel rounded-2xl p-5">
        <h3 className="text-sm font-bold text-gray-300 mb-4">Alert Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {infoItems.map((item) => (
            <div key={item.label} className="flex items-start space-x-3 p-3 bg-dark-800/60 rounded-xl">
              <item.icon className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-[11px] text-gray-500 uppercase font-semibold tracking-wider">{item.label}</p>
                <p className="text-sm text-gray-200 font-mono">{item.value}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-panel rounded-2xl p-5">
        <h3 className="text-sm font-bold text-gray-300 mb-4">Actions</h3>
        <div className="flex flex-wrap gap-2">
          {['New', 'Investigating', 'Escalated', 'Resolved', 'False Positive'].map((s) => (
            <button
              key={s}
              onClick={() => handleStatusChange(s)}
              disabled={updating || alert.status === s}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                alert.status === s
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                  : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700 border border-gray-700'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
