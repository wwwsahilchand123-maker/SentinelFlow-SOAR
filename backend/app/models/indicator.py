from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, Float, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base
import enum

class IndicatorType(str, enum.Enum):
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    DOMAIN = "domain"
    URL = "url"
    SHA256 = "sha256"
    MD5 = "md5"
    SHA1 = "sha1"
    EMAIL = "email"

class IndicatorReputation(str, enum.Enum):
    MALICIOUS = "Malicious"
    SUSPICIOUS = "Suspicious"
    BENIGN = "Benign"
    UNKNOWN = "Unknown"

class Indicator(Base):
    __tablename__ = "indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, index=True, nullable=False)
    indicator_type = Column(SQLEnum(IndicatorType), nullable=False, index=True)
    reputation = Column(SQLEnum(IndicatorReputation), default=IndicatorReputation.UNKNOWN, index=True)
    confidence = Column(Float, default=0.0)
    source = Column(String)
    tags = Column(String)  # Comma-separated tags
    is_simulation = Column(Boolean, default=True)
    raw_data = Column(JSON, nullable=True)
    
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
