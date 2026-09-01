from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.alert import AlertStatus, AlertSeverity

class AlertBase(BaseModel):
    source: str
    alert_type: str
    category: Optional[str] = None
    severity: AlertSeverity
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    username: Optional[str] = None
    host: Optional[str] = None
    indicator: Optional[str] = None
    description: Optional[str] = None

class AlertCreate(AlertBase):
    timestamp: Optional[datetime] = None

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    severity: Optional[AlertSeverity] = None
    assigned_analyst_id: Optional[int] = None
    incident_id: Optional[int] = None

class AlertResponse(AlertBase):
    id: int
    alert_id: str
    timestamp: datetime
    status: AlertStatus
    assigned_analyst_id: Optional[int] = None
    incident_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
