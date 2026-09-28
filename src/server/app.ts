import express from 'express';
import cors from 'cors';
import { processSaleCheckout } from './services/saleTransaction';
import { processPurchaseRestock } from './services/purchaseTransaction';
import { processKhataPayment } from './services/khataTransaction';
import { getShopFullBusinessContext } from './services/contextService';

export const app = express();

app.use(cors());
app.use(express.json());

// Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// POS Sale Checkout API
app.post('/api/v1/sales/checkout', async (req, res) => {
  try {
    const sale = await processSaleCheckout(req.body);
    res.status(201).json({ success: true, data: sale });
  } catch (error: any) {
    res.status(400).json({ success: false, error: error.message });
  }
});

// Purchase Restock API
app.post('/api/v1/purchases/restock', async (req, res) => {
  try {
    const purchase = await processPurchaseRestock(req.body);
    res.status(201).json({ success: true, data: purchase });
  } catch (error: any) {
    res.status(400).json({ success: false, error: error.message });
  }
});

// Khata Payment Settlement API
app.post('/api/v1/khata/payment', async (req, res) => {
  try {
    const result = await processKhataPayment(req.body);
    res.status(200).json({ success: true, data: result });
  } catch (error: any) {
    res.status(400).json({ success: false, error: error.message });
  }
});

// Expose Shop Business Context for AI / Hindsight Layer
app.get('/api/v1/shops/:shopId/context', async (req, res) => {
  try {
    const context = await getShopFullBusinessContext(req.params.shopId);
    res.status(200).json({ success: true, data: context });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

if (process.env.NODE_ENV !== 'test') {
  const PORT = process.env.PORT || 4000;
  app.listen(PORT, () => {
    console.log(`🚀 Kirana OS Database Backend running on port ${PORT}`);
  });
}
