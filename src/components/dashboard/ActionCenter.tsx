import React from 'react';
import { ArrowRight } from 'lucide-react';
import { ActionItem } from '../../types/kirana';

const ACTION_ITEMS: ActionItem[] = [
  {
    id: 'act1',
    type: 'LOW_STOCK',
    title: '4 Items Below Reorder Level',
    description: 'Maggi 2-Min, Fortune Oil, Parle-G, and Amul Milk require immediate restock order.',
    timestamp: '10 mins ago',
    actionText: 'Review Stock',
    actionType: 'review_stock',
    urgent: true,
  },
  {
    id: 'act2',
    type: 'PAYMENT_DUE',
    title: '2 Khata Accounts Overdue >10 Days',
    description: 'Ramesh Kumar (₹2,450) and Meena Devi (₹4,120) exceed credit terms.',
    timestamp: '1 hour ago',
    actionText: 'Send WhatsApp Reminder',
    actionType: 'view_khata',
    urgent: true,
  },
  {
    id: 'act3',
    type: 'SUPPLIER',
    title: 'Sharma Traders Order Arriving Today',
    description: 'Expected delivery by 4:00 PM (Invoice #ST-9842, 12 Cases).',
    timestamp: '2 hours ago',
    actionText: 'View Order',
    actionType: 'view_supplier',
    urgent: false,
  },
  {
    id: 'act4',
    type: 'BUSINESS_INSIGHT',
    title: 'Snack Demand Velocity Spike Expected',
    description: 'Weekend demand forecasting predicts 35% higher sales for chips & soft drinks.',
    timestamp: 'AI Advisor',
    actionText: 'Explore Insight',
    actionType: 'view_insight',
    urgent: false,
  },
];

interface ActionCenterProps {
  onActionClick: (item: ActionItem) => void;
}

export const ActionCenter: React.FC<ActionCenterProps> = ({ onActionClick }) => {

  const getItemBadgeStyle = (type: ActionItem['type']) => {
    switch (type) {
      case 'LOW_STOCK':
        return 'bg-[#F4C84A] text-[#111111] border-[#111111]';
      case 'PAYMENT_DUE':
        return 'bg-rose-100 text-rose-900 border-rose-600';
      case 'SUPPLIER':
        return 'bg-white text-[#111111] border-[#111111]';
      case 'BUSINESS_INSIGHT':
        return 'bg-purple-100 text-purple-900 border-purple-600';
    }
  };

  return (
    <div className="bg-white rounded-[8px] border border-[#111111] p-5">
      {/* Top Header */}
      <div className="flex items-center justify-between pb-3 border-b border-[#111111] mb-4">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 bg-[#111111] rounded-[2px]" />
          <h2 className="text-xs font-mono font-bold text-[#111111] tracking-wider uppercase">NEEDS ATTENTION</h2>
        </div>
        <span className="text-[10px] font-mono font-bold bg-[#111111] text-white px-2 py-0.5 rounded-[2px]">
          4 OPERATIONAL TASKS
        </span>
      </div>

      {/* 4 Horizontally Structured Items Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {ACTION_ITEMS.map((item) => (
          <div
            key={item.id}
            className="p-3.5 bg-[#F5F4EF] rounded-[6px] border border-[#111111] flex flex-col justify-between hover:bg-white transition-colors"
          >
            <div>
              {/* Category Badge & Timestamp */}
              <div className="flex items-center justify-between mb-2 font-mono">
                <span className={`px-1.5 py-0.2 text-[9px] font-bold uppercase rounded-[2px] border ${getItemBadgeStyle(item.type)}`}>
                  {item.type.replace('_', ' ')}
                </span>
                <span className="text-[9px] text-[#6B6B6B] font-bold">
                  {item.timestamp}
                </span>
              </div>

              {/* Title & Short Description */}
              <h4 className="text-xs font-bold text-[#111111] mb-1 leading-snug">
                {item.title}
              </h4>
              <p className="text-[11px] text-[#6B6B6B] leading-relaxed">
                {item.description}
              </p>
            </div>

            {/* Action Button */}
            <div className="mt-3 pt-2 border-t border-[#111111]/15 flex items-center justify-end">
              <button
                onClick={() => onActionClick(item)}
                className="px-2.5 py-1 bg-[#111111] hover:bg-black text-white text-[11px] font-bold font-mono rounded-[4px] border border-[#111111] flex items-center gap-1 cursor-pointer"
              >
                <span>{item.actionType === 'review_stock' ? 'Review →' : 'View →'}</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
