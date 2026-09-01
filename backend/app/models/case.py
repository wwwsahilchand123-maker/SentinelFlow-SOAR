from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class CasePriority(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class CaseStatus(str, enum.Enum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    PENDING = "Pending"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(SQLEnum(CasePriority), default=CasePriority.MEDIUM)
    status = Column(SQLEnum(CaseStatus), default=CaseStatus.OPEN)
    
    assigned_analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    assigned_analyst = relationship("User", foreign_keys=[assigned_analyst_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    incidents = relationship("Incident", back_populates="case")
    evidence = relationship("CaseEvidence", back_populates="case", cascade="all, delete-orphan")
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan", order_by="CaseNote.created_at")

class CaseEvidence(Base):
    __tablename__ = "case_evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size_bytes = Column(Integer, default=0)
    sha256_hash = Column(String, nullable=False, index=True)
    description = Column(Text)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    case = relationship("Case", back_populates="evidence")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])

class CaseNote(Base):
    __tablename__ = "case_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    case = relationship("Case", back_populates="notes")
    author = relationship("User", foreign_keys=[author_id])
