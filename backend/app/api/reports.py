from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import io
import csv

from app.database import get_db
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.playbook import PlaybookExecution
from app.models.asset import Asset
from app.models.indicator import Indicator
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/executive-summary")
def get_executive_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """High-level executive security posture report for CISO / SOC leadership"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    total_alerts = db.query(Alert).filter(Alert.timestamp >= cutoff).count()
    total_incidents = db.query(Incident).filter(Incident.created_at >= cutoff).count()
    playbook_runs = db.query(PlaybookExecution).filter(PlaybookExecution.started_at >= cutoff).count()
    
    avg_risk = db.query(func.avg(Incident.risk_score)).filter(Incident.created_at >= cutoff).scalar() or 0.0
    
    incidents_by_severity = db.query(Incident.severity, func.count(Incident.id)).filter(Incident.created_at >= cutoff).group_by(Incident.severity).all()
    
    total_assets = db.query(Asset).count()
    threat_indicators = db.query(Indicator).count()
    
    return {
        "timeframe_days": days,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": current_user.username,
        "metrics": {
            "total_alerts_ingested": total_alerts,
            "total_incidents_created": total_incidents,
            "automated_playbook_executions": playbook_runs,
            "average_incident_risk_score": round(float(avg_risk), 1),
            "monitored_assets": total_assets,
            "active_threat_indicators": threat_indicators
        },
        "severity_breakdown": {
            str(sev.value if hasattr(sev, 'value') else sev): count for sev, count in incidents_by_severity
        }
    }

@router.get("/export-incidents-csv")
def export_incidents_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export all incidents as CSV for external compliance audit reporting"""
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Incident ID", "Title", "Severity", "Status", "Risk Score", "Source", "MITRE Technique", "Created At"])
    
    for inc in incidents:
        writer.writerow([
            inc.incident_id,
            inc.title,
            inc.severity.value if hasattr(inc.severity, 'value') else str(inc.severity),
            inc.status.value if hasattr(inc.status, 'value') else str(inc.status),
            inc.risk_score,
            inc.source,
            inc.mitre_technique_id or "N/A",
            inc.created_at.isoformat() if inc.created_at else ""
        ])
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentinelflow_incidents.csv"}
    )
