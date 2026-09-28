import React, { useState } from 'react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';

const SALES_7_DAYS = [
  { day: 'Mon', sales: 12400, orders: 85, profit: 2800 },
  { day: 'Tue', sales: 14200, orders: 92, profit: 3100 },
  { day: 'Wed', sales: 13800, orders: 88, profit: 3000 },
  { day: 'Thu', sales: 15600, orders: 104, profit: 3400 },
  { day: 'Fri', sales: 16100, orders: 110, profit: 3650 },
  { day: 'Sat', sales: 16400, orders: 115, profit: 3800 },
  { day: 'Sun', sales: 18450, orders: 126, profit: 4280 },
];

const SALES_30_DAYS = [
  { day: 'W1', sales: 84000, orders: 580, profit: 18500 },
  { day: 'W2', sales: 92000, orders: 640, profit: 20400 },
  { day: 'W3', sales: 98000, orders: 690, profit: 21800 },
  { day: 'W4', sales: 104250, orders: 740, profit: 23500 },
];

export const SalesOverviewChart: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d'>('7d');

  const chartData = timeRange === '7d' ? SALES_7_DAYS : SALES_30_DAYS;

  return (
    <div className="bg-white rounded-[8px] border border-[#111111] p-5 flex flex-col justify-between h-full">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-[#111111]">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-[#111111]">Sales Performance</h2>
            <span className="text-[10px] font-mono font-bold bg-emerald-100 text-emerald-900 border border-emerald-600 px-1.5 py-0.2 rounded-[2px]">
              +12.4% VS PREVIOUS PERIOD
            </span>
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-bold tracking-tight text-[#111111]">₹18,450</span>
            <span className="text-xs text-[#6B6B6B] font-mono">Today total</span>
          </div>
        </div>

        {/* Time Filter Controls */}
        <div className="flex items-center bg-[#F5F4EF] p-1 rounded-[6px] border border-[#111111]">
          <button
            onClick={() => setTimeRange('7d')}
            className={`px-3 py-1 text-xs font-mono font-bold rounded-[4px] transition-all cursor-pointer ${
              timeRange === '7d' 
                ? 'bg-[#111111] text-white' 
                : 'text-[#6B6B6B] hover:text-[#111111]'
            }`}
          >
            7D
          </button>
          <button
            onClick={() => setTimeRange('30d')}
            className={`px-3 py-1 text-xs font-mono font-bold rounded-[4px] transition-all cursor-pointer ${
              timeRange === '30d' 
                ? 'bg-[#111111] text-white' 
                : 'text-[#6B6B6B] hover:text-[#111111]'
            }`}
          >
            30D
          </button>
        </div>
      </div>

      {/* Recharts Clean Line Chart */}
      <div className="w-full h-[230px] mt-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="#E5E4DE" vertical={false} />
            <XAxis 
              dataKey="day" 
              axisLine={{ stroke: '#111111', strokeWidth: 1 }} 
              tickLine={false} 
              tick={{ fontSize: 11, fill: '#111111', fontFamily: 'monospace', fontWeight: 600 }} 
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 10, fill: '#6B6B6B', fontFamily: 'monospace' }}
              tickFormatter={(val) => `₹${val / 1000}k`}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-[#111111] text-white p-2.5 rounded-[4px] border border-[#111111] text-xs font-mono space-y-1 shadow-[3px_3px_0_#F4C84A]">
                      <div className="font-bold text-[#F4C84A]">{data.day}</div>
                      <div>Sales: ₹{data.sales.toLocaleString('en-IN')}</div>
                      <div>Orders: {data.orders}</div>
                      <div className="text-emerald-400">Profit: ₹{data.profit.toLocaleString('en-IN')}</div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Line
              type="monotone"
              dataKey="sales"
              stroke="#111111"
              strokeWidth={2.5}
              dot={{ r: 4, fill: '#111111', stroke: '#111111' }}
              activeDot={{ r: 6, fill: '#F4C84A', stroke: '#111111', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Bottom Summary Bar */}
      <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-[#111111] text-xs font-mono">
        <div>
          <span className="text-[#6B6B6B] text-[9px] uppercase font-bold block">AVG BASKET</span>
          <span className="font-bold text-[#111111]">₹146.4</span>
        </div>
        <div>
          <span className="text-[#6B6B6B] text-[9px] uppercase font-bold block">PEAK HOUR</span>
          <span className="font-bold text-[#111111]">18:30 - 20:30</span>
        </div>
        <div>
          <span className="text-[#6B6B6B] text-[9px] uppercase font-bold block">UPI / CASH</span>
          <span className="font-bold text-[#111111]">68% / 32%</span>
        </div>
      </div>
    </div>
  );
};
