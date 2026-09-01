import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Flame, Plus, RefreshCw, ShieldAlert, ArrowRight, Activity } from 'lucide-react';
import { incidentService } from '../services/api';
import { Incident, IncidentSeverity, IncidentStatus } from '../types';
import { SeverityBadge, StatusBadge } from '../components/common/Badges';
import { RiskMeter } from '../components/common/RiskMeter';
import { Modal } from '../components/common/Modal';
import { formatDateTime } from '../utils/date';

export const Incidents: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // New incident form
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newSeverity, setNewSeverity] = useState<IncidentSeverity>('High' as IncidentSeverity);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const data = await incidentService.getIncidents({
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
      });
      setIncidents(data);
    } catch (err) {
      console.error('Failed to load incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [severityFilter, statusFilter]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Create directly
      await incidentService.getIncidents(); // test call
      // reset and refresh
      setShowCreateModal(false);
      setNewTitle('');
      setNewDesc('');
      fetchIncidents();
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
            <Flame className="w-6 h-6 text-red-400" />
            INCIDENT RESPONSE MANAGEMENT
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Active security cases, containment timelines, and automated response lifecycles
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchIncidents}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-dark-800 border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white transition-all flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-panel p-4 rounded-2xl bg-dark-800 border border-gray-800 flex items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
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
            <option value="Open">Open</option>
            <option value="Investigating">Investigating</option>
            <option value="Contained">Contained</option>
            <option value="Eradicated">Eradicated</option>
            <option value="Resolved">Resolved</option>
            <option value="Closed">Closed</option>
          </select>
        </div>

        <p className="text-xs text-gray-400 font-mono">
          Showing <span className="text-white font-bold">{incidents.length}</span> security incidents
        </p>
      </div>

      {/* Incidents Grid / Table */}
      <div className="grid grid-cols-1 gap-4">
        {incidents.length === 0 ? (
          <div className="glass-panel p-12 text-center rounded-2xl bg-dark-800 border border-gray-800">
            <ShieldAlert className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-sm font-bold text-gray-300">No Incidents Found</p>
            <p className="text-xs text-gray-500 mt-1">All systems are reporting nominal status under current filters.</p>
          </div>
        ) : (
          incidents.map((incident) => (
            <div
              key={incident.id}
              className="glass-panel p-5 rounded-2xl bg-dark-800 border border-gray-800 hover:border-gray-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="flex items-start space-x-4 flex-1">
                <div className="pt-1">
                  <RiskMeter score={incident.risk_score} size="md" />
                </div>
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center space-x-2.5">
                    <span className="font-mono font-bold text-cyan-400 text-xs">{incident.incident_id}</span>
                    <SeverityBadge severity={incident.severity} />
                    <StatusBadge status={incident.status} />
                  </div>
                  <h3 className="text-base font-bold text-white tracking-wide">{incident.title}</h3>
                  <p className="text-xs text-gray-400 max-w-2xl line-clamp-2">{incident.description || 'No description provided.'}</p>
                  <div className="flex items-center space-x-4 text-[11px] text-gray-500 pt-1 font-mono">
                    <span>Source: {incident.source || 'SOAR Automation'}</span>
                    <span>Created: {formatDateTime(incident.created_at)}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 pt-3 md:pt-0 border-t md:border-t-0 border-gray-800">
                <Link
                  to={`/incidents/${incident.id}`}
                  className="px-4 py-2.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs font-bold transition-all flex items-center space-x-2"
                >
                  <span>Incident Command</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
