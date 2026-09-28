import React from 'react';

const TOP_SELLING_PRODUCTS = [
  { rank: 1, name: "Amul Taaza T-Special 500ml", category: "Dairy & Eggs", salesCount: 42, revenue: 1176, growth: "+14%" },
  { rank: 2, name: "Maggi 2-Min Masala Noodle 70g", category: "Packaged Food", salesCount: 38, revenue: 532, growth: "+18%" },
  { rank: 3, name: "Fortune Sunlite Sunflower Oil 1L", category: "Edible Oil", salesCount: 15, revenue: 2025, growth: "+6%" },
  { rank: 4, name: "Parle-G Gold Biscuits 100g", category: "Snacks", salesCount: 30, revenue: 300, growth: "+10%" },
];

export const TopProductsCard: React.FC = () => {
  return (
    <div className="bg-white rounded-[8px] border border-[#111111] p-5 flex flex-col justify-between h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#111111] mb-4">
          <h2 className="text-xs font-mono font-bold text-[#111111] tracking-wider uppercase">TOP SELLERS</h2>
          <span className="text-[10px] font-mono font-bold bg-[#111111] text-white px-1.5 py-0.2 rounded-[2px]">
            TODAY RANKING
          </span>
        </div>

        {/* Ranked Product List */}
        <div className="space-y-2">
          {TOP_SELLING_PRODUCTS.slice(0, 4).map((prod) => (
            <div
              key={prod.rank}
              className="flex items-center justify-between p-2.5 rounded-[6px] bg-[#F5F4EF] border border-[#111111] transition-colors"
            >
              <div className="flex items-center gap-3">
                {/* Large Mono Rank Number */}
                <span className="font-mono font-black text-sm text-[#111111] w-6">
                  0{prod.rank}
                </span>

                <div>
                  <div className="font-bold text-xs text-[#111111] leading-snug">
                    {prod.name}
                  </div>
                  <div className="text-[10px] font-mono text-[#6B6B6B]">
                    {prod.category} • {prod.growth}
                  </div>
                </div>
              </div>

              <div className="text-right font-mono">
                <div className="font-black text-xs text-[#111111]">
                  {prod.salesCount} sold
                </div>
                <div className="text-[10px] text-[#6B6B6B]">
                  ₹{prod.revenue.toLocaleString('en-IN')}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Banner */}
      <div className="mt-4 pt-3 border-t border-[#111111] flex items-center justify-between text-[10px] font-mono text-[#6B6B6B]">
        <span>⚡ TOP 2 ITEMS MAKE UP 42% OF DAILY SNACK SALES</span>
      </div>
    </div>
  );
};
