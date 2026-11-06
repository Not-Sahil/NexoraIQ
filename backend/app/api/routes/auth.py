from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.models.all_models import User, Organization, OrganizationMember, Workspace
from backend.app.schemas.all_schemas import UserRegister, UserLogin, TokenResponse, UserOut
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Registers a new user, provisions an organization, and initializes a default workspace."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
        
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(user)
    db.flush()
    
    # Create Organization
    slug = user_in.organization_name.lower().replace(" ", "-").replace("_", "-")
    org = Organization(
        name=user_in.organization_name,
        slug=f"{slug}-{user.id[:8]}",
        billing_plan="enterprise"
    )
    db.add(org)
    db.flush()
    
    # Assign Owner membership
    member = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role="owner"
    )
    db.add(member)
    db.flush()
    
    # Create default workspace
    ws = Workspace(
        organization_id=org.id,
        name="Main Enterprise Workspace",
        description="Primary business analytics and forecasting workspace",
        domain_type="retail"
    )
    db.add(ws)
    db.commit()
    db.refresh(user)
    
    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "organization_id": org.id,
            "workspace_id": ws.id,
            "role": "owner"
        }
    }

@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user and returns JWT access token along with active workspace context."""
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
        
    membership = db.query(OrganizationMember).filter(OrganizationMember.user_id == user.id).first()
    org_id = membership.organization_id if membership else None
    role = membership.role if membership else "analyst"
    
    ws = db.query(Workspace).filter(Workspace.organization_id == org_id).first() if org_id else None
    ws_id = ws.id if ws else None
    
    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "organization_id": org_id,
            "workspace_id": ws_id,
            "role": role
        }
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns the authenticated user profile with organization and workspace links."""
    membership = db.query(OrganizationMember).filter(OrganizationMember.user_id == current_user.id).first()
    org_id = membership.organization_id if membership else None
    role = membership.role if membership else "analyst"
    
    ws = db.query(Workspace).filter(Workspace.organization_id == org_id).first() if org_id else None
    ws_id = ws.id if ws else None
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "organization_id": org_id,
        "workspace_id": ws_id,
        "role": role
    }

