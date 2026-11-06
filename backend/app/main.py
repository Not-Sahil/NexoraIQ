import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.core.security import get_password_hash
from backend.app.models.all_models import User, Organization, OrganizationMember, Workspace, Dataset
from ml_engine.ingestion.universal_parser import UniversalDataIngestionEngine

# Import Routers
from backend.app.api.routes import (
    auth, workspaces, datasets, dashboard,
    analytics, forecasting, anomalies,
    customers, explainability, advisor, reports
)

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

def seed_initial_demo_environment():
    """Seeds a ready-to-explore demo organization, user, workspace, and datasets."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@nexoraiq.com").first()
        if not user:
            # 1. Demo User
            user = User(
                email="demo@nexoraiq.com",
                hashed_password=get_password_hash("demo1234"),
                full_name="Alex Vance (Senior Business Analyst)"
            )
            db.add(user)
            db.flush()
            
            # 2. Demo Organization
            org = Organization(
                name="Nexora Enterprise Global",
                slug="nexora-enterprise-global",
                industry="Omnichannel Retail & SaaS",
                billing_plan="enterprise"
            )
            db.add(org)
            db.flush()
            
            # 3. Membership
            member = OrganizationMember(
                organization_id=org.id,
                user_id=user.id,
                role="owner"
            )
            db.add(member)
            db.flush()
            
            # 4. Main Workspace
            ws = Workspace(
                organization_id=org.id,
                name="Retail & E-Commerce Operations",
                description="Primary live operations and predictive forecasting workspace",
                domain_type="retail"
            )
            db.add(ws)
            db.flush()
            
            # 5. Seed Benchmark Datasets
            parser = UniversalDataIngestionEngine()
            seed_files = [
                ("data/samples/realistic_retail_business_data.csv", "Realistic Retail Business Metrics (Benchmark)"),
                ("data/samples/realistic_saas_business_data.csv", "Realistic SaaS Business Metrics (Benchmark)"),
                ("data/samples/business_data.csv", "Weekly General Business Operations (Benchmark)"),
                ("data/synthetic/retail_ecommerce/retail_ecommerce_full.csv", "E-Commerce Multi-Channel Sales (Synthetic Ground-Truth)"),
                ("data/synthetic/customers/customer_rfm_churn_full.csv", "Customer RFM & Churn Profile (Synthetic Ground-Truth)")
            ]
            
            for path, name in seed_files:
                if os.path.exists(path):
                    try:
                        res = parser.process_file(path)
                        ds = Dataset(
                            workspace_id=ws.id,
                            organization_id=org.id,
                            name=name,
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
                    except Exception as err:
                        print(f"Error seeding demo dataset {path}: {err}")
                        
            db.commit()
            print("NexoraIQ Demo Environment successfully initialized!")
    finally:
        db.close()

seed_initial_demo_environment()

# Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Enterprise AI-Powered Business Intelligence, Predictive Analytics & Decision Support Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
api_v1 = settings.API_V1_STR
app.include_router(auth.router, prefix=api_v1)
app.include_router(workspaces.router, prefix=api_v1)
app.include_router(datasets.router, prefix=api_v1)
app.include_router(dashboard.router, prefix=api_v1)
app.include_router(analytics.router, prefix=api_v1)
app.include_router(forecasting.router, prefix=api_v1)
app.include_router(anomalies.router, prefix=api_v1)
app.include_router(customers.router, prefix=api_v1)
app.include_router(explainability.router, prefix=api_v1)
app.include_router(advisor.router, prefix=api_v1)
app.include_router(reports.router, prefix=api_v1)

@app.get("/health")
def health_check():
    """Health check endpoint for Docker and uptime probes."""
    return {
        "status": "healthy",
        "platform": "NexoraIQ",
        "version": "1.0.0",
        "ml_engine": "online"
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to NexoraIQ AI Decision Intelligence Platform API",
        "documentation": f"{settings.API_V1_STR}/docs"
    }

