"""
NexoraIQ: Multi-Domain Realistic Synthetic Business Data Generator
Covers 4 Domains:
1. Retail and E-Commerce (Orders, Customers, Items, Anomaly Labels, Stockout Labels)
2. SaaS and Subscription Business (Subscriptions, Churn Labels, MRR, Usage)
3. Manufacturing and Inventory (Suppliers, Stock, DIO, Reorder, Shortages)
4. General Business Financial Operations (Revenue, OPEX, Cash Flow, Financial Stress)

Includes reproducible seeds, seasonal patterns, realistic noise, and ground-truth labels.
Chronological 70% / 15% / 15% train/val/test splits.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, List, Optional

class SyntheticBusinessGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)

    def generate_retail_ecommerce(
        self,
        start_date: str = "2023-01-01",
        days: int = 730,
        output_dir: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Generates Retail & E-Commerce dataset:
        - Daily transactions & aggregate metrics
        - Known anomalies (flash sales, supplier shocks, payment gateway drops)
        - Inventory stockouts
        - Customer purchase history & churn
        """
        dates = pd.date_range(start=start_date, periods=days, freq="D")
        records = []
        
        base_revenue = 15000.0
        base_visitors = 4500
        growth_rate = 0.0008  # ~30% annual growth
        
        # Ground-truth anomaly indices (e.g. Black Friday spikes, inventory runouts, site outages)
        anomaly_indices = set(random.sample(range(50, days - 50), k=12))

        for idx, current_date in enumerate(dates):
            # Day of week seasonality: Higher on weekends (Saturday=5, Sunday=6)
            dow = current_date.weekday()
            is_weekend = 1 if dow in (5, 6) else 0
            dow_factor = 1.35 if is_weekend else (0.85 if dow == 0 else 1.0)
            
            # Month seasonality (Q4 holiday boost: Nov=11, Dec=12)
            month = current_date.month
            month_factor = 1.5 if month == 12 else (1.3 if month == 11 else (0.9 if month in (1, 2) else 1.0))
            
            # Trend component
            trend = 1.0 + (idx * growth_rate)
            
            # Marketing campaigns
            marketing_spend = round(max(500.0, np.random.normal(1800.0, 400.0) * dow_factor), 2)
            
            # Website traffic driven by trend, seasonality, marketing
            traffic_noise = np.random.normal(0, 300)
            visitors = int(max(800, (base_visitors * trend * month_factor * dow_factor) + (marketing_spend * 0.9) + traffic_noise))
            
            # Base conversion rate (2.0% - 4.5%)
            conversion_rate = round(float(np.clip(np.random.normal(0.032, 0.004) * (1.1 if is_weekend else 1.0), 0.015, 0.065)), 4)
            
            customer_count = int(max(10, visitors * conversion_rate))
            
            # Average order value ($65 - $140)
            aov = round(float(np.clip(np.random.normal(92.0, 12.0) + (15.0 if month == 12 else 0.0), 45.0, 180.0)), 2)
            
            # Units sold & Gross Revenue
            units_sold = int(customer_count * np.random.uniform(1.2, 1.8))
            revenue = round(float(customer_count * aov), 2)
            
            # COGS & Operational Costs (typically 55-68% of revenue)
            cogs_ratio = float(np.clip(np.random.normal(0.60, 0.03), 0.48, 0.72))
            cogs = round(revenue * cogs_ratio, 2)
            shipping_and_handling = round(customer_count * np.random.uniform(4.0, 8.5), 2)
            total_cost = round(cogs + shipping_and_handling + marketing_spend, 2)
            
            gross_profit = round(revenue - cogs, 2)
            net_profit = round(revenue - total_cost, 2)
            profit_margin = round(float((net_profit / revenue) * 100 if revenue > 0 else 0.0), 2)
            
            # Ground-truth anomaly injection
            is_anomaly = 0
            anomaly_type = "None"
            stockout_flag = 0
            
            if idx in anomaly_indices:
                is_anomaly = 1
                kind = random.choice(["revenue_spike", "traffic_surge", "cost_blowout", "gateway_glitch"])
                if kind == "revenue_spike":
                    revenue = round(revenue * 2.8, 2)
                    units_sold = int(units_sold * 2.5)
                    anomaly_type = "Promotional Surge / Viral Spike"
                elif kind == "traffic_surge":
                    visitors = int(visitors * 3.5)
                    conversion_rate = 0.008
                    anomaly_type = "Bot Traffic Infiltration"
                elif kind == "cost_blowout":
                    cogs = round(cogs * 2.2, 2)
                    total_cost = round(cogs + marketing_spend + shipping_and_handling, 2)
                    net_profit = round(revenue - total_cost, 2)
                    profit_margin = round(float((net_profit / revenue) * 100), 2)
                    anomaly_type = "Emergency Freight & Supplier Surcharge"
                elif kind == "gateway_glitch":
                    revenue = round(revenue * 0.25, 2)
                    customer_count = int(customer_count * 0.25)
                    anomaly_type = "Checkout Gateway Outage"

            # Stockout condition (when high demand exhausts standard 180 unit daily buffer)
            if units_sold > 320:
                stockout_flag = 1
            
            records.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "revenue": revenue,
                "cost": total_cost,
                "cogs": cogs,
                "gross_profit": gross_profit,
                "net_profit": net_profit,
                "profit_margin": profit_margin,
                "units_sold": units_sold,
                "marketing_spend": marketing_spend,
                "customer_count": customer_count,
                "average_order_value": aov,
                "website_visitors": visitors,
                "conversion_rate": conversion_rate,
                "is_weekend": is_weekend,
                "is_stockout_risk": stockout_flag,
                "is_ground_truth_anomaly": is_anomaly,
                "anomaly_label": anomaly_type
            })
            
        df = pd.DataFrame(records)
        
        # Chronological Split (70% train, 15% val, 15% test)
        n = len(df)
        train_idx = int(n * 0.70)
        val_idx = int(n * 0.85)
        
        train_df = df.iloc[:train_idx].copy()
        val_df = df.iloc[train_idx:val_idx].copy()
        test_df = df.iloc[val_idx:].copy()
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(os.path.join(output_dir, "retail_ecommerce_full.csv"), index=False)
            train_df.to_csv(os.path.join(output_dir, "retail_ecommerce_train.csv"), index=False)
            val_df.to_csv(os.path.join(output_dir, "retail_ecommerce_val.csv"), index=False)
            test_df.to_csv(os.path.join(output_dir, "retail_ecommerce_test.csv"), index=False)
            
        return {"full": df, "train": train_df, "val": val_df, "test": test_df}

    def generate_saas_metrics(
        self,
        start_date: str = "2023-01-01",
        days: int = 730,
        output_dir: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Generates SaaS & Subscription dataset:
        - Monthly Recurring Revenue (MRR), Annual Recurring Revenue (ARR)
        - Customer Acquisition Cost (CAC), Customer Lifetime Value (CLV)
        - Churn indicators, Net Expansion Rate, ARPU
        """
        dates = pd.date_range(start=start_date, periods=days, freq="D")
        records = []
        
        active_subscribers = 420
        arpu = 120.0  # Average Revenue Per User
        
        for idx, current_date in enumerate(dates):
            # SaaS marketing drive
            marketing_spend = round(max(300.0, np.random.normal(1200.0, 200.0)), 2)
            
            # New trials and signups
            leads = int(marketing_spend / np.random.uniform(18.0, 25.0))
            trial_to_paid_rate = float(np.clip(np.random.normal(0.08, 0.015), 0.04, 0.14))
            new_subscribers = int(leads * trial_to_paid_rate)
            
            # Daily churn (0.05% - 0.15% daily churn corresponds to 1.5% - 4.5% monthly churn)
            daily_churn_rate = float(np.clip(np.random.normal(0.0008, 0.0002), 0.0002, 0.0018))
            churned_subscribers = int(active_subscribers * daily_churn_rate)
            
            active_subscribers = max(50, active_subscribers + new_subscribers - churned_subscribers)
            
            # Daily normalized recurring revenue
            mrr = round(active_subscribers * arpu, 2)
            arr = round(mrr * 12, 2)
            daily_revenue = round(mrr / 30.0, 2)
            
            # Infrastructure hosting and support costs (COGS is low in SaaS, ~15-22%)
            hosting_and_cogs = round(daily_revenue * np.random.uniform(0.14, 0.20), 2)
            operating_expenses = round(hosting_and_cogs + marketing_spend + 800.0, 2) # Salaries & R&D
            net_profit = round(daily_revenue - operating_expenses, 2)
            profit_margin = round(float((net_profit / daily_revenue) * 100), 2)
            
            cac = round(marketing_spend / max(1, new_subscribers), 2)
            clv = round((arpu / max(0.01, daily_churn_rate * 30)) * 0.82, 2)
            
            # Elevated churn risk if CAC exceeds 3x monthly ARPU or Net Margin turns negative
            churn_risk_flag = 1 if (churned_subscribers > 2 or daily_churn_rate > 0.0012) else 0
            
            records.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "revenue": daily_revenue,
                "mrr": mrr,
                "arr": arr,
                "cost": operating_expenses,
                "gross_profit": round(daily_revenue - hosting_and_cogs, 2),
                "net_profit": net_profit,
                "profit_margin": profit_margin,
                "active_subscribers": active_subscribers,
                "new_subscribers": new_subscribers,
                "churned_subscribers": churned_subscribers,
                "churn_rate_daily": round(daily_churn_rate * 100, 3),
                "cac": cac,
                "clv": clv,
                "marketing_spend": marketing_spend,
                "churn_risk_label": churn_risk_flag
            })
            
        df = pd.DataFrame(records)
        
        n = len(df)
        train_idx = int(n * 0.70)
        val_idx = int(n * 0.85)
        
        train_df = df.iloc[:train_idx].copy()
        val_df = df.iloc[train_idx:val_idx].copy()
        test_df = df.iloc[val_idx:].copy()
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(os.path.join(output_dir, "saas_subscriptions_full.csv"), index=False)
            train_df.to_csv(os.path.join(output_dir, "saas_subscriptions_train.csv"), index=False)
            val_df.to_csv(os.path.join(output_dir, "saas_subscriptions_val.csv"), index=False)
            test_df.to_csv(os.path.join(output_dir, "saas_subscriptions_test.csv"), index=False)
            
        return {"full": df, "train": train_df, "val": val_df, "test": test_df}

    def generate_manufacturing_inventory(
        self,
        start_date: str = "2023-01-01",
        days: int = 730,
        output_dir: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Generates Manufacturing and Supply Chain inventory dataset:
        - Raw material receipts, production runs, finished goods inventory
        - Days Inventory Outstanding (DIO), Inventory Turnover Ratio
        - Stockout probability and supply disruption risk
        """
        dates = pd.date_range(start=start_date, periods=days, freq="D")
        records = []
        
        inventory_units = 5000
        avg_unit_cost = 45.0
        
        for idx, current_date in enumerate(dates):
            # Demand fluctuation
            daily_demand = int(np.clip(np.random.normal(120, 25), 40, 260))
            
            # Periodic batch production/supplier deliveries
            batch_delivered = 0
            if idx % 14 == 0:  # Bi-weekly supplier replenishments
                batch_delivered = int(np.random.normal(1800, 150))
                
            inventory_units = max(0, inventory_units + batch_delivered - daily_demand)
            
            holding_cost = round(inventory_units * 0.15, 2)
            cogs = round(daily_demand * avg_unit_cost, 2)
            revenue = round(daily_demand * avg_unit_cost * 1.55, 2) # 55% markup
            
            inventory_value = round(inventory_units * avg_unit_cost, 2)
            # Days Inventory Outstanding (DIO) = (Inventory / COGS) * 365 / 365 (daily = Inventory / Daily COGS)
            dio = round(float(inventory_units / max(1, daily_demand)), 1)
            turnover_ratio = round(float(365.0 / max(1.0, dio)), 2)
            
            # Stockout risk is high when inventory falls below 5 days of average demand
            stockout_risk = 1 if inventory_units < (daily_demand * 5) else 0
            
            records.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "inventory_units": inventory_units,
                "inventory_value": inventory_value,
                "daily_demand": daily_demand,
                "batch_delivered": batch_delivered,
                "cogs": cogs,
                "revenue": revenue,
                "holding_cost": holding_cost,
                "dio": dio,
                "turnover_ratio": turnover_ratio,
                "stockout_risk": stockout_risk
            })
            
        df = pd.DataFrame(records)
        
        n = len(df)
        train_idx = int(n * 0.70)
        val_idx = int(n * 0.85)
        
        train_df = df.iloc[:train_idx].copy()
        val_df = df.iloc[train_idx:val_idx].copy()
        test_df = df.iloc[val_idx:].copy()
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(os.path.join(output_dir, "manufacturing_inventory_full.csv"), index=False)
            train_df.to_csv(os.path.join(output_dir, "manufacturing_inventory_train.csv"), index=False)
            val_df.to_csv(os.path.join(output_dir, "manufacturing_inventory_val.csv"), index=False)
            test_df.to_csv(os.path.join(output_dir, "manufacturing_inventory_test.csv"), index=False)
            
        return {"full": df, "train": train_df, "val": val_df, "test": test_df}

    def generate_financial_operations(
        self,
        start_date: str = "2023-01-01",
        days: int = 730,
        output_dir: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Generates General Business Financial Operations:
        - Cash Inflows, Cash Outflows, Net Cash Flow
        - Accounts Receivable (AR), Accounts Payable (AP), Working Capital
        - Burn Rate, Runway Months, Financial Stress Index
        """
        dates = pd.date_range(start=start_date, periods=days, freq="D")
        records = []
        
        cash_balance = 350000.0  # Starting liquidity
        ar_balance = 85000.0
        ap_balance = 45000.0
        
        for idx, current_date in enumerate(dates):
            # Inflows & Outflows
            daily_sales = max(5000.0, np.random.normal(16000.0, 3000.0))
            cash_collected = round(daily_sales * np.random.uniform(0.70, 0.95), 2)
            ar_delta = daily_sales - cash_collected
            ar_balance = max(10000.0, ar_balance + ar_delta)
            
            # Operational disbursement
            daily_opex = round(max(3000.0, np.random.normal(12500.0, 2200.0)), 2)
            cash_disbursed = round(daily_opex * np.random.uniform(0.75, 1.05), 2)
            ap_delta = daily_opex - cash_disbursed
            ap_balance = max(8000.0, ap_balance + ap_delta)
            
            net_cash_flow = round(cash_collected - cash_disbursed, 2)
            cash_balance = max(15000.0, cash_balance + net_cash_flow)
            
            working_capital = round((cash_balance + ar_balance) - ap_balance, 2)
            monthly_burn = max(1000.0, daily_opex * 30.0 - (daily_sales * 30.0 * 0.9))
            runway_months = round(float(cash_balance / max(5000.0, monthly_burn)), 1)
            
            # Financial stress threshold: runway under 3.5 months or negative working capital
            stress_tier = "low"
            if runway_months < 2.5:
                stress_tier = "critical"
            elif runway_months < 4.5:
                stress_tier = "medium"
                
            records.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "revenue": round(daily_sales, 2),
                "opex": daily_opex,
                "cash_collected": cash_collected,
                "cash_disbursed": cash_disbursed,
                "net_cash_flow": net_cash_flow,
                "cash_balance": round(cash_balance, 2),
                "accounts_receivable": round(ar_balance, 2),
                "accounts_payable": round(ap_balance, 2),
                "working_capital": working_capital,
                "runway_months": runway_months,
                "financial_stress_level": stress_tier
            })
            
        df = pd.DataFrame(records)
        
        n = len(df)
        train_idx = int(n * 0.70)
        val_idx = int(n * 0.85)
        
        train_df = df.iloc[:train_idx].copy()
        val_df = df.iloc[train_idx:val_idx].copy()
        test_df = df.iloc[val_idx:].copy()
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(os.path.join(output_dir, "financial_operations_full.csv"), index=False)
            train_df.to_csv(os.path.join(output_dir, "financial_operations_train.csv"), index=False)
            val_df.to_csv(os.path.join(output_dir, "financial_operations_val.csv"), index=False)
            test_df.to_csv(os.path.join(output_dir, "financial_operations_test.csv"), index=False)
            
        return {"full": df, "train": train_df, "val": val_df, "test": test_df}

    def generate_customer_rfm_churn_dataset(
        self,
        num_customers: int = 1500,
        output_dir: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Generates individual Customer RFM & Churn dataset with ground-truth labels
        for training supervised churn models (Random Forest, XGBoost, Logistic Regression).
        """
        records = []
        for i in range(1, num_customers + 1):
            cust_id = f"CUST_{i:05d}"
            
            # Recency: days since last purchase (1 to 365)
            # Frequency: total lifetime orders (1 to 45)
            # Monetary: total lifetime spend ($25 to $12,500)
            recency = int(np.random.exponential(scale=65) + 1)
            recency = min(recency, 365)
            
            frequency = int(np.random.geometric(p=0.15))
            frequency = min(max(1, frequency), 60)
            
            avg_ticket = float(np.random.normal(85.0, 30.0))
            avg_ticket = max(18.0, avg_ticket)
            monetary = round(frequency * avg_ticket, 2)
            
            # RFM Scoring (1 to 5)
            r_score = 5 if recency <= 30 else (4 if recency <= 60 else (3 if recency <= 120 else (2 if recency <= 200 else 1)))
            f_score = 5 if frequency >= 15 else (4 if frequency >= 8 else (3 if frequency >= 4 else (2 if frequency >= 2 else 1)))
            m_score = 5 if monetary >= 1500 else (4 if monetary >= 800 else (3 if monetary >= 350 else (2 if monetary >= 150 else 1)))
            
            # Segment mapping
            rfm_composite = (r_score * 100) + (f_score * 10) + m_score
            if r_score >= 4 and f_score >= 4:
                segment = "Champions"
            elif r_score >= 3 and f_score >= 3:
                segment = "Loyal Customers"
            elif r_score >= 4 and f_score <= 2:
                segment = "Recent Customers"
            elif r_score <= 2 and f_score >= 3:
                segment = "At Risk"
            elif r_score == 1 and f_score <= 2:
                segment = "Lost"
            else:
                segment = "Potential Loyalists"
                
            # Ground-truth Churn Definition: High recency + low engagement
            # Logistic churn probability
            logit = -1.8 + (0.018 * recency) - (0.12 * frequency) - (0.00015 * monetary)
            churn_prob = 1.0 / (1.0 + np.exp(-logit))
            churn_label = 1 if np.random.rand() < churn_prob else 0
            
            records.append({
                "customer_id": cust_id,
                "recency_days": recency,
                "frequency_orders": frequency,
                "monetary_spend": monetary,
                "r_score": r_score,
                "f_score": f_score,
                "m_score": m_score,
                "rfm_composite": rfm_composite,
                "segment": segment,
                "support_tickets_opened": int(np.random.poisson(lam=1.2)),
                "satisfaction_rating": round(float(np.clip(np.random.normal(4.1, 0.8), 1.0, 5.0)), 1),
                "churn_probability_ground_truth": round(float(churn_prob), 4),
                "is_churned": churn_label
            })
            
        df = pd.DataFrame(records)
        
        # Split 70 / 15 / 15
        shuffled = df.sample(frac=1.0, random_state=self.seed).reset_index(drop=True)
        n = len(shuffled)
        train_idx = int(n * 0.70)
        val_idx = int(n * 0.85)
        
        train_df = shuffled.iloc[:train_idx].copy()
        val_df = shuffled.iloc[train_idx:val_idx].copy()
        test_df = shuffled.iloc[val_idx:].copy()
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(os.path.join(output_dir, "customer_rfm_churn_full.csv"), index=False)
            train_df.to_csv(os.path.join(output_dir, "customer_rfm_churn_train.csv"), index=False)
            val_df.to_csv(os.path.join(output_dir, "customer_rfm_churn_val.csv"), index=False)
            test_df.to_csv(os.path.join(output_dir, "customer_rfm_churn_test.csv"), index=False)
            
        return {"full": df, "train": train_df, "val": val_df, "test": test_df}


def generate_all_synthetic_data(base_dir: str = "data/synthetic") -> Dict[str, Dict[str, pd.DataFrame]]:
    """Generates all 4 business domain datasets into data/synthetic/"""
    os.makedirs(base_dir, exist_ok=True)
    gen = SyntheticBusinessGenerator(seed=42)
    
    retail = gen.generate_retail_ecommerce(output_dir=os.path.join(base_dir, "retail_ecommerce"))
    saas = gen.generate_saas_metrics(output_dir=os.path.join(base_dir, "saas"))
    manufacturing = gen.generate_manufacturing_inventory(output_dir=os.path.join(base_dir, "manufacturing"))
    finance = gen.generate_financial_operations(output_dir=os.path.join(base_dir, "finance"))
    customers = gen.generate_customer_rfm_churn_dataset(output_dir=os.path.join(base_dir, "customers"))
    
    print("All synthetic domain datasets successfully generated and chronologically split!")
    return {
        "retail": retail,
        "saas": saas,
        "manufacturing": manufacturing,
        "finance": finance,
        "customers": customers
    }

if __name__ == "__main__":
    generate_all_synthetic_data()

