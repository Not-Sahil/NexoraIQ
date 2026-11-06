import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.all_models import Dataset, Workspace, ForecastRecord, User
from backend.app.api.deps import get_current_user
from ml_engine.ingestion.universal_parser import UniversalDataIngestionEngine
from ml_engine.business_intelligence.profitability import ProfitabilityAnalyticsEngine
from ml_engine.anomaly_detection.detector import MultiMethodAnomalyDetector
from ml_engine.business_intelligence.advisor import GroundedBusinessAdvisor
from ml_engine.business_intelligence.reports import BusinessReportGenerator

router = APIRouter(prefix="/reports", tags=["Reports"])
parser = UniversalDataIngestionEngine()
profit_engine = ProfitabilityAnalyticsEngine()
advisor = GroundedBusinessAdvisor()
report_gen = BusinessReportGenerator(output_dir=settings.REPORTS_DIR)

@router.post("/generate")
def generate_report(
    workspace_id: str,
    report_format: str = Query("excel", pattern="^(excel|pdf)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates an executive analytical report (Excel multi-tab or ReportLab PDF)."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found.")
        
    ds = db.query(Dataset).filter(Dataset.workspace_id == ws.id).order_by(Dataset.created_at.desc()).first()
    if not ds or not os.path.exists(ds.file_path):
        raise HTTPException(status_code=400, detail="Cannot generate report: No active dataset found in workspace.")
        
    df = parser.load_dataset(ds.file_path)
    profit = profit_engine.analyze_profitability(df)
    
    # Anomaly
    target_col = next((c for c in ["revenue", "sales_amount", "mrr"] if c in df.columns), df.select_dtypes(include=["number"]).columns[0])
    date_col = next((c for c in ["date", "Date", "timestamp"] if c in df.columns), "date")
    if date_col not in df.columns:
        df[date_col] = pd.date_range(start="2023-01-01", periods=len(df), freq="D")
    detector = MultiMethodAnomalyDetector(date_col=date_col, target_col=target_col)
    anomalies_res = detector.detect_anomalies(df)
    anomalies = anomalies_res.get("anomalies", [])
    
    # Recommendations
    recs = advisor.generate_recommendations(profit, profit, anomalies, {}, {}, {}, {})
    
    # Forecasts
    fc_record = db.query(ForecastRecord).filter(ForecastRecord.workspace_id == ws.id).order_by(ForecastRecord.created_at.desc()).first()
    forecast_list = fc_record.future_forecast if fc_record else []
    
    if report_format == "excel":
        file_path = report_gen.generate_excel_report(
            workspace_name=ws.name,
            kpis=profit,
            profitability=profit,
            forecast_data=forecast_list,
            anomalies_data=anomalies,
            recommendations=recs
        )
    else:
        fc_meta = {
            "best_model_name": fc_record.best_model_name if fc_record else "Random Forest Regressor",
            "val_mape": fc_record.validation_metrics.get("mape", 5.0) if fc_record else 5.0
        }
        file_path = report_gen.generate_pdf_summary(
            workspace_name=ws.name,
            profitability=profit,
            forecast_metrics=fc_meta,
            anomalies=anomalies,
            recommendations=recs
        )
        
    filename = os.path.basename(file_path)
    return {
        "message": f"Successfully generated {report_format.upper()} report.",
        "filename": filename,
        "download_url": f"/api/v1/reports/download/{filename}"
    }

@router.get("/download/{filename}")
def download_report(filename: str):
    """Downloads a generated report file."""
    file_path = os.path.join(settings.REPORTS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found.")
        
    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if filename.endswith(".xlsx") else "application/pdf"
    return FileResponse(file_path, filename=filename, media_type=media_type)
