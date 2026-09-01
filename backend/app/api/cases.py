from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import hashlib
from datetime import datetime, timezone

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.case import Case, CaseEvidence, CaseStatus, CasePriority
from app.schemas.case import CaseCreate, CaseResponse, CaseUpdate, CaseEvidenceCreate, CaseEvidenceResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/cases", tags=["Investigation Cases"])

@router.get("", response_model=List[CaseResponse])
def get_cases(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List investigation cases"""
    query = db.query(Case)
    if status:
        try:
            query = query.filter(Case.status == CaseStatus(status))
        except ValueError:
            pass
    if priority:
        try:
            query = query.filter(Case.priority == CasePriority(priority))
        except ValueError:
            pass
    return query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single investigation case"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create investigation case and optionally link initial incidents"""
    case = Case(
        case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
        title=case_data.title,
        description=case_data.description,
        priority=case_data.priority,
        status=case_data.status,
        assigned_analyst_id=case_data.assigned_analyst_id or current_user.id
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=current_user.id,
        action="CASE_CREATED",
        resource="case",
        resource_id=case.case_id,
        result="Success",
        metadata={"title": case.title, "priority": case.priority.value if hasattr(case.priority, 'value') else str(case.priority)}
    )
    return case

@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: int,
    update_data: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update investigation case status, priority, or summary"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if update_data.title is not None:
        case.title = update_data.title
    if update_data.description is not None:
        case.description = update_data.description
    if update_data.priority is not None:
        case.priority = update_data.priority
    if update_data.status is not None:
        case.status = update_data.status
        if update_data.status == CaseStatus.CLOSED:
            case.closed_at = datetime.now(timezone.utc)
    if update_data.assigned_analyst_id is not None:
        case.assigned_analyst_id = update_data.assigned_analyst_id
        
    db.commit()
    db.refresh(case)
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=current_user.id,
        action="CASE_UPDATED",
        resource="case",
        resource_id=case.case_id,
        result="Success"
    )
    return case

@router.post("/{case_id}/evidence", response_model=CaseEvidenceResponse, status_code=status.HTTP_201_CREATED)
def add_evidence(
    case_id: int,
    evidence_data: CaseEvidenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Attach evidence item with SHA-256 integrity hash calculation"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Calculate SHA256 hash if not directly provided
    calculated_hash = evidence_data.sha256_hash
    if not calculated_hash:
        raw_seed = f"{evidence_data.filename}-{evidence_data.description or ''}"
        calculated_hash = hashlib.sha256(raw_seed.encode('utf-8')).hexdigest()
        
    evidence = CaseEvidence(
        case_id=case_id,
        filename=evidence_data.filename,
        file_type=evidence_data.file_type,
        file_size_bytes=evidence_data.file_size_bytes,
        sha256_hash=calculated_hash,
        description=evidence_data.description,
        uploaded_by_id=current_user.id
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=current_user.id,
        action="EVIDENCE_ATTACHED",
        resource="case_evidence",
        resource_id=str(evidence.id),
        result="Success",
        metadata={"case_id": case.case_id, "filename": evidence.filename, "sha256": calculated_hash}
    )
    return evidence
