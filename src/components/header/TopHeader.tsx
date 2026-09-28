import React, { useState } from 'react';
import { 
  Search, 
  Bell, 
  Store, 
  ChevronDown, 
  Menu, 
  Receipt, 
  PackagePlus, 
  CreditCard, 
  UserPlus,
  ArrowUpRight,
  Mic,
  FileText,
  LogOut,
  User as UserIcon,
  Check
} from 'lucide-react';
import { User, Shop } from '../../api/services';

interface TopHeaderProps {
  currentUser?: User | null;
  availableShops?: Shop[];
  currentShop?: Shop | null;
  onSelectShop?: (shopId: string) => void;
  onLogout?: () => void;
  onOpenSearch: () => void;
  onOpenQuickBilling: () => void;
  onOpenVoiceBilling?: () => void;
  onOpenReceiptScanner?: () => void;
  onOpenAddProduct: () => void;
  onOpenAddExpense: () => void;
  onOpenAddCustomer: () => void;
  onOpenRecordPayment: () => void;
  onOpenMobileMenu?: () => void;
}

export const TopHeader: React.FC<TopHeaderProps> = ({
  currentUser,
  availableShops = [],
  currentShop,
  onSelectShop,
  onLogout,
  onOpenSearch,
  onOpenQuickBilling,
  onOpenVoiceBilling,
  onOpenReceiptScanner,
  onOpenAddProduct,
  onOpenAddExpense,
  onOpenAddCustomer,
  onOpenRecordPayment,
  onOpenMobileMenu,
}) => {
  const [storeDropdownOpen, setStoreDropdownOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const userName = currentUser?.name || "Store Owner";
  const storeName = currentShop?.name || "Gupta Kirana & General Store";

  return (
    <header className="sticky top-0 z-30 bg-[#F5F4EF] border-b border-[#111111] px-4 lg:px-6 py-3">
      <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        
        {/* Left Greeting */}
        <div className="flex items-center gap-3">
          <button 
            onClick={onOpenMobileMenu}
            className="p-1.5 rounded-[6px] bg-white border border-[#111111] text-[#111111] lg:hidden"
            aria-label="Open sidebar menu"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg lg:text-xl font-bold tracking-tight text-[#111111]">
                Welcome back, {userName}.
              </h1>
              <span className="inline-flex items-center text-[10px] font-mono font-bold bg-[#111111] text-white px-1.5 py-0.5 rounded-[3px]">
                STORE ONLINE
              </span>
            </div>
            <p className="text-xs text-[#6B6B6B] font-medium mt-0.5">
              DukaanPulse Operational Console · Active Store: {storeName}
            </p>
          </div>
        </div>

        {/* Right Search, Actions & Profile */}
        <div className="flex items-center flex-wrap gap-2">
          {/* Quick Search */}
          <button
            onClick={onOpenSearch}
            className="flex items-center gap-2 px-3 py-1.5 bg-white rounded-[6px] border border-[#111111] text-xs font-semibold text-[#111111] hover:bg-[#F4C84A] transition-colors"
          >
            <Search className="w-3.5 h-3.5 text-[#111111]" />
            <span className="hidden sm:inline">Search products, customers, bills...</span>
            <span className="sm:hidden">Search...</span>
            <kbd className="hidden md:inline-block px-1 py-0.2 text-[9px] font-mono font-bold bg-[#111111] text-white rounded-[2px]">
              ⌘K
            </kbd>
          </button>

          {/* Store Dropdown & Profile */}
          <div className="relative">
            <button
              onClick={() => setStoreDropdownOpen(!storeDropdownOpen)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-white rounded-[6px] border border-[#111111] text-xs font-bold text-[#111111] hover:bg-[#F5F4EF]"
            >
              <Store className="w-3.5 h-3.5 text-[#111111]" />
              <span className="truncate max-w-[120px]">{storeName}</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>

            {storeDropdownOpen && (
              <div className="absolute right-0 mt-1 w-64 bg-white rounded-[8px] border-2 border-[#111111] shadow-[4px_4px_0_#111111] p-2.5 z-50 space-y-2">
                <div className="flex items-center justify-between pb-1 border-b border-[#111111]">
                  <div>
                    <div className="text-[11px] font-bold text-[#111111] truncate">{userName}</div>
                    <div className="text-[9px] font-mono text-[#6B6B6B] truncate">{currentUser?.email}</div>
                  </div>
                  <button
                    onClick={() => {
                      setStoreDropdownOpen(false);
                      if (onLogout) onLogout();
                    }}
                    className="p-1.5 bg-rose-50 text-rose-700 hover:bg-rose-100 rounded-[4px] border border-rose-300 font-bold text-[10px] flex items-center gap-1 cursor-pointer"
                    title="Sign Out"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Logout</span>
                  </button>
                </div>

                <div className="px-1 text-[9px] font-mono font-bold text-[#6B6B6B] uppercase">Active Stores ({availableShops.length || 1})</div>
                
                <div className="space-y-1 max-h-36 overflow-y-auto pr-0.5">
                  {availableShops.length > 0 ? (
                    availableShops.map((s) => (
                      <button
                        key={s.id}
                        onClick={() => {
                          if (onSelectShop) onSelectShop(s.id);
                          setStoreDropdownOpen(false);
                        }}
                        className={`w-full text-left p-2 rounded-[4px] border text-xs font-bold flex items-center justify-between transition-colors cursor-pointer ${
                          currentShop?.id === s.id
                            ? 'bg-[#111111] text-white border-[#111111]'
                            : 'bg-white text-[#111111] border-gray-300 hover:border-[#111111]'
                        }`}
                      >
                        <div className="truncate">
                          <div>{s.name}</div>
                          {s.city && <div className={`text-[9px] font-normal ${currentShop?.id === s.id ? 'text-[#D0D0D0]' : 'text-[#6B6B6B]'}`}>{s.city}</div>}
                        </div>
                        {currentShop?.id === s.id && <Check className="w-3.5 h-3.5 text-[#F4C84A] shrink-0" />}
                      </button>
                    ))
                  ) : (
                    <div className="p-2 rounded-[4px] bg-[#F5F4EF] border border-[#111111] text-[#111111] font-bold text-xs">
                      {storeName}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Notifications Bell */}
          <button
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            className="p-1.5 bg-white rounded-[6px] border border-[#111111] text-[#111111] hover:bg-[#F4C84A] relative"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-rose-600 border border-[#111111]" />
          </button>

          {/* Voice Billing Button */}
          <button
            onClick={onOpenVoiceBilling}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#111111] hover:bg-black text-white rounded-[6px] border border-[#111111] text-xs font-bold shadow-[2px_2px_0_#111111] cursor-pointer"
            title="Voice Billing POS"
          >
            <Mic className="w-3.5 h-3.5 text-[#F4C84A] animate-pulse" />
            <span className="hidden sm:inline">VOICE BILL</span>
          </button>

          {/* OCR Receipt Scanner Button */}
          <button
            onClick={onOpenReceiptScanner}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#111111] hover:bg-black text-white rounded-[6px] border border-[#111111] text-xs font-bold shadow-[2px_2px_0_#111111] cursor-pointer"
            title="Scan Invoice Receipt"
          >
            <FileText className="w-3.5 h-3.5 text-[#F4C84A]" />
            <span className="hidden sm:inline">SCAN RECEIPT</span>
          </button>

          {/* Primary CTA */}
          <button
            onClick={onOpenQuickBilling}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-[#111111] hover:bg-black text-white font-bold text-xs rounded-[6px] border border-[#111111] shadow-[2px_2px_0_#111111] cursor-pointer"
          >
            <Receipt className="w-3.5 h-3.5 text-[#F4C84A]" />
            <span>+ NEW BILL</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export const QuickActionsRow: React.FC<{
  onOpenQuickBilling: () => void;
  onOpenAddProduct: () => void;
  onOpenAddExpense: () => void;
  onOpenAddCustomer: () => void;
  onOpenRecordPayment: () => void;
  onOpenReceiptScanner?: () => void;
}> = ({
  onOpenQuickBilling,
  onOpenAddProduct,
  onOpenAddExpense,
  onOpenAddCustomer,
  onOpenRecordPayment,
  onOpenReceiptScanner,
}) => {
  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-1 no-scrollbar">
      <button
        onClick={onOpenQuickBilling}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-[#111111] text-white rounded-[6px] text-xs font-bold border border-[#111111] shadow-[2px_2px_0_#111111] hover:translate-x-[-1px] transition-transform cursor-pointer shrink-0"
      >
        <Receipt className="w-3.5 h-3.5 text-[#F4C84A]" />
        <span>+ NEW BILL</span>
      </button>

      <button
        onClick={onOpenReceiptScanner}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-[#111111] text-white rounded-[6px] text-xs font-bold border border-[#111111] shadow-[2px_2px_0_#111111] hover:translate-x-[-1px] transition-transform cursor-pointer shrink-0"
      >
        <FileText className="w-3.5 h-3.5 text-[#F4C84A]" />
        <span>SCAN RECEIPT</span>
      </button>

      <button
        onClick={onOpenAddProduct}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-[#111111] border border-[#111111] rounded-[6px] text-xs font-bold hover:bg-[#F5F4EF] transition-colors shrink-0 cursor-pointer"
      >
        <PackagePlus className="w-3.5 h-3.5" />
        <span>+ PRODUCT</span>
      </button>

      <button
        onClick={onOpenAddExpense}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-[#111111] border border-[#111111] rounded-[6px] text-xs font-bold hover:bg-[#F5F4EF] transition-colors shrink-0 cursor-pointer"
      >
        <CreditCard className="w-3.5 h-3.5" />
        <span>+ EXPENSE</span>
      </button>

      <button
        onClick={onOpenAddCustomer}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-[#111111] border border-[#111111] rounded-[6px] text-xs font-bold hover:bg-[#F5F4EF] transition-colors shrink-0 cursor-pointer"
      >
        <UserPlus className="w-3.5 h-3.5" />
        <span>+ CUSTOMER</span>
      </button>

      <button
        onClick={onOpenRecordPayment}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-[#111111] border border-[#111111] rounded-[6px] text-xs font-bold hover:bg-[#F5F4EF] transition-colors shrink-0 cursor-pointer"
      >
        <ArrowUpRight className="w-3.5 h-3.5" />
        <span>+ PAYMENT</span>
      </button>
    </div>
  );
};
