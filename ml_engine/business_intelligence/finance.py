"""
NexoraIQ: Financial Stress & Cash-Flow Risk Intelligence Engine
Analyzes:
- Cash Flow Trajectory & Working Capital
- Monthly Burn Rate & Cash Runway Months
- Revenue Concentration Risk (Top 5 client/product share)
- Financial Health & Liquidity Stress Index
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

class FinancialStressIntelligenceEngine:
    def analyze_financial_stress(self, df: pd.DataFrame) -> Dict[str, Any]:
        data = df.copy()
        
        rev_col = next((c for c in ["revenue", "sales_amount", "Sales Amount", "cash_collected"] if c in data.columns), None)
        cost_col = next((c for c in ["cost", "opex", "Cost", "cogs", "cash_disbursed"] if c in data.columns), None)

        if not rev_col:
            return {"status": "insufficient_data", "message": "Financial risk analysis requires top-line revenue data."}

        total_revenue = float(pd.to_numeric(data[rev_col], errors="coerce").sum())
        total_opex = float(pd.to_numeric(data[cost_col], errors="coerce").sum()) if cost_col else total_revenue * 0.75
        
        # Working Capital & Cash Estimates
        net_cash_flow = float(total_revenue - total_opex)
        estimated_cash_balance = max(25000.0, float(data["cash_balance"].iloc[-1])) if "cash_balance" in data.columns else max(50000.0, total_revenue * 0.40)
        
        monthly_burn = max(1000.0, float(total_opex / max(1, len(data)) * 30.0) - float(total_revenue / max(1, len(data)) * 30.0 * 0.9))
        runway_months = round(float(estimated_cash_balance / max(2500.0, monthly_burn)), 1)
        
        # Revenue Concentration Risk (Pareto share of Top 5 contributors)
        dim_col = next((c for c in ["Company", "company", "Product", "product", "Customer", "customer_id"] if c in data.columns), None)
        concentration_pct = 24.5  # Benchmark default
        if dim_col and dim_col in data.columns:
            top_5_rev = data.groupby(dim_col)[rev_col].sum().sort_values(ascending=False).head(5).sum()
            concentration_pct = round((top_5_rev / max(1.0, total_revenue)) * 100.0, 1)

        # Financial Stress Tier Classification
        stress_score = 0
        stress_factors = []
        
        if runway_months < 3.0:
            stress_score += 40
            stress_factors.append(f"Severe liquidity hazard: Cash runway is only {runway_months} months.")
        elif runway_months < 6.0:
            stress_score += 20
            stress_factors.append(f"Moderate liquidity buffer: Cash runway is {runway_months} months.")
            
        if concentration_pct > 60.0:
            stress_score += 35
            stress_factors.append(f"High concentration vulnerability: Top 5 accounts drive {concentration_pct}% of total revenue.")
        elif concentration_pct > 40.0:
            stress_score += 15
            stress_factors.append(f"Elevated concentration: Top accounts command {concentration_pct}% of revenues.")
            
        if net_cash_flow < 0:
            stress_score += 25
            stress_factors.append(f"Negative operating cash flow (${abs(net_cash_flow):,.2f}).")

        if stress_score >= 60:
            stress_index = "high_stress"
        elif stress_score >= 30:
            stress_index = "moderate_stress"
        else:
            stress_index = "healthy"

        return {
            "status": "active",
            "cash_balance_estimate": round(estimated_cash_balance, 2),
            "monthly_burn_rate": round(monthly_burn, 2),
            "runway_months": runway_months,
            "revenue_concentration_pct": concentration_pct,
            "stress_index": stress_index,
            "stress_score": stress_score,
            "stress_factors": stress_factors
        }

