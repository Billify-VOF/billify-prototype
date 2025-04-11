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
  
  const data = [
    { day: 'Mon', thisWeek: 20000, lastWeek: 50000 },
    { day: 'Tue', thisWeek: 50000, lastWeek: 35000 },
    { day: 'Wed', thisWeek: 40000, lastWeek: 30000 },
    { day: 'Thu', thisWeek: 100000, lastWeek: 40000 },
    { day: 'Fri', thisWeek: 50000, lastWeek: 55000 },
    { day: 'Sat', thisWeek: 30000, lastWeek: 45000 },
    { day: 'Sun', thisWeek: 60000, lastWeek: 30000 },
  ];
  
  export default function CashFlowChart() {
    return (
      <div className="w-full max-w-4xl mx-auto p-6 bg-white shadow-md rounded-lg">
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
  