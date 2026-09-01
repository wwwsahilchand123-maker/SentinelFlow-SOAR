from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.database import get_db
from app.models.approval import ApprovalRequest, ApprovalStatus
from app.models.playbook import PlaybookExecution, ExecutionStatus
from app.models.user import User, RoleEnum
from app.core.dependencies import get_current_user, require_role
from app.services.audit_service import AuditService
from app.services.playbook_engine import PlaybookEngine
from pydantic import BaseModel

router = APIRouter(prefix="/approvals", tags=["Approvals"])

class ApprovalDecisionRequest(BaseModel):
    decision: str  # "Approved" or "Rejected"
    notes: Optional[str] = None

class ApprovalResponse(BaseModel):
    id: int
    request_id: str
    action_type: str
    target: str
    risk_score: float
    reason: Optional[str] = None
    status: str
    playbook_id: Optional[int] = None
    execution_id: Optional[int] = None
    incident_id: Optional[int] = None
    requested_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    decision_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None

    class Config:
        from_attributes = True

@router.get("", response_model=List[ApprovalResponse])
def get_approvals(
    status: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List pending and historical human-in-the-loop approval requests"""
    query = db.query(ApprovalRequest)
    if status:
        query = query.filter(ApprovalRequest.status == status)
    return query.order_by(ApprovalRequest.created_at.desc()).limit(limit).all()

@router.post("/{approval_id}/decision", response_model=ApprovalResponse)
async def process_approval_decision(
    approval_id: int,
    body: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    analyst_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.SOC_ANALYST]))
):
    """Analyst/Admin: Approve or Reject a sensitive response containment action"""
    req = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found")
        
    if req.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Request is already {req.status.value}")
        
    decision = body.decision.capitalize()
    if decision not in ("Approved", "Rejected"):
        raise HTTPException(status_code=400, detail="Decision must be 'Approved' or 'Rejected'")
        
    req.status = ApprovalStatus.APPROVED if decision == "Approved" else ApprovalStatus.REJECTED
    req.approved_by_id = analyst_user.id
    req.decision_notes = body.notes
    req.decided_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)
    
    # If approved, resume the playbook execution
    if req.status == ApprovalStatus.APPROVED and req.playbook_id:
        engine = PlaybookEngine(db)
        await engine.execute_playbook(
            playbook_id=req.playbook_id,
            trigger_data={
                "indicator": req.target,
                "source_ip": req.target,
                "host": req.target,
                "approval_granted": True,
                "source": "Approved Workflow"
            },
            user_id=analyst_user.id
        )
        
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=analyst_user.id,
        action="APPROVAL_DECIDED",
        resource="approval",
        resource_id=req.request_id,
        result=req.status.value,
        metadata={"target": req.target, "action": req.action_type, "notes": req.decision_notes}
    )
    
    return req
