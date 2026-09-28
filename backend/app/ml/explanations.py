from typing import List, Dict, Any


def generate_interpretable_factors(features: Dict[str, Any], forecast_7d: float, stockout_risk: float) -> List[Dict[str, str]]:
    factors = []
    sales_growth = features.get("sales_growth", 0.0)
    stock_coverage = features.get("stock_coverage_days", 999.0)
    current_stock = features.get("current_stock", 0.0)

    if sales_growth > 0.10:
        factors.append({
            "factor": "recent_sales",
            "impact": "high",
            "explanation": f"Sales increased by {int(sales_growth * 100)}% over the last 14 days."
        })
    elif sales_growth < -0.10:
        factors.append({
            "factor": "recent_sales",
            "impact": "medium",
            "explanation": f"Sales dropped by {abs(int(sales_growth * 100))}% recently."
        })

    if stock_coverage < 5.0:
        factors.append({
            "factor": "stock_coverage",
            "impact": "critical",
            "explanation": f"Current stock ({int(current_stock)}) covers only ~{stock_coverage:.1f} days of demand."
        })

    if stockout_risk > 0.70:
        factors.append({
            "factor": "stockout_warning",
            "impact": "high",
            "explanation": "High likelihood of running out of stock before the next weekly restock."
        })

    if not factors:
        factors.append({
            "factor": "stable_demand",
            "impact": "low",
            "explanation": "Consistent historical sales velocity observed."
        })

    return factors
