import pytest
from app.services.risk_scoring import RiskScoringEngine
from app.models.alert import AlertSeverity
from app.models.indicator import IndicatorReputation
from app.models.asset import AssetCriticality

def test_deterministic_risk_scoring_bounds():
    # Minimal score case (benign, low severity, low asset, 0 attempts)
    result_low = RiskScoringEngine.calculate_risk(
        severity=AlertSeverity.LOW,
        indicator_reputation=IndicatorReputation.BENIGN,
        asset_criticality=AssetCriticality.LOW,
        failed_attempts=0
    )
    score_low = result_low["risk_score"]
    assert 0.0 <= score_low <= 100.0
    assert score_low <= 30.0
    assert "severity_score" in result_low["breakdown"]
    
    # Maximal score case (critical, malicious, high confidence, critical asset, 20 attempts)
    result_high = RiskScoringEngine.calculate_risk(
        severity=AlertSeverity.CRITICAL,
        indicator_reputation=IndicatorReputation.MALICIOUS,
        asset_criticality=AssetCriticality.CRITICAL,
        failed_attempts=25
    )
    score_high = result_high["risk_score"]
    assert 0.0 <= score_high <= 100.0
    assert score_high >= 80.0
    assert result_high["risk_level"] == "Critical"
    assert result_high["breakdown"]["severity_score"] == 35.0
    assert result_high["breakdown"]["threat_score"] == 35.0

def test_risk_scoring_reproducibility():
    res1 = RiskScoringEngine.calculate_risk(
        severity=AlertSeverity.HIGH,
        indicator_reputation=IndicatorReputation.SUSPICIOUS,
        asset_criticality=AssetCriticality.HIGH,
        failed_attempts=5
    )
    res2 = RiskScoringEngine.calculate_risk(
        severity=AlertSeverity.HIGH,
        indicator_reputation=IndicatorReputation.SUSPICIOUS,
        asset_criticality=AssetCriticality.HIGH,
        failed_attempts=5
    )
    assert res1["risk_score"] == res2["risk_score"]
    assert res1["risk_level"] == res2["risk_level"]
