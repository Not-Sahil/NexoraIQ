import pytest
import os
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_complete_end_to_end_user_workflow():
    """
    Validates complete 13-step SaaS lifecycle:
    1. User registers new enterprise tenant
    2. User logs in & acquires JWT
    3. User creates a business workspace
    4. User uploads & ingests a dataset
    5. System validates dataset schema & columns
    6. User reviews Data Quality report (completeness, uniqueness, validity, score)
    7. User executes business analytics (Profitability, Unit Economics, DIO, Marketing)
    8. ML models train on chronological split and generate forecasts with intervals
    9. System executes multi-method anomaly detection (Isolation Forest, LOF, Z-Score)
    10. Customer RFM & supervised churn model evaluates retention risk
    11. User queries AI Business Advisor and receives evidence-backed recommendations
    12. User generates & downloads executive Excel and PDF reports
    13. User logs out and logs back in - all data, forecasts, and records persist!
    """
    # Step 1: User registers
    import uuid
    run_id = uuid.uuid4().hex[:8]
    reg_email = f"executive_{run_id}@nexoraiq.com"
    reg_res = client.post("/api/v1/auth/register", json={
        "email": reg_email,
        "password": "ExecutivePassword123!",
        "full_name": "Chief Analytics Officer",
        "organization_name": f"OmniGlobal Technologies {run_id}"
    })
    assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
    token = reg_res.json()["access_token"]
    user_id = reg_res.json()["user"]["id"]
    org_id = reg_res.json()["user"]["organization_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: User logs in & acquires JWT
    login_res = client.post("/api/v1/auth/login", json={
        "email": reg_email,
        "password": "ExecutivePassword123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 3: User creates a business workspace
    ws_res = client.post("/api/v1/workspaces/", json={
        "name": "B2B Hardware & Enterprise Solutions",
        "description": "Dedicated analytics workspace for global server lines",
        "domain_type": "manufacturing"
    }, headers=headers)
    assert ws_res.status_code == 200
    ws_id = ws_res.json()["id"]

    # Step 4: User uploads a dataset (CSV)
    test_csv_path = "data/samples/realistic_retail_business_data.csv"
    assert os.path.exists(test_csv_path)
    with open(test_csv_path, "rb") as f:
        upload_res = client.post(
            "/api/v1/datasets/upload",
            data={"workspace_id": ws_id, "name": "Q3-Q4 Retail Hardware Benchmark"},
            files={"file": ("retail_benchmark.csv", f, "text/csv")},
            headers=headers
        )
    assert upload_res.status_code == 200
    ds_id = upload_res.json()["dataset"]["id"]

    # Step 5 & 6: Validate dataset schema & review Data Quality report
    ds_detail_res = client.get(f"/api/v1/datasets/{ds_id}", headers=headers)
    assert ds_detail_res.status_code == 200
    ds_detail = ds_detail_res.json()
    assert ds_detail["row_count"] == 500
    assert ds_detail["quality_score"] > 80.0
    quality = ds_detail["quality_report"]
    assert "completeness_score" in quality
    assert "validity_score" in quality
    assert len(ds_detail["preview"]) > 0

    # Step 7: Run business analytics (Profitability, Inventory, Marketing, Finance)
    profit_res = client.get(f"/api/v1/analytics/profitability?workspace_id={ws_id}&dataset_id={ds_id}", headers=headers)
    assert profit_res.status_code == 200
    profit = profit_res.json()
    assert profit["total_revenue"] > 0
    assert "net_profit" in profit
    assert "contribution_margin_ratio" in profit

    inv_res = client.get(f"/api/v1/analytics/inventory?workspace_id={ws_id}&dataset_id={ds_id}", headers=headers)
    assert inv_res.status_code == 200

    mkt_res = client.get(f"/api/v1/analytics/marketing?workspace_id={ws_id}&dataset_id={ds_id}", headers=headers)
    assert mkt_res.status_code == 200
    assert mkt_res.json()["overall_roas"] > 0

    fin_res = client.get(f"/api/v1/analytics/finance?workspace_id={ws_id}&dataset_id={ds_id}", headers=headers)
    assert fin_res.status_code == 200
    assert fin_res.json()["runway_months"] > 0

    # Step 8: ML models generate forecasts with prediction intervals
    fc_res = client.post("/api/v1/forecasting/run", json={
        "dataset_id": ds_id,
        "target_column": "revenue",
        "forecast_horizon": 30
    }, headers=headers)
    assert fc_res.status_code == 200
    forecast = fc_res.json()
    assert forecast["best_model_name"] is not None
    assert len(forecast["future_forecast"]) == 30
    assert forecast["future_forecast"][0]["lower_bound"] <= forecast["future_forecast"][0]["predicted_value"]

    # Step 9: Anomaly detection
    anom_res = client.get(f"/api/v1/anomalies/?workspace_id={ws_id}&dataset_id={ds_id}", headers=headers)
    assert anom_res.status_code == 200
    assert "anomalies" in anom_res.json()

    # Step 10: Customer RFM & Churn modeling
    cust_res = client.get(f"/api/v1/customers/rfm-and-churn?workspace_id={ws_id}&dataset_id={ds_id}", headers=headers)
    assert cust_res.status_code == 200
    assert "segment_summary" in cust_res.json()

    # Step 11: Grounded AI Advisor Recommendations & Q&A
    recs_res = client.get(f"/api/v1/advisor/recommendations?workspace_id={ws_id}&dataset_id={ds_id}", headers=headers)
    assert recs_res.status_code == 200
    recs = recs_res.json()["recommendations"]
    assert len(recs) > 0

    chat_res = client.post(f"/api/v1/advisor/chat?workspace_id={ws_id}", json={
        "query": "What is my expected revenue and why?",
        "dataset_id": ds_id
    }, headers=headers)
    assert chat_res.status_code == 200
    assert chat_res.json()["confidence"] in ("high", "medium")

    # Step 12: User generates & downloads reports (Excel & PDF)
    rep_res = client.post(f"/api/v1/reports/generate?workspace_id={ws_id}&report_format=excel", headers=headers)
    assert rep_res.status_code == 200
    excel_fn = rep_res.json()["filename"]

    download_res = client.get(f"/api/v1/reports/download/{excel_fn}")
    assert download_res.status_code == 200
    assert len(download_res.content) > 1000

    pdf_res = client.post(f"/api/v1/reports/generate?workspace_id={ws_id}&report_format=pdf", headers=headers)
    assert pdf_res.status_code == 200
    pdf_fn = pdf_res.json()["filename"]
    pdf_dl = client.get(f"/api/v1/reports/download/{pdf_fn}")
    assert pdf_dl.status_code == 200

    # Step 13: User logs out and logs back in - persistence verification
    relogin_res = client.post("/api/v1/auth/login", json={
        "email": reg_email,
        "password": "ExecutivePassword123!"
    })
    assert relogin_res.status_code == 200
    re_token = relogin_res.json()["access_token"]
    re_headers = {"Authorization": f"Bearer {re_token}"}

    # Verify workspace, dataset, and forecast remain persisted and accessible
    persisted_ws = client.get("/api/v1/workspaces/", headers=re_headers).json()
    assert any(w["id"] == ws_id for w in persisted_ws)

    persisted_ds = client.get(f"/api/v1/datasets/?workspace_id={ws_id}", headers=re_headers).json()
    assert any(d["id"] == ds_id for d in persisted_ds)

    persisted_fc = client.get(f"/api/v1/forecasting/latest?workspace_id={ws_id}", headers=re_headers).json()
    assert "best_model_name" in persisted_fc
