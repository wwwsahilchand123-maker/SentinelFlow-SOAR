from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class AlertStatus(str, enum.Enum):
    NEW = "New"
    INVESTIGATING = "Investigating"
    ESCALATED = "Escalated"
    RESOLVED = "Resolved"
    FALSE_POSITIVE = "False Positive"

class AlertSeverity(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True)
    dedup_hash = Column(String, index=True, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    source = Column(String, nullable=False)
    alert_type = Column(String, nullable=False)
    category = Column(String)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.MEDIUM)
    source_ip = Column(String, index=True)
    destination_ip = Column(String)
    username = Column(String, index=True)
    host = Column(String, index=True)
    indicator = Column(String, index=True)
    mitre_technique_id = Column(String, nullable=True)
    description = Column(Text)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.NEW)
    assigned_analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    raw_data = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    assigned_analyst = relationship("User", foreign_keys=[assigned_analyst_id])
    incident = relationship("Incident", back_populates="alerts")
