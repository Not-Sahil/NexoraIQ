import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.all_models import Dataset, User
from backend.app.api.deps import get_current_user
from ml_engine.ingestion.universal_parser import UniversalDataIngestionEngine
from ml_engine.feature_engineering.pipeline import TimeSeriesFeatureEngineer
from ml_engine.explainability.explainer import BusinessExplainabilityEngine
from sklearn.ensemble import RandomForestRegressor

router = APIRouter(prefix="/explainability", tags=["Explainable AI"])
parser = UniversalDataIngestionEngine()
explainer = BusinessExplainabilityEngine()

@router.get("/attribution")
def get_prediction_attribution(
    workspace_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Computes SHAP values and directional feature contributions for current business predictions."""
    if dataset_id:
        ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    elif workspace_id:
        ds = db.query(Dataset).filter(Dataset.workspace_id == workspace_id).order_by(Dataset.created_at.desc()).first()
    else:
        ds = db.query(Dataset).order_by(Dataset.created_at.desc()).first()
        
    if not ds or not os.path.exists(ds.file_path):
        raise HTTPException(status_code=404, detail="Dataset not found for explainability analysis.")
        
    df = parser.load_dataset(ds.file_path)
    
    target_col = next((c for c in ["revenue", "sales_amount", "Sales Amount", "mrr"] if c in df.columns), None)
    if not target_col:
        target_col = df.select_dtypes(include=["number"]).columns[0]
        
    date_col = next((c for c in ["date", "Date", "timestamp"] if c in df.columns), "date")
    if date_col not in df.columns:
        df[date_col] = pd.date_range(start="2023-01-01", periods=len(df), freq="D")

    # Feature engineer & fit a reference random forest model for SHAP interpretation
    fe = TimeSeriesFeatureEngineer(date_col=date_col, target_col=target_col)
    transformed_df, feature_cols = fe.fit_transform(df)
    
    X = transformed_df[feature_cols].fillna(0)
    y = transformed_df[target_col].values
    
    rf = RandomForestRegressor(n_estimators=60, max_depth=6, random_state=42)
    rf.fit(X, y)
    
    res = explainer.explain_model_predictions(rf, transformed_df, feature_cols)
    res["target_column"] = target_col
    res["dataset_name"] = ds.name
    return res

