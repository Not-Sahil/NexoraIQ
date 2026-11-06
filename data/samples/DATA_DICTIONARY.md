# NexoraIQ - Benchmark Data Dictionaries

This document provides schema definitions and column semantics for all benchmark datasets included with NexoraIQ.

---

## 1. business_data.csv (Weekly General Business Metrics)
- **Granularity:** Weekly (76 periods, 2023)
- **Columns:**
  - `date`: Start date of weekly reporting period (YYYY-MM-DD)
  - `revenue`: Gross top-line revenue generated during the week (USD)
  - `cost`: Cost of Goods Sold (COGS) and direct operational fulfillment cost (USD)
  - `profit_margin`: Net profit margin expressed as percentage (%)
  - `units_sold`: Volume count of units or subscriptions sold
  - `marketing_spend`: Total advertising and acquisition expenditure across all channels (USD)
  - `customer_count`: Total active purchasing customers in the week
  - `average_order_value`: Mean revenue per transaction (USD)
  - `website_visitors`: Total unique traffic sessions on platform
  - `conversion_rate`: Percentage of web visitors converting to paying customers (%)
  - `employee_count`: Full-time headcount supporting operations

---

## 2. realistic_olist_business_data.csv (E-Commerce Marketplace Dynamics)
- **Granularity:** Daily (500 records, 2022-2023)
- **Context:** Modeled after Brazilian multi-vendor marketplace data
- **Columns:**
  - `date`: Daily timestamp (YYYY-MM-DD)
  - `revenue`: Daily gross sales volume (USD)
  - `cost`: Direct supplier payments and freight costs (USD)
  - `units_sold`: Order items processed
  - `marketing_spend`: Daily PPC and performance marketing investment
  - `customer_count`: Daily unique buyers
  - `website_visitors`: Unique digital visits
  - `employee_count`: Active marketplace support and catalog staff
  - `profit_margin`: Daily calculated gross margin ratio (0.00 to 1.00)
  - `average_order_value`: Revenue / Orders
  - `conversion_rate`: Customer count / Website visitors

---

## 3. realistic_retail_business_data.csv (Brick-and-Mortar / Omnichannel Retail)
- **Granularity:** Daily (500 records)
- **Context:** Retail chains experiencing weekend seasonality, promotions, and occasional stockouts
- **Columns:**
  - `date`, `revenue`, `cost`, `units_sold`, `marketing_spend`, `customer_count`, `website_visitors`, `employee_count`, `profit_margin`, `average_order_value`, `conversion_rate`
  - High inventory unit throughput with tighter margins (-15% to +45%).

---

## 4. realistic_saas_business_data.csv (Subscription B2B / SaaS)
- **Granularity:** Daily (500 records)
- **Context:** High gross margin (60-85%), recurring contracts, higher AOV, lower daily unit volume
- **Columns:**
  - `date`, `revenue`, `cost`, `units_sold`, `marketing_spend`, `customer_count`, `website_visitors`, `employee_count`, `profit_margin`, `average_order_value`, `conversion_rate`

---

## 5. real_company_sales_data.csv.xlsx (Multi-Dimensional Enterprise Sales)
- **Granularity:** Transactional / Regional Aggregation (55 records, 2024)
- **Columns:**
  - `Date`: Order / batch transaction date
  - `Company`: Client / Enterprise vendor identifier (e.g. HP, Dell, Apple, Lenovo)
  - `Product`: Specific hardware / SKU line (e.g. Envy x360, XPS 15, MacBook Pro)
  - `Category`: High-level taxonomy (Electronics, Computing)
  - `Region`: Geographic sales territory (North America, Europe, Japan, Australia, APAC)
  - `Sales Amount`: Gross invoice total (USD)
  - `Cost`: Direct unit manufacturing & logistics cost (USD)
  - `Profit`: Net transaction profit (Sales Amount - Cost)
  - `Quantity Sold`: Physical batch units

