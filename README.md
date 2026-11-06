# NexoraIQ: AI-Powered Business Intelligence, Predictive Analytics & Decision Support Platform

NexoraIQ is an enterprise-grade AI decision-support SaaS platform that transforms fragmented business data into actionable operational and financial intelligence.

Built to replace legacy desktop prototypes and static dashboards, NexoraIQ delivers a full predictive stack: universal data ingestion, leakage-free feature engineering, multi-model chronological forecasting, multi-method anomaly detection, customer RFM churn prediction, profitability unit economics, and a tool-grounded AI Business Advisor.

---

## 🌟 Key Application Modules

| Module | Core Functionality | Algorithms & Tech Stack |
| :--- | :--- | :--- |
| **Executive Dashboard** | Real-time KPIs (Revenue, Profit, Margins, CAC, CLV, Growth %) | Dynamic Pandas Aggregations, Recharts Area/Bar |
| **Universal Data Ingestion** | Dynamic schema inference, semantic role mapping & data quality grading (0-100%) | RegEx heuristics, Outlier IQR, pandas, openpyxl |
| **Leakage-Free Feature Pipeline** | Autoregressive lags (1, 7, 14, 30), rolling stats, cyclical calendar sine/cosine transforms | Strict chronological Train/Val/Test fitting |
| **Predictive Forecasting** | Walk-forward cross-validation, 95% confidence intervals, recursive forward projections | Ridge, Random Forest, XGBoost, LightGBM, ARIMA |
| **Profitability & Unit Economics** | Gross/Net margins, contribution margins, break-even analysis, margin leakage flags | Micro-economic unit accounting formulas |
| **Customer Intelligence** | RFM customer segmentation & supervised churn risk classification with ROC-AUC & confusion matrix | Random Forest, Gradient Boosting, Logistic Regression |
| **Ensemble Anomaly Detection** | Operational outlier detection with business-language root cause attribution | Isolation Forest, Local Outlier Factor (LOF), Rolling Z-Score |
| **Inventory & Operational DIO** | Inventory turnover, Days Inventory Outstanding (DIO), ABC Pareto classification & stockout risk | Pareto 80/15/5 distribution, velocity buffers |
| **Marketing Attribution & ROAS** | Channel CAC, ROAS multiple, conversion funnels & budget reallocation recommendations | Attribution models, channel return matrices |
| **Cash-Flow & Financial Stress** | Solvency stress index, monthly net burn rate, runway months projection & concentration risk | Working capital & liquidity stress models |
| **Explainable AI (XAI)** | Global feature importance & directional contribution attributions translated to plain English | SHAP TreeExplainer (`shap.TreeExplainer`) |
| **Grounded AI Business Advisor** | Controlled tool-based natural language Q&A and prioritized strategic action feed | Grounded deterministic reasoning engine |
| **Executive Decision Reports** | Board-ready stylized PDF briefs & multi-tab financial Excel workbooks | ReportLab PDF engine, openpyxl |

---

## 🏗️ Technology Stack

- **Frontend:** React 18, Vite, Tailwind CSS, Lucide React, Recharts, React Router v6, TanStack Query, Axios
- **Backend:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy, Uvicorn
- **Machine Learning:** Scikit-learn, XGBoost, LightGBM, Statsmodels (ARIMA), SHAP, NumPy, Pandas, Joblib
- **Database:** Supabase PostgreSQL with Row Level Security (RLS) + Dual-mode local SQLite fallback
- **Authentication:** Supabase Auth compatible JWT Bearer tokens with Bcrypt password hashing
- **Testing:** Pytest, FastAPI TestClient, Vitest/Vite Build Pipeline
- **Containerization:** Docker, Docker Compose

---

## 🚀 Quick Start Guide (Local Setup)

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm 9+

### 2. Backend Setup
```bash
# Navigate to project root
cd NexoralQ

# Create and activate virtual environment
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
pip install "email-validator>=2.0.0"

# Generate synthetic domain datasets (optional, pre-generated in data/synthetic/)
python -m ml_engine.synthetic.generator

# Start the FastAPI backend server
uvicorn backend.app.main:app --reload --port 8000
```
*The backend API documentation will be available at: http://127.0.0.1:8000/api/v1/docs*

### 3. Frontend Setup
```bash
# Open a new terminal in the frontend directory
cd frontend

# Install dependencies (already installed)
npm install

# Start Vite development server
npm run dev
```
*The frontend application will be live at: http://localhost:5173*

---

## 🔑 Demo Access Credentials
NexoraIQ automatically provisions an enterprise demo environment upon startup:
- **Email:** `demo@nexoraiq.com`
- **Password:** `demo1234`
*(Or simply click **1-Click Demo Reviewer Login** on the login page)*

---

## 🧪 Running Automated Tests

Run the backend and ML test suite with Pytest:
```bash
# Run unit & ML tests
python -m pytest backend/tests/test_backend_and_ml.py -v

# Run complete 13-step End-to-End User Lifecycle test
python -m pytest backend/tests/test_e2e_workflow.py -v
```

---

## 🐳 Docker Deployment
To launch the entire platform via Docker:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:80`
- Backend: `http://localhost:8000`

---

## 📚 Complete Documentation
- [System Architecture](documentation/ARCHITECTURE.md)
- [ML Methodology & Validation](documentation/ML_METHODOLOGY.md)
- [REST API Specification](documentation/API_SPECIFICATION.md)
- [Database Schema & Migrations](documentation/DATABASE_SCHEMA.md)
- [User & Analyst Guide](documentation/USER_GUIDE.md)
- [Benchmark Data Dictionaries](data/samples/DATA_DICTIONARY.md)
- [Migration Report & Architectural Audit](C:\Users\Sahil\.gemini\antigravity\brain\89dcd80c-4629-471e-8156-475fbc7e8822\migration_and_architecture_plan.md)

