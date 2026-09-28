import { prisma } from '../db';

export async function getShopFullBusinessContext(shopId: string) {
  // 1. Fetch Shop Profile
  const shop = await prisma.shop.findUnique({
    where: { id: shopId },
    include: { owner: { select: { name: true, phone: true, email: true } } },
  });

  if (!shop) {
    throw new Error(`Shop with ID ${shopId} not found`);
  }

  // 2. Fetch Business Snapshot
  const [
    inventoryCount,
    lowStockItems,
    todaySalesAgg,
    recentSales,
    khataDuesAgg,
    activeRecommendations,
    recentOutcomes,
    recentWeather,
  ] = await Promise.all([
    // Inventory Count
    prisma.inventory.count({
      where: { shopId },
    }),

    // Low Stock Alert Items
    prisma.product.findMany({
      where: {
        shopId,
        isActive: true,
      },
      include: { inventory: true },
      take: 10,
    }),

    // Today's Sales Aggregate
    prisma.sale.aggregate({
      where: {
        shopId,
        saleDate: { gte: new Date(new Date().setHours(0, 0, 0, 0)) },
      },
      _sum: { totalAmount: true },
      _count: { id: true },
    }),

    // Recent 10 Sales
    prisma.sale.findMany({
      where: { shopId },
      orderBy: { saleDate: 'desc' },
      take: 10,
      include: {
        customer: { select: { name: true, phone: true } },
        items: { include: { product: { select: { name: true } } } },
      },
    }),

    // Khata Dues Aggregate
    prisma.khataAccount.aggregate({
      where: { shopId },
      _sum: { currentBalance: true },
      _count: { id: true },
    }),

    // Active AI Recommendations
    prisma.recommendation.findMany({
      where: { shopId, status: 'NEW' },
      orderBy: { generatedAt: 'desc' },
      take: 5,
    }),

    // Recommendation Outcomes Loop
    prisma.recommendationOutcome.findMany({
      where: { shopId },
      orderBy: { createdAt: 'desc' },
      take: 5,
      include: { recommendation: { select: { title: true, type: true } } },
    }),

    // Recent Weather Context
    prisma.weatherObservation.findFirst({
      where: { locationName: shop.city || 'Bengaluru' },
      orderBy: { observedAt: 'desc' },
    }),
  ]);

  return {
    shopContext: {
      shopId: shop.id,
      shopName: shop.name,
      ownerName: shop.owner.name,
      city: shop.city,
    },
    metricsSnapshot: {
      inventoryItemCount: inventoryCount,
      todaySalesTotal: todaySalesAgg._sum.totalAmount || 0,
      todayOrderCount: todaySalesAgg._count.id,
      totalKhataOutstanding: khataDuesAgg._sum.currentBalance || 0,
      khataAccountCount: khataDuesAgg._count.id,
    },
    lowStockAlerts: lowStockItems.map((p: any) => ({
      productId: p.id,
      productName: p.name,
      currentStock: p.inventory?.quantity,
      reorderLevel: p.reorderLevel,
    })),
    recentSalesHistory: recentSales,
    activeRecommendations,
    recentOutcomes,
    weatherObservation: recentWeather,
  };
}
