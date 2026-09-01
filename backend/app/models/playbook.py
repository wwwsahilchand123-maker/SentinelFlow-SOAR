from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class PlaybookStatus(str, enum.Enum):
    ENABLED = "Enabled"
    DISABLED = "Disabled"
    DRAFT = "Draft"

class ExecutionStatus(str, enum.Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    PARTIALLY_COMPLETED = "Partially Completed"
    CANCELLED = "Cancelled"
    WAITING_APPROVAL = "Waiting Approval"

class Playbook(Base):
    __tablename__ = "playbooks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(PlaybookStatus), default=PlaybookStatus.ENABLED)
    trigger_type = Column(String, default="alert")
    version = Column(String, default="1.0.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    steps = relationship("PlaybookStep", back_populates="playbook", cascade="all, delete-orphan", order_by="PlaybookStep.order")
    executions = relationship("PlaybookExecution", back_populates="playbook", cascade="all, delete-orphan")
    versions = relationship("PlaybookVersion", back_populates="playbook", cascade="all, delete-orphan")

class PlaybookVersion(Base):
    __tablename__ = "playbook_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    playbook_id = Column(Integer, ForeignKey("playbooks.id"), nullable=False)
    version = Column(String, nullable=False)
    definition = Column(JSON, nullable=False)
    change_summary = Column(String, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    playbook = relationship("Playbook", back_populates="versions")

class PlaybookStep(Base):
    __tablename__ = "playbook_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    playbook_id = Column(Integer, ForeignKey("playbooks.id"))
    order = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    parameters = Column(JSON)
    requires_approval = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    
    playbook = relationship("Playbook", back_populates="steps")

class PlaybookExecution(Base):
    __tablename__ = "playbook_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, unique=True, index=True)
    playbook_id = Column(Integer, ForeignKey("playbooks.id"))
    playbook_version = Column(String, default="1.0.0")
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING)
    trigger_source = Column(String)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    
    playbook = relationship("Playbook", back_populates="executions")
    logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan", order_by="ExecutionLog.id")

class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("playbook_executions.id"))
    step_id = Column(Integer, nullable=True)
    step_name = Column(String, nullable=False)
    action = Column(String, nullable=True)
    status = Column(String, nullable=False)
    duration_ms = Column(Float, default=0.0)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    execution = relationship("PlaybookExecution", back_populates="logs")
