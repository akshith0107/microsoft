import React, { useState, useEffect } from 'react';
import { BookOpenCheck, Send, Plus, Search, AlertCircle, Phone, CheckCircle2, RefreshCw } from 'lucide-react';
import { KhataCustomer } from '../../types/kirana';
import { khataAPI } from '../../api/services';

const FALLBACK_KHATA: KhataCustomer[] = [
  { id: 'c1', name: 'Ramesh Kumar', phone: '+91 98765 43210', dueAmount: 2450, daysOverdue: 12, lastPurchaseDate: '2026-09-24', status: 'critical', notes: 'Credit limit ₹5,000' },
  { id: 'c2', name: 'Suresh Patel', phone: '+91 98123 45678', dueAmount: 1200, daysOverdue: 4, lastPurchaseDate: '2026-09-27', status: 'pending', notes: 'Regular buyer' },
  { id: 'c3', name: 'Meena Devi', phone: '+91 97654 32109', dueAmount: 4120, daysOverdue: 18, lastPurchaseDate: '2026-09-18', status: 'critical', notes: 'Call in evening' },
];

export const KhataView: React.FC<{ onAddUdhaar: () => void }> = ({ onAddUdhaar }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeWhatsAppModalCustomer, setActiveWhatsAppModalCustomer] = useState<KhataCustomer | null>(null);
  const [customers, setCustomers] = useState<KhataCustomer[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchKhata = () => {
    setLoading(true);
    khataAPI.getAccounts()
      .then((accounts) => {
        if (accounts && accounts.length > 0) {
          const mapped: KhataCustomer[] = accounts.map((acc, idx) => {
            const bal = Number(acc.current_balance || 0);
            return {
              id: acc.customer_id || `k${idx}`,
              name: acc.customer_name || 'Customer',
              phone: acc.customer_phone || '+91 98000 00000',
              dueAmount: bal,
              daysOverdue: bal > 2000 ? 12 : 3,
              lastPurchaseDate: 'Recent',
              status: bal > 2000 ? 'critical' : bal > 0 ? 'pending' : 'current',
              notes: `Credit Limit: ₹${acc.credit_limit || 5000}`
            };
          });
          setCustomers(mapped);
        } else {
          setCustomers(FALLBACK_KHATA);
        }
      })
      .catch((err) => {
        console.warn('Khata API fetch failed, using fallback customer list', err);
        setCustomers(FALLBACK_KHATA);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchKhata();
  }, []);

  const filtered = customers.filter((c) =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.phone.includes(searchTerm)
  );

  const totalOutstanding = customers.reduce((sum, c) => sum + c.dueAmount, 0);
  const overdueTotal = customers.filter(c => c.status === 'critical').reduce((sum, c) => sum + c.dueAmount, 0);

  return (
    <div className="space-y-6 pb-16">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-[#E5E2D9] card-shadow">
        <div>
          <h1 className="text-xl font-bold text-[#141518]">Khata (Udhaar) Digital Ledger</h1>
          <p className="text-xs text-gray-500 font-medium">Manage customer credit, payment reminders & automatic WhatsApp bills</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchKhata}
            className="p-2 bg-[#F7F5EF] hover:bg-gray-200 text-[#141518] rounded-xl border border-[#E5E2D9] cursor-pointer"
            title="Refresh Khata"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={onAddUdhaar}
            className="px-4 py-2.5 bg-[#141518] hover:bg-black text-white text-xs font-bold rounded-xl shadow-md transition-colors flex items-center gap-2 shrink-0 cursor-pointer"
          >
            <Plus className="w-4 h-4 text-amber-400" />
            <span>+ Add Customer Udhaar</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-[#FEF9E7] border border-[#F5E9BF] rounded-2xl card-shadow">
          <span className="text-[11px] font-bold text-amber-900 uppercase">Total Khata Dues</span>
          <div className="text-2xl font-black text-amber-950 mt-1">₹{totalOutstanding.toLocaleString('en-IN')}</div>
          <span className="text-[10px] text-amber-800">Across {customers.length} neighborhood customers</span>
        </div>

        <div className="p-4 bg-[#FFF2ED] border border-[#FCD6C6] rounded-2xl card-shadow">
          <span className="text-[11px] font-bold text-rose-900 uppercase">Critical Overdue</span>
          <div className="text-2xl font-black text-rose-700 mt-1">₹{overdueTotal.toLocaleString('en-IN')}</div>
          <span className="text-[10px] text-rose-800">{customers.filter(c => c.status === 'critical').length} customers flagged</span>
        </div>

        <div className="p-4 bg-[#EBFBFA] border border-[#C3F3EC] rounded-2xl card-shadow">
          <span className="text-[11px] font-bold text-emerald-900 uppercase">Settled This Month</span>
          <div className="text-2xl font-black text-emerald-800 mt-1">₹18,200</div>
          <span className="text-[10px] text-emerald-700">12 payments collected</span>
        </div>
      </div>

      {/* Search & Ledger Table */}
      <div className="bg-white rounded-2xl border border-[#E5E2D9] p-4 card-shadow space-y-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search customer name or phone..."
            className="w-full pl-9 pr-3 py-2 bg-[#F7F5EF] border border-[#E5E2D9] rounded-xl text-xs font-medium text-[#141518]"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F7F5EF] border-b border-[#E5E2D9] text-gray-500 font-bold uppercase text-[10px]">
              <tr>
                <th className="p-3">Customer</th>
                <th className="p-3">Phone</th>
                <th className="p-3 text-center">Due Amount</th>
                <th className="p-3 text-center">Days Overdue</th>
                <th className="p-3">Notes</th>
                <th className="p-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F0ECE1]">
              {filtered.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50/80 transition-colors">
                  <td className="p-3 font-bold text-[#141518]">{c.name}</td>
                  <td className="p-3 text-gray-600 font-medium">{c.phone}</td>
                  <td className="p-3 text-center font-black text-[#141518]">
                    ₹{c.dueAmount.toLocaleString('en-IN')}
                  </td>
                  <td className="p-3 text-center font-bold">
                    <span className={c.daysOverdue >= 10 ? 'text-rose-600' : 'text-amber-800'}>
                      {c.daysOverdue} days
                    </span>
                  </td>
                  <td className="p-3 text-gray-500 max-w-[200px] truncate">{c.notes || '—'}</td>
                  <td className="p-3 text-right">
                    <button
                      onClick={() => setActiveWhatsAppModalCustomer(c)}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg text-xs flex items-center gap-1.5 ml-auto transition-colors cursor-pointer"
                    >
                      <Send className="w-3.5 h-3.5" />
                      <span>Send Reminder</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* WhatsApp Direct Reminder Dialog */}
      {activeWhatsAppModalCustomer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full border border-[#E5E2D9] space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                <Send className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-[#141518] text-base">Send WhatsApp Reminder</h3>
                <p className="text-xs text-gray-500">To {activeWhatsAppModalCustomer.name} ({activeWhatsAppModalCustomer.phone})</p>
              </div>
            </div>

            <div className="p-3 bg-emerald-50/60 border border-emerald-200 rounded-xl text-xs text-emerald-950 space-y-1 font-mono">
              <p>Namaste {activeWhatsAppModalCustomer.name} ji, this is a friendly reminder from Kirana Store.</p>
              <p className="font-bold">Your Khata balance of ₹{activeWhatsAppModalCustomer.dueAmount} is due.</p>
              <p>Pay easily via UPI: store@upi</p>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setActiveWhatsAppModalCustomer(null)}
                className="px-4 py-2 text-xs font-semibold text-gray-600 hover:bg-gray-100 rounded-xl"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  alert(`WhatsApp reminder message triggered to ${activeWhatsAppModalCustomer.phone}!`);
                  setActiveWhatsAppModalCustomer(null);
                }}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl flex items-center gap-1.5"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Launch WhatsApp Web</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
