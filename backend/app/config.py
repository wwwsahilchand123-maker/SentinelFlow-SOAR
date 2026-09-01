from pydantic_settings import BaseSettings
from typing import Optional, List, Union
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SentinelFlow SOAR Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database (PostgreSQL primary; fallback to local SQLite for dev if postgres not reachable)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./soar.db")
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "sentinelflow-enterprise-jwt-secret-key-32-chars-minimum")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours
    
    # Rate Limiting
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_WEBHOOKS: str = "60/minute"
    
    # Threat Intelligence
    VIRUSTOTAL_API_KEY: Optional[str] = os.getenv("VIRUSTOTAL_API_KEY", None)
    ABUSEIPDB_API_KEY: Optional[str] = os.getenv("ABUSEIPDB_API_KEY", None)
    THREAT_INTEL_CACHE_TTL_HOURS: int = 24
    
    # SOAR Execution & Safety
    SIMULATION_MODE: bool = True
    REQUIRE_APPROVAL_RISK_THRESHOLD: int = 80
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
