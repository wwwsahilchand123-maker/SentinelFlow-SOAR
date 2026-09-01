from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging
from app.models.audit import AuditLog

logger = logging.getLogger(__name__)

class AuditService:
    """Immutable Append-Only Audit Logging Service"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def log_action(
        self,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        result: str = "Success",
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Record an immutable audit entry.
        Audit records can never be updated or deleted via application APIs.
        """
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            result=result,
            ip_address=ip_address,
            metadata_json=metadata or {},
            timestamp=datetime.now(timezone.utc)
        )
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        logger.info(f"AUDIT_EVENT: [{action}] resource={resource}:{resource_id} result={result} user_id={user_id}")
        return log_entry
