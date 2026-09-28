import { api, setAuthToken, setSelectedShopId } from './client';

export interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  preferred_language: string;
}

export interface Shop {
  id: string;
  name: string;
  owner_id: string;
  phone?: string;
  city?: string;
  currency: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in_seconds: number;
  user_id: string;
  shop_id?: string;
}

export interface DashboardSummary {
  today_sales: number;
  today_orders: number;
  today_expenses: number;
  today_profit: number;
  inventory_value: number;
  low_stock_count: number;
  out_of_stock_count: number;
  pending_khata: number;
  open_complaints_count: number;
  pending_supplier_orders_count: number;
  active_recommendations_count: number;
}

export interface Product {
  id: string;
  shop_id: string;
  category_id?: string;
  sku: string;
  barcode?: string;
  name: string;
  brand?: string;
  unit: string;
  purchase_price: number;
  selling_price: number;
  tax_rate: number;
  reorder_level: number;
  target_stock: number;
  is_active: boolean;
  current_stock: number;
}

export interface InventoryItem {
  id: string;
  shop_id: string;
  product_id: string;
  product_name?: string;
  product_sku?: string;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  average_cost: number;
  last_purchase_price: number;
}

export interface KhataAccount {
  id: string;
  shop_id: string;
  customer_id: string;
  customer_name?: string;
  customer_phone?: string;
  credit_limit?: number;
  current_balance: number;
}

export interface SaleItemInput {
  product_id: string;
  quantity: number;
  unit_price: number;
  discount?: number;
  tax_rate?: number;
}

export interface SaleCreateInput {
  customer_id?: string;
  invoice_number?: string;
  payment_method: 'CASH' | 'UPI' | 'CARD' | 'CREDIT' | 'OTHER';
  payment_status: 'PAID' | 'PARTIAL' | 'PENDING' | 'CANCELLED';
  discount_amount?: number;
  notes?: string;
  items: SaleItemInput[];
}

export interface SaleRead {
  id: string;
  invoice_number: string;
  sale_date: string;
  total_amount: number;
  payment_method: string;
  payment_status: string;
}

export interface AssistantResponse {
  response: string;
  conversation_id: string;
  message_id: string;
  intent?: string;
  recommendation_id?: string;
}

export const authAPI = {
  login: async (email: string, password: string) => {
    const res = await api.post<TokenResponse>('/auth/login', { email, password });
    setAuthToken(res.access_token);
    if (res.shop_id) {
      setSelectedShopId(res.shop_id);
    }
    return res;
  },

  signup: async (data: { name: string; email: string; phone?: string; password: string; shop_name: string }) => {
    const res = await api.post<TokenResponse>('/auth/signup', {
      name: data.name,
      email: data.email,
      phone: data.phone,
      password: data.password,
      shop_name: data.shop_name,
      preferred_language: 'en'
    });
    setAuthToken(res.access_token);
    if (res.shop_id) {
      setSelectedShopId(res.shop_id);
    }
    return res;
  },

  getMe: () => api.get<User>('/auth/me'),
  getShops: () => api.get<Shop[]>('/auth/shops'),
};

export const dashboardAPI = {
  getSummary: () => api.get<DashboardSummary>('/dashboard'),
};

export const productsAPI = {
  getProducts: () => api.get<Product[]>('/products'),
  createProduct: (data: Partial<Product> & { initial_stock?: number }) => api.post<Product>('/products', data),
  deleteProduct: (id: string) => api.delete<boolean>(`/products/${id}`),
};

export const inventoryAPI = {
  getInventory: () => api.get<InventoryItem[]>('/inventory'),
  adjustStock: (productId: string, data: { movement_type: string; quantity: number; notes?: string }) =>
    api.post<InventoryItem>(`/inventory/${productId}/adjust`, data),
};

export const salesAPI = {
  createSale: (saleInput: SaleCreateInput) => api.post<SaleRead>('/sales', saleInput),
  getSales: () => api.get<SaleRead[]>('/sales'),
};

export const khataAPI = {
  getAccounts: () => api.get<KhataAccount[]>('/khata'),
  recordPayment: (customerId: string, amount: number, description: string = 'Payment received') =>
    api.post<any>(`/khata/${customerId}/payment`, { amount, description }),
};

export const assistantAPI = {
  chat: (message: string, conversationId?: string) =>
    api.post<AssistantResponse>('/assistant/chat', { message, conversation_id: conversationId }),
};

export interface VoiceCommandResponse {
  transcript: string;
  intent: string;
  response_text: string;
  action_executed: boolean;
  data?: any;
}

export const voiceAPI = {
  processCommand: (data: { transcript: string; audio_url?: string; language?: string }) =>
    api.post<VoiceCommandResponse>('/voice/command', data),
  getInteractions: (limit: number = 20) =>
    api.get<any[]>(`/voice/interactions?limit=${limit}`),
};

export interface ReceiptScanItemRead {
  id: string;
  receipt_scan_id: string;
  product_id?: string;
  extracted_name: string;
  quantity: number;
  unit_price: number;
  total: number;
  confidence?: number;
}

export interface ReceiptScanRead {
  id: string;
  shop_id: string;
  uploaded_by: string;
  image_url: string;
  vendor_name?: string;
  invoice_number?: string;
  subtotal?: number;
  tax_amount?: number;
  total_amount?: number;
  processing_status: string;
  created_at: string;
  items: ReceiptScanItemRead[];
}

export const receiptsAPI = {
  process: (imageUrl?: string) =>
    api.post<ReceiptScanRead>(`/receipts/process?image_url=${encodeURIComponent(imageUrl || 'https://example.com/receipt.png')}`),
  confirm: (id: string, data: { supplier_id?: string; invoice_number?: string; items: any[] }) =>
    api.post<ReceiptScanRead>(`/receipts/${id}/confirm`, data),
  getReceipts: (limit: number = 20) =>
    api.get<ReceiptScanRead[]>(`/receipts?limit=${limit}`),
};

export interface ForecastFactor {
  factor: string;
  impact: string;
  explanation: string;
}

export interface ForecastResultRead {
  product_id: string;
  product_name: string;
  forecast_7d: number;
  daily_average: number;
  stock_coverage_days: number;
  stockout_risk: number;
  recommended_order_quantity: number;
  confidence: number;
  factors: ForecastFactor[];
}

export interface RecommendationOutcomeRead {
  id: string;
  recommendation_id: string;
  shop_id: string;
  decision: 'ACCEPTED' | 'REJECTED' | 'MODIFIED';
  decision_notes?: string;
  outcome?: string;
  outcome_notes?: string;
  measured_at?: string;
  created_at: string;
}

export interface RecommendationRead {
  id: string;
  shop_id: string;
  type: string;
  title: string;
  recommendation: string;
  reasoning: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  related_product_id?: string;
  related_supplier_id?: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'EXPIRED';
  generated_at: string;
  created_at: string;
  outcomes?: RecommendationOutcomeRead[];
}

export interface ComplaintRead {
  id: string;
  shop_id: string;
  customer_id?: string;
  customer_name?: string;
  sale_id?: string;
  subject: string;
  description: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  resolution?: string;
  resolved_at?: string;
  created_at: string;
}

export interface OrderItemRead {
  id: string;
  order_id: string;
  product_id: string;
  product_name?: string;
  quantity: number;
  unit_price?: number;
  total?: number;
}

export interface OrderRead {
  id: string;
  shop_id: string;
  supplier_id?: string;
  supplier_name?: string;
  order_type: string;
  status: 'PENDING' | 'ORDERED' | 'DELIVERED' | 'CANCELLED';
  ordered_at: string;
  expected_delivery_date?: string;
  total_amount?: number;
  notes?: string;
  items: OrderItemRead[];
}

export interface SupplierRead {
  id: string;
  shop_id: string;
  name: string;
  phone?: string;
  email?: string;
  address?: string;
  notes?: string;
  payment_terms?: string;
  average_lead_time_days?: number;
  reliability_score?: number;
  is_active: boolean;
}

export interface ExpenseRead {
  id: string;
  shop_id: string;
  category_id?: string;
  category_name?: string;
  amount: number;
  description: string;
  expense_date: string;
  payment_method: string;
}

export const analyticsAPI = {
  getForecast: (productId: string) => api.get<ForecastResultRead>(`/analytics/forecast/${productId}`),
};

export const recommendationsAPI = {
  getRecommendations: () => api.get<RecommendationRead[]>('/recommendations'),
  recordDecision: (id: string, data: { decision: 'ACCEPTED' | 'REJECTED'; decision_notes?: string; outcome?: string; outcome_notes?: string }) =>
    api.post<RecommendationOutcomeRead>(`/recommendations/${id}/decision`, data),
};

export const complaintsAPI = {
  getComplaints: () => api.get<ComplaintRead[]>('/complaints'),
  createComplaint: (data: { customer_id?: string; sale_id?: string; subject: string; description: string; priority?: string }) =>
    api.post<ComplaintRead>('/complaints', data),
  resolveComplaint: (id: string, data: { resolution: string }) =>
    api.post<ComplaintRead>(`/complaints/${id}/resolve`, data),
};

export const ordersAPI = {
  getOrders: () => api.get<OrderRead[]>('/orders'),
  createOrder: (data: { supplier_id?: string; order_type?: string; expected_delivery_date?: string; notes?: string; items: { product_id: string; quantity: number; unit_price?: number }[] }) =>
    api.post<OrderRead>('/orders', data),
};

export const suppliersAPI = {
  getSuppliers: () => api.get<SupplierRead[]>('/suppliers'),
  createSupplier: (data: { name: string; phone?: string; email?: string; address?: string; notes?: string; payment_terms?: string; average_lead_time_days?: number }) =>
    api.post<SupplierRead>('/suppliers', data),
};

export const expensesAPI = {
  getExpenses: () => api.get<ExpenseRead[]>('/expenses'),
  createExpense: (data: { category_id?: string; amount: number; description: string; expense_date?: string; payment_method?: string }) =>
    api.post<ExpenseRead>('/expenses', data),
};

export const weatherAPI = {
  getWeather: (location?: string) => api.get<any>(`/weather${location ? `?location=${encodeURIComponent(location)}` : ''}`),
};

export const marketAPI = {
  getMarketPrices: (commodity: string = 'Wheat', state: string = 'Delhi') =>
    api.get<any[]>(`/market/prices?commodity=${encodeURIComponent(commodity)}&state=${encodeURIComponent(state)}`),
};
