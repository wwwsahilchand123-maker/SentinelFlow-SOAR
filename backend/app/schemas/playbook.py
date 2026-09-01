from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.playbook import PlaybookStatus, ExecutionStatus

class PlaybookStepBase(BaseModel):
    name: Optional[str] = None
    action: str
    requires_approval: bool = False
    retry_count: int = 0
    parameters: Optional[Dict[str, Any]] = None

class PlaybookStepCreate(PlaybookStepBase):
    order: int
    name: str

class PlaybookStepResponse(PlaybookStepBase):
    id: int
    order: int
    name: str
    
    class Config:
        from_attributes = True

class PlaybookBase(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: Optional[str] = "alert"
    version: Optional[str] = "1.0.0"

class PlaybookCreate(PlaybookBase):
    steps: List[PlaybookStepCreate] = []

class PlaybookUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PlaybookStatus] = None
    trigger_type: Optional[str] = None
    version: Optional[str] = None

class PlaybookResponse(PlaybookBase):
    id: int
    status: PlaybookStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    steps: List[PlaybookStepResponse] = []
    
    class Config:
        from_attributes = True

class ExecutionLogResponse(BaseModel):
    id: int
    timestamp: datetime
    step_name: str
    status: str
    message: Optional[str] = None
    duration_ms: Optional[float] = 0.0
    metadata_info: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class PlaybookExecutionResponse(BaseModel):
    id: int
    execution_id: str
    playbook_id: int
    playbook_version: Optional[str] = "1.0.0"
    status: ExecutionStatus
    trigger_source: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[float] = 0.0
    error_message: Optional[str] = None
    logs: List[ExecutionLogResponse] = []
    
    class Config:
        from_attributes = True
