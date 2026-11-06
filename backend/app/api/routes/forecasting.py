import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.all_models import Dataset, ForecastRecord, User
from backend.app.schemas.all_schemas import ForecastRunRequest
from backend.app.api.deps import get_current_user
from ml_engine.ingestion.universal_parser import UniversalDataIngestionEngine
from ml_engine.forecasting.engine import BusinessForecastingEngine

router = APIRouter(prefix="/forecasting", tags=["Forecasting"])
parser = UniversalDataIngestionEngine()

@router.post("/run")
def run_forecasting_pipeline(
    req: ForecastRunRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executes full chronological training, walk-forward validation, model selection, and forward projection."""
    ds = db.query(Dataset).filter(Dataset.id == req.dataset_id).first()
    if not ds or not os.path.exists(ds.file_path):
        raise HTTPException(status_code=404, detail="Dataset not found on filesystem.")
        
    df = parser.load_dataset(ds.file_path)
    
    # Auto-detect target column if requested target isn't present
    target_col = req.target_column
    if target_col not in df.columns:
        target_col = next((c for c in ["revenue", "sales_amount", "Sales Amount", "mrr", "sales"] if c in df.columns), None)
        if not target_col:
            num_cols = df.select_dtypes(include=["number"]).columns
            if len(num_cols) == 0:
                raise HTTPException(status_code=400, detail="No numeric target column available for time-series forecasting.")
            target_col = num_cols[0]

    date_col = next((c for c in ["date", "Date", "timestamp", "period"] if c in df.columns), None)
    if not date_col:
        # Create sequential date index if missing
        df["date"] = pd.date_range(start="2023-01-01", periods=len(df), freq="D")
        date_col = "date"
        
    engine = BusinessForecastingEngine(
        date_col=date_col,
        target_col=target_col,
        forecast_horizon=req.forecast_horizon or 30
    )
    
    try:
        results = engine.train_and_evaluate(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting engine failed: {str(e)}")
        
    # Persist forecast record
    record = ForecastRecord(
        workspace_id=ds.workspace_id,
        dataset_id=ds.id,
        target_column=target_col,
        best_model_name=results["best_model_name"],
        validation_metrics=results["validation_metrics"],
        test_metrics=results["test_metrics"],
        model_comparison=results["model_comparison"],
        future_forecast=results["future_forecast"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    results["record_id"] = record.id
    results["dataset_name"] = ds.name
    results["target_column"] = target_col
    return results

@router.get("/latest")
def get_latest_forecast(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves the most recent forecast run for the workspace, or auto-runs if none exist."""
    record = db.query(ForecastRecord).filter(
        ForecastRecord.workspace_id == workspace_id
    ).order_by(ForecastRecord.created_at.desc()).first()
    
    if record:
        return {
            "record_id": record.id,
            "best_model_name": record.best_model_name,
            "target_column": record.target_column,
            "validation_metrics": record.validation_metrics,
            "test_metrics": record.test_metrics,
            "model_comparison": record.model_comparison,
            "future_forecast": record.future_forecast
        }
        
    # Auto-run with first available dataset
    ds = db.query(Dataset).filter(Dataset.workspace_id == workspace_id).order_by(Dataset.created_at.desc()).first()
    if ds and os.path.exists(ds.file_path):
        return run_forecasting_pipeline(ForecastRunRequest(dataset_id=ds.id), current_user, db)
        
    return {"message": "No forecast runs available. Please upload a dataset and run forecasting."}

