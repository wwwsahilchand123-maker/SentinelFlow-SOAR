from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any
from app.models.incident import IncidentStatus, IncidentSeverity

class IncidentEventBase(BaseModel):
    event_type: str
    description: str

class IncidentEventCreate(IncidentEventBase):
    incident_id: int
    user_id: Optional[int] = None
    metadata_info: Optional[str] = None

class IncidentEventResponse(IncidentEventBase):
    id: int
    incident_id: int
    timestamp: datetime
    user_id: Optional[int] = None
    metadata_info: Optional[str] = None
    
    class Config:
        from_attributes = True

class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    source: Optional[str] = None

class IncidentCreate(IncidentBase):
    assigned_analyst_id: Optional[int] = None

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    assigned_analyst_id: Optional[int] = None
    risk_score: Optional[float] = None

class IncidentResponse(IncidentBase):
    id: int
    incident_id: str
    risk_score: float
    status: IncidentStatus
    assigned_analyst_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    events: List[IncidentEventResponse] = []
    
    class Config:
        from_attributes = True
