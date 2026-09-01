import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: string;
    isPositive?: boolean;
  };
  highlightColor?: 'cyan' | 'red' | 'amber' | 'emerald' | 'purple';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  highlightColor = 'cyan',
}) => {
  const colorMap = {
    cyan: 'border-cyan-500/30 text-cyan-400',
    red: 'border-red-500/30 text-red-400',
    amber: 'border-amber-500/30 text-amber-400',
    emerald: 'border-emerald-500/30 text-emerald-400',
    purple: 'border-purple-500/30 text-purple-400',
  };

  return (
    <div className="glass-panel p-5 rounded-xl transition-all duration-200 hover:border-gray-600 relative overflow-hidden group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">{title}</p>
          <h3 className="text-3xl font-extrabold mt-2 text-white font-mono tracking-tight">{value}</h3>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg bg-gray-800/80 border ${colorMap[highlightColor]}`}>
          {icon}
        </div>
      </div>
      {trend && (
        <div className="mt-3 flex items-center text-xs font-medium">
          <span className={trend.isPositive ? 'text-emerald-400' : 'text-red-400'}>
            {trend.value}
          </span>
          <span className="text-gray-500 ml-1.5">vs last 24 hours</span>
        </div>
      )}
      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
    </div>
  );
};
