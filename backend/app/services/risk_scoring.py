from typing import Dict, Any, Optional
from app.models.alert import AlertSeverity
from app.models.indicator import IndicatorReputation
from app.models.asset import AssetCriticality

class RiskScoringEngine:
    """
    Deterministic 5-Factor Risk Scoring Engine
    
    Formula:
    Risk Score = min(100.0, Severity_Weight + Threat_Intel_Weight + Asset_Weight + Behavior_Multiplier + History_Weight)
    
    Score Bands:
    - 0  to 30: Low
    - 31 to 60: Medium
    - 61 to 80: High
    - 81 to 100: Critical
    """
    
    SEVERITY_WEIGHTS = {
        AlertSeverity.CRITICAL: 35.0,
        AlertSeverity.HIGH: 25.0,
        AlertSeverity.MEDIUM: 15.0,
        AlertSeverity.LOW: 5.0,
        AlertSeverity.INFORMATIONAL: 0.0
    }
    
    REPUTATION_WEIGHTS = {
        IndicatorReputation.MALICIOUS: 35.0,
        IndicatorReputation.SUSPICIOUS: 20.0,
        IndicatorReputation.UNKNOWN: 10.0,
        IndicatorReputation.BENIGN: 0.0
    }
    
    ASSET_CRITICALITY_WEIGHTS = {
        AssetCriticality.CRITICAL: 20.0,
        AssetCriticality.HIGH: 15.0,
        AssetCriticality.MEDIUM: 10.0,
        AssetCriticality.LOW: 5.0
    }

    @classmethod
    def calculate_risk(
        cls,
        severity: AlertSeverity,
        indicator_reputation: IndicatorReputation = IndicatorReputation.UNKNOWN,
        asset_criticality: AssetCriticality = AssetCriticality.MEDIUM,
        failed_attempts: int = 0,
        historical_incident_count: int = 0
    ) -> Dict[str, Any]:
        """
        Calculate total risk score with complete factor breakdown
        """
        severity_score = cls.SEVERITY_WEIGHTS.get(severity, 10.0)
        threat_score = cls.REPUTATION_WEIGHTS.get(indicator_reputation, 10.0)
        asset_score = cls.ASSET_CRITICALITY_WEIGHTS.get(asset_criticality, 10.0)
        
        # Behavior score (e.g. brute force failed attempts, capped at 20)
        behavior_score = min(float(failed_attempts) * 2.0, 20.0) if failed_attempts > 0 else 0.0
        
        # History score (previous incidents involving this entity, capped at 10)
        history_score = min(float(historical_incident_count) * 2.5, 10.0) if historical_incident_count > 0 else 0.0
        
        total_score = min(100.0, max(0.0, severity_score + threat_score + asset_score + behavior_score + history_score))
        
        level = cls.get_risk_level(total_score)
        
        return {
            "risk_score": round(total_score, 1),
            "risk_level": level,
            "breakdown": {
                "severity_score": severity_score,
                "threat_score": threat_score,
                "asset_score": asset_score,
                "behavior_score": behavior_score,
                "history_score": history_score
            },
            "formula": "Severity(max 35) + Threat(max 35) + Asset(max 20) + Behavior(max 20) + History(max 10) [Capped at 100]"
        }

    @classmethod
    def calculate_alert_risk(
        cls,
        severity: AlertSeverity,
        indicator_reputation: IndicatorReputation = IndicatorReputation.UNKNOWN,
        asset_criticality: AssetCriticality = AssetCriticality.MEDIUM,
        failed_attempts: int = 0
    ) -> float:
        """Helper returning float score directly for backward compatibility"""
        res = cls.calculate_risk(severity, indicator_reputation, asset_criticality, failed_attempts)
        return res["risk_score"]

    @staticmethod
    def get_risk_level(score: float) -> str:
        """Convert numeric risk score to severity tier"""
        if score >= 81.0:
            return "Critical"
        elif score >= 61.0:
            return "High"
        elif score >= 31.0:
            return "Medium"
        else:
            return "Low"

RiskScoringService = RiskScoringEngine
