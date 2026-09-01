from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.models.automation import AutomationRule
from app.models.alert import Alert
import logging

logger = logging.getLogger(__name__)

class AutomationService:
    """Evaluate automation rules and trigger associated playbooks"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate_alert(self, alert: Alert) -> List[AutomationRule]:
        """Evaluate all enabled automation rules against an alert in priority order"""
        triggered_rules = []
        
        rules = self.db.query(AutomationRule).filter(
            AutomationRule.enabled == True
        ).order_by(AutomationRule.priority.desc()).all()
        
        for rule in rules:
            if self._evaluate_conditions(rule.conditions, alert):
                triggered_rules.append(rule)
                logger.info(f"Rule '{rule.name}' triggered for alert {alert.alert_id}")
        
        return triggered_rules
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], alert: Alert) -> bool:
        """Evaluate rule condition groups (all / any) against an alert"""
        try:
            if not conditions:
                return False
                
            if "all" in conditions:
                return all(self._evaluate_condition(cond, alert) for cond in conditions["all"])
            elif "any" in conditions:
                return any(self._evaluate_condition(cond, alert) for cond in conditions["any"])
            else:
                return self._evaluate_condition(conditions, alert)
                
        except Exception as e:
            logger.error(f"Error evaluating conditions: {e}")
            return False
    
    def _evaluate_condition(self, condition: Dict[str, Any], alert: Alert) -> bool:
        """Evaluate a single condition against alert attributes"""
        field = condition.get("field")
        operator = condition.get("operator")
        expected_value = condition.get("value")
        
        if not field or not operator:
            return False
        
        alert_value = getattr(alert, field, None)
        if alert_value is None:
            return False
        
        # Convert enum to string value if necessary
        if hasattr(alert_value, 'value'):
            alert_value = alert_value.value
        
        alert_str = str(alert_value).lower()
        expected_str = str(expected_value).lower()
        
        if operator == "equals":
            return alert_str == expected_str
        elif operator == "contains":
            return expected_str in alert_str
        elif operator == "starts_with":
            return alert_str.startswith(expected_str)
        elif operator == "greater_than":
            try:
                return float(alert_value) > float(expected_value)
            except Exception:
                return False
        elif operator == "less_than":
            try:
                return float(alert_value) < float(expected_value)
            except Exception:
                return False
        
        return False
