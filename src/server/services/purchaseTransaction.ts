import { prisma } from '../db';
import { Prisma } from '@prisma/client';

export interface PurchaseItemInput {
  productId: string;
  quantity: number;
  unitCost: number;
  taxRate?: number;
  discount?: number;
}

export interface RestockPurchaseInput {
  shopId: string;
  userId: string;
  supplierId?: string;
  invoiceNumber?: string;
  items: PurchaseItemInput[];
  notes?: string;
}

export async function processPurchaseRestock(input: RestockPurchaseInput) {
  const { shopId, userId, supplierId, invoiceNumber, items, notes } = input;

  return await prisma.$transaction(async (tx) => {
    let subtotal = new Prisma.Decimal(0);
    let totalTax = new Prisma.Decimal(0);
    let totalDiscount = new Prisma.Decimal(0);

    const purchaseItemsData = [];

    for (const item of items) {
      const qty = new Prisma.Decimal(item.quantity);
      const cost = new Prisma.Decimal(item.unitCost);
      const disc = new Prisma.Decimal(item.discount || 0);
      const taxRate = new Prisma.Decimal(item.taxRate || 0);

      const itemSubtotal = qty.mul(cost).sub(disc);
      const itemTax = itemSubtotal.mul(taxRate).div(100);
      const itemTotal = itemSubtotal.add(itemTax);

      subtotal = subtotal.add(itemSubtotal);
      totalTax = totalTax.add(itemTax);
      totalDiscount = totalDiscount.add(disc);

      purchaseItemsData.push({
        productId: item.productId,
        quantity: qty,
        unitCost: cost,
        taxRate: taxRate,
        discount: disc,
        total: itemTotal,
      });

      // 1. Get current inventory for weighted average cost calculation
      const existingInventory = await tx.inventory.findUnique({
        where: { shopId_productId: { shopId, productId: item.productId } },
      });

      const currentQty = existingInventory?.quantity || new Prisma.Decimal(0);
      const currentAvgCost = existingInventory?.averageCost || new Prisma.Decimal(0);

      // Weighted Average Cost formula: ((CurrentQty * CurrentAvgCost) + (NewQty * NewCost)) / (CurrentQty + NewQty)
      const totalNewValue = currentQty.mul(currentAvgCost).add(qty.mul(cost));
      const totalNewQty = currentQty.add(qty);
      const newAverageCost = totalNewQty.gt(0) ? totalNewValue.div(totalNewQty) : cost;

      // 2. Upsert Inventory
      await tx.inventory.upsert({
        where: { shopId_productId: { shopId, productId: item.productId } },
        create: {
          shopId,
          productId: item.productId,
          quantity: qty,
          averageCost: cost,
          lastPurchasePrice: cost,
          lastRestockedAt: new Date(),
        },
        update: {
          quantity: { increment: qty },
          averageCost: newAverageCost,
          lastPurchasePrice: cost,
          lastRestockedAt: new Date(),
        },
      });

      // 3. Record Inventory Movement
      await tx.inventoryMovement.create({
        data: {
          shopId,
          productId: item.productId,
          movementType: 'PURCHASE',
          quantity: qty,
          unitCost: cost,
          referenceType: 'PURCHASE',
          notes: `Restock Invoice #${invoiceNumber || 'N/A'}`,
          createdBy: userId,
        },
      });
    }

    const grandTotal = subtotal.add(totalTax);

    // 4. Create Purchase Record
    const purchase = await tx.purchase.create({
      data: {
        shopId,
        supplierId,
        invoiceNumber,
        subtotal,
        taxAmount: totalTax,
        discountAmount: totalDiscount,
        totalAmount: grandTotal,
        paymentStatus: 'PAID',
        notes,
        createdBy: userId,
        items: {
          create: purchaseItemsData,
        },
      },
      include: {
        items: true,
      },
    });

    // 5. Record Audit Log
    await tx.auditLog.create({
      data: {
        shopId,
        userId,
        action: 'CREATE_PURCHASE',
        entityType: 'PURCHASE',
        entityId: purchase.id,
        newValues: { invoiceNumber, totalAmount: grandTotal.toNumber() },
      },
    });

    return purchase;
  });
}
