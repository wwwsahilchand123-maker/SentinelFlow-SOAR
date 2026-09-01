from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid
import time
import logging
from app.models.playbook import Playbook, PlaybookExecution, ExecutionLog, ExecutionStatus
from app.models.incident import Incident, IncidentEvent, IncidentSeverity, IncidentStatus
from app.models.indicator import Indicator, IndicatorType, IndicatorReputation
from app.models.asset import Asset, AssetStatus
from app.models.approval import ApprovalRequest, ApprovalStatus
from app.services.threat_intelligence import ThreatIntelligenceService
from app.services.risk_scoring import RiskScoringEngine
from app.services.response_engine import SafeResponseEngine
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService
from app.config import settings

logger = logging.getLogger(__name__)

class PlaybookEngine:
    """Enterprise SOAR Playbook Orchestration Engine with step telemetry and human approvals"""
    
    def __init__(self, db: Session):
        self.db = db
        self.threat_intel = ThreatIntelligenceService()
        self.risk_engine = RiskScoringEngine()
        self.response_engine = SafeResponseEngine()
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)

    async def execute_playbook(
        self,
        playbook_id: int,
        trigger_data: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> PlaybookExecution:
        """Execute a playbook with detailed step tracking and failure containment"""
        
        playbook = self.db.query(Playbook).filter(Playbook.id == playbook_id).first()
        if not playbook:
            raise ValueError(f"Playbook {playbook_id} not found")
            
        execution_id_str = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
        start_time = time.perf_counter()
        
        execution = PlaybookExecution(
            execution_id=execution_id_str,
            playbook_id=playbook.id,
            playbook_version=playbook.version or "1.0.0",
            status=ExecutionStatus.RUNNING,
            trigger_source=trigger_data.get("source", "Automated Triage")
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        
        context = {
            "trigger_data": trigger_data,
            "results": {},
            "execution_id": execution_id_str,
            "incident_id": None
        }
        
        self._log_step(
            execution.id,
            step_id=0,
            step_name="Playbook Initialization",
            action="init",
            status="Completed",
            duration_ms=round((time.perf_counter() - start_time) * 1000, 2),
            output_data={"playbook_name": playbook.name, "version": playbook.version, "trigger_data": trigger_data}
        )
        
        has_failed = False
        waiting_for_approval = False
        
        try:
            for step in playbook.steps:
                step_start = time.perf_counter()
                
                # Check human approval requirement
                risk_score = float(trigger_data.get("risk_score", 0.0))
                requires_approval = step.requires_approval or (
                    step.action.endswith("_simulation") and risk_score >= settings.REQUIRE_APPROVAL_RISK_THRESHOLD
                )
                
                if requires_approval and not trigger_data.get("approval_granted", False):
                    # Create Approval Request record
                    app_req = ApprovalRequest(
                        request_id=f"APP-{uuid.uuid4().hex[:8].upper()}",
                        action_type=step.action,
                        target=str(trigger_data.get("indicator") or trigger_data.get("source_ip") or trigger_data.get("host") or "Target Entity"),
                        risk_score=risk_score,
                        reason=f"High risk response containment action requires SOC analyst approval: {step.action}",
                        status=ApprovalStatus.PENDING,
                        playbook_id=playbook.id,
                        execution_id=execution.id,
                        incident_id=context.get("incident_id"),
                        requested_by_id=user_id
                    )
                    self.db.add(app_req)
                    self.db.commit()
                    
                    self._log_step(
                        execution.id,
                        step_id=step.id,
                        step_name=f"{step.name} (Approval Required)",
                        action=step.action,
                        status="Waiting Approval",
                        duration_ms=round((time.perf_counter() - step_start) * 1000, 2),
                        output_data={"approval_request_id": app_req.request_id, "status": "Pending Analyst Review"}
                    )
                    
                    self.notification_service.create_notification(
                        title=f"Approval Required: {step.action}",
                        message=f"Playbook {playbook.name} is waiting for human approval for target {app_req.target}.",
                        severity="High"
                    )
                    
                    waiting_for_approval = True
                    break
                
                # Execute step action
                step_result = await self._execute_step_action(step.action, step.parameters or {}, context, user_id)
                step_duration = round((time.perf_counter() - step_start) * 1000, 2)
                context["results"][step.action] = step_result
                
                self._log_step(
                    execution.id,
                    step_id=step.id,
                    step_name=step.name,
                    action=step.action,
                    status="Completed",
                    duration_ms=step_duration,
                    input_data=step.parameters,
                    output_data=step_result
                )
                
            total_duration = round((time.perf_counter() - start_time) * 1000, 2)
            execution.duration_ms = total_duration
            execution.completed_at = datetime.now(timezone.utc)
            
            if waiting_for_approval:
                execution.status = ExecutionStatus.WAITING_APPROVAL
            elif has_failed:
                execution.status = ExecutionStatus.FAILED
            else:
                execution.status = ExecutionStatus.COMPLETED
                
        except Exception as e:
            logger.error(f"Playbook execution error: {e}", exc_info=True)
            total_duration = round((time.perf_counter() - start_time) * 1000, 2)
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.duration_ms = total_duration
            execution.completed_at = datetime.now(timezone.utc)
            
            self._log_step(
                execution.id,
                step_id=999,
                step_name="Step Execution Failure",
                action="error",
                status="Failed",
                duration_ms=total_duration,
                error_message=str(e)
            )
            
        self.db.commit()
        self.db.refresh(execution)
        
        # Log to immutable audit service
        self.audit_service.log_action(
            user_id=user_id,
            action="PLAYBOOK_EXECUTED",
            resource="playbook",
            resource_id=str(playbook.id),
            result=execution.status.value,
            metadata={"execution_id": execution.execution_id, "playbook_name": playbook.name, "duration_ms": execution.duration_ms}
        )
        
        return execution

    async def _execute_step_action(
        self,
        action: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any],
        user_id: Optional[int]
    ) -> Any:
        """Route and execute individual action with context state"""
        trigger = context["trigger_data"]
        
        if action == "extract_indicator":
            indicator_val = trigger.get("indicator") or trigger.get("source_ip") or trigger.get("host")
            ind_type = self.threat_intel.detect_indicator_type(str(indicator_val))
            return {"indicator": indicator_val, "type": ind_type.value}
            
        elif action == "threat_intelligence_lookup":
            ind_val = trigger.get("indicator") or trigger.get("source_ip") or "127.0.0.1"
            res = await self.threat_intel.lookup_indicator(str(ind_val))
            
            # Upsert into indicators table
            ind_record = self.db.query(Indicator).filter(Indicator.value == ind_val).first()
            if not ind_record:
                ind_record = Indicator(
                    value=ind_val,
                    indicator_type=self.threat_intel.detect_indicator_type(ind_val),
                    reputation=res["reputation"],
                    confidence=res["confidence"],
                    source=res["provider"],
                    is_simulation=res.get("is_simulation", True),
                    raw_data=res.get("raw_data")
                )
                self.db.add(ind_record)
            else:
                ind_record.reputation = res["reputation"]
                ind_record.confidence = res["confidence"]
                ind_record.source = res["provider"]
                ind_record.is_simulation = res.get("is_simulation", True)
            self.db.commit()
            return res
            
        elif action == "calculate_risk":
            sev = trigger.get("severity", "Medium")
            rep = IndicatorReputation.UNKNOWN
            if "threat_intelligence_lookup" in context["results"]:
                rep = context["results"]["threat_intelligence_lookup"].get("reputation", IndicatorReputation.UNKNOWN)
            risk_calc = self.risk_engine.calculate_risk(
                severity=sev,
                indicator_reputation=rep,
                failed_attempts=int(trigger.get("failed_attempts", 0))
            )
            trigger["risk_score"] = risk_calc["risk_score"]
            return risk_calc
            
        elif action == "create_incident":
            inc_id_str = f"INC-{uuid.uuid4().hex[:8].upper()}"
            title = trigger.get("title") or f"SOAR Incident: {trigger.get('alert_type', 'Security Threat')}"
            desc = trigger.get("description", "Automated SOAR response incident created from alert ingestion.")
            
            risk_val = trigger.get("risk_score", 65.0)
            sev_val = IncidentSeverity.HIGH if risk_val >= 60.0 else IncidentSeverity.MEDIUM
            
            inc = Incident(
                incident_id=inc_id_str,
                title=title,
                description=desc,
                severity=sev_val,
                status=IncidentStatus.INVESTIGATING,
                risk_score=risk_val,
                source=trigger.get("source", "SOAR Playbook Engine")
            )
            self.db.add(inc)
            self.db.commit()
            self.db.refresh(inc)
            
            context["incident_id"] = inc.id
            
            # Add initial timeline event
            evt = IncidentEvent(
                incident_id=inc.id,
                event_type="INCIDENT_CREATED",
                description=f"Incident {inc_id_str} automatically created by SOAR playbook engine.",
                details=f"Calculated Risk: {risk_val}/100 | Severity: {sev_val.value}"
            )
            self.db.add(evt)
            self.db.commit()
            return {"incident_id": inc_id_str, "id": inc.id, "risk_score": risk_val}
            
        elif action == "block_ip_simulation":
            ip = trigger.get("source_ip") or trigger.get("indicator") or "185.220.101.45"
            res = self.response_engine.block_ip_simulation(str(ip), reason=parameters.get("reason", "Automated Playbook Block"))
            if context.get("incident_id"):
                self.db.add(IncidentEvent(
                    incident_id=context["incident_id"],
                    event_type="RESPONSE_EXECUTED",
                    description=f"Perimeter firewall block rule injected for {ip} (SIMULATED).",
                    details=res.get("message")
                ))
                self.db.commit()
            return res
            
        elif action == "isolate_endpoint_simulation":
            host = trigger.get("host") or "WORKSTATION-042"
            res = self.response_engine.isolate_endpoint_simulation(str(host), reason=parameters.get("reason", "EDR Host Isolation"))
            # Update asset status in DB
            asset = self.db.query(Asset).filter(Asset.hostname == host).first()
            if asset:
                asset.status = AssetStatus.ISOLATED
                self.db.commit()
            if context.get("incident_id"):
                self.db.add(IncidentEvent(
                    incident_id=context["incident_id"],
                    event_type="RESPONSE_EXECUTED",
                    description=f"EDR Host quarantine executed on {host} (SIMULATED).",
                    details=res.get("message")
                ))
                self.db.commit()
            return res
            
        elif action == "disable_user_simulation":
            user = trigger.get("username") or "compromised_user"
            res = self.response_engine.disable_user_simulation(str(user), reason=parameters.get("reason", "User Account Lock"))
            if context.get("incident_id"):
                self.db.add(IncidentEvent(
                    incident_id=context["incident_id"],
                    event_type="RESPONSE_EXECUTED",
                    description=f"IdP credentials locked and active tokens revoked for user {user} (SIMULATED).",
                    details=res.get("message")
                ))
                self.db.commit()
            return res
            
        elif action == "quarantine_email_simulation":
            ind = trigger.get("indicator") or "malicious-domain.xyz"
            res = self.response_engine.quarantine_email_simulation(str(ind))
            if context.get("incident_id"):
                self.db.add(IncidentEvent(
                    incident_id=context["incident_id"],
                    event_type="RESPONSE_EXECUTED",
                    description=f"Phishing emails targeting domain/url {ind} purged from mailboxes (SIMULATED).",
                    details=res.get("message")
                ))
                self.db.commit()
            return res
            
        elif action == "notify_analyst":
            msg = parameters.get("message") or f"SOAR Alert processed: {trigger.get('alert_type', 'Security Event')}"
            notif = self.notification_service.create_notification(
                title=f"SOAR Notification: {trigger.get('alert_type', 'Threat Triage')}",
                message=msg,
                severity=trigger.get("severity", "Medium")
            )
            return {"notification_id": notif.id, "status": "Dispatched"}
            
        return {"action": action, "status": "Executed", "parameters": parameters}

    def _log_step(
        self,
        execution_id: int,
        step_id: Optional[int],
        step_name: str,
        action: str,
        status: str,
        duration_ms: float = 0.0,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> ExecutionLog:
        """Append-only step execution telemetries"""
        log = ExecutionLog(
            execution_id=execution_id,
            step_id=step_id,
            step_name=step_name,
            action=action,
            status=status,
            duration_ms=duration_ms,
            input_data=input_data,
            output_data=output_data,
            error_message=error_message
        )
        self.db.add(log)
        self.db.commit()
        return log
