from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
import httpx
import logging
import re
from app.config import settings
from app.models.indicator import IndicatorType, IndicatorReputation

logger = logging.getLogger(__name__)

# In-memory lookup cache to reduce redundant API calls
_THREAT_INTEL_CACHE: Dict[str, Dict[str, Any]] = {}

class ThreatIntelProvider(ABC):
    """Abstract Base Class for Threat Intelligence Providers"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def is_live(self) -> bool:
        pass

    @abstractmethod
    async def lookup(self, value: str, indicator_type: IndicatorType) -> Optional[Dict[str, Any]]:
        pass

class AbuseIPDBProvider(ThreatIntelProvider):
    """Live AbuseIPDB Threat Intelligence Provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ABUSEIPDB_API_KEY

    @property
    def name(self) -> str:
        return "AbuseIPDB (Live)"
        
    @property
    def is_live(self) -> bool:
        return bool(self.api_key)

    async def lookup(self, value: str, indicator_type: IndicatorType) -> Optional[Dict[str, Any]]:
        if not self.api_key or indicator_type not in (IndicatorType.IPV4, IndicatorType.IPV6):
            return None
        
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                response = await client.get(
                    "https://api.abuseipdb.com/api/v2/check",
                    headers={"Key": self.api_key, "Accept": "application/json"},
                    params={"ipAddress": value, "maxAgeInDays": 90}
                )
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    score = float(data.get("abuseConfidenceScore", 0))
                    
                    if score >= 70:
                        reputation = IndicatorReputation.MALICIOUS
                    elif score >= 25:
                        reputation = IndicatorReputation.SUSPICIOUS
                    else:
                        reputation = IndicatorReputation.BENIGN
                        
                    return {
                        "provider": self.name,
                        "is_simulation": False,
                        "reputation": reputation,
                        "confidence": score,
                        "raw_data": data,
                        "details": f"Abuse Confidence Score: {score}% | Country: {data.get('countryCode', 'N/A')}"
                    }
        except Exception as e:
            logger.warning(f"AbuseIPDB lookup failed for {value}: {e}")
        return None

class VirusTotalProvider(ThreatIntelProvider):
    """Live VirusTotal Threat Intelligence Provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.VIRUSTOTAL_API_KEY

    @property
    def name(self) -> str:
        return "VirusTotal (Live)"
        
    @property
    def is_live(self) -> bool:
        return bool(self.api_key)

    async def lookup(self, value: str, indicator_type: IndicatorType) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None
            
        endpoint_map = {
            IndicatorType.IPV4: f"https://www.virustotal.com/api/v3/ip_addresses/{value}",
            IndicatorType.DOMAIN: f"https://www.virustotal.com/api/v3/domains/{value}",
            IndicatorType.SHA256: f"https://www.virustotal.com/api/v3/files/{value}",
            IndicatorType.MD5: f"https://www.virustotal.com/api/v3/files/{value}",
        }
        
        url = endpoint_map.get(indicator_type)
        if not url:
            return None
            
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                response = await client.get(
                    url,
                    headers={"x-apikey": self.api_key, "Accept": "application/json"}
                )
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    stats = data.get("attributes", {}).get("last_analysis_stats", {})
                    malicious = stats.get("malicious", 0)
                    suspicious = stats.get("suspicious", 0)
                    total = sum(stats.values()) or 1
                    
                    confidence = min(100.0, float((malicious * 2 + suspicious) / total * 100))
                    
                    if malicious >= 5:
                        reputation = IndicatorReputation.MALICIOUS
                    elif malicious > 0 or suspicious >= 2:
                        reputation = IndicatorReputation.SUSPICIOUS
                    else:
                        reputation = IndicatorReputation.BENIGN
                        
                    return {
                        "provider": self.name,
                        "is_simulation": False,
                        "reputation": reputation,
                        "confidence": round(confidence, 1),
                        "raw_data": stats,
                        "details": f"VT Detections: {malicious} malicious / {suspicious} suspicious out of {total} engines"
                    }
        except Exception as e:
            logger.warning(f"VirusTotal lookup failed for {value}: {e}")
        return None

class MockThreatIntelProvider(ThreatIntelProvider):
    """Deterministic Simulation Threat Intelligence Provider clearly labeled as SIMULATED DATA"""
    
    @property
    def name(self) -> str:
        return "SentinelFlow Mock Threat Intel (SIMULATED DATA)"
        
    @property
    def is_live(self) -> bool:
        return False

    async def lookup(self, value: str, indicator_type: IndicatorType) -> Dict[str, Any]:
        val = str(value).lower().strip()
        
        # Deterministic simulation based on recognizable attack indicators
        if any(term in val for term in ["tor", "185.220.101", "185.220.102", "botnet", "deadbeef", "bad-actor", "malicious-domain.xyz", "ransomware"]):
            return {
                "provider": self.name,
                "is_simulation": True,
                "reputation": IndicatorReputation.MALICIOUS,
                "confidence": 94.0,
                "raw_data": {"simulated": True, "category": "Known Threat Actor / Botnet / Tor Exit", "flagged_by": "Heuristic Engine"},
                "details": "SIMULATED DATA: Flagged by simulated threat intelligence engine as High-Risk Malicious entity."
            }
        elif any(term in val for term in ["198.51.100", "suspicious", "anomalous", "temp-mail", "unknown-asn"]):
            return {
                "provider": self.name,
                "is_simulation": True,
                "reputation": IndicatorReputation.SUSPICIOUS,
                "confidence": 65.0,
                "raw_data": {"simulated": True, "category": "Suspicious ASN / Geolocation Anomaly"},
                "details": "SIMULATED DATA: Flagged by simulated threat intelligence engine as Suspicious."
            }
        elif any(term in val for term in ["google", "microsoft", "cloudflare", "1.1.1.1", "8.8.8.8", "192.168.", "10.0."]):
            return {
                "provider": self.name,
                "is_simulation": True,
                "reputation": IndicatorReputation.BENIGN,
                "confidence": 99.0,
                "raw_data": {"simulated": True, "category": "Trusted Infrastructure / Internal Network"},
                "details": "SIMULATED DATA: Verified benign infrastructure."
            }
        else:
            # Deterministic hash score for consistent simulation
            score = (sum(ord(c) for c in val) % 100)
            if score > 75:
                rep = IndicatorReputation.MALICIOUS
                conf = 82.0
            elif score > 40:
                rep = IndicatorReputation.SUSPICIOUS
                conf = 58.0
            else:
                rep = IndicatorReputation.UNKNOWN
                conf = 20.0
                
            return {
                "provider": self.name,
                "is_simulation": True,
                "reputation": rep,
                "confidence": conf,
                "raw_data": {"simulated": True, "score": score},
                "details": f"SIMULATED DATA: Heuristic reputation score evaluated as {rep.value}."
            }

class ThreatIntelligenceService:
    """Unified Threat Intelligence Service with live provider fallback and caching"""
    
    def __init__(self):
        self.providers: List[ThreatIntelProvider] = [
            AbuseIPDBProvider(),
            VirusTotalProvider(),
            MockThreatIntelProvider()
        ]
        
    @staticmethod
    def detect_indicator_type(value: str) -> IndicatorType:
        val = value.strip()
        # IPv4
        if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", val):
            return IndicatorType.IPV4
        # IPv6
        if ":" in val and len(val) >= 3:
            return IndicatorType.IPV6
        # Email
        if "@" in val and "." in val:
            return IndicatorType.EMAIL
        # Hashes
        if re.match(r"^[a-fA-F0-9]{64}$", val):
            return IndicatorType.SHA256
        if re.match(r"^[a-fA-F0-9]{32}$", val):
            return IndicatorType.MD5
        if re.match(r"^[a-fA-F0-9]{40}$", val):
            return IndicatorType.SHA1
        # URL
        if val.startswith("http://") or val.startswith("https://"):
            return IndicatorType.URL
        # Domain
        return IndicatorType.DOMAIN

    async def lookup_indicator(self, value: str, indicator_type: Optional[IndicatorType] = None) -> Dict[str, Any]:
        val = value.strip()
        if not indicator_type:
            indicator_type = self.detect_indicator_type(val)
            
        cache_key = f"{indicator_type.value}:{val}"
        now = datetime.now(timezone.utc)
        
        # Check cache
        if cache_key in _THREAT_INTEL_CACHE:
            cached = _THREAT_INTEL_CACHE[cache_key]
            if now - cached["cached_at"] < timedelta(hours=settings.THREAT_INTEL_CACHE_TTL_HOURS):
                return cached["data"]
                
        # Query providers
        result = None
        for provider in self.providers:
            res = await provider.lookup(val, indicator_type)
            if res:
                result = {
                    "value": val,
                    "type": indicator_type.value if hasattr(indicator_type, "value") else str(indicator_type),
                    "reputation": res["reputation"],
                    "confidence": res["confidence"],
                    "provider": res["provider"],
                    "is_simulation": res.get("is_simulation", True),
                    "details": res.get("details", ""),
                    "raw_data": res.get("raw_data", {}),
                    "lookup_timestamp": now.isoformat()
                }
                break
                
        if not result:
            result = {
                "value": val,
                "type": indicator_type.value if hasattr(indicator_type, "value") else str(indicator_type),
                "reputation": IndicatorReputation.UNKNOWN,
                "confidence": 0.0,
                "provider": "Mock Threat Intel (SIMULATED DATA)",
                "is_simulation": True,
                "details": "No threat intel data found.",
                "raw_data": {},
                "lookup_timestamp": now.isoformat()
            }
            
        # Store in cache
        _THREAT_INTEL_CACHE[cache_key] = {"data": result, "cached_at": now}
        return result

ThreatIntelService = ThreatIntelligenceService

