"""
Company ORM model.
Stores company information with UTF-8 support for Indonesian text.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Company(Base):
    """Company model for storing Indonesian company names (PT, CV, UD formats)."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    pt_name = Column(String(255), nullable=False, unique=True, index=True)  # UTF-8 for Indonesian text
    perplexity_search_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    company_data = relationship("CompanyData", back_populates="company", cascade="all, delete-orphan")
    sentiment_results = relationship("SentimentResult", back_populates="company", cascade="all, delete-orphan")
    legal_records = relationship("LegalRecord", back_populates="company", cascade="all, delete-orphan")
    analysis_summaries = relationship("AnalysisSummary", back_populates="company", cascade="all, delete-orphan")


class CompanyData(Base):
    """Company data model for storing raw extracted content."""
    __tablename__ = "company_data"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    source = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=True)  # UTF-8 for Indonesian content
    extracted_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    company = relationship("Company", back_populates="company_data")

