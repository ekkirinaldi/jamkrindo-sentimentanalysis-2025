"""
Legal records ORM model.
Stores Indonesian case types and severity levels in Bahasa Indonesia.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.company import Base


class LegalRecord(Base):
    """Legal records model with Indonesian case types and severity."""
    __tablename__ = "legal_records"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    case_number = Column(String(255), nullable=True)
    case_date = Column(String(50), nullable=True)  # Indonesian date formats
    case_type = Column(String(50), nullable=True)  # pidana, perdata, tata usaha negara, niaga
    verdict_text = Column(Text, nullable=True)  # UTF-8 for Indonesian text
    severity_level = Column(String(20), nullable=True)  # tinggi, sedang, rendah, tidak ada
    source_url = Column(String(500), nullable=True)
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    company = relationship("Company", back_populates="legal_records")

