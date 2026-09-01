from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging
from app.models.notification import Notification, NotificationSeverity

logger = logging.getLogger(__name__)

class NotificationService:
    """Internal In-App Notification Service with Mock External Integration Adapters"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def create_notification(
        self,
        title: str,
        message: str,
        severity: str = "Medium",
        user_id: Optional[int] = None
    ) -> Notification:
        """Create in-app notification and trigger mock external adapters"""
        sev_map = {
            "Critical": NotificationSeverity.CRITICAL,
            "High": NotificationSeverity.HIGH,
            "Medium": NotificationSeverity.MEDIUM,
            "Low": NotificationSeverity.LOW
        }
        notif_sev = sev_map.get(severity, NotificationSeverity.MEDIUM)
        
        notif = Notification(
            title=title,
            message=message,
            severity=notif_sev,
            user_id=user_id,
            is_read=False,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        
        # Dispatch to mock external adapters
        self._dispatch_mock_slack_alert(title, message, severity)
        self._dispatch_mock_email_alert(title, message, severity)
        
        return notif

    def _dispatch_mock_slack_alert(self, title: str, message: str, severity: str):
        """Mock Slack Webhook Adapter (Simulated)"""
        logger.info(f"[MOCK SLACK ADAPTER] Sending alert to #soc-alerts: [{severity}] {title} - {message}")

    def _dispatch_mock_email_alert(self, title: str, message: str, severity: str):
        """Mock Email SMTP Adapter (Simulated)"""
        logger.info(f"[MOCK EMAIL ADAPTER] Dispatching email to soc-oncall@enterprise.local: [{severity}] {title}")
