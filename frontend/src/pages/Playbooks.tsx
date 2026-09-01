import React, { useState, useEffect } from 'react';
import { Workflow, Play, CheckCircle, AlertCircle, Clock, RefreshCw, Eye, Power } from 'lucide-react';
import { playbookService } from '../services/api';
import { Playbook, PlaybookExecution, PlaybookStatus } from '../types';
import { Modal } from '../components/common/Modal';
import { formatDateTime, formatTimeOnly } from '../utils/date';

export const Playbooks: React.FC = () => {
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [executions, setExecutions] = useState<PlaybookExecution[]>([]);
  const [selectedPlaybook, setSelectedPlaybook] = useState<Playbook | null>(null);
  const [selectedExecution, setSelectedExecution] = useState<PlaybookExecution | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Manual Trigger inputs
  const [triggerIp, setTriggerIp] = useState('185.220.101.45');
  const [triggerDesc, setTriggerDesc] = useState('Manual trigger for security response validation');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [pData, eData] = await Promise.all([
        playbookService.getPlaybooks(),
        playbookService.getAllExecutions(),
      ]);
      setPlaybooks(pData);
      setExecutions(eData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleStatus = async (pb: Playbook) => {
    const nextStatus: PlaybookStatus = pb.status === 'Enabled' ? 'Disabled' : 'Enabled';
    try {
      await playbookService.toggleStatus(pb.id, nextStatus);
      setActionSuccess(`Playbook "${pb.name}" status changed to ${nextStatus}`);
      setTimeout(() => setActionSuccess(null), 3000);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleExecute = async () => {
    if (!selectedPlaybook) return;
    try {
      const res = await playbookService.executePlaybook(selectedPlaybook.id, {
        source: 'Manual Playbook Studio',
        indicator: triggerIp,
        source_ip: triggerIp,
        description: triggerDesc,
        severity: 'High',
      });
      setSelectedPlaybook(null);
      setActionSuccess(`Playbook dispatched! Execution ID: ${res.execution_id}`);
      setTimeout(() => setActionSuccess(null), 4000);
      fetchData();
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
            <Workflow className="w-6 h-6 text-cyan-400" />
            AUTOMATED PLAYBOOK STUDIO
          </h2>
          <p className="text-xs text-gray-400 mt-1">
            Visual orchestration pipelines, threat enrichment workflows, and response action sequences
          </p>
        </div>

        <button
          onClick={fetchData}
          disabled={loading}
          className="px-3.5 py-2 rounded-xl bg-dark-800 border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white transition-all flex items-center space-x-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Studio</span>
        </button>
      </div>

      {actionSuccess && (
        <div className="p-3 rounded-xl bg-emerald-950/80 border border-emerald-800 text-emerald-300 text-xs flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 flex-shrink-0" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {/* Playbook Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {playbooks.map((pb) => (
          <div
            key={pb.id}
            className="glass-panel p-6 rounded-2xl bg-dark-800 border border-gray-800 flex flex-col justify-between space-y-4 hover:border-gray-700 transition-all"
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase font-bold tracking-widest px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                  Trigger: {pb.trigger}
                </span>
                <button
                  onClick={() => handleToggleStatus(pb)}
                  className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                    pb.status === 'Enabled'
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-800 hover:bg-emerald-900'
                      : 'bg-gray-800 text-gray-400 border border-gray-700 hover:bg-gray-700'
                  }`}
                >
                  <Power className="w-3 h-3" />
                  <span>{pb.status}</span>
                </button>
              </div>

              <h3 className="text-base font-bold text-white mt-3">{pb.name}</h3>
              <p className="text-xs text-gray-400 mt-1 leading-relaxed">{pb.description || 'Automated SOAR sequence.'}</p>
            </div>

            {/* Workflow Steps Visual Sequence */}
            <div className="space-y-2 pt-2 border-t border-gray-800/80">
              <p className="text-[10px] uppercase font-bold text-gray-500 font-mono">Sequential Actions ({pb.steps?.length || 0})</p>
              <div className="flex flex-wrap gap-1.5">
                {pb.steps?.map((step, idx) => (
                  <span
                    key={step.id || idx}
                    className="px-2 py-1 rounded-md bg-dark-900 border border-gray-800 text-[11px] font-mono text-gray-300"
                  >
                    <span className="text-cyan-400 font-bold mr-1">{step.order}.</span>
                    {step.action.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-gray-800 flex items-center justify-end space-x-2">
              <button
                onClick={() => setSelectedPlaybook(pb)}
                className="px-3 py-1.5 rounded-xl bg-cyan-500 text-dark-900 font-bold text-xs hover:bg-cyan-400 transition-all flex items-center space-x-1.5 shadow-lg shadow-cyan-500/20"
              >
                <Play className="w-3 h-3 fill-dark-900" />
                <span>Run Playbook</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Execution Logs Table */}
      <div className="glass-panel p-6 rounded-2xl bg-dark-800 border border-gray-800 space-y-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            Recent Playbook Execution History
          </h3>
          <p className="text-xs text-gray-400">Audit logs of automated and manual orchestrations</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[10px] uppercase font-bold text-gray-400 border-b border-gray-800 bg-gray-900/60">
              <tr>
                <th className="py-2.5 px-3">Execution ID</th>
                <th className="py-2.5 px-3">Playbook ID</th>
                <th className="py-2.5 px-3">Started At</th>
                <th className="py-2.5 px-3">Trigger Source</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Step Logs</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 font-medium">
              {executions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-gray-500">
                    No execution records logged. Run a playbook or attack simulation to test.
                  </td>
                </tr>
              ) : (
                executions.slice(0, 15).map((ex) => (
                  <tr key={ex.id} className="hover:bg-gray-800/40 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-cyan-400">{ex.execution_id}</td>
                    <td className="py-3 px-3 font-mono text-gray-300">Playbook #{ex.playbook_id}</td>
                    <td className="py-3 px-3 font-mono text-gray-400">
                      {formatDateTime(ex.started_at)}
                    </td>
                    <td className="py-3 px-3 text-gray-300">{ex.trigger_source || 'automation'}</td>
                    <td className="py-3 px-3">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold ${
                          ex.status === 'Completed'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : ex.status === 'Failed'
                            ? 'bg-red-950 text-red-400 border border-red-800'
                            : 'bg-amber-950 text-amber-400 border border-amber-800'
                        }`}
                      >
                        {ex.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => setSelectedExecution(ex)}
                        className="px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-cyan-500/20 text-gray-300 hover:text-cyan-400 border border-gray-700 transition-colors inline-flex items-center space-x-1"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View Logs ({ex.logs?.length || 0})</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Manual Trigger Modal */}
      {selectedPlaybook && (
        <Modal
          isOpen={!!selectedPlaybook}
          onClose={() => setSelectedPlaybook(null)}
          title={`Execute Playbook: ${selectedPlaybook.name}`}
          maxWidth="md"
        >
          <div className="space-y-4">
            <p className="text-xs text-gray-400 leading-relaxed">
              Manually trigger this playbook with specific security parameters. All steps will execute in sequence with audit logs and simulated response actions.
            </p>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-1">
                Target Indicator / IP / Host
              </label>
              <input
                type="text"
                value={triggerIp}
                onChange={(e) => setTriggerIp(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-dark-900 border border-gray-700 text-white font-mono text-xs focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-1">
                Trigger Notes / Description
              </label>
              <input
                type="text"
                value={triggerDesc}
                onChange={(e) => setTriggerDesc(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-dark-900 border border-gray-700 text-white text-xs focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div className="pt-4 border-t border-gray-800 flex items-center justify-end space-x-2">
              <button
                onClick={() => setSelectedPlaybook(null)}
                className="px-4 py-2 rounded-xl bg-gray-800 text-gray-400 hover:text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleExecute}
                className="px-4 py-2 rounded-xl bg-cyan-500 text-dark-900 font-bold text-xs hover:bg-cyan-400 flex items-center space-x-1.5"
              >
                <Play className="w-3.5 h-3.5 fill-dark-900" />
                <span>Confirm & Dispatch</span>
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Execution Logs Modal */}
      {selectedExecution && (
        <Modal
          isOpen={!!selectedExecution}
          onClose={() => setSelectedExecution(null)}
          title={`Execution Logs: ${selectedExecution.execution_id}`}
          maxWidth="2xl"
        >
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs pb-3 border-b border-gray-800">
              <span className="text-gray-400">Playbook #{selectedExecution.playbook_id}</span>
              <span className="font-mono text-cyan-400 font-bold">{selectedExecution.status}</span>
            </div>

            <div className="space-y-2.5 max-h-96 overflow-y-auto">
              {selectedExecution.logs && selectedExecution.logs.length > 0 ? (
                selectedExecution.logs.map((log) => (
                  <div key={log.id} className="p-3 rounded-xl bg-dark-900 border border-gray-800 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-cyan-300">{log.step_name}</span>
                      <span className="text-[10px] font-mono text-gray-500">
                        {formatTimeOnly(log.timestamp)}
                      </span>
                    </div>
                    <p className="text-gray-300">{log.message}</p>
                  </div>
                ))
              ) : (
                <p className="text-xs text-gray-500 text-center py-6">No step logs recorded.</p>
              )}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
