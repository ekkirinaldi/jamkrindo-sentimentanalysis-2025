"""
Analysis summary ORM model.
Stores risk levels and recommendations in Bahasa Indonesia.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.company import Base


class AnalysisSummary(Base):
    """Analysis summary model with Indonesian risk levels and recommendations."""
    __tablename__ = "analysis_summary"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    sentiment_avg_score = Column(Float, nullable=True)
    legal_records_count = Column(Integer, nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)  # HIJAU, KUNING, MERAH
    recommendation = Column(String(500), nullable=True)  # UTF-8 for Bahasa Indonesia recommendations
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    company = relationship("Company", back_populates="analysis_summaries")

