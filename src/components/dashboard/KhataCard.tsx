import React from 'react';
import { ArrowRight, Send } from 'lucide-react';
import { KhataCustomer } from '../../types/kirana';

const KHATA_CUSTOMERS: KhataCustomer[] = [
  { id: 'c1', name: 'Ramesh Kumar', phone: '+91 98765 43210', dueAmount: 2450, lastPurchaseDate: '2026-09-24', status: 'critical', daysOverdue: 12 },
  { id: 'c2', name: 'Suresh Patel', phone: '+91 98123 45678', dueAmount: 1200, lastPurchaseDate: '2026-09-27', status: 'pending', daysOverdue: 4 },
  { id: 'c3', name: 'Meena Devi', phone: '+91 97654 32109', dueAmount: 4120, lastPurchaseDate: '2026-09-18', status: 'critical', daysOverdue: 18 },
];

interface KhataCardProps {
  onViewKhata: () => void;
  onSendReminder?: (customer: KhataCustomer) => void;
  onAddUdhaar?: () => void;
}

export const KhataCard: React.FC<KhataCardProps> = ({
  onViewKhata,
  onSendReminder,
  onAddUdhaar,
}) => {
  const totalOutstanding = 24850;
  const overdueTotal = 6420;
  const customersCount = 18;

  return (
    <div className="bg-white rounded-[8px] border border-[#111111] p-5 flex flex-col justify-between h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#111111] mb-4">
          <h2 className="text-xs font-mono font-bold text-[#111111] tracking-wider uppercase">KHATA</h2>
          <button
            onClick={onViewKhata}
            className="flex items-center gap-1 text-xs font-bold text-[#111111] font-mono hover:underline cursor-pointer"
          >
            <span>VIEW LEDGER</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Highlight Banner */}
        <div className="p-3 bg-[#F5F4EF] rounded-[6px] border border-[#111111] flex items-center justify-between mb-4 font-mono">
          <div>
            <span className="text-[9px] text-[#6B6B6B] font-bold uppercase block">OUTSTANDING DUES</span>
            <span className="text-xl font-extrabold text-[#111111]">₹{totalOutstanding.toLocaleString('en-IN')}</span>
          </div>
          <div className="text-right">
            <span className="text-[9px] text-rose-700 font-bold uppercase block">OVERDUE</span>
            <span className="text-sm font-extrabold text-rose-700">₹{overdueTotal.toLocaleString('en-IN')}</span>
          </div>
          <div className="text-right pl-2 border-l border-[#111111]">
            <span className="text-[9px] text-[#6B6B6B] font-bold block uppercase">CUSTOMERS</span>
            <span className="text-xs font-bold text-[#111111]">{customersCount} active</span>
          </div>
        </div>

        {/* Customer Dues List */}
        <div className="space-y-2">
          {KHATA_CUSTOMERS.slice(0, 3).map((customer) => (
            <div
              key={customer.id}
              className="flex items-center justify-between p-2.5 rounded-[6px] bg-white border border-[#111111] hover:bg-[#F5F4EF] transition-colors"
            >
              <div className="flex items-center gap-2.5">
                <span className="w-5 h-5 rounded-[2px] bg-[#111111] text-white font-mono font-bold text-[10px] flex items-center justify-center">
                  {customer.name.charAt(0)}
                </span>
                <div>
                  <div className="font-bold text-xs text-[#111111]">{customer.name}</div>
                  <div className="text-[10px] font-mono text-[#6B6B6B]">
                    <span className={customer.status === 'critical' ? 'text-rose-700 font-bold' : 'text-[#6B6B6B]'}>
                      {customer.daysOverdue}d overdue
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 font-mono">
                <span className="font-black text-xs text-[#111111]">
                  ₹{customer.dueAmount.toLocaleString('en-IN')}
                </span>

                <button
                  onClick={() => onSendReminder && onSendReminder(customer)}
                  className="px-2 py-1 bg-[#111111] hover:bg-black text-white rounded-[4px] text-[10px] font-bold flex items-center gap-1 cursor-pointer"
                  title="Send WhatsApp Reminder"
                >
                  <Send className="w-3 h-3 text-[#F4C84A]" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Button */}
      <div className="mt-4 pt-3 border-t border-[#111111] flex items-center justify-between">
        <button
          onClick={onViewKhata}
          className="w-full py-2 bg-[#111111] hover:bg-black text-white text-xs font-bold font-mono rounded-[6px] border border-[#111111] shadow-[2px_2px_0_#111111] transition-transform cursor-pointer flex items-center justify-center gap-1"
        >
          <span>View Khata →</span>
        </button>
      </div>
    </div>
  );
};
