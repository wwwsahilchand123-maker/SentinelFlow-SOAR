from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import logging
from app.models.alert import Alert
from app.models.incident import Incident, IncidentStatus, IncidentSeverity, IncidentEvent
from app.services.risk_scoring import RiskScoringEngine

logger = logging.getLogger(__name__)

class CorrelationService:
    """Security Event Correlation Engine for grouping related alerts into unified incidents"""
    
    def __init__(self, db: Session, window_minutes: int = 15):
        self.db = db
        self.window_minutes = window_minutes

    def correlate_alert(self, alert: Alert) -> Optional[Incident]:
        """
        Check if an incoming alert correlates to an existing active incident.
        If found, attach alert to the incident and record a correlation event.
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=self.window_minutes)
        
        # Look for open or investigating incidents matching source_ip, host, or username
        query = self.db.query(Incident).filter(
            Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]),
            Incident.created_at >= cutoff_time
        )
        
        candidates: List[Incident] = query.all()
        matched_incident: Optional[Incident] = None
        
        for inc in candidates:
            # Check related alerts attached to this incident
            for rel_alert in inc.alerts:
                if alert.source_ip and rel_alert.source_ip and alert.source_ip == rel_alert.source_ip:
                    matched_incident = inc
                    break
                if alert.host and rel_alert.host and alert.host.lower() == rel_alert.host.lower():
                    matched_incident = inc
                    break
                if alert.username and rel_alert.username and alert.username.lower() == rel_alert.username.lower():
                    matched_incident = inc
                    break
            if matched_incident:
                break
                
        if matched_incident:
            # Associate alert with existing incident
            alert.incident_id = matched_incident.id
            
            # Recalculate incident risk if new alert is higher severity
            if alert.severity.value in ["Critical", "High"] and matched_incident.severity != IncidentSeverity.CRITICAL:
                matched_incident.severity = IncidentSeverity.HIGH if alert.severity.value == "High" else IncidentSeverity.CRITICAL
                matched_incident.risk_score = min(100.0, matched_incident.risk_score + 10.0)
                
            # Log correlation event on incident timeline
            event = IncidentEvent(
                incident_id=matched_incident.id,
                event_type="ALERT_CORRELATED",
                description=f"Correlated new security alert {alert.alert_id} ({alert.alert_type}) into existing incident via entity matching.",
                details=f"Entity match: IP={alert.source_ip}, Host={alert.host}, User={alert.username}"
            )
            self.db.add(event)
            self.db.commit()
            logger.info(f"Alert {alert.alert_id} correlated to Incident {matched_incident.incident_id}")
            return matched_incident
            
        return None
