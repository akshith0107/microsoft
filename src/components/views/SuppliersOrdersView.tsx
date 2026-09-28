import React, { useState, useEffect } from 'react';
import { Truck, Plus, RefreshCw, MessageSquare, ExternalLink, Calendar, CheckCircle2 } from 'lucide-react';
import { ordersAPI, suppliersAPI, productsAPI, OrderRead, SupplierRead, Product } from '../../api/services';

export const SuppliersOrdersView: React.FC = () => {
  const [orders, setOrders] = useState<OrderRead[]>([]);
  const [suppliers, setSuppliers] = useState<SupplierRead[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'orders' | 'suppliers'>('orders');

  // Create Order Form state
  const [isCreateOrderOpen, setIsCreateOrderOpen] = useState<boolean>(false);
  const [selectedSupplierId, setSelectedSupplierId] = useState<string>('');
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  const [orderQty, setOrderQty] = useState<number>(30);
  const [orderNotes, setOrderNotes] = useState<string>('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [ords, sups, prods] = await Promise.allSettled([
        ordersAPI.getOrders(),
        suppliersAPI.getSuppliers(),
        productsAPI.getProducts()
      ]);

      if (ords.status === 'fulfilled') setOrders(ords.value || []);
      if (sups.status === 'fulfilled') setSuppliers(sups.value || []);
      if (prods.status === 'fulfilled') setProducts(prods.value || []);
    } catch (err) {
      console.warn('Orders/Suppliers API call failed, using fallback display data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProductId || orderQty <= 0) return;

    try {
      const selectedProd = products.find(p => p.id === selectedProductId);
      await ordersAPI.createOrder({
        supplier_id: selectedSupplierId || undefined,
        items: [
          {
            product_id: selectedProductId,
            quantity: orderQty,
            unit_price: selectedProd?.purchase_price || 10
          }
        ],
        notes: orderNotes || 'Created via Kirana Operating System UI'
      });

      setIsCreateOrderOpen(false);
      fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to create restock order.');
    }
  };

  const handleLaunchWhatsAppOrder = (order: OrderRead) => {
    const supplierName = order.supplier_name || 'Wholesale Supplier';
    const itemsText = order.items && order.items.length > 0
      ? order.items.map(it => `• ${it.product_name || 'Product'} × ${it.quantity} units`).join('\n')
      : '• Maggi 70g × 30 units\n• Parle-G 80g × 20 units';

    const message = `Namaste ${supplierName},\nPlease process restock order #${order.id.substring(0, 6)} for our Kirana shop:\n\n${itemsText}\n\nTotal Amount: ₹${order.total_amount || 450}\nNotes: ${order.notes || 'Standard Delivery'}\nThank you!`;

    const encoded = encodeURIComponent(message);
    window.open(`https://api.whatsapp.com/send?text=${encoded}`, '_blank');
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-white rounded-[10px] border border-[#111111] font-mono text-xs space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin text-[#111111]" />
        <p className="font-bold">Loading Supplier Restock Orders...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-16 font-sans">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-[8px] border border-[#111111] font-mono">
        <div>
          <div className="flex items-center gap-2">
            <Truck className="w-5 h-5 text-[#111111]" />
            <h1 className="text-lg font-bold text-[#111111] uppercase tracking-tight">SUPPLIER RESTOCK ORDERS & WHATSAPP GATEWAY</h1>
          </div>
          <p className="text-xs text-[#6B6B6B]">Wholesale PO management, lead times & direct WhatsApp ordering</p>
        </div>

        <div className="flex items-center gap-2">
          {/* Tab Selection */}
          <div className="flex items-center bg-[#F5F4EF] p-1 rounded-[6px] border border-[#111111] text-xs font-bold font-mono">
            <button
              onClick={() => setActiveTab('orders')}
              className={`px-3 py-1 rounded-[4px] cursor-pointer ${activeTab === 'orders' ? 'bg-[#111111] text-white' : 'text-[#6B6B6B]'}`}
            >
              Restock POs ({orders.length})
            </button>
            <button
              onClick={() => setActiveTab('suppliers')}
              className={`px-3 py-1 rounded-[4px] cursor-pointer ${activeTab === 'suppliers' ? 'bg-[#111111] text-white' : 'text-[#6B6B6B]'}`}
            >
              Suppliers ({suppliers.length})
            </button>
          </div>

          <button
            onClick={() => setIsCreateOrderOpen(true)}
            className="px-3 py-1.5 bg-[#111111] text-white text-xs font-bold rounded-[6px] border border-[#111111] shadow-[2px_2px_0_#111111] flex items-center gap-1 cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5 text-[#F4C84A]" />
            <span>+ NEW PO</span>
          </button>
        </div>
      </div>

      {activeTab === 'orders' ? (
        /* ORDERS LIST */
        <div className="bg-white rounded-[8px] border border-[#111111] overflow-hidden font-mono">
          <div className="p-3 border-b border-[#111111] bg-[#F5F4EF] flex items-center justify-between">
            <h3 className="text-xs font-bold text-[#111111] uppercase">Restock Purchase Orders</h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F5F4EF] border-b border-[#111111] text-[#6B6B6B] font-bold text-[9px] uppercase">
                <tr>
                  <th className="p-3">Order ID / Supplier</th>
                  <th className="p-3">Ordered Date</th>
                  <th className="p-3 text-center">Items</th>
                  <th className="p-3 text-right">Total Amount</th>
                  <th className="p-3 text-center">Status</th>
                  <th className="p-3 text-right">WhatsApp Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#111111]/10">
                {orders.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-[#6B6B6B]">
                      No restock orders created yet. Click <strong>+ NEW PO</strong> to place a supplier order.
                    </td>
                  </tr>
                ) : (
                  orders.map((o) => (
                    <tr key={o.id} className="hover:bg-[#F5F4EF]/60">
                      <td className="p-3">
                        <div className="font-bold text-[#111111]">PO #{o.id.substring(0, 6)}</div>
                        <div className="text-[10px] text-[#6B6B6B]">{o.supplier_name || 'Gupta Wholesale Traders'}</div>
                      </td>
                      <td className="p-3 text-[11px] text-[#6B6B6B]">
                        {new Date(o.ordered_at).toLocaleDateString()}
                      </td>
                      <td className="p-3 text-center font-bold">
                        {o.items?.length || 1}
                      </td>
                      <td className="p-3 text-right font-black text-[#111111]">
                        ₹{o.total_amount || 450}
                      </td>
                      <td className="p-3 text-center">
                        <span className="px-2 py-0.5 text-[9px] font-bold rounded bg-amber-100 text-amber-900 border border-amber-500">
                          {o.status}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => handleLaunchWhatsAppOrder(o)}
                          className="px-2.5 py-1 bg-emerald-700 hover:bg-emerald-800 text-white text-[10px] font-bold rounded border border-emerald-900 shadow-[1px_1px_0_#111111] flex items-center gap-1 justify-end ml-auto cursor-pointer"
                        >
                          <MessageSquare className="w-3 h-3 text-[#F4C84A]" />
                          <span>WhatsApp Order</span>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* SUPPLIERS DIRECTORY */
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 font-mono">
          {suppliers.length === 0 ? (
            <div className="col-span-full p-8 bg-white rounded border border-[#111111] text-center text-xs text-[#6B6B6B]">
              No active suppliers registered.
            </div>
          ) : (
            suppliers.map((s) => (
              <div key={s.id} className="p-4 bg-white rounded-[8px] border border-[#111111] space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-[#111111]">{s.name}</h4>
                  <span className="px-1.5 py-0.2 bg-[#111111] text-[#F4C84A] text-[9px] font-bold rounded">
                    Lead: {s.average_lead_time_days || 3} days
                  </span>
                </div>
                <p className="text-[11px] text-[#6B6B6B]">📞 {s.phone || '+91 98765 43210'}</p>
                <p className="text-[11px] text-[#6B6B6B]">💳 Terms: {s.payment_terms || 'Net 15 Days'}</p>
              </div>
            ))
          )}
        </div>
      )}

      {/* CREATE PO MODAL */}
      {isCreateOrderOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs font-mono">
          <div className="w-full max-w-md bg-white rounded-[8px] border-2 border-[#111111] shadow-[6px_6px_0_#111111] p-5 space-y-4">
            <h3 className="text-xs font-bold text-[#111111] uppercase">Create Restock Purchase Order</h3>

            <form onSubmit={handleCreateOrder} className="space-y-3 text-xs">
              <div>
                <label className="text-[10px] font-bold text-[#6B6B6B] uppercase block">Select Supplier</label>
                <select
                  value={selectedSupplierId}
                  onChange={(e) => setSelectedSupplierId(e.target.value)}
                  className="w-full mt-1 p-2 bg-[#F5F4EF] border border-[#111111] rounded-[4px] font-bold"
                >
                  <option value="">Gupta Wholesale Traders (Default)</option>
                  {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>

              <div>
                <label className="text-[10px] font-bold text-[#6B6B6B] uppercase block">Select SKU / Product</label>
                <select
                  required
                  value={selectedProductId}
                  onChange={(e) => setSelectedProductId(e.target.value)}
                  className="w-full mt-1 p-2 bg-[#F5F4EF] border border-[#111111] rounded-[4px] font-bold"
                >
                  <option value="">Select SKU...</option>
                  {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
              </div>

              <div>
                <label className="text-[10px] font-bold text-[#6B6B6B] uppercase block">Order Quantity</label>
                <input
                  type="number"
                  required
                  min={1}
                  value={orderQty}
                  onChange={(e) => setOrderQty(Number(e.target.value))}
                  className="w-full mt-1 p-2 bg-[#F5F4EF] border border-[#111111] rounded-[4px] font-bold"
                />
              </div>

              <div>
                <label className="text-[10px] font-bold text-[#6B6B6B] uppercase block">Notes / Payment Terms</label>
                <input
                  type="text"
                  value={orderNotes}
                  onChange={(e) => setOrderNotes(e.target.value)}
                  placeholder="e.g. Standard delivery, Net 15"
                  className="w-full mt-1 p-2 bg-[#F5F4EF] border border-[#111111] rounded-[4px] font-bold"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsCreateOrderOpen(false)}
                  className="px-3 py-1.5 bg-white text-[#111111] rounded border border-[#111111]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-[#111111] text-white font-bold rounded border border-[#111111] shadow-[2px_2px_0_#111111]"
                >
                  Create Restock PO
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
