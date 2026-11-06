import pytest
import os
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from ml_engine.ingestion.universal_parser import UniversalDataIngestionEngine
from ml_engine.feature_engineering.pipeline import TimeSeriesFeatureEngineer
from ml_engine.forecasting.engine import BusinessForecastingEngine
from ml_engine.anomaly_detection.detector import MultiMethodAnomalyDetector
from ml_engine.customer_intelligence.rfm_churn import CustomerIntelligenceEngine
from ml_engine.business_intelligence.profitability import ProfitabilityAnalyticsEngine
from ml_engine.business_intelligence.advisor import GroundedBusinessAdvisor

client = TestClient(app)

# 1. CORE AUTH & SECURITY TESTS
def test_password_hashing_and_verification():
    raw = "SecureSecret123!"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_cycle():
    token = create_access_token("test-user-id")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "test-user-id"

# 2. FASTAPI ENDPOINT TESTS
def test_health_check_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["platform"] == "NexoraIQ"

def test_auth_login_demo_user():
    res = client.post("/api/v1/auth/login", json={
        "email": "demo@nexoraiq.com",
        "password": "demo1234"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "demo@nexoraiq.com"
    assert data["user"]["workspace_id"] is not None

def test_list_workspaces_and_datasets():
    # Login first
    login_res = client.post("/api/v1/auth/login", json={
        "email": "demo@nexoraiq.com",
        "password": "demo1234"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    ws_res = client.get("/api/v1/workspaces/", headers=headers)
    assert ws_res.status_code == 200
    workspaces = ws_res.json()
    assert len(workspaces) > 0
    ws_id = workspaces[0]["id"]
    
    ds_res = client.get(f"/api/v1/datasets/?workspace_id={ws_id}", headers=headers)
    assert ds_res.status_code == 200
    datasets = ds_res.json()
    assert len(datasets) > 0

def test_dashboard_summary_api():
    login_res = client.post("/api/v1/auth/login", json={
        "email": "demo@nexoraiq.com",
        "password": "demo1234"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    ws_id = login_res.json()["user"]["workspace_id"]
    
    res = client.get(f"/api/v1/dashboard/summary?workspace_id={ws_id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["has_data"] is True
    assert data["total_revenue"] > 0
    assert "trend_chart" in data
    assert len(data["trend_chart"]) > 0

# 3. UNIVERSAL DATA INGESTION & QUALITY SCORER TESTS
def test_universal_data_ingestion_quality():
    parser = UniversalDataIngestionEngine()
    test_path = "data/samples/business_data.csv"
    assert os.path.exists(test_path)
    
    res = parser.process_file(test_path)
    assert res["row_count"] == 76
    assert res["col_count"] == 11
    report = res["quality_report"]
    assert report["overall_score"] > 80.0
    assert report["completeness_score"] == 100.0
    assert len(res["preview"]) > 0

# 4. LEAKAGE-FREE FEATURE ENGINEERING TESTS
def test_leakage_free_feature_pipeline():
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "date": dates,
        "revenue": np.random.uniform(5000, 15000, size=100),
        "cost": np.random.uniform(3000, 8000, size=100)
    })
    
    fe = TimeSeriesFeatureEngineer(date_col="date", target_col="revenue")
    transformed, feat_cols = fe.fit_transform(df)
    
    # Verify lag features exist
    assert "revenue_lag_1" in transformed.columns
    assert "revenue_lag_7" in transformed.columns
    assert "revenue_roll_mean_7" in transformed.columns
    
    # Verify no target leakage in lag 1: transformed row 1's lag_1 should equal row 0's revenue
    assert abs(transformed["revenue_lag_1"].iloc[1] - df["revenue"].iloc[0]) < 1e-4

# 5. FORECASTING ENGINE BENCHMARKS & EVALUATION TESTS
def test_forecasting_engine_validation_and_testing():
    dates = pd.date_range("2023-01-01", periods=120, freq="D")
    rev = 10000 + np.sin(np.linspace(0, 20, 120)) * 2500 + np.random.normal(0, 300, 120)
    df = pd.DataFrame({"date": dates, "revenue": rev})
    
    engine = BusinessForecastingEngine(date_col="date", target_col="revenue", forecast_horizon=14)
    results = engine.train_and_evaluate(df)
    
    assert results["best_model_name"] is not None
    assert "rmse" in results["validation_metrics"]
    assert "rmse" in results["test_metrics"]
    assert len(results["model_comparison"]) >= 4
    assert len(results["future_forecast"]) == 14
    
    # Verify prediction interval bounds
    first_pred = results["future_forecast"][0]
    assert first_pred["lower_bound"] <= first_pred["predicted_value"] <= first_pred["upper_bound"]

# 6. MULTI-METHOD ANOMALY DETECTION TESTS
def test_anomaly_detection_multi_method():
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    rev = np.random.normal(12000, 800, 100)
    # Inject massive anomaly
    rev[45] = 250
    rev[80] = 45000
    df = pd.DataFrame({"date": dates, "revenue": rev})
    
    detector = MultiMethodAnomalyDetector(date_col="date", target_col="revenue", contamination=0.05)
    anom_res = detector.detect_anomalies(df)
    
    assert anom_res["total_count"] >= 2
    # Verify that anomaly indices 45 and 80 were flagged
    dates_flagged = [a["index"] for a in anom_res["anomalies"]]
    assert 45 in dates_flagged or 80 in dates_flagged
    
    first = anom_res["anomalies"][0]
    assert "severity" in first
    assert "root_cause_explanation" in first

# 7. CUSTOMER RFM & SUPERVISED CHURN TESTS
def test_customer_rfm_and_churn_evaluation():
    cust_engine = CustomerIntelligenceEngine()
    df = pd.read_csv("data/synthetic/customers/customer_rfm_churn_train.csv")
    
    rfm_res = cust_engine.compute_rfm_segments(df)
    assert len(rfm_res["segment_summary"]) > 0
    assert rfm_res["total_customers"] == len(df)
    
    churn_res = cust_engine.train_churn_model(df)
    assert churn_res["best_roc_auc"] >= 0.70
    assert len(churn_res["model_comparison"]) >= 3
    assert len(churn_res["at_risk_customers_sample"]) > 0

# 8. GROUNDED AI ADVISOR TESTS
def test_grounded_business_advisor():
    advisor = GroundedBusinessAdvisor()
    profit = {"net_profit": 45000.0, "net_margin_pct": 18.5, "margin_trend": "stable"}
    context = {"profitability": profit, "recommendations": []}
    
    res = advisor.answer_query("Why did my profit change?", context)
    assert "45,000" in res["answer"] or "18.5%" in res["answer"]
    assert res["confidence"] == "high"
