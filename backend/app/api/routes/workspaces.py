from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.all_models import Workspace, OrganizationMember, User
from backend.app.schemas.all_schemas import WorkspaceCreate, WorkspaceOut
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.get("/", response_model=List[WorkspaceOut])
def list_workspaces(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all business workspaces accessible to the user's organization."""
    membership = db.query(OrganizationMember).filter(OrganizationMember.user_id == current_user.id).first()
    if not membership:
        return []
    workspaces = db.query(Workspace).filter(Workspace.organization_id == membership.organization_id).all()
    return workspaces

@router.post("/", response_model=WorkspaceOut)
def create_workspace(ws_in: WorkspaceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Creates a new isolated business workspace within the user's organization."""
    membership = db.query(OrganizationMember).filter(OrganizationMember.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="User does not belong to an active organization.")
        
    ws = Workspace(
        organization_id=membership.organization_id,
        name=ws_in.name,
        description=ws_in.description,
        domain_type=ws_in.domain_type
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws

