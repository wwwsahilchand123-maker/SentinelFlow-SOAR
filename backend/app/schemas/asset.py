from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.asset import AssetCriticality, AssetStatus

class AssetBase(BaseModel):
    hostname: str
    ip_address: Optional[str] = None
    operating_system: Optional[str] = None
    owner: Optional[str] = None
    criticality: AssetCriticality = AssetCriticality.MEDIUM
    status: AssetStatus = AssetStatus.ONLINE
    tags: Optional[str] = None

class AssetCreate(AssetBase):
    asset_id: Optional[str] = None

class AssetUpdate(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    operating_system: Optional[str] = None
    owner: Optional[str] = None
    criticality: Optional[AssetCriticality] = None
    status: Optional[AssetStatus] = None
    tags: Optional[str] = None

class AssetResponse(AssetBase):
    id: int
    asset_id: str
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
