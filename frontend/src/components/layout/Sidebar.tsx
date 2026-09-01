import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  AlertOctagon,
  Flame,
  Workflow,
  Crosshair,
  Globe2,
  Server,
  Cpu,
  FileSpreadsheet
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Security Alerts', path: '/alerts', icon: AlertOctagon },
    { name: 'Incidents', path: '/incidents', icon: Flame },
    { name: 'Playbooks', path: '/playbooks', icon: Workflow },
    { name: 'Attack Simulator', path: '/simulation', icon: Crosshair, highlight: true },
    { name: 'Threat Intel', path: '/threat-intel', icon: Globe2 },
    { name: 'Asset Inventory', path: '/assets', icon: Server },
    { name: 'Automation Rules', path: '/automation', icon: Cpu },
    { name: 'SOC Audit Logs', path: '/audit', icon: FileSpreadsheet },
  ];

  return (
    <aside className="w-64 bg-dark-900 border-r border-gray-800 flex flex-col justify-between py-6 min-h-[calc(100vh-4rem)]">
      <div className="px-4 space-y-1.5">
        <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-gray-500 mb-3 font-mono">
          OPERATIONS CENTER
        </p>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-lg shadow-cyan-500/5'
                  : item.highlight
                  ? 'text-orange-400 hover:bg-orange-500/10 border border-orange-500/20'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
              }`
            }
          >
            <item.icon className="w-4 h-4 flex-shrink-0" />
            <span>{item.name}</span>
            {item.highlight && (
              <span className="ml-auto text-[9px] uppercase font-bold tracking-widest bg-orange-950 text-orange-400 border border-orange-800 px-1.5 py-0.5 rounded">
                DEMO
              </span>
            )}
          </NavLink>
        ))}
      </div>

      <div className="px-6 py-4 mx-4 rounded-xl bg-dark-800/60 border border-gray-800 text-xs">
        <p className="text-gray-400 font-semibold">SOAR Pipeline</p>
        <p className="text-gray-500 text-[11px] mt-1">Autonomous orchestration active across SIEM, EDR & Firewall integrations.</p>
      </div>
    </aside>
  );
};
