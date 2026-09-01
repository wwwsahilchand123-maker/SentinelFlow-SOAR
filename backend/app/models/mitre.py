from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for many-to-many relationship
incident_mitre = Table(
    'incident_mitre',
    Base.metadata,
    Column('incident_id', Integer, ForeignKey('incidents.id')),
    Column('technique_id', Integer, ForeignKey('mitre_techniques.id'))
)

class MitreTechnique(Base):
    __tablename__ = "mitre_techniques"
    
    id = Column(Integer, primary_key=True, index=True)
    technique_id = Column(String, unique=True, nullable=False)  # e.g., T1110
    technique_name = Column(String, nullable=False)
    tactic = Column(String, nullable=False)
    description = Column(Text)
