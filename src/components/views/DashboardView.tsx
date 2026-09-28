import React, { useState, useEffect } from 'react';
import { MetricCard } from '../dashboard/MetricCard';
import { SalesOverviewChart } from '../dashboard/SalesOverviewChart';
import { StoreIntelligenceCard } from '../dashboard/StoreIntelligenceCard';
import { InventoryHealthCard } from '../dashboard/InventoryHealthCard';
import { TopProductsCard } from '../dashboard/TopProductsCard';
import { KhataCard } from '../dashboard/KhataCard';
import { ExpenseBreakdownCard } from '../dashboard/ExpenseBreakdownCard';
import { ActionCenter } from '../dashboard/ActionCenter';
import { QuickActionsRow } from '../header/TopHeader';
import { ActionItem, MetricData } from '../../types/kirana';
import { dashboardAPI, DashboardSummary } from '../../api/services';

const FALLBACK_METRIC_CARDS: MetricData[] = [
  {
    title: "TODAY'S SALES",
    value: "₹18,450",
    numericValue: 18450,
    change: "+12.4% vs yesterday",
    isPositive: true,
    subtitle: "126 total orders completed",
    bgVariant: "yellow",
    sparkline: [12000, 14200, 13800, 15600, 16100, 16400, 18450],
  },
  {
    title: "TODAY'S PROFIT",
    value: "₹4,280",
    numericValue: 4280,
    change: "+8.2% estimated margin",
    isPositive: true,
    subtitle: "23.2% average gross margin",
    bgVariant: "mint",
    sparkline: [2800, 3100, 3400, 3650, 3800, 3950, 4280],
  },
  {
    title: "TOTAL ORDERS",
    value: "126",
    numericValue: 126,
    change: "+14 peak hours",
    isPositive: true,
    subtitle: "Average basket: ₹146.4",
    bgVariant: "lavender",
    sparkline: [85, 92, 104, 110, 115, 112, 126],
  },
  {
    title: "LOW STOCK ITEMS",
    value: "12",
    numericValue: 12,
    change: "4 critical items",
    isPositive: false,
    subtitle: "3 restock orders pending",
    bgVariant: "peach",
    sparkline: [6, 8, 9, 10, 11, 14, 12],
  },
];

interface DashboardViewProps {
  onOpenQuickBilling: () => void;
  onOpenAddProduct: () => void;
  onOpenAddExpense: () => void;
  onOpenAddCustomer: () => void;
  onOpenRecordPayment: () => void;
  onOpenAIAdvisor: (initialQuery?: string) => void;
  onNavigateView: (view: any) => void;
  onOpenReceiptScanner?: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  onOpenQuickBilling,
  onOpenAddProduct,
  onOpenAddExpense,
  onOpenAddCustomer,
  onOpenRecordPayment,
  onOpenAIAdvisor,
  onNavigateView,
  onOpenReceiptScanner,
}) => {
  const [dateFilter, setDateFilter] = useState<'today' | 'week' | 'month'>('today');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    dashboardAPI.getSummary()
      .then((data) => {
        if (isMounted) {
          setSummary(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.warn('Dashboard API call failed, using fallback display metrics', err);
        if (isMounted) setLoading(false);
      });
    return () => { isMounted = false; };
  }, [dateFilter]);

  // Construct metric cards from live API data if available, fallback to mock UI cards
  const metricCards: MetricData[] = summary ? [
    {
      title: "TODAY'S SALES",
      value: `₹${Number(summary.today_sales || 0).toLocaleString('en-IN')}`,
      numericValue: Number(summary.today_sales || 0),
      change: "+12.4% vs yesterday",
      isPositive: true,
      subtitle: `${summary.today_orders || 0} total orders completed`,
      bgVariant: "yellow",
      sparkline: [12000, 14200, 13800, 15600, 16100, 16400, Number(summary.today_sales || 18450)],
    },
    {
      title: "TODAY'S PROFIT",
      value: `₹${Number(summary.today_profit || 0).toLocaleString('en-IN')}`,
      numericValue: Number(summary.today_profit || 0),
      change: "+8.2% estimated margin",
      isPositive: true,
      subtitle: "Net profit calculated from transactions",
      bgVariant: "mint",
      sparkline: [2800, 3100, 3400, 3650, 3800, 3950, Number(summary.today_profit || 4280)],
    },
    {
      title: "TOTAL ORDERS",
      value: `${summary.today_orders || 0}`,
      numericValue: summary.today_orders || 0,
      change: "+14 peak hours",
      isPositive: true,
      subtitle: `Inventory Value ₹${Number(summary.inventory_value || 0).toLocaleString('en-IN')}`,
      bgVariant: "lavender",
      sparkline: [85, 92, 104, 110, 115, 112, summary.today_orders || 126],
    },
    {
      title: "LOW STOCK ITEMS",
      value: `${summary.low_stock_count || 0}`,
      numericValue: summary.low_stock_count || 0,
      change: `${summary.out_of_stock_count || 0} out of stock`,
      isPositive: false,
      subtitle: `${summary.pending_supplier_orders_count || 0} restock orders pending`,
      bgVariant: "peach",
      sparkline: [6, 8, 9, 10, 11, 14, summary.low_stock_count || 12],
    },
  ] : FALLBACK_METRIC_CARDS;

  const handleActionClick = (item: ActionItem) => {
    switch (item.actionType) {
      case 'review_stock':
        onNavigateView('inventory');
        break;
      case 'view_khata':
        onNavigateView('khata');
        break;
      case 'view_supplier':
        onNavigateView('suppliers');
        break;
      case 'view_insight':
        onOpenAIAdvisor("Tell me more about Maggi stock velocity & weekend demand predictions.");
        break;
    }
  };

  return (
    <div className="space-y-5 pb-16 font-sans">
      
      {/* Date Filter & Quick Actions Subheader */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-white p-3 rounded-[8px] border border-[#111111]">
        {/* Date Selector Pill */}
        <div className="flex items-center gap-1 bg-[#F5F4EF] p-1 rounded-[6px] border border-[#111111] self-start font-mono">
          <button
            onClick={() => setDateFilter('today')}
            className={`px-3 py-1 text-xs font-bold rounded-[4px] transition-all cursor-pointer ${
              dateFilter === 'today'
                ? 'bg-[#111111] text-white'
                : 'text-[#6B6B6B] hover:text-[#111111]'
            }`}
          >
            Today
          </button>
          <button
            onClick={() => setDateFilter('week')}
            className={`px-3 py-1 text-xs font-bold rounded-[4px] transition-all cursor-pointer ${
              dateFilter === 'week'
                ? 'bg-[#111111] text-white'
                : 'text-[#6B6B6B] hover:text-[#111111]'
            }`}
          >
            This Week
          </button>
          <button
            onClick={() => setDateFilter('month')}
            className={`px-3 py-1 text-xs font-bold rounded-[4px] transition-all cursor-pointer ${
              dateFilter === 'month'
                ? 'bg-[#111111] text-white'
                : 'text-[#6B6B6B] hover:text-[#111111]'
            }`}
          >
            This Month
          </button>
        </div>

        {/* Horizontal Quick Actions */}
        <QuickActionsRow
          onOpenQuickBilling={onOpenQuickBilling}
          onOpenAddProduct={onOpenAddProduct}
          onOpenAddExpense={onOpenAddExpense}
          onOpenAddCustomer={onOpenAddCustomer}
          onOpenRecordPayment={onOpenRecordPayment}
          onOpenReceiptScanner={onOpenReceiptScanner}
        />
      </div>

      {/* ROW 1: 4 Primary Business Overview Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricCards.map((metric, idx) => (
          <MetricCard
            key={idx}
            data={metric}
            onClick={() => {
              if (metric.title.includes('SALES')) onNavigateView('reports');
              else if (metric.title.includes('STOCK')) onNavigateView('inventory');
            }}
          />
        ))}
      </div>

      {/* ROW 2: Sales Overview Chart (2/3) + Store Intelligence Card (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <SalesOverviewChart />
        </div>
        <div className="lg:col-span-1">
          <StoreIntelligenceCard onOpenAIAdvisor={onOpenAIAdvisor} />
        </div>
      </div>

      {/* ROW 3: Inventory Health (1/2) + Top Selling Products (1/2) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <InventoryHealthCard
          onViewAllInventory={() => onNavigateView('inventory')}
          onReorderProduct={() => onNavigateView('inventory')}
        />
        <TopProductsCard />
      </div>

      {/* ROW 4: Khata Udhaar Ledger (1/2) + Expense Breakdown (1/2) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <KhataCard
          onViewKhata={() => onNavigateView('khata')}
          onAddUdhaar={onOpenRecordPayment}
        />
        <ExpenseBreakdownCard
          onViewExpenses={() => onNavigateView('expenses')}
          onAddExpense={onOpenAddExpense}
        />
      </div>

      {/* ROW 5: Operational Action Center ("NEEDS ATTENTION") */}
      <ActionCenter onActionClick={handleActionClick} />

    </div>
  );
};
