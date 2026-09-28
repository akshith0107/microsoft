import React from 'react';
import { ArrowRight, Plus } from 'lucide-react';

const EXPENSES_CATEGORIES = [
  { name: 'Supplier Restock', amount: 28400, percentage: 66.3 },
  { name: 'Shop Rent & Electric', amount: 8500, percentage: 19.8 },
  { name: 'Staff Wages', amount: 4500, percentage: 10.5 },
  { name: 'Miscellaneous', amount: 1400, percentage: 3.4 },
];

interface ExpenseBreakdownCardProps {
  onViewExpenses: () => void;
  onAddExpense?: () => void;
}

export const ExpenseBreakdownCard: React.FC<ExpenseBreakdownCardProps> = ({
  onViewExpenses,
  onAddExpense,
}) => {
  const totalExpense = 42800;

  return (
    <div className="bg-white rounded-[8px] border border-[#111111] p-5 flex flex-col justify-between h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#111111] mb-4">
          <h2 className="text-xs font-mono font-bold text-[#111111] tracking-wider uppercase">EXPENSES</h2>
          <button
            onClick={onViewExpenses}
            className="flex items-center gap-1 text-xs font-bold text-[#111111] font-mono hover:underline cursor-pointer"
          >
            <span>DETAILS</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Total Expense Banner */}
        <div className="p-3 bg-[#F5F4EF] rounded-[6px] border border-[#111111] mb-4 font-mono flex items-center justify-between">
          <div>
            <span className="text-[9px] text-[#6B6B6B] font-bold uppercase block">THIS MONTH TOTAL</span>
            <span className="text-2xl font-black text-[#111111]">₹{totalExpense.toLocaleString('en-IN')}</span>
          </div>
          <span className="text-[10px] text-emerald-800 font-bold bg-emerald-100 border border-emerald-600 px-2 py-0.5 rounded-[2px]">
            -4.2% VS LAST MONTH
          </span>
        </div>

        {/* Expense Category Rows */}
        <div className="space-y-3 font-mono">
          {EXPENSES_CATEGORIES.map((cat) => (
            <div key={cat.name} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-[#111111] font-bold">{cat.name}</span>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-[#111111]">₹{cat.amount.toLocaleString('en-IN')}</span>
                  <span className="text-[10px] text-[#6B6B6B] font-bold w-7 text-right">{cat.percentage}%</span>
                </div>
              </div>
              {/* Progress bar line */}
              <div className="w-full h-2 bg-[#F5F4EF] rounded-[2px] overflow-hidden border border-[#111111]">
                <div
                  className="h-full bg-[#111111]"
                  style={{ width: `${cat.percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-[#111111] flex items-center justify-between">
        <button
          onClick={onAddExpense}
          className="w-full py-2 bg-white hover:bg-[#F5F4EF] text-[#111111] text-xs font-bold font-mono rounded-[6px] border border-[#111111] shadow-[2px_2px_0_#111111] transition-transform cursor-pointer flex items-center justify-center gap-1"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Expense</span>
        </button>
      </div>
    </div>
  );
};
