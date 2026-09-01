import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Flame,
  Clock,
  Shield,
  Send,
  CheckCircle2,
  AlertTriangle,
  Lock,
  UserCheck,
  Server,
  Zap
} from 'lucide-react';
import { incidentService, assetService } from '../services/api';
import { Incident, IncidentStatus, IncidentSeverity } from '../types';
import { SeverityBadge, StatusBadge } from '../components/common/Badges';
import { RiskMeter } from '../components/common/RiskMeter';
import { formatDateTime } from '../utils/date';

export const IncidentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [newNote, setNewNote] = useState('');
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const fetchIncident = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await incidentService.getIncident(Number(id));
      setIncident(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncident();
  }, [id]);

  const handleStatusChange = async (newStatus: IncidentStatus) => {
    if (!incident) return;
    try {
      const updated = await incidentService.updateIncident(incident.id, { status: newStatus });
      setIncident(updated);
      setActionSuccess(`Incident status updated to ${newStatus}`);
      setTimeout(() => setActionSuccess(null), 3000);
      fetchIncident();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!incident || !newNote.trim()) return;
    try {
      await incidentService.addEvent(incident.id, {
        event_type: 'Analyst Note',
        description: newNote.trim(),
      });
      setNewNote('');
      fetchIncident();
    } catch (err) {
      console.error(err);
    }
  };

  const handleQuickMitigation = async (actionType: string) => {
    if (!incident) return;
    try {
      await incidentService.addEvent(incident.id, {
        event_type: 'Manual Containment',
        description: `[SIMULATED] Analyst executed manual mitigation: ${actionType}`,
      });
      setActionSuccess(`Executed mitigation action: ${actionType}`);
      setTimeout(() => setActionSuccess(null), 3000);
      fetchIncident();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="p-12 text-center text-gray-400">Loading incident command center...</div>;
  }

  if (!incident) {
    return (
      <div className="p-12 text-center space-y-4">
        <p className="text-red-400 font-bold">Incident Not Found</p>
        <Link to="/incidents" className="text-xs text-cyan-400 hover:underline">
          Return to incident queue
        </Link>
      </div>
    );
  }

  const statuses: IncidentStatus[] = ['Open', 'Investigating', 'Contained', 'Eradicated', 'Resolved', 'Closed'];

  return (
    <div className="space-y-6">
      {/* Back button & Title */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link
            to="/incidents"
            className="p-2 rounded-xl bg-dark-800 border border-gray-700 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-bold text-cyan-400 text-xs">{incident.incident_id}</span>
              <SeverityBadge severity={incident.severity} />
              <StatusBadge status={incident.status} />
            </div>
            <h2 className="text-xl font-bold text-white mt-1">{incident.title}</h2>
          </div>
        </div>

        <RiskMeter score={incident.risk_score} size="lg" />
      </div>

      {actionSuccess && (
        <div className="p-3 rounded-xl bg-emerald-950/80 border border-emerald-800 text-emerald-300 text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Incident Lifecycle Stepper */}
      <div className="glass-panel p-4 rounded-2xl bg-dark-800 border border-gray-800">
        <p className="text-[10px] uppercase font-bold text-gray-500 mb-3 font-mono">
          INCIDENT LIFECYCLE WORKFLOW
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
          {statuses.map((st) => (
            <button
              key={st}
              onClick={() => handleStatusChange(st)}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all text-center ${
                incident.status === st
                  ? 'bg-cyan-500 text-dark-900 shadow-lg shadow-cyan-500/20'
                  : 'bg-dark-900/80 hover:bg-gray-700/60 text-gray-400 border border-gray-800'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: Details + Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Metadata & Containment Actions */}
        <div className="space-y-6">
          <div className="glass-panel p-5 rounded-2xl bg-dark-800 border border-gray-800 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 font-mono">
              Incident Context
            </h3>
            <div className="p-3 rounded-xl bg-dark-900 border border-gray-800 text-xs text-gray-300 leading-relaxed">
              {incident.description || 'Automated security incident.'}
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-500">Source:</span>
                <span className="text-white font-medium">{incident.source || 'SOAR'}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-500">Created:</span>
                <span className="font-mono text-gray-300">
                  {formatDateTime(incident.created_at)}
                </span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-gray-800">
                <span className="text-gray-500">Last Updated:</span>
                <span className="font-mono text-gray-300">
                  {formatDateTime(incident.updated_at || incident.created_at)}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Containment Controls */}
          <div className="glass-panel p-5 rounded-2xl bg-dark-800 border border-gray-800 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5" />
              Manual Containment Actions
            </h3>
            <p className="text-[11px] text-gray-400">Trigger immediate out-of-band response tasks</p>
            <div className="space-y-2 pt-1">
              <button
                onClick={() => handleQuickMitigation('Firewall Perimeter Block (IP)')}
                className="w-full py-2 px-3 rounded-xl bg-red-950/60 hover:bg-red-900/80 text-red-300 border border-red-800/80 text-xs font-bold transition-all text-left flex items-center justify-between"
              >
                <span>Add IP to Firewall Blocklist</span>
                <Lock className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleQuickMitigation('EDR Endpoint Network Quarantine')}
                className="w-full py-2 px-3 rounded-xl bg-orange-950/60 hover:bg-orange-900/80 text-orange-300 border border-orange-800/80 text-xs font-bold transition-all text-left flex items-center justify-between"
              >
                <span>Isolate Host via EDR Agent</span>
                <Server className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleQuickMitigation('Revoke Active User Session & Force MFA')}
                className="w-full py-2 px-3 rounded-xl bg-purple-950/60 hover:bg-purple-900/80 text-purple-300 border border-purple-800/80 text-xs font-bold transition-all text-left flex items-center justify-between"
              >
                <span>Revoke Target User Sessions</span>
                <UserCheck className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Timeline & Evidence Locker */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl bg-dark-800 border border-gray-800 space-y-6">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              Investigation Timeline & Containment Events
            </h3>
            <p className="text-xs text-gray-400 mt-0.5">Chronological audit log of response actions and analyst notes</p>
          </div>

          {/* Timeline Feed */}
          <div className="space-y-4 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-800">
            {incident.events && incident.events.length > 0 ? (
              incident.events.map((evt, idx) => (
                <div key={idx} className="relative pl-8 text-xs">
                  <div className="absolute left-1.5 top-1.5 w-3.5 h-3.5 rounded-full bg-dark-900 border-2 border-cyan-400"></div>
                  <div className="p-3.5 rounded-xl bg-dark-900/80 border border-gray-800">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-cyan-300">{evt.event_type}</span>
                      <span className="text-[10px] font-mono text-gray-500">
                        {formatDateTime(evt.timestamp)}
                      </span>
                    </div>
                    <p className="text-gray-300 mt-1">{evt.description}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-gray-500 pl-8">No events logged yet.</p>
            )}
          </div>

          {/* Add Analyst Note Form */}
          <form onSubmit={handleAddNote} className="pt-4 border-t border-gray-800 space-y-2">
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-400">
              Add Analyst Note / Action Record
            </label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Log investigative notes, triage findings, or containment confirmation..."
                className="flex-1 px-4 py-2.5 rounded-xl bg-dark-900 border border-gray-700 text-white placeholder-gray-500 text-xs focus:outline-none focus:border-cyan-500"
              />
              <button
                type="submit"
                className="px-4 py-2.5 rounded-xl bg-cyan-500 text-dark-900 font-bold text-xs hover:bg-cyan-400 transition-colors flex items-center space-x-1.5"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Post Note</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
