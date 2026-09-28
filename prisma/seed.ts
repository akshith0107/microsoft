import { 
  PrismaClient, 
  Role, 
  Unit, 
  MovementType, 
  PaymentStatus, 
  PaymentMethod, 
  KhataTransactionType, 
  ComplaintStatus, 
  ComplaintPriority, 
  OrderType, 
  OrderStatus, 
  RecommendationType, 
  RecommendationStatus, 
  DecisionType, 
  OutcomeType, 
  MessageRole, 
  MessageType, 
  OCRProcessingStatus,
  OTPPurpose
} from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Starting Kirana OS Complete Database Seed...');

  // ==========================================
  // 1. CLEANUP (DEV RESET)
  // ==========================================
  await prisma.auditLog.deleteMany();
  await prisma.receiptScanItem.deleteMany();
  await prisma.receiptScan.deleteMany();
  await prisma.voiceInteraction.deleteMany();
  await prisma.conversationMessage.deleteMany();
  await prisma.conversation.deleteMany();
  await prisma.recommendationOutcome.deleteMany();
  await prisma.recommendation.deleteMany();
  await prisma.weatherObservation.deleteMany();
  await prisma.productMarketMapping.deleteMany();
  await prisma.marketPriceObservation.deleteMany();
  await prisma.orderItem.deleteMany();
  await prisma.order.deleteMany();
  await prisma.complaint.deleteMany();
  await prisma.expense.deleteMany();
  await prisma.expenseCategory.deleteMany();
  await prisma.khataTransaction.deleteMany();
  await prisma.khataAccount.deleteMany();
  await prisma.customer.deleteMany();
  await prisma.saleItem.deleteMany();
  await prisma.sale.deleteMany();
  await prisma.purchaseItem.deleteMany();
  await prisma.purchase.deleteMany();
  await prisma.supplier.deleteMany();
  await prisma.inventoryMovement.deleteMany();
  await prisma.inventory.deleteMany();
  await prisma.product.deleteMany();
  await prisma.category.deleteMany();
  await prisma.shopMember.deleteMany();
  await prisma.shop.deleteMany();

  // Auth cleanup
  await prisma.oTPVerification.deleteMany();
  await prisma.emailVerificationToken.deleteMany();
  await prisma.passwordResetToken.deleteMany();
  await prisma.userSession.deleteMany();
  await prisma.user.deleteMany();

  // ==========================================
  // 2. USERS & AUTHENTICATION
  // ==========================================
  // Dev Password: ChangeMe123! (bcrypt hash)
  const devPasswordHash = '$2b$10$e8w8G8T3p.z5J4QxWqZ6eO/Y9uX4pQz5aZ6eO/Y9uX4pQz5aZ6eO';

  const ownerRajesh = await prisma.user.create({
    data: {
      name: 'Rajesh Kumar',
      email: 'owner@sharmastore.test',
      phone: '+919845011111',
      passwordHash: devPasswordHash,
      preferredLanguage: 'hinglish',
      isActive: true,
      emailVerified: true,
      phoneVerified: true,
      lastLoginAt: new Date(),
    },
  });

  const staffAmit = await prisma.user.create({
    data: {
      name: 'Amit Kumar',
      email: 'staff@sharmastore.test',
      phone: '+919845022222',
      passwordHash: devPasswordHash,
      preferredLanguage: 'hi',
      isActive: true,
      emailVerified: true,
      phoneVerified: true,
      lastLoginAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    },
  });

  // Second shop owner for Multi-Tenant Isolation Testing
  const ownerSureshGupta = await prisma.user.create({
    data: {
      name: 'Suresh Gupta',
      email: 'owner@guptastore.test',
      phone: '+919845033333',
      passwordHash: devPasswordHash,
      preferredLanguage: 'en',
      isActive: true,
      emailVerified: true,
      phoneVerified: true,
    },
  });

  // Active Sessions
  await prisma.userSession.create({
    data: {
      userId: ownerRajesh.id,
      sessionTokenHash: 'sess_hash_rajesh_owner_123',
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
      ipAddress: '127.0.0.1',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    },
  });

  // OTP Verification Record
  await prisma.oTPVerification.create({
    data: {
      userId: ownerRajesh.id,
      phone: '+919845011111',
      otpHash: 'otp_hash_sample_9921',
      purpose: OTPPurpose.LOGIN,
      expiresAt: new Date(Date.now() + 5 * 60 * 1000),
      verifiedAt: new Date(),
      attempts: 1,
    },
  });

  // ==========================================
  // 3. SHOPS & TENANCY
  // ==========================================
  const shopSharma = await prisma.shop.create({
    data: {
      name: 'Sharma General Store',
      ownerId: ownerRajesh.id,
      phone: '+919845011111',
      email: 'owner@sharmastore.test',
      addressLine1: '12th Main Road, 4th Block',
      addressLine2: 'Near Indiranagar Metro Station',
      city: 'Bengaluru',
      state: 'Karnataka',
      pincode: '560038',
      country: 'IN',
      currency: 'INR',
      timezone: 'Asia/Kolkata',
    },
  });

  const shopGupta = await prisma.shop.create({
    data: {
      name: 'Gupta Kirana Store',
      ownerId: ownerSureshGupta.id,
      phone: '+919845033333',
      email: 'owner@guptastore.test',
      addressLine1: 'Sector 15, HSR Layout',
      city: 'Bengaluru',
      state: 'Karnataka',
      pincode: '560102',
    },
  });

  await prisma.shopMember.createMany({
    data: [
      { shopId: shopSharma.id, userId: ownerRajesh.id, role: Role.OWNER },
      { shopId: shopSharma.id, userId: staffAmit.id, role: Role.STAFF },
      { shopId: shopGupta.id, userId: ownerSureshGupta.id, role: Role.OWNER },
    ],
  });

  // ==========================================
  // 4. CATEGORIES & PRODUCTS
  // ==========================================
  const catPackaged = await prisma.category.create({
    data: { shopId: shopSharma.id, name: 'Packaged Foods', description: 'Noodles, snacks & instant food' },
  });
  const catBiscuits = await prisma.category.create({
    data: { shopId: shopSharma.id, name: 'Biscuits & Snacks', description: 'Tea biscuits & bakery snacks' },
  });
  const catDairy = await prisma.category.create({
    data: { shopId: shopSharma.id, name: 'Dairy & Bakery', description: 'Fresh milk, curd & daily bread' },
  });
  const catStaples = await prisma.category.create({
    data: { shopId: shopSharma.id, name: 'Staples & Atta', description: 'Grains, flour, salt & spices' },
  });
  const catBeverages = await prisma.category.create({
    data: { shopId: shopSharma.id, name: 'Beverages', description: 'Soft drinks, juices & tea' },
  });
  const catHousehold = await prisma.category.create({
    data: { shopId: shopSharma.id, name: 'Household & Personal', description: 'Soaps, detergents & toothpaste' },
  });

  const productsData = [
    { sku: 'MAG-70G', barcode: '8901058852310', name: 'Maggi 2-Minute Masala Noodles 70g', brand: 'Nestlé', categoryId: catPackaged.id, unit: Unit.packet, purchasePrice: 11.20, sellingPrice: 14.00, taxRate: 5.00, reorderLevel: 30, targetStock: 100, initialQty: 35 },
    { sku: 'PAR-100G', barcode: '8901063001017', name: 'Parle-G Gold Biscuits 100g', brand: 'Parle', categoryId: catBiscuits.id, unit: Unit.packet, purchasePrice: 8.10, sellingPrice: 10.00, taxRate: 0.00, reorderLevel: 25, targetStock: 120, initialQty: 80 },
    { sku: 'AMU-500ML', barcode: '8901262010050', name: 'Amul Taaza Toned Milk 500ml', brand: 'Amul', categoryId: catDairy.id, unit: Unit.packet, purchasePrice: 24.50, sellingPrice: 27.00, taxRate: 0.00, reorderLevel: 20, targetStock: 60, initialQty: 25 },
    { sku: 'TAT-1KG', barcode: '8901058000018', name: 'Tata Vacuum Evaporated Salt 1kg', brand: 'Tata', categoryId: catStaples.id, unit: Unit.packet, purchasePrice: 23.00, sellingPrice: 28.00, taxRate: 0.00, reorderLevel: 20, targetStock: 50, initialQty: 12 },
    { sku: 'AAS-5KG', barcode: '8901725111124', name: 'Aashirvaad Shuddh Chakki Atta 5kg', brand: 'ITC', categoryId: catStaples.id, unit: Unit.box, purchasePrice: 205.00, sellingPrice: 240.00, taxRate: 5.00, reorderLevel: 10, targetStock: 40, initialQty: 31 },
    { sku: 'BRI-120G', barcode: '8901063140020', name: 'Britannia Good Day Butter Biscuits 120g', brand: 'Britannia', categoryId: catBiscuits.id, unit: Unit.packet, purchasePrice: 24.00, sellingPrice: 30.00, taxRate: 0.00, reorderLevel: 15, targetStock: 50, initialQty: 18 },
    { sku: 'COC-750ML', barcode: '8901764012019', name: 'Coca-Cola Soft Drink 750ml', brand: 'Coca-Cola', categoryId: catBeverages.id, unit: Unit.bottle, purchasePrice: 32.00, sellingPrice: 40.00, taxRate: 12.00, reorderLevel: 15, targetStock: 50, initialQty: 40 },
    { sku: 'THU-750ML', barcode: '8901764012026', name: 'Thums Up Soft Drink 750ml', brand: 'Coca-Cola', categoryId: catBeverages.id, unit: Unit.bottle, purchasePrice: 32.00, sellingPrice: 40.00, taxRate: 12.00, reorderLevel: 15, targetStock: 50, initialQty: 22 },
    { sku: 'SUR-1KG', barcode: '8901030001234', name: 'Surf Excel Easy Wash Detergent 1kg', brand: 'HUL', categoryId: catHousehold.id, unit: Unit.packet, purchasePrice: 120.00, sellingPrice: 145.00, taxRate: 18.00, reorderLevel: 8, targetStock: 25, initialQty: 14 },
    { sku: 'FOR-1L', barcode: '8906007280145', name: 'Fortune Sunlite Refined Sunflower Oil 1L', brand: 'Fortune', categoryId: catStaples.id, unit: Unit.packet, purchasePrice: 128.00, sellingPrice: 145.00, taxRate: 5.00, reorderLevel: 15, targetStock: 40, initialQty: 9 },
    { sku: 'COL-100G', barcode: '8901123000456', name: 'Colgate Strong Teeth Toothpaste 100g', brand: 'Colgate', categoryId: catHousehold.id, unit: Unit.packet, purchasePrice: 50.00, sellingPrice: 62.00, taxRate: 18.00, reorderLevel: 10, targetStock: 30, initialQty: 20 },
    { sku: 'DET-250ML', barcode: '8901396000789', name: 'Dettol Original Liquid Handwash 250ml', brand: 'Reckitt', categoryId: catHousehold.id, unit: Unit.bottle, purchasePrice: 78.00, sellingPrice: 99.00, taxRate: 18.00, reorderLevel: 5, targetStock: 20, initialQty: 4 },
  ];

  const createdProductsMap: Record<string, any> = {};

  for (const p of productsData) {
    const product = await prisma.product.create({
      data: {
        shopId: shopSharma.id,
        categoryId: p.categoryId,
        sku: p.sku,
        barcode: p.barcode,
        name: p.name,
        brand: p.brand,
        unit: p.unit as Unit,
        purchasePrice: p.purchasePrice,
        sellingPrice: p.sellingPrice,
        taxRate: p.taxRate,
        reorderLevel: p.reorderLevel,
        targetStock: p.targetStock,
      },
    });

    createdProductsMap[p.sku] = product;

    await prisma.inventory.create({
      data: {
        shopId: shopSharma.id,
        productId: product.id,
        quantity: p.initialQty,
        reservedQuantity: 0,
        averageCost: p.purchasePrice,
        lastPurchasePrice: p.purchasePrice,
        lastRestockedAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
      },
    });

    await prisma.inventoryMovement.create({
      data: {
        shopId: shopSharma.id,
        productId: product.id,
        movementType: MovementType.PURCHASE,
        quantity: p.initialQty + 50,
        unitCost: p.purchasePrice,
        referenceType: 'INITIAL_SEED',
        notes: 'Initial opening stock allocation',
        createdBy: ownerRajesh.id,
      },
    });
  }

  // ==========================================
  // 5. SUPPLIERS & PURCHASES
  // ==========================================
  const supplierSharmaTraders = await prisma.supplier.create({
    data: {
      shopId: shopSharma.id,
      name: 'Sharma FMCG Traders',
      phone: '+919876543210',
      email: 'orders@sharmatraders.in',
      address: 'APMC Market Yard, Bengaluru',
      paymentTerms: 'NET 15',
      averageLeadTimeDays: 2,
      reliabilityScore: 95.50,
    },
  });

  const supplierMetroBeverages = await prisma.supplier.create({
    data: {
      shopId: shopSharma.id,
      name: 'Metro Beverage Distributors',
      phone: '+919876543211',
      email: 'sales@metrobeverages.com',
      address: 'Kalyan Nagar, Bengaluru',
      paymentTerms: 'NET 7',
      averageLeadTimeDays: 1,
      reliabilityScore: 98.00,
    },
  });

  const supplierAnnapurnaStaples = await prisma.supplier.create({
    data: {
      shopId: shopSharma.id,
      name: 'Annapurna Staples Wholesaler',
      phone: '+919876543212',
      email: 'annapurnastaples@gmail.com',
      address: 'Yeshwanthpur APMC Market, Bengaluru',
      paymentTerms: 'COD',
      averageLeadTimeDays: 3,
      reliabilityScore: 88.00,
    },
  });

  await prisma.purchase.create({
    data: {
      shopId: shopSharma.id,
      supplierId: supplierSharmaTraders.id,
      invoiceNumber: 'INV-ST-2026-889',
      purchaseDate: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000),
      subtotal: 12500.00,
      taxAmount: 625.00,
      discountAmount: 200.00,
      totalAmount: 12925.00,
      paymentStatus: PaymentStatus.PAID,
      createdBy: ownerRajesh.id,
      items: {
        create: [
          { productId: createdProductsMap['MAG-70G'].id, quantity: 100, unitCost: 11.20, taxRate: 5.00, total: 1176.00 },
          { productId: createdProductsMap['PAR-100G'].id, quantity: 200, unitCost: 8.10, taxRate: 0.00, total: 1620.00 },
        ],
      },
    },
  });

  // ==========================================
  // 6. CUSTOMERS & KHATA LEDGER
  // ==========================================
  const customersData = [
    { name: 'Ramesh Kumar', phone: '+919845012345', due: 350.00, days: 12 },
    { name: 'Suresh Patel', phone: '+919731298765', due: 1280.00, days: 5 },
    { name: 'Anil Sharma', phone: '+919900155432', due: 890.00, days: 2 },
    { name: 'Meena Devi', phone: '+919448122334', due: 4120.00, days: 18 },
    { name: 'Priya Nair', phone: '+918884566778', due: 0.00, days: 0 },
  ];

  for (const c of customersData) {
    const customer = await prisma.customer.create({
      data: {
        shopId: shopSharma.id,
        name: c.name,
        phone: c.phone,
        creditLimit: 5000.00,
      },
    });

    const khataAccount = await prisma.khataAccount.create({
      data: {
        shopId: shopSharma.id,
        customerId: customer.id,
        creditLimit: 5000.00,
        currentBalance: c.due,
      },
    });

    if (c.due > 0) {
      await prisma.khataTransaction.create({
        data: {
          shopId: shopSharma.id,
          khataAccountId: khataAccount.id,
          transactionType: KhataTransactionType.CREDIT,
          amount: c.due + 300,
          description: 'Grocery credit purchase',
          transactionDate: new Date(Date.now() - c.days * 24 * 60 * 60 * 1000),
          createdBy: ownerRajesh.id,
        },
      });

      await prisma.khataTransaction.create({
        data: {
          shopId: shopSharma.id,
          khataAccountId: khataAccount.id,
          transactionType: KhataTransactionType.PAYMENT,
          amount: 300.00,
          description: 'UPI partial payment received',
          transactionDate: new Date(Date.now() - (c.days - 1) * 24 * 60 * 60 * 1000),
          createdBy: ownerRajesh.id,
        },
      });
    }
  }

  // ==========================================
  // 7. 30-DAY HISTORICAL SALES
  // ==========================================
  const rameshCustomer = await prisma.customer.findFirst({ where: { phone: '+919845012345' } });

  for (let dayOffset = 30; dayOffset >= 0; dayOffset--) {
    const saleDate = new Date(Date.now() - dayOffset * 24 * 60 * 60 * 1000);
    const isWeekend = saleDate.getDay() === 0 || saleDate.getDay() === 6;

    const maggiQty = isWeekend ? 8 : 3;
    const milkQty = 4;

    const maggiPrice = createdProductsMap['MAG-70G'].sellingPrice;
    const milkPrice = createdProductsMap['AMU-500ML'].sellingPrice;
    const subtotal = (maggiQty * maggiPrice) + (milkQty * milkPrice);
    const total = subtotal * 1.05;

    const sale = await prisma.sale.create({
      data: {
        shopId: shopSharma.id,
        customerId: dayOffset % 5 === 0 ? rameshCustomer?.id : null,
        invoiceNumber: `INV-2026-${1000 + dayOffset}`,
        saleDate,
        subtotal: subtotal,
        taxAmount: total - subtotal,
        discountAmount: 0.00,
        totalAmount: total,
        paymentMethod: dayOffset % 3 === 0 ? PaymentMethod.UPI : PaymentMethod.CASH,
        paymentStatus: PaymentStatus.PAID,
        createdBy: ownerRajesh.id,
        items: {
          create: [
            { productId: createdProductsMap['MAG-70G'].id, quantity: maggiQty, unitPrice: maggiPrice, total: maggiQty * maggiPrice },
            { productId: createdProductsMap['AMU-500ML'].id, quantity: milkQty, unitPrice: milkPrice, total: milkQty * milkPrice },
          ],
        },
      },
    });

    await prisma.inventoryMovement.create({
      data: {
        shopId: shopSharma.id,
        productId: createdProductsMap['MAG-70G'].id,
        movementType: MovementType.SALE,
        quantity: maggiQty,
        unitCost: createdProductsMap['MAG-70G'].purchasePrice,
        referenceType: 'SALE',
        referenceId: sale.id,
        createdBy: ownerRajesh.id,
        createdAt: saleDate,
      },
    });
  }

  // ==========================================
  // 8. EXPENSES & COMPLAINTS
  // ==========================================
  const expCatRent = await prisma.expenseCategory.create({ data: { shopId: shopSharma.id, name: 'Shop Rent' } });
  const expCatElec = await prisma.expenseCategory.create({ data: { shopId: shopSharma.id, name: 'Electricity' } });

  await prisma.expense.createMany({
    data: [
      { shopId: shopSharma.id, categoryId: expCatRent.id, amount: 8000.00, description: 'Monthly lease rent', paymentMethod: PaymentMethod.UPI, createdBy: ownerRajesh.id, expenseDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000) },
      { shopId: shopSharma.id, categoryId: expCatElec.id, amount: 4200.00, description: 'Electricity bill for cooling', paymentMethod: PaymentMethod.UPI, createdBy: ownerRajesh.id, expenseDate: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000) },
    ],
  });

  await prisma.complaint.create({
    data: {
      shopId: shopSharma.id,
      customerId: rameshCustomer?.id,
      subject: 'Leaking milk pouch delivered',
      description: 'One packet of Amul Taaza 500ml was torn at corner.',
      status: ComplaintStatus.RESOLVED,
      priority: ComplaintPriority.MEDIUM,
      resolution: 'Replaced pouch on next visit',
      resolvedAt: new Date(),
      createdBy: ownerRajesh.id,
    },
  });

  // ==========================================
  // 9. AI RECOMMENDATIONS & LEARNING LOOP
  // ==========================================
  const rec1 = await prisma.recommendation.create({
    data: {
      shopId: shopSharma.id,
      type: RecommendationType.STOCK,
      title: 'Maggi stock may run low before weekend',
      recommendation: 'Order 3 extra cartons of Maggi 2-Min Noodles from Sharma FMCG Traders before Thursday.',
      reasoning: 'Weekend sales velocity is 23% higher than weekday baselines.',
      priority: ComplaintPriority.HIGH,
      relatedProductId: createdProductsMap['MAG-70G'].id,
      relatedSupplierId: supplierSharmaTraders.id,
      status: RecommendationStatus.ACCEPTED,
    },
  });

  await prisma.recommendationOutcome.create({
    data: {
      recommendationId: rec1.id,
      shopId: shopSharma.id,
      decision: DecisionType.MODIFIED,
      decisionNotes: 'Owner ordered 2 cases instead of 3.',
      outcome: OutcomeType.SUCCESS,
      outcomeNotes: 'Stock covered weekend demand without stockout.',
    },
  });

  // ==========================================
  // 10. CONVERSATIONS & VOICE LOGS
  // ==========================================
  const conv = await prisma.conversation.create({
    data: {
      shopId: shopSharma.id,
      userId: ownerRajesh.id,
      title: 'Daily Business Overview Query',
    },
  });

  await prisma.conversationMessage.createMany({
    data: [
      { conversationId: conv.id, role: MessageRole.USER, content: 'Aaj ka sales total kitna hai?', messageType: MessageType.TEXT },
      { conversationId: conv.id, role: MessageRole.ASSISTANT, content: 'Aaj ka total sales ₹18,450.00 across 126 bills.', messageType: MessageType.TEXT },
    ],
  });

  await prisma.voiceInteraction.create({
    data: {
      shopId: shopSharma.id,
      userId: ownerRajesh.id,
      transcript: 'Aaj ka profit kitna hai?',
      language: 'hi',
      intent: 'DAILY_PROFIT',
      confidence: 0.985,
      actionExecuted: true,
    },
  });

  await prisma.receiptScan.create({
    data: {
      shopId: shopSharma.id,
      uploadedBy: ownerRajesh.id,
      imageUrl: 'https://storage.neon.tech/receipts/placeholder-inv-992.jpg',
      vendorName: 'Sharma FMCG Traders',
      invoiceNumber: 'INV-99283',
      subtotal: 3500.00,
      taxAmount: 175.00,
      totalAmount: 3675.00,
      processingStatus: OCRProcessingStatus.COMPLETED,
    },
  });

  await prisma.marketPriceObservation.create({
    data: {
      commodityName: 'Wheat (Atta)',
      marketName: 'Yeshwanthpur APMC',
      state: 'Karnataka',
      arrivalDate: new Date(),
      minPrice: 2400.00,
      maxPrice: 2800.00,
      modalPrice: 2600.00,
      unit: 'Quintal',
      source: 'AGMARKNET',
    },
  });

  await prisma.weatherObservation.create({
    data: {
      locationName: 'Bengaluru',
      latitude: 12.9716,
      longitude: 77.5946,
      observedAt: new Date(),
      temperatureC: 28.5,
      humidity: 65,
      weatherCondition: 'Partly Cloudy',
    },
  });

  await prisma.auditLog.create({
    data: {
      shopId: shopSharma.id,
      userId: ownerRajesh.id,
      action: 'SYSTEM_SEED',
      entityType: 'SHOP',
      entityId: shopSharma.id,
      newValues: { seedStatus: 'COMPLETED', timestamp: new Date().toISOString() },
    },
  });

  console.log('✅ Complete Database Seed Finished Successfully!');
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error('❌ Seed Error:', e);
    await prisma.$disconnect();
    process.exit(1);
  });
