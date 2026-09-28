import React from 'react';
import { 
  LayoutDashboard, 
  Receipt, 
  Package, 
  Boxes, 
  Users, 
  Truck, 
  BookOpenCheck, 
  CreditCard, 
  TrendingUp, 
  Sparkles, 
  Bot, 
  Settings, 
  Store,
  ChevronRight,
  LogOut
} from 'lucide-react';
import { NavView } from '../../types/kirana';

interface SidebarProps {
  activeView: NavView;
  onSelectView: (view: NavView) => void;
  isOpenMobile?: boolean;
  onCloseMobile?: () => void;
}

interface NavItem {
  id: NavView;
  label: string;
  icon: React.ElementType;
  badge?: string;
}

interface NavGroup {
  groupName: string;
  items: NavItem[];
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  activeView, 
  onSelectView,
  isOpenMobile,
  onCloseMobile
}) => {

  const navGroups: NavGroup[] = [
    {
      groupName: "OVERVIEW",
      items: [
        { id: 'overview', label: 'Overview', icon: LayoutDashboard },
      ]
    },
    {
      groupName: "OPERATIONS",
      items: [
        { id: 'billing', label: 'Billing POS', icon: Receipt, badge: 'POS' },
        { id: 'products', label: 'Products', icon: Package },
        { id: 'inventory', label: 'Inventory', icon: Boxes, badge: '12 Low' },
      ]
    },
    {
      groupName: "RELATIONSHIPS",
      items: [
        { id: 'customers', label: 'Customers', icon: Users },
        { id: 'suppliers', label: 'Suppliers', icon: Truck },
        { id: 'khata', label: 'Khata Ledger', icon: BookOpenCheck, badge: '₹24.8k' },
      ]
    },
    {
      groupName: "BUSINESS",
      items: [
        { id: 'expenses', label: 'Expenses', icon: CreditCard },
        { id: 'reports', label: 'Reports', icon: TrendingUp },
        { id: 'insights', label: 'Insights', icon: Sparkles },
      ]
    },
    {
      groupName: "INTELLIGENCE",
      items: [
        { id: 'ai-advisor', label: 'AI Advisor', icon: Bot },
      ]
    }
  ];

  return (
    <>
      {/* Mobile overlay backdrop */}
      {isOpenMobile && (
        <div 
          className="fixed inset-0 bg-black/70 z-40 lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      <aside 
        className={`
          fixed top-0 bottom-0 left-0 z-50 w-[224px] bg-[#111111] text-[#888888] flex flex-col justify-between
          border-r border-[#222222] transition-transform duration-200 ease-in-out font-sans select-none
          ${isOpenMobile ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Top Brand Logo */}
        <div>
          <div className="h-14 px-4 flex items-center justify-between border-b border-[#222222]">
            <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => onSelectView('overview')}>
              {/* Monochrome geometric mark */}
              <div className="w-6 h-6 bg-[#F4C84A] text-[#111111] font-black text-xs flex items-center justify-center rounded-[3px]">
                D
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-white text-sm tracking-tight leading-none">DukaanPulse</span>
                <span className="text-[10px] text-[#666666] font-mono tracking-widest uppercase mt-0.5">STORE OS</span>
              </div>
            </div>
          </div>

          {/* Navigation Items */}
          <div className="px-2.5 py-3 space-y-4 overflow-y-auto max-h-[calc(100vh-130px)]">
            {navGroups.map((group) => (
              <div key={group.groupName} className="space-y-0.5">
                <div className="px-2 py-1 text-[9px] font-mono font-bold text-[#555555] tracking-widest uppercase">
                  {group.groupName}
                </div>
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeView === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => {
                        onSelectView(item.id);
                        if (onCloseMobile) onCloseMobile();
                      }}
                      className={`
                        w-full flex items-center justify-between px-2.5 py-1.5 rounded-[6px] text-xs font-semibold transition-all duration-100 cursor-pointer
                        ${isActive 
                          ? 'bg-white text-[#111111] border border-white font-bold' 
                          : 'text-[#888888] hover:text-white hover:bg-[#1A1A1A]'
                        }
                      `}
                    >
                      <div className="flex items-center gap-2">
                        <Icon 
                          className={`w-4 h-4 ${
                            isActive ? 'text-[#111111] stroke-[2.2]' : 'text-[#666666]'
                          }`} 
                        />
                        <span>{item.label}</span>
                      </div>
                      
                      {item.badge && (
                        <span className={`
                          text-[9px] px-1.5 py-0.2 font-mono font-bold rounded-[3px]
                          ${isActive 
                            ? 'bg-[#111111] text-white' 
                            : 'bg-[#222222] text-[#888888]'
                          }
                        `}>
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom User Profile */}
        <div className="p-2.5 border-t border-[#222222] space-y-1.5 bg-[#111111]">
          <button 
            onClick={() => onSelectView('settings')}
            className={`
              w-full flex items-center justify-between px-2.5 py-1.5 rounded-[6px] text-xs font-semibold transition-colors
              ${activeView === 'settings' 
                ? 'bg-white text-[#111111]' 
                : 'text-[#888888] hover:text-white hover:bg-[#1A1A1A]'
              }
            `}
          >
            <div className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              <span>Store Settings</span>
            </div>
            <ChevronRight className="w-3.5 h-3.5 opacity-50" />
          </button>

          <div className="flex items-center justify-between p-2 rounded-[6px] bg-[#1A1A1A] border border-[#262626]">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-6 h-6 rounded-[3px] bg-[#F4C84A] text-[#111111] font-bold flex items-center justify-center text-[10px] shrink-0">
                RK
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-[11px] font-bold text-white truncate leading-none">Rajesh Kumar</span>
                <span className="text-[9px] text-[#666666] truncate font-mono">Store Owner</span>
              </div>
            </div>
            <button 
              title="Logout" 
              className="text-[#666666] hover:text-white p-1 rounded hover:bg-[#262626]"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
