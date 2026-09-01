from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.case import CasePriority, CaseStatus

class CaseEvidenceBase(BaseModel):
    filename: str
    file_type: str
    file_size_bytes: int = 0
    sha256_hash: str
    description: Optional[str] = None

class CaseEvidenceCreate(BaseModel):
    filename: str
    file_type: str
    file_size_bytes: int = 0
    sha256_hash: Optional[str] = None
    description: Optional[str] = None

class CaseEvidenceResponse(CaseEvidenceBase):
    id: int
    case_id: int
    uploaded_by_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: CasePriority = CasePriority.MEDIUM
    status: CaseStatus = CaseStatus.OPEN
    assigned_analyst_id: Optional[int] = None

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[CasePriority] = None
    status: Optional[CaseStatus] = None
    assigned_analyst_id: Optional[int] = None

class CaseResponse(CaseBase):
    id: int
    case_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    evidence: List[CaseEvidenceResponse] = []

    class Config:
        from_attributes = True
