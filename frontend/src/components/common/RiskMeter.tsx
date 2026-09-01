import React from 'react';

export const RiskMeter: React.FC<{ score: number; size?: 'sm' | 'md' | 'lg' }> = ({ score, size = 'md' }) => {
  const getRiskColor = (val: number) => {
    if (val >= 80) return 'text-red-500 stroke-red-500';
    if (val >= 60) return 'text-orange-500 stroke-orange-500';
    if (val >= 30) return 'text-amber-500 stroke-amber-500';
    return 'text-emerald-500 stroke-emerald-500';
  };

  const getRiskLabel = (val: number) => {
    if (val >= 80) return 'CRITICAL';
    if (val >= 60) return 'HIGH';
    if (val >= 30) return 'MEDIUM';
    return 'LOW';
  };

  const radius = size === 'lg' ? 42 : size === 'md' ? 30 : 20;
  const strokeWidth = size === 'lg' ? 7 : size === 'md' ? 5 : 3.5;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(Math.max(score, 0), 100);
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  const dimension = (radius + strokeWidth) * 2;

  return (
    <div className="flex items-center space-x-3">
      <div className="relative inline-flex items-center justify-center">
        <svg width={dimension} height={dimension} className="transform -rotate-90">
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            className="stroke-gray-800"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            className={`transition-all duration-1000 ease-out ${getRiskColor(score)}`}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>
        <span className={`absolute font-mono font-bold ${size === 'lg' ? 'text-lg' : size === 'md' ? 'text-sm' : 'text-xs'}`}>
          {Math.round(score)}
        </span>
      </div>
      <div>
        <p className="text-xs uppercase font-semibold text-gray-400">Risk Score</p>
        <p className={`text-xs font-extrabold ${getRiskColor(score)}`}>
          {getRiskLabel(score)}
        </p>
      </div>
    </div>
  );
};
