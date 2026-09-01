from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.database import get_db
from app.models.alert import Alert
from app.models.incident import Incident
from app.models.indicator import Indicator
from app.models.asset import Asset
from app.models.case import Case
from app.models.playbook import Playbook
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("")
def global_search(
    q: str = Query(..., min_length=2, description="Search query for IOCs, IDs, hostnames, IPs"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Universal search across Alerts, Incidents, Indicators, Assets, Cases, and Playbooks"""
    term = f"%{q}%"
    
    alerts = db.query(Alert).filter(
        (Alert.alert_id.ilike(term)) |
        (Alert.alert_type.ilike(term)) |
        (Alert.source_ip.ilike(term)) |
        (Alert.host.ilike(term)) |
        (Alert.indicator.ilike(term)) |
        (Alert.description.ilike(term))
    ).limit(10).all()
    
    incidents = db.query(Incident).filter(
        (Incident.incident_id.ilike(term)) |
        (Incident.title.ilike(term)) |
        (Incident.description.ilike(term))
    ).limit(10).all()
    
    indicators = db.query(Indicator).filter(
        (Indicator.value.ilike(term)) |
        (Indicator.tags.ilike(term))
    ).limit(10).all()
    
    assets = db.query(Asset).filter(
        (Asset.asset_id.ilike(term)) |
        (Asset.hostname.ilike(term)) |
        (Asset.ip_address.ilike(term))
    ).limit(10).all()
    
    cases = db.query(Case).filter(
        (Case.case_id.ilike(term)) |
        (Case.title.ilike(term))
    ).limit(10).all()
    
    playbooks = db.query(Playbook).filter(
        (Playbook.name.ilike(term)) |
        (Playbook.description.ilike(term))
    ).limit(10).all()
    
    return {
        "query": q,
        "results": {
            "alerts": [{"id": a.id, "alert_id": a.alert_id, "title": a.alert_type, "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity), "source_ip": a.source_ip} for a in alerts],
            "incidents": [{"id": i.id, "incident_id": i.incident_id, "title": i.title, "severity": i.severity.value if hasattr(i.severity, "value") else str(i.severity), "status": i.status.value if hasattr(i.status, "value") else str(i.status)} for i in incidents],
            "indicators": [{"id": ind.id, "value": ind.value, "type": ind.indicator_type.value if hasattr(ind.indicator_type, "value") else str(ind.indicator_type), "reputation": ind.reputation.value if hasattr(ind.reputation, "value") else str(ind.reputation)} for ind in indicators],
            "assets": [{"id": ast.id, "asset_id": ast.asset_id, "hostname": ast.hostname, "ip_address": ast.ip_address, "criticality": ast.criticality.value if hasattr(ast.criticality, "value") else str(ast.criticality)} for ast in assets],
            "cases": [{"id": c.id, "case_id": c.case_id, "title": c.title, "priority": c.priority.value if hasattr(c.priority, "value") else str(c.priority)} for c in cases],
            "playbooks": [{"id": p.id, "name": p.name, "status": p.status.value if hasattr(p.status, "value") else str(p.status)} for p in playbooks]
        }
    }
