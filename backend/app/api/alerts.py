from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import hashlib
from app.database import get_db
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.user import User, RoleEnum
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate
from app.core.dependencies import get_current_user, require_role
from app.services.audit_service import AuditService
from app.services.automation_service import AutomationService
from app.services.playbook_engine import PlaybookEngine
from app.services.correlation_service import CorrelationService

router = APIRouter(prefix="/alerts", tags=["Alerts"])

def compute_alert_dedup_hash(source: str, alert_type: str, source_ip: Optional[str], host: Optional[str]) -> str:
    raw = f"{source}:{alert_type}:{source_ip or ''}:{host or ''}".lower()
    return hashlib.sha256(raw.encode()).hexdigest()

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve normalized security alerts with multi-factor filtering"""
    query = db.query(Alert)
    
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    if source:
        query = query.filter(Alert.source == source)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Alert.alert_id.ilike(s)) |
            (Alert.description.ilike(s)) |
            (Alert.source_ip.ilike(s)) |
            (Alert.indicator.ilike(s)) |
            (Alert.host.ilike(s)) |
            (Alert.username.ilike(s))
        )
    
    return query.order_by(Alert.timestamp.desc()).offset(offset).limit(limit).all()

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_by_id(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single alert details"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def ingest_alert(
    alert_in: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.SOC_ANALYST]))
):
    """Ingest a new normalized alert, evaluate automation rules, and trigger playbooks"""
    dedup_hash = compute_alert_dedup_hash(alert_in.source, alert_in.alert_type, alert_in.source_ip, alert_in.host)
    
    alert = Alert(
        alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
        dedup_hash=dedup_hash,
        timestamp=alert_in.timestamp or datetime.now(timezone.utc),
        source=alert_in.source,
        alert_type=alert_in.alert_type,
        category=alert_in.category,
        severity=alert_in.severity,
        source_ip=alert_in.source_ip,
        destination_ip=alert_in.destination_ip,
        username=alert_in.username,
        host=alert_in.host,
        indicator=alert_in.indicator,
        description=alert_in.description,
        status=AlertStatus.NEW
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # Correlate alert with existing active incidents
    correlation_service = CorrelationService(db)
    correlation_service.correlate_alert(alert)
    
    # Evaluate automation rules
    automation_service = AutomationService(db)
    triggered_rules = automation_service.evaluate_alert(alert)
    
    if triggered_rules:
        playbook_engine = PlaybookEngine(db)
        for rule in triggered_rules:
            for action in rule.actions:
                if action.get("type") == "trigger_playbook":
                    await playbook_engine.execute_playbook(
                        playbook_id=action.get("playbook_id"),
                        trigger_data={
                            "alert_id": alert.alert_id,
                            "severity": alert.severity.value,
                            "source_ip": alert.source_ip,
                            "indicator": alert.indicator or alert.source_ip,
                            "description": alert.description,
                            "source": "Automated Ingestion Rule",
                            "host": alert.host
                        },
                        user_id=current_user.id
                    )
                    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=current_user.id,
        action="ALERT_INGESTED",
        resource="alert",
        resource_id=alert.alert_id,
        result="Success"
    )
    
    return alert

@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    analyst_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.SOC_ANALYST]))
):
    """Analyst/Admin: Update alert status, severity, or analyst assignment"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    if alert_update.status:
        alert.status = alert_update.status
    if alert_update.severity:
        alert.severity = alert_update.severity
    if alert_update.assigned_analyst_id is not None:
        alert.assigned_analyst_id = alert_update.assigned_analyst_id
    if alert_update.incident_id is not None:
        alert.incident_id = alert_update.incident_id
        
    db.commit()
    db.refresh(alert)
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=analyst_user.id,
        action="ALERT_UPDATED",
        resource="alert",
        resource_id=alert.alert_id,
        result="Success",
        metadata={"new_status": str(alert.status), "assigned_to": alert.assigned_analyst_id}
    )
    
    return alert
