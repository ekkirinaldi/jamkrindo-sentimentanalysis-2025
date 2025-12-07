"""
Sentiment analysis results ORM model.
Stores sentiment labels in Bahasa Indonesia: POSITIF, NETRAL, NEGATIF.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.company import Base


class SentimentResult(Base):
    """Sentiment results model with Indonesian text support."""
    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    text_analyzed = Column(Text, nullable=True)  # UTF-8 for Indonesian text
    positive_score = Column(Float, nullable=True)
    negative_score = Column(Float, nullable=True)
    neutral_score = Column(Float, nullable=True)
    compound_score = Column(Float, nullable=True)
    sentiment_label = Column(String(20), nullable=True)  # POSITIF, NETRAL, NEGATIF
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    company = relationship("Company", back_populates="sentiment_results")

