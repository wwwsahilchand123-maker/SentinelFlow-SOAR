import React from 'react';
import { AlertSeverity, AlertStatus, IncidentSeverity, IncidentStatus, IndicatorReputation } from '../../types';

export const SeverityBadge: React.FC<{ severity: AlertSeverity | IncidentSeverity | string }> = ({ severity }) => {
  const styles: Record<string, string> = {
    Critical: 'bg-red-950/80 text-red-400 border border-red-800/60',
    High: 'bg-orange-950/80 text-orange-400 border border-orange-800/60',
    Medium: 'bg-amber-950/80 text-amber-400 border border-amber-800/60',
    Low: 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60',
    Informational: 'bg-blue-950/80 text-blue-400 border border-blue-800/60',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wider ${styles[severity] || 'bg-gray-800 text-gray-300'}`}>
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current animate-pulse"></span>
      {severity}
    </span>
  );
};

export const StatusBadge: React.FC<{ status: AlertStatus | IncidentStatus | string }> = ({ status }) => {
  const styles: Record<string, string> = {
    New: 'bg-blue-900/50 text-blue-300 border border-blue-700/50',
    Open: 'bg-red-900/50 text-red-300 border border-red-700/50',
    Investigating: 'bg-amber-900/50 text-amber-300 border border-amber-700/50',
    Contained: 'bg-purple-900/50 text-purple-300 border border-purple-700/50',
    Eradicated: 'bg-indigo-900/50 text-indigo-300 border border-indigo-700/50',
    Resolved: 'bg-emerald-900/50 text-emerald-300 border border-emerald-700/50',
    Closed: 'bg-gray-800 text-gray-400 border border-gray-700',
    'False Positive': 'bg-gray-800 text-gray-400 border border-gray-700',
    Escalated: 'bg-red-900 text-red-200 border border-red-600',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${styles[status] || 'bg-gray-800 text-gray-300'}`}>
      {status}
    </span>
  );
};

export const ReputationBadge: React.FC<{ reputation: IndicatorReputation | string }> = ({ reputation }) => {
  const styles: Record<string, string> = {
    Malicious: 'bg-red-900/60 text-red-300 border border-red-700',
    Suspicious: 'bg-amber-900/60 text-amber-300 border border-amber-700',
    Benign: 'bg-emerald-900/60 text-emerald-300 border border-emerald-700',
    Unknown: 'bg-gray-800 text-gray-400 border border-gray-700',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${styles[reputation] || 'bg-gray-800 text-gray-300'}`}>
      {reputation}
    </span>
  );
};
