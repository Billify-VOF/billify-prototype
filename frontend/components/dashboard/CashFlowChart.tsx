import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
    Area,
  } from 'recharts';
  
  interface CashFlowData {
    day: string;
    thisWeek: number;
    lastWeek: number;
  }

  const defaultData: CashFlowData[] = [
    { day: 'Mon', thisWeek: 4000, lastWeek: 3000 },
    { day: 'Tue', thisWeek: 3000, lastWeek: 2000 },
    { day: 'Wed', thisWeek: 2000, lastWeek: 4000 },
    { day: 'Thu', thisWeek: 2780, lastWeek: 3908 },
    { day: 'Fri', thisWeek: 1890, lastWeek: 4800 },
    { day: 'Sat', thisWeek: 2390, lastWeek: 3800 },
    { day: 'Sun', thisWeek: 3490, lastWeek: 4300 },
  ];

  interface CashFlowChartProps {
    data?: CashFlowData[];
    isLoading?: boolean;
    error?: Error | null;
  }

  export default function CashFlowChart({ 
    data = defaultData, 
    isLoading = false, 
    error = null 
  }: CashFlowChartProps) {
    if (isLoading) {
      return (
        <div className="flex h-[400px] w-full max-w-4xl items-center justify-center rounded-lg bg-white p-6 shadow-md">
          <div className="animate-pulse">Loading chart data...</div>
        </div>
      );
    }
    
    if (error) {
      return (
        <div className="flex h-[400px] w-full max-w-4xl items-center justify-center rounded-lg bg-white p-6 shadow-md">
          <div className="text-red-500">Error loading chart: {error.message}</div>
        </div>
      );
    }

    return (
      <div className="w-full max-w-4xl rounded-lg bg-white p-6 shadow-md">
        <div className="mb-6">
          <h2 className="text-xl font-bold">Cash Flow</h2>
          <p className="text-gray-500">Compare this week vs last week</p>
        </div>
        {/* Title + Dropdown */}
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold text-gray-800">Cash Flow Analysis</h2>
          <span className="text-blue-600 font-medium cursor-pointer">Weekly ▾</span>
        </div>
  
        {/* Manual Legend */}
        <div className="flex items-center space-x-6 mb-4">
          <div className="flex items-center space-x-2">
            <span className="text-blue-600 text-lg">●</span>
            <span className="text-sm text-gray-700">This Week</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-red-500 text-lg">●</span>
            <span className="text-sm text-gray-700">Last Week</span>
          </div>
        </div>
  
        {/* Chart */}
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <defs>
              <linearGradient id="colorThisWeek" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
              </linearGradient>
            </defs>
  
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="day" />
            <YAxis tickFormatter={(v) => `$${v / 1000}K`} />
            <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
            <Area
              type="monotone"
              dataKey="thisWeek"
              stroke="none"
              fillOpacity={1}
              fill="url(#colorThisWeek)"
            />
            <Line
              type="monotone"
              dataKey="thisWeek"
              stroke="#2563eb"
              strokeWidth={3}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="lastWeek"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }
  