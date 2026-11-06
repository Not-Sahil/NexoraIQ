import os
import shutil
import glob
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.all_models import Dataset, Workspace, OrganizationMember, User
from backend.app.schemas.all_schemas import DatasetOut, ColumnMappingUpdate
from backend.app.api.deps import get_current_user
from ml_engine.ingestion.universal_parser import UniversalDataIngestionEngine

router = APIRouter(prefix="/datasets", tags=["Datasets"])
parser = UniversalDataIngestionEngine()

@router.get("/", response_model=List[DatasetOut])
def list_datasets(
    workspace_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all datasets belonging to the active workspace."""
    query = db.query(Dataset)
    if workspace_id:
        query = query.filter(Dataset.workspace_id == workspace_id)
    return query.order_by(Dataset.created_at.desc()).all()

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    workspace_id: str = Form(...),
    name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploads a CSV or Excel dataset, executes schema inference and quality scoring."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found.")
        
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = file.filename or "dataset.csv"
    save_path = os.path.join(settings.UPLOAD_DIR, f"{ws.id[:8]}_{filename}")
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(save_path)
    
    try:
        profile_res = parser.process_file(save_path)
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(status_code=400, detail=f"Failed to process dataset: {str(e)}")
        
    ds = Dataset(
        workspace_id=ws.id,
        organization_id=ws.organization_id,
        name=name or filename,
        filename=filename,
        file_path=save_path,
        file_size_bytes=file_size,
        row_count=profile_res["row_count"],
        col_count=profile_res["col_count"],
        status="ready",
        quality_score=profile_res["quality_report"]["overall_score"],
        quality_report=profile_res["quality_report"],
        columns_meta=profile_res["columns"]
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)
    
    return {
        "dataset": ds,
        "quality_report": profile_res["quality_report"],
        "columns": profile_res["columns"],
        "preview": profile_res["preview"]
    }

@router.get("/{dataset_id}")
def get_dataset_details(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves full metadata, data quality report, and interactive data preview for a dataset."""
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found.")
        
    preview = []
    if os.path.exists(ds.file_path):
        try:
            df = parser.load_dataset(ds.file_path)
            preview = df.head(20).replace({float('nan'): None}).to_dict(orient="records")
        except Exception:
            pass
            
    return {
        "id": ds.id,
        "name": ds.name,
        "filename": ds.filename,
        "row_count": ds.row_count,
        "col_count": ds.col_count,
        "quality_score": ds.quality_score,
        "quality_report": ds.quality_report,
        "columns": ds.columns_meta,
        "preview": preview,
        "created_at": ds.created_at
    }

@router.post("/{dataset_id}/mappings")
def update_column_mappings(
    dataset_id: str,
    mapping_update: ColumnMappingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Allows manual user override of inferred column semantic roles."""
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found.")
        
    cols = list(ds.columns_meta) if ds.columns_meta else []
    for col in cols:
        name = col.get("column_name")
        if name in mapping_update.mappings:
            col["mapped_semantic_role"] = mapping_update.mappings[name]
            
    ds.columns_meta = cols
    db.commit()
    return {"message": "Column mappings updated successfully.", "columns": ds.columns_meta}

@router.post("/seed-demo-datasets")
def seed_demo_datasets(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seeds real benchmark and synthetic datasets into the workspace for instant exploration."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found.")
        
    candidates = [
        ("data/samples/realistic_retail_business_data.csv", "Realistic Retail Business Metrics (Benchmark)"),
        ("data/samples/realistic_saas_business_data.csv", "Realistic SaaS Business Metrics (Benchmark)"),
        ("data/samples/business_data.csv", "General Weekly Business Metrics (Benchmark)"),
        ("data/synthetic/retail_ecommerce/retail_ecommerce_full.csv", "E-Commerce Multi-Channel Sales (Synthetic Ground-Truth)"),
        ("data/synthetic/customers/customer_rfm_churn_full.csv", "Customer RFM & Churn Profile (Synthetic Ground-Truth)")
    ]
    
    seeded = []
    for path, label in candidates:
        if os.path.exists(path):
            existing = db.query(Dataset).filter(Dataset.workspace_id == ws.id, Dataset.name == label).first()
            if not existing:
                try:
                    res = parser.process_file(path)
                    ds = Dataset(
                        workspace_id=ws.id,
                        organization_id=ws.organization_id,
                        name=label,
                        filename=os.path.basename(path),
                        file_path=os.path.abspath(path),
                        file_size_bytes=os.path.getsize(path),
                        row_count=res["row_count"],
                        col_count=res["col_count"],
                        status="ready",
                        quality_score=res["quality_report"]["overall_score"],
                        quality_report=res["quality_report"],
                        columns_meta=res["columns"]
                    )
                    db.add(ds)
                    seeded.append(label)
                except Exception as e:
                    print(f"Error seeding {path}: {e}")
                    
    db.commit()
    return {"message": f"Successfully seeded {len(seeded)} benchmark datasets.", "seeded": seeded}

