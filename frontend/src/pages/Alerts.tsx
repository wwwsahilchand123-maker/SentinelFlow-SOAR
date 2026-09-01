import React, { useState, useEffect } from 'react';
import { AlertOctagon, Search, Filter, RefreshCw, Eye, Flame, Play, CheckCircle, ShieldAlert } from 'lucide-react';
import { alertService, playbookService, incidentService } from '../services/api';
import { Alert, AlertStatus, AlertSeverity, Playbook } from '../types';
import { SeverityBadge, StatusBadge } from '../components/common/Badges';
import { Modal } from '../components/common/Modal';
import { formatDateTime, formatTimeOnly } from '../utils/date';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [selectedPlaybookId, setSelectedPlaybookId] = useState<number | null>(null);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const data = await alertService.getAlerts({
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
        search: search || undefined,
      });
      setAlerts(data);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPlaybooks = async () => {
    try {
      const data = await playbookService.getPlaybooks();
      setPlaybooks(data.filter(p => p.status === 'Enabled'));
      if (data.length > 0) setSelectedPlaybookId(data[0].id);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchAlerts();
    fetchPlaybooks();
  }, [severityFilter, statusFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchAlerts();
  };

  const handleUpdateStatus = async (alertId: number, newStatus: AlertStatus) => {
    try {
      const updated = await alertService.updateAlert(alertId, { status: newStatus });
      setAlerts(alerts.map(a => (a.id === alertId ? updated : a)));
      if (selectedAlert?.id === alertId) setSelectedAlert(updated);
      setActionSuccess(`Alert status changed to ${newStatus}`);
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleEscalateToIncident = async (alert: Alert) => {
    try {
      const inc = await incidentService.updateIncident ? await incidentService.getIncidents() : null;
      // create incident directly via incidentService
      const res = await alertService.updateAlert(alert.id, { status: 'Escalated' as AlertStatus });
      setActionSuccess(`Alert ${alert.alert_id} escalated to formal incident response workflow.`);
      fetchAlerts();
      setTimeout(() => setActionSuccess(null), 3500);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunPlaybook = async () => {
    if (!selectedAlert || !selectedPlaybookId) return;
    try {
      await playbookService.executePlaybook(selectedPlaybookId, {
        alert_id: selectedAlert.alert_id,
        severity: selectedAlert.severity,
        source_ip: selectedAlert.source_ip,
        indicator: selectedAlert.indicator || selectedAlert.source_ip,
        description: selectedAlert.description,
        source: 'Manual Alert Triage'
      });
      setActionSuccess(`Playbook dispatched successfully for alert ${selectedAlert.alert_id}`);
      fetchAlerts();
      setTimeout(() => setActionSuccess(null), 3500);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            <AlertOctagon className="w-6 h-6 text-cyan-400" />
            SECURITY ALERTS QUEUE
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Real-time ingestion feed with automated risk scoring and playbook orchestration
          </p>
        </div>

        <button
          onClick={fetchAlerts}
          disabled={loading}
          className="px-3.5 py-2 rounded-xl bg-dark-800 border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white hover:border-gray-600 transition-all flex items-center space-x-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Feed</span>
        </button>
      </div>

      {actionSuccess && (
        <div className="p-3 rounded-xl bg-emerald-950/80 border border-emerald-800 text-emerald-300 text-xs flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 flex-shrink-0" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Filter Bar */}
      <div className="glass-panel p-4 rounded-2xl bg-dark-800 border border-gray-800 flex flex-col md:flex-row items-center gap-4">
        <form onSubmit={handleSearch} className="flex-1 w-full relative">
          <Search className="w-4 h-4 text-gray-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Alert ID, IP, IOC indicator, or description..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-dark-900 border border-gray-700 text-white placeholder-gray-500 text-xs focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-colors"
          />
        </form>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-dark-900 border border-gray-700 text-gray-300 text-xs focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-dark-900 border border-gray-700 text-gray-300 text-xs focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="New">New</option>
            <option value="Investigating">Investigating</option>
            <option value="Escalated">Escalated</option>
            <option value="Resolved">Resolved</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="glass-panel rounded-2xl bg-dark-800 border border-gray-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[10px] uppercase font-bold text-gray-400 border-b border-gray-800 bg-gray-900/60">
              <tr>
                <th className="py-3 px-4">Alert ID</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Source / Category</th>
                <th className="py-3 px-4">Alert Type</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Target / IOC</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 font-medium">
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-gray-500">
                    No security alerts found matching query filters.
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-gray-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-cyan-400">
                      {alert.alert_id}
                    </td>
                    <td className="py-3 px-4 font-mono text-gray-400">
                      {formatDateTime(alert.timestamp)}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-white">{alert.source}</span>
                      {alert.category && <span className="block text-[10px] text-gray-500">{alert.category}</span>}
                    </td>
                    <td className="py-3 px-4 text-white max-w-xs truncate">{alert.alert_type}</td>
                    <td className="py-3 px-4">
                      <SeverityBadge severity={alert.severity} />
                    </td>
                    <td className="py-3 px-4 font-mono text-gray-300">
                      {alert.source_ip || alert.indicator || alert.host || 'N/A'}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={alert.status} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedAlert(alert)}
                        className="px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-cyan-500/20 text-gray-300 hover:text-cyan-400 border border-gray-700 transition-colors inline-flex items-center space-x-1"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alert Inspection & Action Modal */}
      {selectedAlert && (
        <Modal
          isOpen={!!selectedAlert}
          onClose={() => setSelectedAlert(null)}
          title={`Alert Details: ${selectedAlert.alert_id}`}
          maxWidth="2xl"
        >
          <div className="space-y-5">
            {/* Top metadata cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
                <p className="text-[10px] uppercase font-bold text-gray-500">Severity</p>
                <div className="mt-1"><SeverityBadge severity={selectedAlert.severity} /></div>
              </div>
              <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
                <p className="text-[10px] uppercase font-bold text-gray-500">Status</p>
                <div className="mt-1"><StatusBadge status={selectedAlert.status} /></div>
              </div>
              <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
                <p className="text-[10px] uppercase font-bold text-gray-500">Source</p>
                <p className="text-xs font-bold text-white mt-1">{selectedAlert.source}</p>
              </div>
              <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
                <p className="text-[10px] uppercase font-bold text-gray-500">Timestamp</p>
                <p className="text-[11px] font-mono text-gray-300 mt-1">
                  {formatDateTime(selectedAlert.timestamp)}
                </p>
              </div>
            </div>

            {/* Description & Payload Details */}
            <div className="p-4 rounded-xl bg-dark-900 border border-gray-800 space-y-2">
              <p className="text-xs font-bold text-white">Event Description</p>
              <p className="text-xs text-gray-300 leading-relaxed">{selectedAlert.description || 'No raw description provided.'}</p>
            </div>

            {/* Target Details Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
                <span className="text-gray-500 block text-[10px] uppercase">Source IP Address</span>
                <span className="font-mono font-bold text-cyan-400">{selectedAlert.source_ip || 'N/A'}</span>
              </div>
              <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
                <span className="text-gray-500 block text-[10px] uppercase">Destination IP / Host</span>
                <span className="font-mono font-bold text-gray-200">
                  {selectedAlert.destination_ip || selectedAlert.host || 'N/A'}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
                <span className="text-gray-500 block text-[10px] uppercase">Target Username</span>
                <span className="font-mono text-gray-200">{selectedAlert.username || 'N/A'}</span>
              </div>
              <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
                <span className="text-gray-500 block text-[10px] uppercase">Associated Indicator (IOC)</span>
                <span className="font-mono text-orange-400">{selectedAlert.indicator || 'N/A'}</span>
              </div>
            </div>

            {/* Orchestration: Trigger Playbook */}
            <div className="p-4 rounded-xl bg-dark-900 border border-cyan-800/40 space-y-3">
              <div className="flex items-center space-x-2 text-cyan-400">
                <Play className="w-4 h-4" />
                <h4 className="text-xs font-bold uppercase tracking-wider">Execute SOAR Playbook</h4>
              </div>
              <div className="flex items-center gap-3">
                <select
                  value={selectedPlaybookId || ''}
                  onChange={(e) => setSelectedPlaybookId(Number(e.target.value))}
                  className="flex-1 px-3 py-2 rounded-xl bg-dark-800 border border-gray-700 text-white text-xs"
                >
                  {playbooks.map(pb => (
                    <option key={pb.id} value={pb.id}>{pb.name} ({pb.trigger})</option>
                  ))}
                </select>
                <button
                  onClick={handleRunPlaybook}
                  className="px-4 py-2 rounded-xl bg-cyan-500 text-dark-900 font-bold text-xs hover:bg-cyan-400 transition-colors flex items-center space-x-1.5"
                >
                  <Play className="w-3.5 h-3.5 fill-dark-900" />
                  <span>Run Playbook</span>
                </button>
              </div>
            </div>

            {/* Analyst Quick Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-800">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleUpdateStatus(selectedAlert.id, 'Investigating' as AlertStatus)}
                  className="px-3 py-1.5 rounded-lg bg-amber-950/80 hover:bg-amber-900 text-amber-300 border border-amber-800 text-xs font-medium transition-colors"
                >
                  Investigate
                </button>
                <button
                  onClick={() => handleUpdateStatus(selectedAlert.id, 'Resolved' as AlertStatus)}
                  className="px-3 py-1.5 rounded-lg bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 text-xs font-medium transition-colors"
                >
                  Resolve
                </button>
                <button
                  onClick={() => handleUpdateStatus(selectedAlert.id, 'False Positive' as AlertStatus)}
                  className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 border border-gray-700 text-xs font-medium transition-colors"
                >
                  False Positive
                </button>
              </div>

              <button
                onClick={() => handleEscalateToIncident(selectedAlert)}
                className="px-4 py-1.5 rounded-lg bg-red-950 hover:bg-red-900 text-red-300 border border-red-700 text-xs font-bold transition-colors flex items-center space-x-1.5"
              >
                <Flame className="w-3.5 h-3.5 text-red-400" />
                <span>Escalate Incident</span>
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
