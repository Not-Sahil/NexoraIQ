import os
from typing import List, Union
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NexoraIQ AI Business Intelligence"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "nexoraiq-super-secret-jwt-key-for-development-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database: Dual mode (Supabase PostgreSQL / local SQLite fallback)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./nexoraiq.db")
    
    # Supabase Cloud configuration (optional if running in local standalone mode)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # File storage paths
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/uploads")
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", "data/reports")
    SAMPLES_DIR: str = os.getenv("SAMPLES_DIR", "data/samples")
    SYNTHETIC_DIR: str = os.getenv("SYNTHETIC_DIR", "data/synthetic")
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

