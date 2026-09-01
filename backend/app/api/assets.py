from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.asset import Asset, AssetStatus, AssetCriticality
from app.schemas.asset import AssetCreate, AssetResponse, AssetUpdate
from app.services.audit_service import AuditService

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("", response_model=List[AssetResponse])
def get_assets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    criticality: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of protected network and endpoint assets"""
    query = db.query(Asset)
    if status:
        try:
            query = query.filter(Asset.status == AssetStatus(status))
        except ValueError:
            pass
    if criticality:
        try:
            query = query.filter(Asset.criticality == AssetCriticality(criticality))
        except ValueError:
            pass
    return query.order_by(Asset.hostname.asc()).offset(skip).limit(limit).all()

@router.post("/{asset_id}/isolate", response_model=AssetResponse)
def toggle_isolate_asset(
    asset_id: int,
    isolate: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Isolate or restore network access for an endpoint"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    asset.status = AssetStatus.QUARANTINED if isolate else AssetStatus.ONLINE
    db.commit()
    db.refresh(asset)
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=current_user.id,
        action="ASSET_QUARANTINED" if isolate else "ASSET_RESTORED",
        resource="asset",
        resource_id=asset.hostname,
        result="Success"
    )
    return asset

@router.post("", response_model=AssetResponse)
def create_asset(
    asset_data: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new asset"""
    asset = Asset(
        asset_id=asset_data.asset_id or f"AST-{uuid.uuid4().hex[:6].upper()}",
        hostname=asset_data.hostname,
        ip_address=asset_data.ip_address,
        operating_system=asset_data.operating_system,
        owner=asset_data.owner,
        criticality=asset_data.criticality,
        status=asset_data.status,
        tags=asset_data.tags
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset
