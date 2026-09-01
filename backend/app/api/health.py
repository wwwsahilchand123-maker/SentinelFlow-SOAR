from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import time

from app.database import get_db, check_db_health
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def full_health_check(db: Session = Depends(get_db)):
    "ssl_ok = True"
    start_time = time.time()
    db_ok = check_db_health()
    latency_ms = round((time.time() - start_time) * 1000, 2)
    
    return {
        "status": "healthy" if db_ok else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latency_ms": latency_ms,
        "components": {
            "database": {
                "status": "healthy" if db_ok else "unhealthy",
                "engine": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite"
            },
            "threat_intelligence": {
                "status": "online",
                "virustotal_configured": bool(settings.VIRUSTOTAL_API_KEY),
                "abuseipdb_configured": bool(settings.ABUSEIPDB_API_KEY),
                "mode": "live" if (settings.VIRUSTOTAL_API_KEY or settings.ABUSEIPDB_API_KEY) else "mock_fallback",
                "cache_ttl_hours": settings.THREAT_INTEL_CACHE_TTL_HOURS
            },
            "playbook_engine": {
                "status": "online",
                "simulation_mode": settings.SIMULATION_MODE,
                "require_approval_threshold": settings.REQUIRE_APPROVAL_RISK_THRESHOLD
            },
            "response_engine": {
                "status": "online",
                "sandbox_active": True
            }
        }
    }
