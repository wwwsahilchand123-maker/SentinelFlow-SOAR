from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum

class AssetType(str, enum.Enum):
    SERVER = "Server"
    WORKSTATION = "Workstation"
    FIREWALL = "Firewall"
    ROUTER = "Router"
    DATABASE = "Database"
    CLOUD_RESOURCE = "Cloud Resource"

class AssetCriticality(str, enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class AssetStatus(str, enum.Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"
    QUARANTINED = "Quarantined"
    ISOLATED = "Isolated"
    MAINTENANCE = "Maintenance"

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String, unique=True, index=True)
    hostname = Column(String, nullable=False)
    asset_type = Column(SQLEnum(AssetType), default=AssetType.SERVER)
    ip_address = Column(String)
    operating_system = Column(String)
    owner = Column(String)
    criticality = Column(SQLEnum(AssetCriticality), default=AssetCriticality.MEDIUM)
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.ONLINE)
    last_seen = Column(DateTime(timezone=True), default=func.now())
    tags = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
