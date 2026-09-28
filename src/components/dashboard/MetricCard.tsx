import React from 'react';
import { TrendingUp, AlertTriangle } from 'lucide-react';
import { MetricData } from '../../types/kirana';

interface MetricCardProps {
  data: MetricData;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({ data, onClick }) => {
  // Determine accent bar style based on metric type
  const getMetricAccent = () => {
    if (data.title.includes("SALES")) {
      return {
        topBar: "bg-[#F4C84A]",
        badge: "bg-[#F4C84A] text-[#111111]",
        sparkColor: "#111111"
      };
    }
    if (data.title.includes("PROFIT")) {
      return {
        topBar: "bg-emerald-600",
        badge: "bg-emerald-100 text-emerald-900 border border-emerald-600",
        sparkColor: "#059669"
      };
    }
    if (data.title.includes("ORDERS")) {
      return {
        topBar: "bg-[#111111]",
        badge: "bg-[#111111] text-white",
        sparkColor: "#111111"
      };
    }
    // LOW STOCK
    return {
      topBar: "bg-[#F4C84A] border-b border-[#111111]",
      badge: "bg-rose-100 text-rose-900 border border-rose-600",
      sparkColor: "#DC2626"
    };
  };

  const accent = getMetricAccent();

  // SVG Sparkline calculation
  const points = data.sparkline;
  const max = Math.max(...points);
  const min = Math.min(...points);
  const range = max - min || 1;
  const svgWidth = 70;
  const svgHeight = 24;

  const polylinePoints = points
    .map((val, idx) => {
      const x = (idx / (points.length - 1)) * svgWidth;
      const y = svgHeight - ((val - min) / range) * (svgHeight - 4) - 2;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-[8px] border border-[#111111] p-4 cursor-pointer flex flex-col justify-between hover:bg-[#F5F4EF] transition-colors relative overflow-hidden group select-none"
    >
      {/* Top Accent Line */}
      <div className={`absolute top-0 left-0 right-0 h-1 ${accent.topBar}`} />

      {/* Title & Badge */}
      <div className="flex items-start justify-between gap-2 pt-1">
        <span className="text-[10px] font-mono font-bold tracking-widest text-[#6B6B6B] uppercase">
          {data.title}
        </span>

        <span className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded-[2px] ${accent.badge}`}>
          {data.change}
        </span>
      </div>

      {/* Main Metric Value */}
      <div className="text-2xl lg:text-3xl font-bold tracking-tight text-[#111111] mt-2 mb-3">
        {data.value}
      </div>

      {/* Bottom Subtitle & Minimal Sparkline */}
      <div className="flex items-end justify-between pt-2 border-t border-[#111111]/10 text-xs">
        <span className="text-[11px] text-[#6B6B6B] font-medium truncate max-w-[130px]">
          {data.subtitle}
        </span>

        {/* SVG Sparkline */}
        <div className="w-[70px] h-[24px]">
          <svg width={svgWidth} height={svgHeight} className="overflow-visible">
            <polyline
              fill="none"
              stroke={accent.sparkColor}
              strokeWidth="2"
              strokeLinecap="square"
              strokeLinejoin="miter"
              points={polylinePoints}
            />
          </svg>
        </div>
      </div>
    </div>
  );
};
