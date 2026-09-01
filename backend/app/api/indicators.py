from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.indicator import Indicator, IndicatorType, IndicatorReputation
from app.schemas.indicator import IndicatorCreate, IndicatorResponse, IndicatorUpdate
from app.services.threat_intelligence import ThreatIntelligenceService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/indicators", tags=["Threat Intelligence"])

@router.get("", response_model=List[IndicatorResponse])
def get_indicators(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    reputation: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List threat indicators"""
    query = db.query(Indicator)
    if type:
        try:
            query = query.filter(Indicator.indicator_type == IndicatorType(type))
        except ValueError:
            pass
    if reputation:
        try:
            query = query.filter(Indicator.reputation == IndicatorReputation(reputation))
        except ValueError:
            pass
    return query.order_by(Indicator.last_seen.desc()).offset(skip).limit(limit).all()

@router.post("/lookup")
async def lookup_indicator(
    value: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enrich and analyze an indicator value"""
    val = value.strip()
    if "." in val and all(part.isdigit() for part in val.split(".")):
        ind_type = IndicatorType.IPV4
    elif len(val) == 64 and "." not in val:
        ind_type = IndicatorType.SHA256
    elif len(val) == 32 and "." not in val:
        ind_type = IndicatorType.MD5
    elif len(val) == 40 and "." not in val:
        ind_type = IndicatorType.SHA1
    elif "@" in val:
        ind_type = IndicatorType.EMAIL
    else:
        ind_type = IndicatorType.DOMAIN
        
    threat_service = ThreatIntelligenceService()
    result = await threat_service.lookup_indicator(val, ind_type)
    
    # Save/Update in DB
    indicator = db.query(Indicator).filter(Indicator.value == val).first()
    if not indicator:
        indicator = Indicator(
            value=val,
            indicator_type=ind_type,
            reputation=result["reputation"],
            confidence=result["confidence"],
            source="SOC Analyst Lookup"
        )
        db.add(indicator)
    else:
        indicator.reputation = result["reputation"]
        indicator.confidence = result["confidence"]
    db.commit()
    db.refresh(indicator)
    
    return {"indicator": indicator, "enrichment": result}

@router.post("", response_model=IndicatorResponse)
def create_indicator(
    ind_data: IndicatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a threat indicator"""
    existing = db.query(Indicator).filter(Indicator.value == ind_data.value).first()
    if existing:
        raise HTTPException(status_code=400, detail="Indicator already registered")
    
    ind = Indicator(
        value=ind_data.value,
        indicator_type=ind_data.indicator_type,
        reputation=ind_data.reputation,
        confidence=ind_data.confidence,
        source=ind_data.source or "Manual",
        tags=ind_data.tags
    )
    db.add(ind)
    db.commit()
    db.refresh(ind)
    return ind
