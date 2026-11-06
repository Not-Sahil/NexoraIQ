import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.all_models import Dataset, BusinessRecommendationRecord, User
from backend.app.schemas.all_schemas import AdvisorQueryRequest
from backend.app.api.deps import get_current_user
from ml_engine.ingestion.universal_parser import UniversalDataIngestionEngine
from ml_engine.business_intelligence.profitability import ProfitabilityAnalyticsEngine
from ml_engine.business_intelligence.inventory import InventoryIntelligenceEngine
from ml_engine.business_intelligence.marketing import MarketingIntelligenceEngine
from ml_engine.business_intelligence.finance import FinancialStressIntelligenceEngine
from ml_engine.anomaly_detection.detector import MultiMethodAnomalyDetector
from ml_engine.customer_intelligence.rfm_churn import CustomerIntelligenceEngine
from ml_engine.business_intelligence.advisor import GroundedBusinessAdvisor

router = APIRouter(prefix="/advisor", tags=["AI Business Advisor"])
parser = UniversalDataIngestionEngine()
advisor = GroundedBusinessAdvisor()
profit_engine = ProfitabilityAnalyticsEngine()
inv_engine = InventoryIntelligenceEngine()
mkt_engine = MarketingIntelligenceEngine()
fin_engine = FinancialStressIntelligenceEngine()
cust_engine = CustomerIntelligenceEngine()

def _gather_context(workspace_id: Optional[str], dataset_id: Optional[str], db: Session):
    if dataset_id:
        ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    elif workspace_id:
        ds = db.query(Dataset).filter(Dataset.workspace_id == workspace_id).order_by(Dataset.created_at.desc()).first()
    else:
        ds = db.query(Dataset).order_by(Dataset.created_at.desc()).first()
        
    if not ds or not os.path.exists(ds.file_path):
        return {}, {}, [], {}, {}, {}, {}
        
    df = parser.load_dataset(ds.file_path)
    
    # Run analytical engines
    profitability = profit_engine.analyze_profitability(df)
    inventory = inv_engine.analyze_inventory(df)
    marketing = mkt_engine.analyze_marketing(df)
    finance = fin_engine.analyze_financial_stress(df)
    
    # Target col for anomaly
    target_col = next((c for c in ["revenue", "sales_amount", "mrr"] if c in df.columns), df.select_dtypes(include=["number"]).columns[0])
    date_col = next((c for c in ["date", "Date", "timestamp"] if c in df.columns), "date")
    if date_col not in df.columns:
        df[date_col] = pd.date_range(start="2023-01-01", periods=len(df), freq="D")
        
    detector = MultiMethodAnomalyDetector(date_col=date_col, target_col=target_col)
    anomalies = detector.detect_anomalies(df).get("anomalies", [])
    
    churn_data = cust_engine.train_churn_model(df)
    
    return profitability, inventory, anomalies, churn_data, marketing, finance, ds

@router.get("/recommendations")
def get_recommendations(
    workspace_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates prioritized, evidence-backed business recommendations."""
    profit, inv, anomalies, churn, mkt, fin, ds = _gather_context(workspace_id, dataset_id, db)
    if not profit:
        return {"recommendations": [], "message": "No active dataset found for generating recommendations."}
        
    recs = advisor.generate_recommendations(
        metrics=profit,
        profitability=profit,
        anomalies=anomalies,
        churn_data=churn,
        inventory_data=inv,
        marketing_data=mkt,
        financial_stress=fin
    )
    return {"recommendations": recs, "total_count": len(recs), "dataset_name": getattr(ds, "name", "Active Dataset")}

@router.post("/chat")
def chat_with_advisor(
    req: AdvisorQueryRequest,
    workspace_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Processes natural language business questions using tool-retrieved actual business metrics."""
    profit, inv, anomalies, churn, mkt, fin, ds = _gather_context(workspace_id, req.dataset_id, db)
    
    context = {
        "profitability": profit,
        "inventory": inv,
        "anomalies": {"anomalies": anomalies},
        "churn": churn,
        "marketing": mkt,
        "finance": fin,
        "recommendations": advisor.generate_recommendations(profit, profit, anomalies, churn, inv, mkt, fin)
    }
    
    response = advisor.answer_query(req.query, context)
    return response

