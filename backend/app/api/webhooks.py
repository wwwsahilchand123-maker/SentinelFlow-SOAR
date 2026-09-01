from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
import uuid
import hashlib
from app.database import get_db
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.services.automation_service import AutomationService
from app.services.playbook_engine import PlaybookEngine
from app.services.correlation_service import CorrelationService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/security-alert")
async def receive_security_alert_webhook(
    payload: Dict[str, Any],
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Public ingest webhook for external security telemetry (SIEM, EDR, Firewalls, Email Gateways).
    Performs normalization, deduplication, correlation, and automated rule evaluation.
    """
    source = payload.get("source") or payload.get("vendor") or "Generic Webhook"
    alert_type = payload.get("alert_type") or payload.get("title") or "External Security Event"
    raw_severity = str(payload.get("severity", "Medium")).capitalize()
    
    sev_map = {
        "Critical": AlertSeverity.CRITICAL,
        "High": AlertSeverity.HIGH,
        "Medium": AlertSeverity.MEDIUM,
        "Low": AlertSeverity.LOW,
        "Informational": AlertSeverity.INFORMATIONAL
    }
    severity = sev_map.get(raw_severity, AlertSeverity.MEDIUM)
    
    source_ip = payload.get("source_ip") or payload.get("src_ip") or payload.get("attacker_ip")
    dest_ip = payload.get("destination_ip") or payload.get("dst_ip") or payload.get("target_ip")
    username = payload.get("username") or payload.get("user")
    host = payload.get("host") or payload.get("hostname") or payload.get("computer_name")
    indicator = payload.get("indicator") or payload.get("ioc") or payload.get("file_hash")
    description = payload.get("description") or payload.get("details") or f"Ingested alert from {source}"
    
    # Compute deduplication hash
    dedup_raw = f"{source}:{alert_type}:{source_ip}:{host}".lower()
    dedup_hash = hashlib.sha256(dedup_raw.encode()).hexdigest()
    
    # Check for duplicate within 15-minute sliding window
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    existing = db.query(Alert).filter(
        Alert.dedup_hash == dedup_hash,
        Alert.timestamp >= cutoff
    ).first()
    
    if existing:
        return {
            "status": "deduplicated",
            "message": "Alert matches recent event; deduplicated to prevent alert storm.",
            "existing_alert_id": existing.alert_id
        }
        
    alert = Alert(
        alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
        dedup_hash=dedup_hash,
        timestamp=datetime.now(timezone.utc),
        source=source,
        alert_type=alert_type,
        category=payload.get("category", "Uncategorized"),
        severity=severity,
        source_ip=source_ip,
        destination_ip=dest_ip,
        username=username,
        host=host,
        indicator=indicator,
        description=description,
        status=AlertStatus.NEW,
        raw_data=str(payload)
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # Run correlation
    correlation_service = CorrelationService(db)
    correlation_service.correlate_alert(alert)
    
    # Trigger automation rules
    automation_service = AutomationService(db)
    triggered_rules = automation_service.evaluate_alert(alert)
    
    dispatched_playbooks = []
    if triggered_rules:
        playbook_engine = PlaybookEngine(db)
        for rule in triggered_rules:
            for action in rule.actions:
                if action.get("type") == "trigger_playbook":
                    exec_res = await playbook_engine.execute_playbook(
                        playbook_id=action.get("playbook_id"),
                        trigger_data={
                            "alert_id": alert.alert_id,
                            "severity": alert.severity.value,
                            "source_ip": alert.source_ip,
                            "indicator": alert.indicator or alert.source_ip,
                            "description": alert.description,
                            "source": f"Webhook: {source}",
                            "host": alert.host
                        }
                    )
                    dispatched_playbooks.append(exec_res.execution_id)
                    
    audit_service = AuditService(db)
    audit_service.log_action(
        action="WEBHOOK_ALERT_INGESTED",
        resource="webhook",
        resource_id=alert.alert_id,
        result="Success",
        ip_address=request.client.host if request.client else None,
        metadata={"source": source, "alert_type": alert_type, "dispatched_playbooks": dispatched_playbooks}
    )
    
    return {
        "status": "success",
        "alert_id": alert.alert_id,
        "triggered_rules_count": len(triggered_rules),
        "dispatched_playbooks": dispatched_playbooks
    }
