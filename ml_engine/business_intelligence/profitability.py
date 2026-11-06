"""
NexoraIQ: Profitability & Unit Economics Engine
Analyzes:
- Revenue, Cost, Gross Profit, Operating Expenses, Net Profit, Contribution Margins
- Break-Even Analysis
- Multi-dimensional breakdown (Product, Category, Region, Time-period)
- Identification of high-revenue / low-profit products & margin deterioration
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

class ProfitabilityAnalyticsEngine:
    def analyze_profitability(self, df: pd.DataFrame) -> Dict[str, Any]:
        data = df.copy()
        
        # Identify revenue and cost columns
        rev_col = "revenue" if "revenue" in data.columns else ("sales_amount" if "sales_amount" in data.columns else "Sales Amount")
        cost_col = "cost" if "cost" in data.columns else ("Cost" if "Cost" in data.columns else "cogs")
        profit_col = "profit" if "profit" in data.columns else ("net_profit" if "net_profit" in data.columns else "Profit")
        
        if rev_col not in data.columns:
            # Fallback numeric detection
            nums = data.select_dtypes(include=[np.number]).columns
            rev_col = nums[0] if len(nums) > 0 else None
            
        if not rev_col:
            return {"error": "No revenue or numerical metric found."}

        rev_series = pd.to_numeric(data[rev_col], errors="coerce").fillna(0)
        total_revenue = float(rev_series.sum())
        
        if cost_col in data.columns:
            cost_series = pd.to_numeric(data[cost_col], errors="coerce").fillna(0)
            total_cost = float(cost_series.sum())
        else:
            total_cost = float(total_revenue * 0.62) # Standard 62% baseline estimate
            cost_series = rev_series * 0.62
            
        gross_profit = float(total_revenue - total_cost)
        gross_margin_pct = round((gross_profit / max(1.0, total_revenue)) * 100.0, 2)
        
        # Operational expenses (marketing + salaries + overhead if present)
        opex = 0.0
        if "marketing_spend" in data.columns:
            opex += float(pd.to_numeric(data["marketing_spend"], errors="coerce").sum())
        if "employee_count" in data.columns:
            opex += float(pd.to_numeric(data["employee_count"], errors="coerce").mean() * 4500.0) # monthly payroll baseline
            
        if opex == 0.0:
            opex = total_revenue * 0.15 # estimated 15% OPEX
            
        net_profit = float(gross_profit - opex)
        net_margin_pct = round((net_profit / max(1.0, total_revenue)) * 100.0, 2)
        
        # Contribution Margin Ratio
        contribution_margin_ratio = round((gross_profit / max(1.0, total_revenue)), 4)
        break_even_revenue = round(opex / max(0.05, contribution_margin_ratio), 2)
        
        # Margin Trend (is margin expanding or compressing?)
        date_col = next((c for c in ["date", "Date", "timestamp"] if c in data.columns), None)
        margin_trend = "stable"
        if date_col and len(data) >= 10:
            data_sorted = data.sort_values(by=date_col)
            first_half = data_sorted.iloc[:len(data)//2]
            second_half = data_sorted.iloc[len(data)//2:]
            
            m1 = (first_half[rev_col].sum() - first_half[cost_col].sum()) / max(1.0, first_half[rev_col].sum())
            m2 = (second_half[rev_col].sum() - second_half[cost_col].sum()) / max(1.0, second_half[rev_col].sum())
            if m2 < m1 - 0.03:
                margin_trend = "compressing"
            elif m2 > m1 + 0.03:
                margin_trend = "expanding"

        # Multi-dimensional breakdowns
        dimension_analysis = {}
        for dim in ["Product", "product", "Category", "category", "Region", "region", "Company", "company"]:
            if dim in data.columns:
                grouped = data.groupby(dim).agg(
                    revenue=(rev_col, "sum"),
                    cost=(cost_col, "sum") if cost_col in data.columns else (rev_col, lambda x: x.sum() * 0.62)
                ).reset_index()
                grouped["profit"] = grouped["revenue"] - grouped["cost"]
                grouped["margin_pct"] = round((grouped["profit"] / grouped["revenue"].replace(0, 1.0)) * 100.0, 2)
                
                # Flag high-revenue low-profit entities (Revenue top 40% but Margin bottom 25%)
                rev_threshold = grouped["revenue"].quantile(0.60)
                margin_threshold = grouped["margin_pct"].quantile(0.35)
                grouped["is_high_revenue_low_profit"] = (grouped["revenue"] >= rev_threshold) & (grouped["margin_pct"] <= margin_threshold)
                
                dim_records = grouped.sort_values(by="revenue", ascending=False).to_dict(orient="records")
                dimension_analysis[dim.lower()] = dim_records

        return {
            "total_revenue": round(total_revenue, 2),
            "total_cost": round(total_cost, 2),
            "gross_profit": round(gross_profit, 2),
            "operating_expenses": round(opex, 2),
            "net_profit": round(net_profit, 2),
            "gross_margin_pct": gross_margin_pct,
            "net_margin_pct": net_margin_pct,
            "contribution_margin_ratio": contribution_margin_ratio,
            "break_even_revenue": break_even_revenue,
            "margin_trend": margin_trend,
            "dimension_breakdowns": dimension_analysis
        }

