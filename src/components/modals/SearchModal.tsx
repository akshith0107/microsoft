import React, { useState, useEffect } from 'react';
import { Search, X, Package, User } from 'lucide-react';
import { productsAPI, khataAPI, Product, KhataAccount } from '../../api/services';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectProduct?: (product: any) => void;
  onSelectCustomer?: (customer: any) => void;
}

export const SearchModal: React.FC<SearchModalProps> = ({
  isOpen,
  onClose,
  onSelectProduct,
  onSelectCustomer,
}) => {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<KhataAccount[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      Promise.all([
        productsAPI.getProducts().catch(() => []),
        khataAPI.getAccounts().catch(() => []),
      ]).then(([prods, custs]) => {
        setProducts(prods);
        setCustomers(custs);
      }).finally(() => {
        setLoading(false);
      });
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const matchedProducts = products.filter(
    (p) =>
      p.name.toLowerCase().includes(query.toLowerCase()) ||
      (p.sku && p.sku.toLowerCase().includes(query.toLowerCase())) ||
      (p.brand && p.brand.toLowerCase().includes(query.toLowerCase()))
  );

  const matchedCustomers = customers.filter(
    (c) =>
      (c.customer_name && c.customer_name.toLowerCase().includes(query.toLowerCase())) ||
      (c.customer_phone && c.customer_phone.includes(query))
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4 bg-black/60 backdrop-blur-xs font-sans">
      <div className="w-full max-w-xl bg-white rounded-[10px] border-2 border-[#111111] shadow-[6px_6px_0_#111111] overflow-hidden">
        {/* Header */}
        <div className="p-3 border-b border-[#111111] flex items-center gap-2">
          <Search className="w-4 h-4 text-[#111111] shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search products, SKUs, customer phone numbers..."
            className="w-full text-xs font-mono text-[#111111] placeholder-[#6B6B6B] focus:outline-none bg-transparent"
            autoFocus
          />
          <button onClick={onClose} className="p-1 text-[#111111] hover:bg-[#F5F4EF] rounded">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results */}
        <div className="max-h-[360px] overflow-y-auto p-2 space-y-3 divide-y divide-[#111111]/10 font-mono">
          {loading && (
            <div className="p-4 text-center text-xs font-mono text-gray-500">Searching store database...</div>
          )}

          {!loading && matchedProducts.length === 0 && matchedCustomers.length === 0 && (
            <div className="p-4 text-center text-xs font-mono text-gray-500">No matching products or customers found.</div>
          )}

          {!loading && matchedProducts.length > 0 && (
            <div className="pt-1">
              <div className="px-2 text-[9px] font-bold text-[#6B6B6B] uppercase tracking-wider mb-1 flex items-center gap-1">
                <Package className="w-3 h-3 text-[#111111]" />
                PRODUCTS ({matchedProducts.length})
              </div>
              <div className="space-y-1">
                {matchedProducts.map((p) => (
                  <div
                    key={p.id}
                    onClick={() => {
                      if (onSelectProduct) onSelectProduct(p);
                      onClose();
                    }}
                    className="p-2 rounded-[4px] hover:bg-[#F5F4EF] flex items-center justify-between cursor-pointer border border-transparent hover:border-[#111111] transition-all"
                  >
                    <div>
                      <div className="font-bold text-xs text-[#111111] font-sans">{p.name}</div>
                      <div className="text-[10px] text-[#6B6B6B]">SKU: {p.sku} • Stock: {p.current_stock}</div>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-xs text-[#111111]">₹{p.selling_price}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!loading && matchedCustomers.length > 0 && (
            <div className="pt-2">
              <div className="px-2 text-[9px] font-bold text-[#6B6B6B] uppercase tracking-wider mb-1 flex items-center gap-1">
                <User className="w-3 h-3 text-[#111111]" />
                CUSTOMERS ({matchedCustomers.length})
              </div>
              <div className="space-y-1">
                {matchedCustomers.map((c) => (
                  <div
                    key={c.id}
                    onClick={() => {
                      if (onSelectCustomer) onSelectCustomer(c);
                      onClose();
                    }}
                    className="p-2 rounded-[4px] hover:bg-[#F5F4EF] flex items-center justify-between cursor-pointer border border-transparent hover:border-[#111111] transition-all"
                  >
                    <div>
                      <div className="font-bold text-xs text-[#111111] font-sans">{c.customer_name || 'Customer'}</div>
                      <div className="text-[10px] text-[#6B6B6B]">{c.customer_phone || 'No phone'}</div>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-xs text-rose-700">₹{c.current_balance} balance</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-2 bg-[#F5F4EF] border-t border-[#111111] text-[9px] font-mono text-[#6B6B6B] flex items-center justify-between">
          <span>Press ESC to exit</span>
          <span>DukaanPulse Live Backend Search</span>
        </div>
      </div>
    </div>
  );
};
