# NexoraIQ Business Analyst & User Guide

Welcome to **NexoraIQ**, an enterprise AI-powered business intelligence, predictive analytics, and decision-support SaaS platform.

---

## 1. Quick Start Walkthrough

### Step 1: Login & Workspace Selection
1. Navigate to the login page (`/login`).
2. Use the instant **1-Click Demo Reviewer Login** or enter:
   - **Email:** `demo@nexoraiq.com`
   - **Password:** `demo1234`
3. In the top navigation bar, select your active **Workspace** (e.g. *Retail & E-Commerce Operations* or *European B2B Wholesale*) and your **Active Dataset**.

### Step 2: Exploring the Executive Dashboard
- Review **Gross Revenue**, **Net Operating Profit**, **Customer Acquisition Cost (CAC)**, and **Marketing ROAS**.
- Inspect the **Revenue vs Net Profit Trajectory** chart to observe historical seasonality and period trends.
- Review the **Operating Cost Breakdown** to see COGS versus marketing and headcount distribution.

### Step 3: Managing & Auditing Datasets
- Navigate to **Data Management** (`/data`):
  - Drag-and-drop any CSV or Excel (`.xlsx`) business dataset.
  - Review the automatically inferred column types and mapped semantic roles (`revenue`, `transaction_date`, `customer_id`, `units_sold`).
  - Click **Seed Benchmark Datasets** at any time to populate pre-verified retail, SaaS, or financial benchmarks.
- Navigate to **Data Quality Audit** (`/quality`):
  - Check your dataset's **Data Health Grade** (0-100%).
  - Review Completeness, Uniqueness, Validity, and Consistency scores.
  - Review actionable remedies for missing dates, negative values, or extreme outliers.

### Step 4: Unit Economics & Profitability Analytics
- Navigate to **Profitability** (`/profitability`):
  - Check the **Contribution Margin Ratio** and **Break-Even Revenue Threshold**.
  - Monitor the **Sequential Margin Trend** alert to identify whether profit margins are expanding or compressing.
  - Review the **Margin Leakage Table** to isolate high-volume products that generate low profits.

### Step 5: Running Predictive Machine Learning Forecasts
- Navigate to **Forecasting** (`/forecasting`):
  - Select your forecast horizon (14, 30, 60, or 90 days).
  - Click **Run Walk-Forward Forecast**.
  - The system will chronologically split your data (70% train, 15% validation, 15% test), benchmark all algorithms (Ridge, Random Forest, XGBoost, LightGBM, ARIMA, Naive Baselines), select the winner, and plot future predictions with 95% Confidence Intervals.

### Step 6: Investigating Operational Anomalies
- Navigate to **Anomaly Detection** (`/anomalies`):
  - Adjust the **Contamination Sensitivity** slider (2%, 5%, or 10%).
  - Inspect flagged anomaly events categorized as Critical, High, or Medium severity.
  - Read the automated **Root Cause Explanations** (e.g. conversion funnel failure, traffic spikes, freight blowouts).

### Step 7: Customer Retention & Churn Risk
- Navigate to **Customer Churn** (`/customers`):
  - View RFM customer segmentation (Champions, Loyal Buyers, At-Risk, Lost).
  - Review the supervised churn model's ROC-AUC, precision, and recall metrics.
  - View the list of **High-Risk Accounts** and trigger targeted customer success interventions.

### Step 8: Consulting the Grounded AI Business Advisor
- Navigate to **AI Business Advisor** (`/advisor`):
  - Ask natural language questions like *"Why did my profit decrease this month?"* or *"What is my expected revenue over the next 30 days?"*.
  - Review the **Prioritized Action Feed** containing identified problems, supporting evidence, root causes, recommended actions, and expected business impacts.

### Step 9: Exporting Executive Decision Reports
- Navigate to **Reports** (`/reports`):
  - Select **Excel Workbook (.xlsx)** or **PDF Executive Brief (.pdf)**.
  - Click **Compile & Export** to generate a board-ready report for download.

