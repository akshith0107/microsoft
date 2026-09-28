import React, { useState } from 'react';
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

export function App() {
  const [activeView, setActiveView] = useState<NavView>('overview');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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

  const handleOpenAIAdvisor = (query?: string) => {
    setAiInitialQuery(query);
    setAiAdvisorOpen(true);
  };

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
