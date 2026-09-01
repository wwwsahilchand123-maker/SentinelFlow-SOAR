from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from app.database import get_db
from app.models.incident import Incident, IncidentStatus, IncidentSeverity, IncidentEvent
from app.models.user import User, RoleEnum
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentUpdate, IncidentEventCreate, IncidentEventResponse
from app.core.dependencies import get_current_user, require_role
from app.services.audit_service import AuditService

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentResponse])
def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List security incidents with filtering by status and severity"""
    query = db.query(Incident)
    
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Incident.incident_id.ilike(s)) |
            (Incident.title.ilike(s)) |
            (Incident.description.ilike(s))
        )
        
    return query.order_by(Incident.created_at.desc()).offset(offset).limit(limit).all()

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_by_id(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full incident details including events and linked alerts"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(
    inc_in: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.SOC_ANALYST]))
):
    """Analyst/Admin: Create a new incident"""
    incident = Incident(
        incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
        title=inc_in.title,
        description=inc_in.description,
        severity=inc_in.severity,
        status=IncidentStatus.OPEN,
        risk_score=inc_in.risk_score or 50.0,
        source=inc_in.source or "Manual SOC Escalation",
        mitre_technique_id=inc_in.mitre_technique_id,
        mitre_tactic=inc_in.mitre_tactic,
        assigned_analyst_id=inc_in.assigned_analyst_id
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    # Add creation timeline event
    evt = IncidentEvent(
        incident_id=incident.id,
        event_type="INCIDENT_CREATED",
        description=f"Incident {incident.incident_id} created by {current_user.username}",
        details=incident.description,
        created_by_id=current_user.id
    )
    db.add(evt)
    db.commit()
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=current_user.id,
        action="INCIDENT_CREATED",
        resource="incident",
        resource_id=incident.incident_id,
        result="Success"
    )
    
    return incident

@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    inc_update: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.SOC_ANALYST]))
):
    """Analyst/Admin: Update incident lifecycle status, severity, risk score, or analyst"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    old_status = incident.status
    
    if inc_update.title:
        incident.title = inc_update.title
    if inc_update.description:
        incident.description = inc_update.description
    if inc_update.severity:
        incident.severity = inc_update.severity
    if inc_update.risk_score is not None:
        incident.risk_score = inc_update.risk_score
    if inc_update.assigned_analyst_id is not None:
        incident.assigned_analyst_id = inc_update.assigned_analyst_id
    if inc_update.case_id is not None:
        incident.case_id = inc_update.case_id
        
    if inc_update.status:
        incident.status = inc_update.status
        if inc_update.status == IncidentStatus.CONTAINED and not incident.contained_at:
            incident.contained_at = datetime.now(timezone.utc)
        elif inc_update.status in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED) and not incident.resolved_at:
            incident.resolved_at = datetime.now(timezone.utc)
            
        # Log timeline status transition
        evt = IncidentEvent(
            incident_id=incident.id,
            event_type="STATUS_CHANGED",
            description=f"Incident status transitioned from {old_status.value} to {inc_update.status.value}",
            details=f"Updated by {current_user.username}",
            created_by_id=current_user.id
        )
        db.add(evt)
        
    db.commit()
    db.refresh(incident)
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=current_user.id,
        action="INCIDENT_UPDATED",
        resource="incident",
        resource_id=incident.incident_id,
        result="Success",
        metadata={"new_status": str(incident.status), "risk_score": incident.risk_score}
    )
    
    return incident

@router.post("/{incident_id}/events", response_model=IncidentEventResponse, status_code=status.HTTP_201_CREATED)
def add_incident_event(
    incident_id: int,
    evt_in: IncidentEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.SOC_ANALYST]))
):
    """Add investigative notes or timeline records to an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    event = IncidentEvent(
        incident_id=incident.id,
        event_type=evt_in.event_type or "NOTE_ADDED",
        description=evt_in.description,
        details=evt_in.details,
        created_by_id=current_user.id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event

@router.get("/{incident_id}/events", response_model=List[IncidentEventResponse])
def get_incident_events(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chronological investigation timeline events for an incident"""
    return db.query(IncidentEvent).filter(
        IncidentEvent.incident_id == incident_id
    ).order_by(IncidentEvent.timestamp.asc()).all()
