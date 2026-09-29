import React, { useState } from 'react';
import { X, PackagePlus, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { productsAPI } from '../../api/services';

interface AddProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onProductAdded: () => void;
}

export const AddProductModal: React.FC<AddProductModalProps> = ({
  isOpen,
  onClose,
  onProductAdded,
}) => {
  const [name, setName] = useState('');
  const [brand, setBrand] = useState('');
  const [unit, setUnit] = useState('packet');
  const [barcode, setBarcode] = useState('');
  const [purchasePrice, setPurchasePrice] = useState<number | ''>('');
  const [sellingPrice, setSellingPrice] = useState<number | ''>('');
  const [initialStock, setInitialStock] = useState<number | ''>('');
  const [reorderLevel, setReorderLevel] = useState<number | ''>(10);
  const [targetStock, setTargetStock] = useState<number | ''>(50);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!name.trim()) {
      setErrorMessage('Please enter a product name.');
      return;
    }

    if (purchasePrice === '' || Number(purchasePrice) < 0) {
      setErrorMessage('Please enter a valid purchase price.');
      return;
    }

    if (sellingPrice === '' || Number(sellingPrice) < 0) {
      setErrorMessage('Please enter a valid selling price.');
      return;
    }

    setIsLoading(true);

    try {
      const generatedSku = barcode.trim() || `SKU-${Date.now().toString().slice(-6)}`;

      await productsAPI.createProduct({
        name: name.trim(),
        brand: brand.trim() || 'General',
        sku: generatedSku,
        barcode: barcode.trim() || generatedSku,
        unit: unit,
        purchase_price: Number(purchasePrice),
        selling_price: Number(sellingPrice),
        initial_stock: initialStock === '' ? 0 : Number(initialStock),
        reorder_level: reorderLevel === '' ? 10 : Number(reorderLevel),
        target_stock: targetStock === '' ? 50 : Number(targetStock),
        is_active: true,
      });

      // Reset form
      setName('');
      setBrand('');
      setBarcode('');
      setPurchasePrice('');
      setSellingPrice('');
      setInitialStock('');
      setReorderLevel(10);
      setTargetStock(50);

      onProductAdded();
      onClose();
    } catch (err: any) {
      console.error('Failed to create product:', err);
      setErrorMessage(err?.message || 'Failed to add product SKU to backend.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/60 backdrop-blur-xs font-sans">
      <div className="w-full max-w-lg bg-white rounded-[10px] border-2 border-[#111111] shadow-[6px_6px_0_#111111] overflow-hidden flex flex-col font-mono text-[#111111]">
        
        {/* Modal Header */}
        <div className="p-3.5 bg-[#111111] text-white flex items-center justify-between border-b border-[#111111]">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-[#F4C84A] rounded-[2px]" />
            <div>
              <h3 className="font-bold text-white text-xs uppercase tracking-wider">ADD NEW PRODUCT SKU</h3>
              <p className="text-[10px] text-[#888888]">PostgreSQL Inventory & POS Catalogue Registration</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-white rounded cursor-pointer">
            <X className="w-4.5 h-4.5" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-5 bg-[#F5F4EF] space-y-4 max-h-[80vh] overflow-y-auto">
          {errorMessage && (
            <div className="p-3 bg-rose-50 border border-rose-400 rounded-[6px] flex items-start gap-2 text-rose-900 text-xs font-medium">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div>{errorMessage}</div>
            </div>
          )}

          {/* Product Name */}
          <div className="space-y-1">
            <label className="text-[10px] font-bold uppercase text-[#111111]">Product Name *</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Maggi 2-Min Masala Noodle 70g"
              className="w-full px-3 py-2 bg-white rounded-[4px] border border-[#111111] text-xs font-bold text-[#111111] focus:outline-none focus:ring-2 focus:ring-[#F4C84A]"
            />
          </div>

          {/* Brand & Unit */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase text-[#111111]">Brand / Category</label>
              <input
                type="text"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                placeholder="e.g. Nestle / FMCG"
                className="w-full px-3 py-2 bg-white rounded-[4px] border border-[#111111] text-xs font-bold text-[#111111] focus:outline-none focus:ring-2 focus:ring-[#F4C84A]"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase text-[#111111]">Packaging Unit</label>
              <select
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                className="w-full px-3 py-2 bg-white rounded-[4px] border border-[#111111] text-xs font-bold text-[#111111] focus:outline-none"
              >
                <option value="packet">packet (pkt)</option>
                <option value="piece">piece (pc)</option>
                <option value="pouch">pouch</option>
                <option value="bottle">bottle</option>
                <option value="box">box</option>
                <option value="kg">kg</option>
                <option value="liter">liter</option>
              </select>
            </div>
          </div>

          {/* Prices & Barcode */}
          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase text-[#111111]">Cost Price (₹) *</label>
              <input
                type="number"
                step="0.01"
                required
                value={purchasePrice}
                onChange={(e) => setPurchasePrice(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="11.00"
                className="w-full px-3 py-2 bg-white rounded-[4px] border border-[#111111] text-xs font-bold text-[#111111] focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase text-[#111111]">Selling Price (₹) *</label>
              <input
                type="number"
                step="0.01"
                required
                value={sellingPrice}
                onChange={(e) => setSellingPrice(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="14.00"
                className="w-full px-3 py-2 bg-white rounded-[4px] border border-[#111111] text-xs font-bold text-[#111111] focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase text-[#111111]">Barcode / SKU</label>
              <input
                type="text"
                value={barcode}
                onChange={(e) => setBarcode(e.target.value)}
                placeholder="89010580..."
                className="w-full px-3 py-2 bg-white rounded-[4px] border border-[#111111] text-xs font-bold text-[#111111] focus:outline-none"
              />
            </div>
          </div>

          {/* Stock Levels */}
          <div className="grid grid-cols-3 gap-3 pt-1 border-t border-[#111111]/20">
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase text-[#111111]">Initial Stock</label>
              <input
                type="number"
                value={initialStock}
                onChange={(e) => setInitialStock(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="0"
                className="w-full px-3 py-2 bg-white rounded-[4px] border border-[#111111] text-xs font-bold text-[#111111] focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase text-[#111111]">Reorder Alert Level</label>
              <input
                type="number"
                value={reorderLevel}
                onChange={(e) => setReorderLevel(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="10"
                className="w-full px-3 py-2 bg-white rounded-[4px] border border-[#111111] text-xs font-bold text-[#111111] focus:outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase text-[#111111]">Target Max Stock</label>
              <input
                type="number"
                value={targetStock}
                onChange={(e) => setTargetStock(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="50"
                className="w-full px-3 py-2 bg-white rounded-[4px] border border-[#111111] text-xs font-bold text-[#111111] focus:outline-none"
              />
            </div>
          </div>

          {/* Modal Action Buttons */}
          <div className="grid grid-cols-2 gap-2 pt-3 border-t border-[#111111]">
            <button
              type="button"
              onClick={onClose}
              className="py-2.5 bg-white hover:bg-gray-100 text-[#111111] text-xs font-bold rounded-[6px] border border-[#111111] cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="py-2.5 bg-[#111111] hover:bg-black text-white text-xs font-bold rounded-[6px] border border-[#111111] shadow-[2px_2px_0_#111111] flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-75"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin text-[#F4C84A]" />
              ) : (
                <CheckCircle2 className="w-4 h-4 text-[#F4C84A]" />
              )}
              <span>SAVE PRODUCT SKU</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
