from typing import Dict, Any, List, Optional
from pydantic import BaseModel, EmailStr

# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: Optional[str] = "Acme Global Enterprise"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    role: Optional[str] = "owner"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# Workspace & Org Schemas
class OrganizationOut(BaseModel):
    id: str
    name: str
    slug: str
    industry: str
    billing_plan: str

class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    domain_type: Optional[str] = "retail"

class WorkspaceOut(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    domain_type: str

# Dataset Schemas
class ColumnMappingUpdate(BaseModel):
    mappings: Dict[str, str]  # col_name -> semantic_role

class DatasetOut(BaseModel):
    id: str
    workspace_id: str
    name: str
    filename: str
    file_size_bytes: int
    row_count: int
    col_count: int
    quality_score: float
    status: str

# Analytics & Forecast Schemas
class ForecastRunRequest(BaseModel):
    dataset_id: str
    target_column: Optional[str] = "revenue"
    forecast_horizon: Optional[int] = 30

class AdvisorQueryRequest(BaseModel):
    query: str
    dataset_id: Optional[str] = None

