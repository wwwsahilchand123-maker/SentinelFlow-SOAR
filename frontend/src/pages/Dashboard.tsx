import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertOctagon,
  Flame,
  Zap,
  Clock,
  ShieldAlert,
  Server,
  Activity,
  ArrowUpRight,
  RefreshCw,
  TrendingUp,
  Cpu
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { dashboardService, incidentService } from '../services/api';
import { DashboardStats, Incident } from '../types';
import { StatCard } from '../components/common/StatCard';
import { SeverityBadge, StatusBadge } from '../components/common/Badges';
import { formatTimeOnly } from '../utils/date';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [alertsOverTime, setAlertsOverTime] = useState<any[]>([]);
  const [incidentsBySeverity, setIncidentsBySeverity] = useState<any[]>([]);
  const [alertSources, setAlertSources] = useState<any[]>([]);
  const [activeIncidents, setActiveIncidents] = useState<Incident[]>([]);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [sData, aData, iSevData, srcData, incData, actData] = await Promise.all([
        dashboardService.getStats(),
        dashboardService.getAlertsOverTime(7),
        dashboardService.getIncidentsBySeverity(),
        dashboardService.getAlertSources(),
        incidentService.getIncidents({ status: 'Open' }),
        dashboardService.getRecentActivity(8),
      ]);
      setStats(sData);
      setAlertsOverTime(aData);
      setIncidentsBySeverity(iSevData);
      setAlertSources(srcData);
      setActiveIncidents(incData.slice(0, 5));
      setRecentActivity(actData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const SEVERITY_COLORS: Record<string, string> = {
    Critical: '#EF4444',
    High: '#F97316',
    Medium: '#FBBF24',
    Low: '#10B981',
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Refresh */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            SOC COMMAND CENTER
            <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
              REAL-TIME ORCHESTRATION
            </span>
          </h2>
          <p className="text-xs text-gray-400 mt-1">Autonomous alert triage, threat enrichment, and mitigation engine</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-dark-800 border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white hover:border-gray-600 transition-all flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Telemetry</span>
          </button>
          <Link
            to="/simulation"
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 text-dark-900 font-bold text-xs hover:from-orange-400 hover:to-amber-400 transition-all flex items-center space-x-1.5 shadow-lg shadow-orange-500/20"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Launch Attack Simulator</span>
          </Link>
        </div>
      </div>

      {/* KPI Stat Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Ingested Alerts"
          value={stats?.total_alerts || 0}
          subtitle="Past 7 days volume"
          icon={<AlertOctagon className="w-6 h-6 text-cyan-400" />}
          highlightColor="cyan"
          trend={{ value: '+14%', isPositive: false }}
        />
        <StatCard
          title="Active Critical Incidents"
          value={stats?.critical_alerts || 0}
          subtitle="Requiring immediate response"
          icon={<Flame className="w-6 h-6 text-red-400" />}
          highlightColor="red"
          trend={{ value: '-5%', isPositive: true }}
        />
        <StatCard
          title="Automated Actions"
          value={stats?.automated_actions || 0}
          subtitle="Simulated mitigations executed"
          icon={<Cpu className="w-6 h-6 text-emerald-400" />}
          highlightColor="emerald"
        />
        <StatCard
          title="Mean Time To Respond"
          value={`${stats?.mean_time_to_respond || 6.5}m`}
          subtitle={`MTTR Resolution: ${stats?.mean_time_to_resolve || 32}m`}
          icon={<Clock className="w-6 h-6 text-amber-400" />}
          highlightColor="amber"
          trend={{ value: '-42%', isPositive: true }}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts Ingestion Trend */}
        <div className="lg:col-span-2 glass-panel bg-dark-800 p-5 rounded-2xl border border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-cyan-400" />
                Alert Ingestion Timeline
              </h3>
              <p className="text-xs text-gray-400">Security event frequency aggregated daily</p>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={alertsOverTime} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="alertGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#00F0FF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="date" stroke="#6B7280" fontSize={11} tickLine={false} />
                <YAxis stroke="#6B7280" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '0.75rem', fontSize: '12px' }}
                  itemStyle={{ color: '#00F0FF' }}
                />
                <Area type="monotone" dataKey="count" stroke="#00F0FF" strokeWidth={2.5} fillOpacity={1} fill="url(#alertGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Breakdown */}
        <div className="glass-panel bg-dark-800 p-5 rounded-2xl border border-gray-800">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-1">
            <ShieldAlert className="w-4 h-4 text-orange-400" />
            Incidents by Severity
          </h3>
          <p className="text-xs text-gray-400 mb-4">Distribution by threat impact level</p>
          <div className="h-64 flex items-center justify-center">
            {incidentsBySeverity.length === 0 ? (
              <p className="text-xs text-gray-500">No active incident data</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={incidentsBySeverity}
                    dataKey="count"
                    nameKey="severity"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={4}
                  >
                    {incidentsBySeverity.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={SEVERITY_COLORS[entry.severity] || '#6B7280'} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '0.75rem', fontSize: '12px' }}
                  />
                  <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '11px' }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Lower Row: Active Incidents & Automation Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Incidents Queue */}
        <div className="lg:col-span-2 glass-panel bg-dark-800 p-5 rounded-2xl border border-gray-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Flame className="w-4 h-4 text-red-400" />
                Active Security Incidents
              </h3>
              <p className="text-xs text-gray-400">Cases undergoing containment or investigation</p>
            </div>
            <Link
              to="/incidents"
              className="text-xs text-cyan-400 hover:underline flex items-center gap-1 font-semibold"
            >
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[10px] uppercase font-bold text-gray-500 border-b border-gray-800 bg-gray-900/40">
                <tr>
                  <th className="py-2.5 px-3">Incident ID</th>
                  <th className="py-2.5 px-3">Title</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Risk Score</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 font-medium">
                {activeIncidents.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-6 text-center text-gray-500">
                      No active open incidents. System secure.
                    </td>
                  </tr>
                ) : (
                  activeIncidents.map((inc) => (
                    <tr key={inc.id} className="hover:bg-gray-800/40 transition-colors">
                      <td className="py-3 px-3 font-mono font-bold text-cyan-400">
                        <Link to={`/incidents/${inc.id}`} className="hover:underline">
                          {inc.incident_id}
                        </Link>
                      </td>
                      <td className="py-3 px-3 text-white max-w-xs truncate">{inc.title}</td>
                      <td className="py-3 px-3">
                        <SeverityBadge severity={inc.severity} />
                      </td>
                      <td className="py-3 px-3 font-mono font-bold">
                        <span className={inc.risk_score >= 80 ? 'text-red-400' : inc.risk_score >= 60 ? 'text-orange-400' : 'text-amber-400'}>
                          {Math.round(inc.risk_score)}/100
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <StatusBadge status={inc.status} />
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Live SOC Activity Stream */}
        <div className="glass-panel bg-dark-800 p-5 rounded-2xl border border-gray-800">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-1">
            <Activity className="w-4 h-4 text-cyan-400" />
            SOC Activity Stream
          </h3>
          <p className="text-xs text-gray-400 mb-4">Real-time audit & automation logs</p>

          <div className="space-y-3">
            {recentActivity.length === 0 ? (
              <p className="text-xs text-gray-500 text-center py-6">No recent actions logged</p>
            ) : (
              recentActivity.map((act, i) => (
                <div key={i} className="p-2.5 rounded-xl bg-gray-900/50 border border-gray-800 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-cyan-300">{act.action}</span>
                    <span className="text-[10px] text-gray-500 font-mono">
                      {formatTimeOnly(act.timestamp)}
                    </span>
                  </div>
                  <p className="text-gray-400 text-[11px] mt-1">
                    Resource: <span className="text-gray-200 font-semibold">{act.resource}</span> ({act.resource_id || 'N/A'})
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
