from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, ForeignKey, Float, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class IncidentSeverity(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class IncidentStatus(str, enum.Enum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    CONTAINED = "Contained"
    ERADICATED = "Eradicated"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(SQLEnum(IncidentSeverity), default=IncidentSeverity.MEDIUM)
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.OPEN)
    risk_score = Column(Float, default=50.0)
    source = Column(String)
    
    mitre_technique_id = Column(String, nullable=True)
    mitre_tactic = Column(String, nullable=True)
    
    assigned_analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    
    contained_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    assigned_analyst = relationship("User", foreign_keys=[assigned_analyst_id])
    alerts = relationship("Alert", back_populates="incident")
    events = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentEvent.timestamp")
    case = relationship("Case", back_populates="incidents")

class IncidentEvent(Base):
    __tablename__ = "incident_events"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    event_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    details = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    incident = relationship("Incident", back_populates="events")
    created_by = relationship("User", foreign_keys=[created_by_id])
