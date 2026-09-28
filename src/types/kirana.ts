export type NavView = 
  | 'overview' 
  | 'billing' 
  | 'products' 
  | 'inventory' 
  | 'customers' 
  | 'suppliers' 
  | 'khata' 
  | 'expenses' 
  | 'reports' 
  | 'insights' 
  | 'ai-advisor' 
  | 'settings';

export interface ProductItem {
  id: string;
  name: string;
  category: string;
  brand: string;
  price: number; // MRP / selling price in ₹
  costPrice: number;
  stock: number;
  minStockThreshold: number;
  unit: string;
  status: 'healthy' | 'low' | 'critical';
  salesCountToday: number;
  barcode: string;
}

export interface MetricData {
  title: string;
  value: string;
  numericValue: number;
  change: string;
  isPositive: boolean;
  subtitle: string;
  bgVariant: 'yellow' | 'lavender' | 'mint' | 'blue' | 'peach';
  sparkline: number[];
}

export interface SalesDataPoint {
  day: string;
  sales: number;
  orders: number;
  profit: number;
}

export interface KhataCustomer {
  id: string;
  name: string;
  phone: string;
  dueAmount: number;
  daysOverdue: number;
  lastPurchaseDate: string;
  status: 'current' | 'pending' | 'critical';
  notes?: string;
}

export interface ExpenseCategory {
  name: string;
  amount: number;
  percentage: number;
  color: string;
}

export interface ActionItem {
  id: string;
  type: 'LOW_STOCK' | 'PAYMENT_DUE' | 'SUPPLIER' | 'BUSINESS_INSIGHT';
  title: string;
  description: string;
  timestamp: string;
  actionText: string;
  actionType: 'review_stock' | 'view_khata' | 'view_supplier' | 'view_insight';
  urgent: boolean;
  metadata?: {
    productId?: string;
    customerId?: string;
    supplierId?: string;
    amount?: number;
  };
}

export interface TopProduct {
  rank: number;
  name: string;
  salesCount: number;
  revenue: number;
  growth: string;
  category: string;
}

export interface StoreInsight {
  title: string;
  summary: string;
  details: string;
  impact: string;
  recommendation: string;
  confidenceScore: number;
  hindsightContext: string;
}

export interface CartItem {
  product: ProductItem;
  quantity: number;
}
