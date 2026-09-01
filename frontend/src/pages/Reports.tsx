import React from 'react';
import { BarChart3, PieChart, TrendingUp, Download, Calendar } from 'lucide-react';

export default function Reports() {
  const reports = [
    {
      title: 'Weekly Threat Summary',
      description: 'Summary of all security threats detected in the past week',
      icon: BarChart3,
      status: 'Available',
      lastGenerated: new Date().toLocaleDateString(),
    },
    {
      title: 'Incident Response Metrics',
      description: 'MTTR, MTTD, and other key incident response performance metrics',
      icon: TrendingUp,
      status: 'Available',
      lastGenerated: new Date().toLocaleDateString(),
    },
    {
      title: 'SOC Performance Dashboard',
      description: 'Analyst productivity, case closure rates, and alert handling times',
      icon: PieChart,
      status: 'Available',
      lastGenerated: new Date().toLocaleDateString(),
    },
    {
      title: 'Compliance Audit Report',
      description: 'NIST, MITRE ATT&CK coverage analysis and compliance posture',
      icon: BarChart3,
      status: 'Generating',
      lastGenerated: '—',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Reports</h1>
        <p className="text-sm text-gray-400">Generate and download security reports</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reports.map((report) => (
          <div key={report.title} className="glass-panel rounded-2xl p-6 hover:border-cyan-500/30 transition-all">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 rounded-xl bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center flex-shrink-0">
                <report.icon className="w-6 h-6 text-cyan-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-bold text-white">{report.title}</h3>
                <p className="text-xs text-gray-400 mt-1">{report.description}</p>
                <div className="flex items-center justify-between mt-4">
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>Last generated: {report.lastGenerated}</span>
                  </div>
                  <button
                    className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      report.status === 'Available'
                        ? 'bg-cyan-950/60 text-cyan-400 border border-cyan-800/40 hover:bg-cyan-900/60'
                        : 'bg-gray-800 text-gray-500 border border-gray-700 cursor-not-allowed'
                    }`}
                    disabled={report.status !== 'Available'}
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>{report.status === 'Available' ? 'Download' : 'Generating...'}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
