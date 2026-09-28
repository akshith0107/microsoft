import React from 'react';
import { ArrowRight } from 'lucide-react';
import { ProductItem } from '../../types/kirana';

const INVENTORY_PRODUCTS: ProductItem[] = [
  { id: 'p1', name: 'Maggi 2-Min Masala Noodle 70g', category: 'Packaged Food', price: 14, costPrice: 11, stock: 18, minStockThreshold: 30, unit: 'packets', brand: 'Nestle', status: 'low', salesCountToday: 38, barcode: '890105800001' },
  { id: 'p2', name: 'Amul Taaza T-Special 500ml', category: 'Dairy & Eggs', price: 28, costPrice: 24, stock: 65, minStockThreshold: 20, unit: 'pouches', brand: 'Amul', status: 'healthy', salesCountToday: 42, barcode: '890126200002' },
  { id: 'p3', name: 'Fortune Sunlite Sunflower Oil 1L', category: 'Edible Oil', price: 135, costPrice: 115, stock: 4, minStockThreshold: 15, unit: 'bottles', brand: 'Fortune', status: 'critical', salesCountToday: 15, barcode: '890600700003' },
  { id: 'p4', name: 'Tata Salt Vacuum Evaporated 1kg', category: 'Staples & Spices', price: 28, costPrice: 22, stock: 42, minStockThreshold: 25, unit: 'packs', brand: 'Tata', status: 'healthy', salesCountToday: 20, barcode: '890105800004' },
];

interface InventoryHealthCardProps {
  onViewAllInventory: () => void;
  onReorderProduct?: (product: ProductItem) => void;
}

export const InventoryHealthCard: React.FC<InventoryHealthCardProps> = ({
  onViewAllInventory,
  onReorderProduct,
}) => {
  const healthyCount = 128;
  const lowCount = 12;
  const criticalCount = 4;
  const total = healthyCount + lowCount + criticalCount;

  const healthyPct = Math.round((healthyCount / total) * 100);
  const lowPct = Math.round((lowCount / total) * 100);
  const criticalPct = Math.round((criticalCount / total) * 100);

  const mockVelocity: Record<string, string> = {
    p1: "5/day",
    p2: "8/day",
    p3: "7/day",
    p4: "3/day",
  };

  const getStatusBadge = (status: ProductItem['status']) => {
    switch (status) {
      case 'healthy':
        return (
          <span className="font-mono text-[9px] font-bold px-1.5 py-0.2 rounded-[2px] bg-emerald-100 text-emerald-900 border border-emerald-600">
            HEALTHY
          </span>
        );
      case 'low':
        return (
          <span className="font-mono text-[9px] font-bold px-1.5 py-0.2 rounded-[2px] bg-[#F4C84A] text-[#111111] border border-[#111111]">
            LOW
          </span>
        );
      case 'critical':
        return (
          <span className="font-mono text-[9px] font-bold px-1.5 py-0.2 rounded-[2px] bg-rose-100 text-rose-900 border border-rose-600">
            CRITICAL
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-[8px] border border-[#111111] p-5 flex flex-col justify-between h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#111111] mb-4">
          <div className="flex items-center gap-2">
            <h2 className="text-xs font-mono font-bold text-[#111111] tracking-wider uppercase">INVENTORY HEALTH</h2>
            <span className="text-[10px] font-mono text-[#6B6B6B]">144 SKUs</span>
          </div>
          <button
            onClick={onViewAllInventory}
            className="flex items-center gap-1 text-xs font-bold text-[#111111] hover:underline cursor-pointer font-mono"
          >
            <span>VIEW ALL</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Segmented Horizontal Bar & Summary */}
        <div className="p-3 bg-[#F5F4EF] rounded-[6px] border border-[#111111] mb-4 space-y-2">
          <div className="flex items-center justify-between text-xs font-mono font-bold">
            <span className="text-[#111111]">{healthyCount} healthy</span>
            <span className="text-amber-800">{lowCount} low</span>
            <span className="text-rose-700">{criticalCount} critical</span>
          </div>

          <div className="w-full h-3 bg-[#111111]/10 rounded-[2px] flex overflow-hidden border border-[#111111]">
            <div style={{ width: `${healthyPct}%` }} className="bg-emerald-600 h-full" title="Healthy" />
            <div style={{ width: `${lowPct}%` }} className="bg-[#F4C84A] h-full" title="Low Stock" />
            <div style={{ width: `${criticalPct}%` }} className="bg-rose-600 h-full" title="Critical" />
          </div>
        </div>

        {/* Compact Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#111111] text-[#6B6B6B] font-bold uppercase text-[9px]">
                <th className="pb-2">PRODUCT</th>
                <th className="pb-2 text-center">STOCK</th>
                <th className="pb-2 text-center">VELOCITY</th>
                <th className="pb-2 text-right">STATUS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#111111]/10">
              {INVENTORY_PRODUCTS.slice(0, 4).map((item) => (
                <tr key={item.id} className="hover:bg-[#F5F4EF] transition-colors">
                  <td className="py-2.5 font-bold text-[#111111] font-sans">
                    {item.name}
                  </td>
                  <td className="py-2.5 text-center font-bold text-[#111111]">
                    {item.stock} {item.unit}
                  </td>
                  <td className="py-2.5 text-center font-semibold text-[#6B6B6B]">
                    {mockVelocity[item.id] || '4/day'}
                  </td>
                  <td className="py-2.5 text-right">
                    {getStatusBadge(item.status)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
