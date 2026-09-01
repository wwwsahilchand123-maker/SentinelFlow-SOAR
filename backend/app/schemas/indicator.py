from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.indicator import IndicatorType, IndicatorReputation

class IndicatorBase(BaseModel):
    value: str
    indicator_type: IndicatorType
    reputation: IndicatorReputation = IndicatorReputation.UNKNOWN
    confidence: float = 0.0
    source: Optional[str] = None
    tags: Optional[str] = None
    metadata_info: Optional[str] = None

class IndicatorCreate(IndicatorBase):
    pass

class IndicatorUpdate(BaseModel):
    reputation: Optional[IndicatorReputation] = None
    confidence: Optional[float] = None
    tags: Optional[str] = None

class IndicatorResponse(IndicatorBase):
    id: int
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
