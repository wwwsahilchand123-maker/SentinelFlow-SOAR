from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from datetime import datetime, timezone

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.alert import Alert, AlertSeverity
from app.services.automation_service import AutomationService
from app.services.playbook_engine import PlaybookEngine
from app.services.correlation_service import CorrelationService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/simulation", tags=["Simulation"])

async def run_simulation_scenario(scenario: str, db: Session, user_id: int):
    """Run simulation scenario synchronously or in background"""
    scenarios = {
        "brute_force": {
            "source": "Authentication System",
            "alert_type": "Brute Force Attack",
            "category": "Authentication",
            "severity": AlertSeverity.HIGH,
            "source_ip": "185.220.101.45",
            "username": "admin",
            "description": "Multiple failed SSH/RDP login attempts detected from known Tor exit node",
            "failed_attempts": 25
        },
        "phishing": {
            "source": "Email Security",
            "alert_type": "Phishing Email",
            "category": "Email",
            "severity": AlertSeverity.HIGH,
            "source_ip": "203.0.113.42",
            "indicator": "malicious-domain.xyz",
            "description": "Spear phishing email detected targeting corporate finance with credential harvest link",
            "failed_attempts": 0
        },
        "malicious_ip": {
            "source": "Firewall",
            "alert_type": "Malicious IP Connection",
            "category": "Network",
            "severity": AlertSeverity.CRITICAL,
            "source_ip": "185.220.102.8",
            "destination_ip": "192.168.1.100",
            "description": "Inbound connection attempt from known C2 scanner IP address",
            "failed_attempts": 0
        },
        "malware": {
            "source": "Endpoint Security",
            "alert_type": "Malware Detection",
            "category": "Malware",
            "severity": AlertSeverity.CRITICAL,
            "host": "WORKSTATION-042",
            "indicator": "deadbeef1234567890abcdef",
            "description": "Ransomware dropper binary hash detected in user temp directory",
            "failed_attempts": 0
        },
        "suspicious_login": {
            "source": "Authentication System",
            "alert_type": "Suspicious Login",
            "category": "Authentication",
            "severity": AlertSeverity.MEDIUM,
            "source_ip": "198.51.100.23",
            "username": "jsmith",
            "description": "Concurrent login from anomalous geographic location without MFA",
            "failed_attempts": 2
        },
        "data_exfiltration": {
            "source": "DLP System",
            "alert_type": "Data Exfiltration",
            "category": "Data Loss",
            "severity": AlertSeverity.CRITICAL,
            "source_ip": "192.168.1.150",
            "destination_ip": "198.51.100.99",
            "username": "jdoe",
            "description": "High volume encrypted archive transfer to unauthorized external cloud bucket",
            "failed_attempts": 0
        }
    }
    
    if scenario not in scenarios:
        return {"error": "Scenario not recognized"}
    
    scenario_data = scenarios[scenario]
    
    # Create alert
    alert = Alert(
        alert_id=f"ALT-{uuid.uuid4().hex[:8].upper()}",
        timestamp=datetime.now(timezone.utc),
        source=scenario_data["source"],
        alert_type=scenario_data["alert_type"],
        category=scenario_data["category"],
        severity=scenario_data["severity"],
        source_ip=scenario_data.get("source_ip"),
        destination_ip=scenario_data.get("destination_ip"),
        username=scenario_data.get("username"),
        host=scenario_data.get("host"),
        indicator=scenario_data.get("indicator"),
        description=scenario_data["description"]
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # Correlate alert
    correlation_service = CorrelationService(db)
    correlation_service.correlate_alert(alert)
    
    # Evaluate automation rules
    automation_service = AutomationService(db)
    triggered_rules = automation_service.evaluate_alert(alert)
    
    executed_playbooks = []
    # Execute playbooks
    if triggered_rules:
        playbook_engine = PlaybookEngine(db)
        for rule in triggered_rules:
            for action in rule.actions:
                if action.get("type") == "trigger_playbook":
                    playbook_id = action.get("playbook_id")
                    exec_res = await playbook_engine.execute_playbook(
                        playbook_id=playbook_id,
                        trigger_data={
                            "alert_id": alert.alert_id,
                            "severity": alert.severity.value if hasattr(alert.severity, "value") else str(alert.severity),
                            "source_ip": alert.source_ip,
                            "indicator": alert.indicator or alert.source_ip,
                            "description": alert.description,
                            "title": f"Automated SOAR: {scenario_data['alert_type']}",
                            "failed_attempts": scenario_data.get("failed_attempts", 0),
                            "host": alert.host
                        },
                        user_id=user_id
                    )
                    executed_playbooks.append(exec_res.execution_id)
    
    # Audit log
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=user_id,
        action="SIMULATION_EXECUTED",
        resource="simulation",
        resource_id=scenario,
        result="Success",
        metadata={"alert_id": alert.alert_id, "playbooks": executed_playbooks}
    )
    
    return {
        "alert_id": alert.alert_id,
        "triggered_rules_count": len(triggered_rules),
        "executed_playbooks": executed_playbooks
    }

@router.post("/brute-force")
async def simulate_brute_force(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    res = await run_simulation_scenario("brute_force", db, current_user.id)
    return {"status": "success", "scenario": "brute_force", "result": res}

@router.post("/phishing")
async def simulate_phishing(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    res = await run_simulation_scenario("phishing", db, current_user.id)
    return {"status": "success", "scenario": "phishing", "result": res}

@router.post("/malicious-ip")
async def simulate_malicious_ip(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    res = await run_simulation_scenario("malicious_ip", db, current_user.id)
    return {"status": "success", "scenario": "malicious_ip", "result": res}

@router.post("/malware")
async def simulate_malware(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    res = await run_simulation_scenario("malware", db, current_user.id)
    return {"status": "success", "scenario": "malware", "result": res}

@router.post("/suspicious-login")
async def simulate_suspicious_login(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    res = await run_simulation_scenario("suspicious_login", db, current_user.id)
    return {"status": "success", "scenario": "suspicious_login", "result": res}

@router.post("/data-exfiltration")
async def simulate_data_exfiltration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    res = await run_simulation_scenario("data_exfiltration", db, current_user.id)
    return {"status": "success", "scenario": "data_exfiltration", "result": res}
