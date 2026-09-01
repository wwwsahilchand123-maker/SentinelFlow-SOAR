from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models.playbook import Playbook, PlaybookExecution, PlaybookStep, PlaybookVersion, PlaybookStatus
from app.models.user import User, RoleEnum
from app.schemas.playbook import PlaybookResponse, PlaybookExecutionResponse, PlaybookCreate, PlaybookUpdate
from app.core.dependencies import get_current_user, require_role
from app.services.playbook_engine import PlaybookEngine
from app.services.audit_service import AuditService

router = APIRouter(prefix="/playbooks", tags=["Playbooks"])

@router.get("", response_model=List[PlaybookResponse])
def get_playbooks(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all SOAR playbooks with step definitions and status"""
    query = db.query(Playbook)
    if status:
        query = query.filter(Playbook.status == status)
    return query.all()

@router.get("/executions", response_model=List[PlaybookExecutionResponse])
def get_all_executions(
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List recent playbook execution runs with step logs and duration telemetry"""
    return db.query(PlaybookExecution).order_by(
        PlaybookExecution.started_at.desc()
    ).offset(offset).limit(limit).all()

@router.get("/{playbook_id}", response_model=PlaybookResponse)
def get_playbook_by_id(
    playbook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single playbook definition"""
    playbook = db.query(Playbook).filter(Playbook.id == playbook_id).first()
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return playbook

@router.post("/{playbook_id}/execute", response_model=PlaybookExecutionResponse)
async def execute_playbook_endpoint(
    playbook_id: int,
    trigger_payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([RoleEnum.ADMIN, RoleEnum.SOC_ANALYST]))
):
    """Analyst/Admin: Manually dispatch and execute a playbook"""
    engine = PlaybookEngine(db)
    try:
        execution = await engine.execute_playbook(
            playbook_id=playbook_id,
            trigger_data=trigger_payload,
            user_id=current_user.id
        )
        return execution
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

@router.get("/executions/{execution_id}", response_model=PlaybookExecutionResponse)
def get_execution_by_id(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve detailed step logs and timing for a specific playbook execution"""
    execution = db.query(PlaybookExecution).filter(
        (PlaybookExecution.execution_id == execution_id) |
        (PlaybookExecution.id == int(execution_id) if execution_id.isdigit() else False)
    ).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

@router.patch("/{playbook_id}/status")
def toggle_playbook_status(
    playbook_id: int,
    status_data: Dict[str, str],
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role([RoleEnum.ADMIN]))
):
    """Admin-only: Enable or disable a playbook"""
    playbook = db.query(Playbook).filter(Playbook.id == playbook_id).first()
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
        
    new_status = status_data.get("status", "Enabled")
    playbook.status = PlaybookStatus(new_status)
    db.commit()
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=admin_user.id,
        action="PLAYBOOK_STATUS_TOGGLED",
        resource="playbook",
        resource_id=str(playbook.id),
        result="Success",
        metadata={"status": new_status}
    )
    
    return {"status": "success", "playbook_id": playbook.id, "new_status": new_status}
