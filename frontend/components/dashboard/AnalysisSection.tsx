import React from 'react';
import { ArrowDownLeft, ArrowUpRight } from 'lucide-react';

type MetricCardProps = {
  label: string;
  value: string;
  icon?: 'up' | 'down';
  color?: 'red' | 'green' | 'blue';
};

const barStyles = {
  red: 'bg-red-500',
  green: 'bg-green-500',
  blue: 'bg-blue-500',
};

const MetricCard: React.FC<MetricCardProps> = ({ label, value, icon, color }) => {
  const bars = [50, 70, 100, 60, 80, 30]; // fake heights
  const highlightedIndex = 3; // index of the colored bar

  return (
    <div className="flex w-full items-center justify-around gap-2 px-4">
      <div className="flex flex-col">
        <div className="flex items-center gap-1 text-xl font-semibold text-slate-800">
          {value}
          {icon === 'down' && <ArrowDownLeft className="h-6 w-6 text-red-500" />}
          {icon === 'up' && <ArrowUpRight className="h-6 w-6 text-green-500" />}
        </div>
        <span className="text-sm text-slate-500">{label}</span>
      </div>

      <div className="flex h-20 items-end gap-1">
        {bars.map((height, index) => (
          <div
            key={index}
            className={`w-3 rounded-sm ${index === highlightedIndex ? barStyles[color || 'blue'] : 'bg-gray-200'}`}
            style={{ height: `${height}%` }}
          />
        ))}
      </div>
    </div>
  );
};

const AnalysisSection: React.FC = () => {
  return (
    <div className="flex w-full flex-col rounded-xl bg-white p-3 shadow-sm">
      <h1 className="text-xl font-bold text-gray-800">Analysis & Predictions</h1>
      <div className="flex flex-col justify-between gap-5 p-3 md:flex-row">
        <MetricCard label="Burn Rate" value="10%" icon="down" color="red" />{' '}
        <div className="w-[2px] bg-gray-300"></div>
        <MetricCard label="Break Event Point" value="$500K" color="blue" />{' '}
        <div className="w-[2px] bg-gray-300"></div>
        <MetricCard label="AI Analysis" value="10%" icon="up" color="green" />
      </div>
    </div>
  );
};

export default AnalysisSection;
