import { prisma } from '../db';
import { Prisma } from '@prisma/client';

export interface KhataPaymentInput {
  shopId: string;
  userId: string;
  customerId: string;
  amount: number;
  transactionType: 'PAYMENT' | 'ADJUSTMENT';
  description: string;
  referenceId?: string;
}

export async function processKhataPayment(input: KhataPaymentInput) {
  const { shopId, userId, customerId, amount, transactionType, description, referenceId } = input;
  const payAmount = new Prisma.Decimal(amount);

  if (payAmount.lte(0)) {
    throw new Error("Transaction amount must be greater than zero");
  }

  return await prisma.$transaction(async (tx) => {
    // 1. Get Khata Account
    let khataAccount = await tx.khataAccount.findUnique({
      where: { shopId_customerId: { shopId, customerId } },
    });

    if (!khataAccount) {
      throw new Error(`Khata account not found for customer ${customerId}`);
    }

    // 2. Record Khata Transaction
    const transaction = await tx.khataTransaction.create({
      data: {
        shopId,
        khataAccountId: khataAccount.id,
        transactionType,
        amount: payAmount,
        referenceType: 'PAYMENT',
        referenceId,
        description,
        createdBy: userId,
      },
    });

    // 3. Update Balance
    // PAYMENT reduces outstanding balance, ADJUSTMENT modifies as specified
    const balanceChange = transactionType === 'PAYMENT' ? payAmount.negated() : payAmount;

    const updatedAccount = await tx.khataAccount.update({
      where: { id: khataAccount.id },
      data: {
        currentBalance: { increment: balanceChange },
      },
    });

    // 4. Audit Log
    await tx.auditLog.create({
      data: {
        shopId,
        userId,
        action: `KHATA_${transactionType}`,
        entityType: 'KHATA_TRANSACTION',
        entityId: transaction.id,
        newValues: { customerId, amount: payAmount.toNumber(), newBalance: updatedAccount.currentBalance.toNumber() },
      },
    });

    return { transaction, newBalance: updatedAccount.currentBalance };
  });
}
