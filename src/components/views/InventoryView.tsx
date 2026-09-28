import React, { useState, useEffect } from 'react';
import { Plus, Search, RefreshCw, Camera } from 'lucide-react';
import { ProductItem } from '../../types/kirana';
import { productsAPI, Product } from '../../api/services';

const FALLBACK_PRODUCTS: ProductItem[] = [
  { id: 'p1', name: 'Maggi 2-Min Masala Noodle 70g', category: 'Packaged Food', price: 14, costPrice: 11, stock: 18, minStockThreshold: 30, unit: 'packets', brand: 'Nestle', status: 'low', salesCountToday: 38, barcode: '890105800001' },
  { id: 'p2', name: 'Amul Taaza T-Special 500ml', category: 'Dairy & Eggs', price: 28, costPrice: 24, stock: 65, minStockThreshold: 20, unit: 'pouches', brand: 'Amul', status: 'healthy', salesCountToday: 42, barcode: '890126200002' },
  { id: 'p3', name: 'Fortune Sunlite Sunflower Oil 1L', category: 'Edible Oil', price: 135, costPrice: 115, stock: 4, minStockThreshold: 15, unit: 'bottles', brand: 'Fortune', status: 'critical', salesCountToday: 15, barcode: '890600700003' },
];

interface InventoryViewProps {
  onAddProduct: () => void;
  onOpenReceiptScanner?: () => void;
}

export const InventoryView: React.FC<InventoryViewProps> = ({ onAddProduct, onOpenReceiptScanner }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'low' | 'critical'>('all');
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchProducts = () => {
    setLoading(true);
    productsAPI.getProducts()
      .then((apiProducts) => {
        if (apiProducts && apiProducts.length > 0) {
          const mapped: ProductItem[] = apiProducts.map((p) => {
            const stock = Number(p.current_stock || 0);
            const reorderLvl = Number(p.reorder_level || 10);
            let status: 'healthy' | 'low' | 'critical' = 'healthy';
            if (stock <= 0) status = 'critical';
            else if (stock <= reorderLvl) status = 'low';

            return {
              id: p.id,
              name: p.name,
              category: p.brand || 'General',
              brand: p.brand || 'Store',
              price: Number(p.selling_price),
              costPrice: Number(p.purchase_price),
              stock: stock,
              minStockThreshold: reorderLvl,
              unit: p.unit,
              status: status,
              salesCountToday: 0,
              barcode: p.barcode || p.sku,
            };
          });
          setProducts(mapped);
        } else {
          setProducts(FALLBACK_PRODUCTS);
        }
      })
      .catch((err) => {
        console.warn('Products API fetch failed, using fallback catalog', err);
        setProducts(FALLBACK_PRODUCTS);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const filtered = products.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase()) || p.category.toLowerCase().includes(searchTerm.toLowerCase());
    if (filterStatus === 'low') return matchesSearch && p.status === 'low';
    if (filterStatus === 'critical') return matchesSearch && p.status === 'critical';
    return matchesSearch;
  });

  return (
    <div className="space-y-4 pb-16 font-sans">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-[8px] border border-[#111111]">
        <div>
          <h1 className="text-lg font-bold text-[#111111] uppercase tracking-tight font-mono">INVENTORY & STOCK</h1>
          <p className="text-xs text-[#6B6B6B] font-medium">SKU management, lead times & stock limits</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchProducts}
            className="p-1.5 bg-[#F5F4EF] hover:bg-gray-200 text-[#111111] rounded-[6px] border border-[#111111] cursor-pointer"
            title="Refresh Inventory"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          {onOpenReceiptScanner && (
            <button
              onClick={onOpenReceiptScanner}
              className="px-3.5 py-1.5 bg-[#F5F4EF] hover:bg-[#EAE7DD] text-[#111111] text-xs font-bold font-mono rounded-[6px] border border-[#111111] shadow-[2px_2px_0_#111111] transition-transform flex items-center gap-1.5 shrink-0 cursor-pointer"
            >
              <Camera className="w-3.5 h-3.5 text-[#E65100]" />
              <span>SCAN RECEIPT</span>
            </button>
          )}
          <button
            onClick={onAddProduct}
            className="px-3.5 py-1.5 bg-[#111111] hover:bg-black text-white text-xs font-bold font-mono rounded-[6px] border border-[#111111] shadow-[2px_2px_0_#111111] transition-transform flex items-center gap-1.5 shrink-0 cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5 text-[#F4C84A]" />
            <span>+ ADD PRODUCT</span>
          </button>
        </div>
      </div>

      {/* Filter & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-3 rounded-[8px] border border-[#111111] font-mono">
        <div className="relative w-full sm:w-80">
          <Search className="w-3.5 h-3.5 text-[#111111] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter SKU or category..."
            className="w-full pl-8 pr-3 py-1.5 bg-[#F5F4EF] border border-[#111111] rounded-[6px] text-xs text-[#111111] focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-1.5 w-full sm:w-auto">
          <button
            onClick={() => setFilterStatus('all')}
            className={`px-3 py-1 text-xs font-bold rounded-[4px] border border-[#111111] transition-all cursor-pointer ${
              filterStatus === 'all' ? 'bg-[#111111] text-white' : 'bg-[#F5F4EF] text-[#111111]'
            }`}
          >
            ALL ({products.length})
          </button>
          <button
            onClick={() => setFilterStatus('low')}
            className={`px-3 py-1 text-xs font-bold rounded-[4px] border border-[#111111] transition-all cursor-pointer ${
              filterStatus === 'low' ? 'bg-[#F4C84A] text-[#111111]' : 'bg-[#F5F4EF] text-[#111111]'
            }`}
          >
            LOW ({products.filter(p => p.status === 'low').length})
          </button>
          <button
            onClick={() => setFilterStatus('critical')}
            className={`px-3 py-1 text-xs font-bold rounded-[4px] border border-[#111111] transition-all cursor-pointer ${
              filterStatus === 'critical' ? 'bg-rose-600 text-white' : 'bg-[#F5F4EF] text-[#111111]'
            }`}
          >
            CRITICAL ({products.filter(p => p.status === 'critical').length})
          </button>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-[8px] border border-[#111111] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#F5F4EF] border-b border-[#111111] text-[#6B6B6B] font-bold uppercase text-[9px]">
              <tr>
                <th className="p-3">PRODUCT</th>
                <th className="p-3">CATEGORY</th>
                <th className="p-3 text-center">MRP PRICE</th>
                <th className="p-3 text-center">COST</th>
                <th className="p-3 text-center">STOCK</th>
                <th className="p-3 text-center">STATUS</th>
                <th className="p-3 text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#111111]/10">
              {filtered.map((item) => (
                <tr key={item.id} className="hover:bg-[#F5F4EF] transition-colors">
                  <td className="p-3 font-bold text-[#111111] font-sans">
                    {item.name}
                  </td>
                  <td className="p-3 text-[#6B6B6B]">{item.category}</td>
                  <td className="p-3 text-center font-bold text-[#111111]">₹{item.price}</td>
                  <td className="p-3 text-center text-[#6B6B6B]">₹{item.costPrice}</td>
                  <td className="p-3 text-center font-bold text-[#111111]">
                    {item.stock} {item.unit}
                  </td>
                  <td className="p-3 text-center">
                    {item.status === 'healthy' && (
                      <span className="px-1.5 py-0.2 rounded-[2px] text-[9px] font-bold bg-emerald-100 text-emerald-900 border border-emerald-600">
                        HEALTHY
                      </span>
                    )}
                    {item.status === 'low' && (
                      <span className="px-1.5 py-0.2 rounded-[2px] text-[9px] font-bold bg-[#F4C84A] text-[#111111] border border-[#111111]">
                        LOW
                      </span>
                    )}
                    {item.status === 'critical' && (
                      <span className="px-1.5 py-0.2 rounded-[2px] text-[9px] font-bold bg-rose-100 text-rose-900 border border-rose-600">
                        CRITICAL
                      </span>
                    )}
                  </td>
                  <td className="p-3 text-right">
                    <button className="px-2.5 py-1 bg-[#111111] hover:bg-black text-white font-bold rounded-[4px] text-[10px] cursor-pointer">
                      Reorder
                    </button>
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
