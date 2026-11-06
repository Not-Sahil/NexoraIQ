import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.all_models import Dataset, User
from backend.app.api.deps import get_current_user
from ml_engine.ingestion.universal_parser import UniversalDataIngestionEngine
from ml_engine.customer_intelligence.rfm_churn import CustomerIntelligenceEngine

router = APIRouter(prefix="/customers", tags=["Customer Intelligence"])
parser = UniversalDataIngestionEngine()
cust_engine = CustomerIntelligenceEngine()

@router.get("/rfm-and-churn")
def get_customer_intelligence(
    workspace_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Computes RFM segmentation and evaluates supervised customer churn prediction models."""
    if dataset_id:
        ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    elif workspace_id:
        # Check if customer-specific synthetic dataset is loaded, otherwise use workspace dataset
        ds = db.query(Dataset).filter(
            Dataset.workspace_id == workspace_id,
            Dataset.name.like("%Customer%")
        ).first()
        if not ds:
            ds = db.query(Dataset).filter(Dataset.workspace_id == workspace_id).order_by(Dataset.created_at.desc()).first()
    else:
        ds = db.query(Dataset).order_by(Dataset.created_at.desc()).first()
        
    # If no customer dataset in workspace, fallback to the pre-generated synthetic customer churn dataset
    file_path = ds.file_path if (ds and os.path.exists(ds.file_path)) else "data/synthetic/customers/customer_rfm_churn_full.csv"
    if not os.path.exists(file_path):
        file_path = "data/samples/realistic_retail_business_data.csv"
        
    df = parser.load_dataset(file_path)
    
    rfm_res = cust_engine.compute_rfm_segments(df)
    churn_res = cust_engine.train_churn_model(df)
    
    return {
        "dataset_name": ds.name if ds else "Customer Benchmark Matrix",
        "total_customers": rfm_res["total_customers"],
        "segment_summary": rfm_res["segment_summary"],
        "customer_sample": rfm_res["customer_records"][:15],
        "churn_evaluation": {
            "best_model_name": churn_res["best_model_name"],
            "best_roc_auc": churn_res["best_roc_auc"],
            "model_comparison": churn_res["model_comparison"],
            "feature_importances": churn_res["feature_importances"]
        },
        "at_risk_customers": churn_res["at_risk_customers_sample"]
    }

