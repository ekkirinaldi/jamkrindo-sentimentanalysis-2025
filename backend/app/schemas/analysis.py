"""
Analysis summary response schemas.
Risk level labels: HIJAU, KUNING, MERAH
Recommendation text in Bahasa Indonesia.
"""

from pydantic import BaseModel


class RiskAssessmentDetails(BaseModel):
    """Risk assessment details."""
    total_texts_analyzed: int
    positive_texts: int
    negative_texts: int
    legal_cases_found: int
    max_case_severity: str


class RiskAssessment(BaseModel):
    """Risk assessment response."""
    risk_score: float
    risk_level: str  # HIJAU, KUNING, MERAH
    sentiment_component: float
    mentions_component: float
    legal_component: float
    details: RiskAssessmentDetails
    recommendation: str  # Bahasa Indonesia recommendation text

