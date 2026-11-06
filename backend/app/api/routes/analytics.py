import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.all_models import Dataset, User
from backend.app.api.deps import get_current_user
from ml_engine.ingestion.universal_parser import UniversalDataIngestionEngine
from ml_engine.business_intelligence.profitability import ProfitabilityAnalyticsEngine
from ml_engine.business_intelligence.inventory import InventoryIntelligenceEngine
from ml_engine.business_intelligence.marketing import MarketingIntelligenceEngine
from ml_engine.business_intelligence.finance import FinancialStressIntelligenceEngine

router = APIRouter(prefix="/analytics", tags=["Analytics"])
parser = UniversalDataIngestionEngine()
profit_engine = ProfitabilityAnalyticsEngine()
inv_engine = InventoryIntelligenceEngine()
mkt_engine = MarketingIntelligenceEngine()
fin_engine = FinancialStressIntelligenceEngine()

def _get_dataset_df(dataset_id: Optional[str], workspace_id: Optional[str], db: Session):
    if dataset_id:
        ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    elif workspace_id:
        ds = db.query(Dataset).filter(Dataset.workspace_id == workspace_id).order_by(Dataset.created_at.desc()).first()
    else:
        ds = db.query(Dataset).order_by(Dataset.created_at.desc()).first()
        
    if not ds or not os.path.exists(ds.file_path):
        raise HTTPException(status_code=404, detail="No active dataset available for analytics.")
    return parser.load_dataset(ds.file_path), ds

@router.get("/profitability")
def get_profitability_analytics(
    workspace_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns detailed unit economics, contribution margins, break-even, and dimensional profitability."""
    df, ds = _get_dataset_df(dataset_id, workspace_id, db)
    res = profit_engine.analyze_profitability(df)
    res["dataset_name"] = ds.name
    return res

@router.get("/inventory")
def get_inventory_analytics(
    workspace_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns inventory turnover, Days Inventory Outstanding (DIO), and ABC classification."""
    df, ds = _get_dataset_df(dataset_id, workspace_id, db)
    res = inv_engine.analyze_inventory(df)
    res["dataset_name"] = ds.name
    return res

@router.get("/marketing")
def get_marketing_analytics(
    workspace_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns channel ROAS, CAC, conversion efficiency, and budget recommendations."""
    df, ds = _get_dataset_df(dataset_id, workspace_id, db)
    res = mkt_engine.analyze_marketing(df)
    res["dataset_name"] = ds.name
    return res

@router.get("/finance")
def get_financial_risk_analytics(
    workspace_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns cash flow indicators, monthly burn rate, runway months, and liquidity stress tier."""
    df, ds = _get_dataset_df(dataset_id, workspace_id, db)
    res = fin_engine.analyze_financial_stress(df)
    res["dataset_name"] = ds.name
    return res

