import React, { useState, useEffect } from 'react';
import { NavView } from './types/kirana';
import { Sidebar } from './components/sidebar/Sidebar';
import { TopHeader } from './components/header/TopHeader';
import { DashboardView } from './components/views/DashboardView';
import { InventoryView } from './components/views/InventoryView';
import { KhataView } from './components/views/KhataView';
import { AnalyticsView } from './components/views/AnalyticsView';
import { RecommendationsView } from './components/views/RecommendationsView';
import { ComplaintsView } from './components/views/ComplaintsView';
import { SuppliersOrdersView } from './components/views/SuppliersOrdersView';
import { ExpensesView } from './components/views/ExpensesView';
import { QuickBillingModal } from './components/modals/QuickBillingModal';
import { VoiceBillingModal } from './components/modals/VoiceBillingModal';
import { SearchModal } from './components/modals/SearchModal';
import { AIAdvisorModal, FloatingAIButton } from './components/ai/AIAdvisorModal';
import { ReceiptScannerModal } from './components/modals/ReceiptScannerModal';
import { LoginPage } from './components/auth/LoginPage';
import { SignUpPage } from './components/auth/SignUpPage';
import { authAPI, User, Shop, TokenResponse } from './api/services';
import { getAuthToken, setAuthToken, getSelectedShopId, setSelectedShopId } from './api/client';
import { Loader2, Store } from 'lucide-react';

export function App() {
  // Navigation & UI state
  const [activeView, setActiveView] = useState<NavView>('overview');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Authentication & Session state
  const [authMode, setAuthMode] = useState<'AUTH_CHECK' | 'LOGIN' | 'SIGNUP' | 'AUTHENTICATED'>('AUTH_CHECK');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [availableShops, setAvailableShops] = useState<Shop[]>([]);
  const [currentShop, setCurrentShop] = useState<Shop | null>(null);

  // Modals state
  const [billingModalOpen, setBillingModalOpen] = useState(false);
  const [voiceModalOpen, setVoiceModalOpen] = useState(false);
  const [receiptScannerOpen, setReceiptScannerOpen] = useState(false);
  const [searchModalOpen, setSearchModalOpen] = useState(false);
  const [aiAdvisorOpen, setAiAdvisorOpen] = useState(false);
  const [aiInitialQuery, setAiInitialQuery] = useState<string | undefined>(undefined);

  // Toast banner state
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async () => {
    const token = getAuthToken();
    if (!token) {
      setAuthMode('LOGIN');
      return;
    }

    try {
      const user = await authAPI.getMe();
      const shops = await authAPI.getShops();

      setCurrentUser(user);
      setAvailableShops(shops);

      let selectedId = getSelectedShopId();
      let active = shops.find((s) => s.id === selectedId);

      if (!active && shops.length > 0) {
        active = shops[0];
        setSelectedShopId(active.id);
      }

      setCurrentShop(active || null);
      setAuthMode('AUTHENTICATED');
    } catch (err: any) {
      console.warn('Session check failed or expired:', err);
      setAuthToken(null);
      setSelectedShopId(null);
      setCurrentUser(null);
      setCurrentShop(null);
      setAuthMode('LOGIN');
    }
  };

  const handleAuthSuccess = async (res: TokenResponse) => {
    try {
      if (res.access_token) {
        setAuthToken(res.access_token);
      }
      if (res.shop_id) {
        setSelectedShopId(res.shop_id);
      }

      const user = await authAPI.getMe();
      const shops = await authAPI.getShops();

      setCurrentUser(user);
      setAvailableShops(shops);

      let selectedId = res.shop_id || getSelectedShopId();
      let active = shops.find((s) => s.id === selectedId);
      if (!active && shops.length > 0) {
        active = shops[0];
        setSelectedShopId(active.id);
      }

      setCurrentShop(active || null);
      setAuthMode('AUTHENTICATED');
      showToast(`Welcome back, ${user.name}!`);
    } catch (e: any) {
      console.error('Post-auth setup error:', e);
      setAuthMode('AUTHENTICATED');
    }
  };

  const handleSelectShop = (shopId: string) => {
    setSelectedShopId(shopId);
    const selected = availableShops.find((s) => s.id === shopId);
    if (selected) {
      setCurrentShop(selected);
      showToast(`Switched active store to: ${selected.name}`);
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    setCurrentUser(null);
    setCurrentShop(null);
    setAvailableShops([]);
    setAuthMode('LOGIN');
    showToast("Logged out of shop account.");
  };

  const handleOpenAIAdvisor = (query?: string) => {
    setAiInitialQuery(query);
    setAiAdvisorOpen(true);
  };

  if (authMode === 'AUTH_CHECK') {
    return (
      <div className="min-h-screen bg-[#F5F4EF] flex flex-col items-center justify-center p-4 font-mono text-[#111111]">
        <div className="flex flex-col items-center gap-3 p-8 bg-white border-2 border-[#111111] shadow-[6px_6px_0_#111111] rounded-[10px]">
          <div className="w-10 h-10 rounded-[6px] bg-[#F4C84A] border border-[#111111] flex items-center justify-center font-bold text-[#111111]">
            <Store className="w-6 h-6" />
          </div>
          <Loader2 className="w-6 h-6 animate-spin text-[#111111] mt-1" />
          <div className="font-bold text-xs uppercase tracking-wider">VERIFYING SHOP SESSION...</div>
          <div className="text-[10px] text-[#6B6B6B]">DukaanPulse Authentication System</div>
        </div>
      </div>
    );
  }

  if (authMode === 'LOGIN') {
    return (
      <LoginPage
        onSuccess={handleAuthSuccess}
        onSwitchToSignUp={() => setAuthMode('SIGNUP')}
      />
    );
  }

  if (authMode === 'SIGNUP') {
    return (
      <SignUpPage
        onSuccess={handleAuthSuccess}
        onSwitchToLogin={() => setAuthMode('LOGIN')}
      />
    );
  }

  const renderCurrentView = () => {
    switch (activeView) {
      case 'overview':
        return (
          <DashboardView
            onOpenQuickBilling={() => setBillingModalOpen(true)}
            onOpenAddProduct={() => showToast("Add Product Form Opened")}
            onOpenAddExpense={() => setActiveView('expenses')}
            onOpenAddCustomer={() => setActiveView('khata')}
            onOpenRecordPayment={() => showToast("Record Payment Modal Opened")}
            onOpenAIAdvisor={handleOpenAIAdvisor}
            onNavigateView={(view) => setActiveView(view)}
            onOpenReceiptScanner={() => setReceiptScannerOpen(true)}
          />
        );
      case 'billing':
        return (
          <div className="bg-white p-6 rounded-3xl border border-[#E5E2D9] card-shadow">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Billing POS Counter</h2>
              <button
                onClick={() => setBillingModalOpen(true)}
                className="px-4 py-2 bg-amber-400 font-bold text-amber-950 text-xs rounded-xl"
              >
                Open Fullscreen Billing Modal
              </button>
            </div>
            <p className="text-xs text-gray-500">Fast barcode scanning & UPI receipt billing counter for shopkeeper.</p>
          </div>
        );
      case 'inventory':
      case 'products':
        return (
          <InventoryView
            onAddProduct={() => showToast("Add New Product SKU modal opened")}
            onOpenReceiptScanner={() => setReceiptScannerOpen(true)}
          />
        );
      case 'khata':
      case 'customers':
        return (
          <KhataView
            onAddUdhaar={() => showToast("Add Customer Udhaar Entry")}
          />
        );
      case 'reports':
      case 'insights':
        return <AnalyticsView />;
      case 'ai-advisor':
        return <RecommendationsView />;
      case 'suppliers':
        return <SuppliersOrdersView />;
      case 'expenses':
        return <ExpensesView />;
      case 'settings':
        return <ComplaintsView />;
      default:
        return <AnalyticsView />;
    }
  };

  return (
    <div className="min-h-screen bg-[#F7F5EF] text-[#141518] flex">
      {/* Fixed Vertical Sidebar */}
      <Sidebar
        activeView={activeView}
        onSelectView={(view) => setActiveView(view)}
        isOpenMobile={mobileMenuOpen}
        onCloseMobile={() => setMobileMenuOpen(false)}
      />

      {/* Main Content Shell */}
      <div className="flex-1 lg:pl-[240px] flex flex-col min-w-0">
        
        {/* Top Sticky Header */}
        <TopHeader
          currentUser={currentUser}
          availableShops={availableShops}
          currentShop={currentShop}
          onSelectShop={handleSelectShop}
          onLogout={handleLogout}
          onOpenSearch={() => setSearchModalOpen(true)}
          onOpenQuickBilling={() => setBillingModalOpen(true)}
          onOpenVoiceBilling={() => setVoiceModalOpen(true)}
          onOpenReceiptScanner={() => setReceiptScannerOpen(true)}
          onOpenAddProduct={() => showToast("Add Product Modal Opened")}
          onOpenAddExpense={() => showToast("Add Expense Modal Opened")}
          onOpenAddCustomer={() => showToast("Add Customer Modal Opened")}
          onOpenRecordPayment={() => showToast("Record Payment Modal Opened")}
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
        />

        {/* Dynamic Page Body */}
        <main className="flex-1 p-4 lg:p-8 max-w-[1400px] w-full mx-auto">
          {renderCurrentView()}
        </main>
      </div>

      {/* Floating AI Advisor Button */}
      <FloatingAIButton onClick={() => handleOpenAIAdvisor()} />

      {/* Modals */}
      <QuickBillingModal
        isOpen={billingModalOpen}
        onClose={() => setBillingModalOpen(false)}
        onSaleComplete={(bill) => {
          showToast(`Bill #${bill.billNo} generated successfully! ₹${bill.total}`);
        }}
      />

      <VoiceBillingModal
        isOpen={voiceModalOpen}
        onClose={() => setVoiceModalOpen(false)}
        onSaleComplete={(bill) => {
          showToast(`Voice Bill #${bill.billNo} confirmed! ₹${bill.total}`);
        }}
      />

      <ReceiptScannerModal
        isOpen={receiptScannerOpen}
        onClose={() => setReceiptScannerOpen(false)}
        onPurchaseConfirmed={(pId) => {
          showToast(`Purchase order confirmed & stock updated!`);
        }}
      />

      <SearchModal
        isOpen={searchModalOpen}
        onClose={() => setSearchModalOpen(false)}
        onSelectProduct={(product) => {
          showToast(`Selected product: ${product.name}`);
        }}
        onSelectCustomer={(customer) => {
          showToast(`Selected customer: ${customer.name}`);
        }}
      />

      <AIAdvisorModal
        isOpen={aiAdvisorOpen}
        onClose={() => setAiAdvisorOpen(false)}
        initialQuery={aiInitialQuery}
      />

      {/* Global Toast Notification */}
      {toastMessage && (
        <div className="fixed top-20 right-6 z-50 bg-[#141518] text-white px-4 py-2.5 rounded-xl shadow-2xl text-xs font-bold border border-amber-400/40 animate-in fade-in slide-in-from-top-4 duration-200">
          ✨ {toastMessage}
        </div>
      )}
    </div>
  );
}

export default App;
