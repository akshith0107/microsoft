import { prisma } from '../db';
import { Prisma } from '@prisma/client';

export interface SaleItemInput {
  productId: string;
  quantity: number;
  unitPrice: number;
  discount?: number;
  taxRate?: number;
}

export interface CheckoutSaleInput {
  shopId: string;
  userId: string;
  customerId?: string;
  invoiceNumber: string;
  paymentMethod: 'CASH' | 'UPI' | 'CARD' | 'CREDIT' | 'MIXED';
  items: SaleItemInput[];
  notes?: string;
}

export async function processSaleCheckout(input: CheckoutSaleInput) {
  const { shopId, userId, customerId, invoiceNumber, paymentMethod, items, notes } = input;

  return await prisma.$transaction(async (tx) => {
    // 1. Calculate Totals
    let subtotal = new Prisma.Decimal(0);
    let totalTax = new Prisma.Decimal(0);
    let totalDiscount = new Prisma.Decimal(0);

    const saleItemsData = [];

    for (const item of items) {
      const qty = new Prisma.Decimal(item.quantity);
      const price = new Prisma.Decimal(item.unitPrice);
      const disc = new Prisma.Decimal(item.discount || 0);
      const taxRate = new Prisma.Decimal(item.taxRate || 0);

      const itemSubtotal = qty.mul(price).sub(disc);
      const itemTax = itemSubtotal.mul(taxRate).div(100);
      const itemTotal = itemSubtotal.add(itemTax);

      subtotal = subtotal.add(itemSubtotal);
      totalTax = totalTax.add(itemTax);
      totalDiscount = totalDiscount.add(disc);

      saleItemsData.push({
        productId: item.productId,
        quantity: qty,
        unitPrice: price,
        discount: disc,
        taxRate: taxRate,
        total: itemTotal,
      });

      // 2. Check and Update Inventory
      const existingInventory = await tx.inventory.findUnique({
        where: { shopId_productId: { shopId, productId: item.productId } },
      });

      if (!existingInventory || existingInventory.quantity.sub(existingInventory.reservedQuantity).lt(qty)) {
        throw new Error(`Insufficient stock for product ID ${item.productId}. Available: ${existingInventory?.quantity || 0}`);
      }

      await tx.inventory.update({
        where: { shopId_productId: { shopId, productId: item.productId } },
        data: {
          quantity: { decrement: qty },
          lastSoldAt: new Date(),
        },
      });

      // 3. Record Inventory Movement
      await tx.inventoryMovement.create({
        data: {
          shopId,
          productId: item.productId,
          movementType: 'SALE',
          quantity: qty,
          unitCost: price,
          referenceType: 'SALE',
          notes: `POS Invoice #${invoiceNumber}`,
          createdBy: userId,
        },
      });
    }

    const grandTotal = subtotal.add(totalTax);

    // 4. Create Sale Record
    const sale = await tx.sale.create({
      data: {
        shopId,
        customerId,
        invoiceNumber,
        subtotal,
        taxAmount: totalTax,
        discountAmount: totalDiscount,
        totalAmount: grandTotal,
        paymentMethod,
        paymentStatus: paymentMethod === 'CREDIT' ? 'PENDING' : 'PAID',
        notes,
        createdBy: userId,
        items: {
          create: saleItemsData,
        },
      },
      include: {
        items: true,
      },
    });

    // 5. Handle Khata Credit if paymentMethod === 'CREDIT'
    if (paymentMethod === 'CREDIT') {
      if (!customerId) {
        throw new Error("Customer ID is required for Credit / Khata sale transactions");
      }

      let khataAccount = await tx.khataAccount.findUnique({
        where: { shopId_customerId: { shopId, customerId } },
      });

      if (!khataAccount) {
        khataAccount = await tx.khataAccount.create({
          data: { shopId, customerId, currentBalance: new Prisma.Decimal(0) },
        });
      }

      // Check Credit Limit
      if (khataAccount.creditLimit && khataAccount.currentBalance.add(grandTotal).gt(khataAccount.creditLimit)) {
        throw new Error(`Credit limit of ₹${khataAccount.creditLimit} exceeded for customer`);
      }

      // Record Khata Transaction
      await tx.khataTransaction.create({
        data: {
          shopId,
          khataAccountId: khataAccount.id,
          transactionType: 'CREDIT',
          amount: grandTotal,
          referenceType: 'SALE',
          referenceId: sale.id,
          description: `Udhaar Sale Invoice #${invoiceNumber}`,
          createdBy: userId,
        },
      });

      // Update Current Balance
      await tx.khataAccount.update({
        where: { id: khataAccount.id },
        data: {
          currentBalance: { increment: grandTotal },
        },
      });
    }

    // 6. Record Audit Log
    await tx.auditLog.create({
      data: {
        shopId,
        userId,
        action: 'CREATE_SALE',
        entityType: 'SALE',
        entityId: sale.id,
        newValues: { invoiceNumber, totalAmount: grandTotal.toNumber(), paymentMethod },
      },
    });

    return sale;
  });
}
