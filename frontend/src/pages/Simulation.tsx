import React, { useState } from 'react';
import {
  Crosshair,
  Zap,
  ShieldAlert,
  Mail,
  Server,
  Terminal,
  Lock,
  Globe2,
  FileCode,
  CheckCircle2,
  Cpu,
  ArrowRight
} from 'lucide-react';
import { simulationService } from '../services/api';

export const Simulation: React.FC = () => {
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [simulationResult, setSimulationResult] = useState<any | null>(null);

  const scenarios = [
    {
      id: 'brute-force',
      title: 'Brute Force Attack',
      vector: 'Authentication / SSH',
      target: '185.220.101.45 (Tor Exit)',
      severity: 'High',
      description: 'Simulates 25 rapid failed SSH/RDP login attempts. Tests auto-escalation, risk score calculation, and simulated perimeter firewall IP blocklist rule injection.',
      icon: Lock,
      color: 'border-orange-500/40 text-orange-400',
    },
    {
      id: 'phishing',
      title: 'Spear Phishing Campaign',
      vector: 'Email Security',
      target: 'malicious-domain.xyz',
      severity: 'High',
      description: 'Simulates an incoming spear-phishing email targeting the corporate finance team. Triggers threat intel domain lookup and automated mailbox quarantine action.',
      icon: Mail,
      color: 'border-cyan-500/40 text-cyan-400',
    },
    {
      id: 'malicious-ip',
      title: 'Malicious C2 IP Connection',
      vector: 'Perimeter Firewall',
      target: '185.220.102.8 (Known C2)',
      severity: 'Critical',
      description: 'Simulates an unauthorized inbound connection attempt from a known botnet command & control server directly into internal subnets.',
      icon: Globe2,
      color: 'border-red-500/40 text-red-400',
    },
    {
      id: 'malware',
      title: 'Endpoint Malware Detection',
      vector: 'EDR / Endpoint Agent',
      target: 'WORKSTATION-042 (Finance)',
      severity: 'Critical',
      description: 'Simulates malware file hash detection in a user temporary folder. Evaluates file reputation against VirusTotal and executes simulated network host isolation.',
      icon: Server,
      color: 'border-red-500/40 text-red-400',
    },
    {
      id: 'suspicious-login',
      title: 'Impossible Travel Login',
      vector: 'Identity Provider (IdP)',
      target: 'User: jsmith (UK -> UA)',
      severity: 'Medium',
      description: 'Simulates simultaneous logins from anomalous geographic regions without multi-factor authentication. Dispatches analyst alert notifications.',
      icon: Terminal,
      color: 'border-amber-500/40 text-amber-400',
    },
    {
      id: 'data-exfiltration',
      title: 'Data Exfiltration Spike',
      vector: 'DLP / Cloud Proxy',
      target: '192.168.1.150 -> Unsanctioned Cloud',
      severity: 'Critical',
      description: 'Simulates an abnormal 8.5 GB encrypted payload transfer to an external bucket during off-hours. Initiates high-severity incident escalation.',
      icon: FileCode,
      color: 'border-purple-500/40 text-purple-400',
    },
  ];

  const handleRun = async (scenarioId: string) => {
    setActiveScenario(scenarioId);
    setRunning(true);
    setSimulationResult(null);

    try {
      const res = await simulationService.triggerScenario(scenarioId);
      setSimulationResult(res);
    } catch (err: any) {
      console.error(err);
      setSimulationResult({ error: err.message || 'Simulation failed' });
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
            <Crosshair className="w-6 h-6 text-orange-400" />
            ATTACK SCENARIO SIMULATOR
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Test and validate end-to-end SOAR detection, automated playbook triage, and simulated containment
          </p>
        </div>
      </div>

      {/* Interactive Simulation Results Banner */}
      {simulationResult && (
        <div className="glass-panel p-6 rounded-2xl bg-dark-800 border border-cyan-500/40 shadow-xl shadow-cyan-500/5 space-y-3 animate-in fade-in zoom-in-95 duration-200">
          <div className="flex items-center space-x-2 text-cyan-400">
            <CheckCircle2 className="w-5 h-5" />
            <h3 className="text-sm font-bold uppercase tracking-wider">
              Simulation Executed Successfully
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-1">
            <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
              <span className="text-gray-500 block text-[10px] uppercase font-mono">Ingested Alert ID</span>
              <span className="font-mono font-bold text-cyan-400">
                {simulationResult.result?.alert_id || 'ALT-CREATED'}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
              <span className="text-gray-500 block text-[10px] uppercase font-mono">Triggered Rules</span>
              <span className="font-mono font-bold text-emerald-400">
                {simulationResult.result?.triggered_rules_count || 1} Rule(s) Matched
              </span>
            </div>
            <div className="p-3 rounded-xl bg-dark-900 border border-gray-800">
              <span className="text-gray-500 block text-[10px] uppercase font-mono">Executed Playbooks</span>
              <span className="font-mono font-bold text-purple-400">
                {simulationResult.result?.executed_playbooks?.join(', ') || 'EXEC-AUTOMATED'}
              </span>
            </div>
          </div>

          <p className="text-xs text-gray-300">
            The security alert was ingested, enriched against threat intelligence feeds, evaluated by automation rules, and dispatched to the corresponding SOAR playbook for mitigation. Check the <strong>Security Alerts</strong> and <strong>Incidents</strong> tabs to view the live case.
          </p>
        </div>
      )}

      {/* Scenario Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {scenarios.map((sc) => {
          const isCurrent = activeScenario === sc.id && running;
          return (
            <div
              key={sc.id}
              className="glass-panel p-6 rounded-2xl bg-dark-800 border border-gray-800 flex flex-col justify-between space-y-4 hover:border-gray-700 transition-all group"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className={`p-3 rounded-xl bg-dark-900 border ${sc.color}`}>
                    <sc.icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded bg-dark-900 text-gray-300 border border-gray-800">
                    {sc.severity}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white mt-4">{sc.title}</h3>
                <span className="text-[11px] font-mono text-cyan-400 block mt-0.5">{sc.vector}</span>
                <p className="text-xs text-gray-400 mt-2 leading-relaxed">{sc.description}</p>
              </div>

              <div className="pt-4 border-t border-gray-800/80 space-y-3">
                <div className="text-[11px] font-mono text-gray-400">
                  <span className="text-gray-600 block text-[10px] uppercase">Simulation Target / IOC</span>
                  <span className="text-gray-200">{sc.target}</span>
                </div>

                <button
                  onClick={() => handleRun(sc.id)}
                  disabled={running}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-orange-500 to-amber-500 text-dark-900 font-bold text-xs hover:from-orange-400 hover:to-amber-400 transition-all flex items-center justify-center space-x-2 shadow-lg shadow-orange-500/20 disabled:opacity-50"
                >
                  <Zap className={`w-3.5 h-3.5 ${isCurrent ? 'animate-spin' : ''}`} />
                  <span>{isCurrent ? 'Simulating Pipeline...' : 'Inject Cyber Attack'}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
