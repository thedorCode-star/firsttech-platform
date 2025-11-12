"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Project
    PROJECT_NAME: str = "FinTech Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/fintech_db"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_SESSION_TTL: int = 3600  # 1 hour
    
    # Encryption
    ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY")  # 32-byte key for AES-256
    USE_ENCRYPTION: bool = True
    
    # MFA
    MFA_ISSUER_NAME: str = "FinTech Platform"
    MFA_REQUIRED_FOR_ADMIN: bool = True
    
    # POPIA Compliance
    DATA_RETENTION_DAYS: int = 2555  # 7 years (financial records)
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    ENABLE_AUDIT_LOGGING: bool = True
    ENABLE_DATA_MINIMIZATION: bool = True
    
    # Cloud Provider (for accountability)
    CLOUD_PROVIDER: str = os.getenv("CLOUD_PROVIDER", "aws")  # aws, azure, gcp
    REGION: str = os.getenv("REGION", "us-east-1")
    AVAILABILITY_ZONES: List[str] = ["us-east-1a", "us-east-1b", "us-east-1c"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

