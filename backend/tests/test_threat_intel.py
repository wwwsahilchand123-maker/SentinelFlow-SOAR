import pytest
import asyncio
from app.services.threat_intelligence import ThreatIntelligenceService
from app.models.indicator import IndicatorType, IndicatorReputation

def test_mock_threat_intel_lookup_malicious_ip():
    service = ThreatIntelligenceService()
    result = asyncio.run(service.lookup_indicator("185.220.101.45", IndicatorType.IPV4))
    assert result["value"] == "185.220.101.45"
    assert result["reputation"] == IndicatorReputation.MALICIOUS
    assert result["confidence"] >= 90.0
    assert result["is_simulation"] is True

def test_threat_intel_caching():
    service = ThreatIntelligenceService()
    # First lookup
    res1 = asyncio.run(service.lookup_indicator("8.8.8.8", IndicatorType.IPV4))
    # Second lookup should hit memory cache
    res2 = asyncio.run(service.lookup_indicator("8.8.8.8", IndicatorType.IPV4))
    assert res1["value"] == res2["value"]
    assert res1["reputation"] == res2["reputation"]
