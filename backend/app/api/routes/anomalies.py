import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.all_models import Dataset, AnomalyRecord, User
from backend.app.api.deps import get_current_user
from ml_engine.ingestion.universal_parser import UniversalDataIngestionEngine
from ml_engine.anomaly_detection.detector import MultiMethodAnomalyDetector

router = APIRouter(prefix="/anomalies", tags=["Anomaly Detection"])
parser = UniversalDataIngestionEngine()

@router.get("/")
def get_anomalies(
    workspace_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    contamination: float = Query(0.05, ge=0.01, le=0.25),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executes multi-method anomaly detection (Isolation Forest, LOF, Rolling Z-score) and returns flagged events."""
    if dataset_id:
        ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    elif workspace_id:
        ds = db.query(Dataset).filter(Dataset.workspace_id == workspace_id).order_by(Dataset.created_at.desc()).first()
    else:
        ds = db.query(Dataset).order_by(Dataset.created_at.desc()).first()
        
    if not ds or not os.path.exists(ds.file_path):
        raise HTTPException(status_code=404, detail="Dataset not found for anomaly detection.")
        
    df = parser.load_dataset(ds.file_path)
    
    # Auto-detect target column
    target_col = next((c for c in ["revenue", "sales_amount", "Sales Amount", "mrr", "sales"] if c in df.columns), None)
    if not target_col:
        num_cols = df.select_dtypes(include=["number"]).columns
        if len(num_cols) == 0:
            raise HTTPException(status_code=400, detail="No numeric columns found for anomaly detection.")
        target_col = num_cols[0]

    date_col = next((c for c in ["date", "Date", "timestamp", "period"] if c in df.columns), "date")
    if date_col not in df.columns:
        df[date_col] = pd.date_range(start="2023-01-01", periods=len(df), freq="D")

    detector = MultiMethodAnomalyDetector(
        date_col=date_col,
        target_col=target_col,
        contamination=contamination
    )
    
    res = detector.detect_anomalies(df)
    res["dataset_name"] = ds.name
    res["target_column"] = target_col
    return res

