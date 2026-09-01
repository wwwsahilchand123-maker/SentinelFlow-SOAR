from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class AuditLogBase(BaseModel):
    action: str
    resource: str
    resource_id: Optional[str] = None
    result: str
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None

class AuditLogResponse(AuditLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
