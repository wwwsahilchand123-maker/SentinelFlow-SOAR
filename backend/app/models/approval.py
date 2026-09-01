from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ApprovalStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    EXPIRED = "Expired"

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True, nullable=False)
    action_type = Column(String, nullable=False)
    target = Column(String, nullable=False)
    risk_score = Column(Float, default=0.0)
    reason = Column(Text, nullable=True)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True)
    
    playbook_id = Column(Integer, ForeignKey("playbooks.id"), nullable=True)
    execution_id = Column(Integer, ForeignKey("playbook_executions.id"), nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    decision_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)
    
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    playbook = relationship("Playbook", foreign_keys=[playbook_id])
    execution = relationship("PlaybookExecution", foreign_keys=[execution_id])
    incident = relationship("Incident", foreign_keys=[incident_id])
