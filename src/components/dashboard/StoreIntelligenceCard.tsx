import React from 'react';
import { ArrowRight, BrainCircuit, CheckCircle2 } from 'lucide-react';

interface StoreIntelligenceCardProps {
  onOpenAIAdvisor: (initialQuery?: string) => void;
}

export const StoreIntelligenceCard: React.FC<StoreIntelligenceCardProps> = ({
  onOpenAIAdvisor,
}) => {
  return (
    <div className="bg-white rounded-[8px] border border-[#111111] p-5 flex flex-col justify-between h-full relative">
      {/* Top Header */}
      <div>
        <div className="flex items-center justify-between gap-2 pb-3 border-b border-[#111111]">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-[#F4C84A] border border-[#111111] rounded-[2px]" />
            <h2 className="text-xs font-mono font-bold text-[#111111] tracking-wider uppercase">
              STORE INTELLIGENCE
            </h2>
          </div>
          <span className="text-[9px] font-mono font-bold bg-[#111111] text-white px-1.5 py-0.5 rounded-[2px]">
            94% CONFIDENCE
          </span>
        </div>

        {/* Main Insight Title & Explanation */}
        <div className="mt-4 space-y-2">
          <div className="text-base font-bold text-[#111111] leading-snug">
            "Maggi 2-Min Noodles may run low before the weekend."
          </div>
          <p className="text-xs text-[#6B6B6B] leading-relaxed font-normal">
            Current stock covers ~3 days at recent sales velocity. Weekend demand has historically been 23% higher.
          </p>
        </div>

        {/* Technical Metadata Box */}
        <div className="mt-4 p-3 bg-[#F5F4EF] rounded-[6px] border border-[#111111] space-y-2 text-xs font-mono">
          <div className="flex items-center justify-between text-[10px] text-[#111111] font-bold uppercase">
            <span>BASED ON</span>
            <span className="text-emerald-700">+₹3,850 POTENTIAL</span>
          </div>
          <div className="text-[11px] text-[#111111] font-medium">
            Sales history · Inventory level · Lead time
          </div>
          
          {/* Subtle Memory Indicator */}
          <div className="pt-2 border-t border-[#111111]/20 text-[10px] text-[#6B6B6B]">
            <span className="font-bold text-[#111111]">MEMORY:</span> Your previous weekend order was 35 units. That quantity covered demand without excess stock.
          </div>
        </div>
      </div>

      {/* Footer CTA */}
      <div className="mt-5 pt-3 border-t border-[#111111] flex items-center justify-between">
        <span className="text-[10px] font-mono text-[#6B6B6B] uppercase">Sharma Traders (2-day lead)</span>

        <button
          onClick={() => onOpenAIAdvisor("Tell me more about Maggi reorder recommendations.")}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-[#111111] hover:bg-black text-white font-bold text-xs rounded-[6px] border border-[#111111] shadow-[2px_2px_0_#111111] transition-transform active:translate-x-0 cursor-pointer"
        >
          <span>Review recommendation</span>
          <ArrowRight className="w-3.5 h-3.5 text-[#F4C84A]" />
        </button>
      </div>
    </div>
  );
};
