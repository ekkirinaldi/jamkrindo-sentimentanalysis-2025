"""
Legal records response schemas.
Case type labels: pidana, perdata, tata usaha negara, niaga
Severity labels: tinggi, sedang, rendah, tidak ada
"""

from pydantic import BaseModel
from typing import List, Optional


class LegalCase(BaseModel):
    """Individual legal case."""
    case_number: str
    case_date: str
    case_title: Optional[str] = None
    case_type: str  # pidana, perdata, tata usaha negara, niaga
    verdict_summary: Optional[str] = None
    severity: str  # tinggi, sedang, rendah, tidak ada
    source_url: Optional[str] = None


class LegalRecords(BaseModel):
    """Legal records response."""
    company_name: str
    cases_found: int
    cases: List[LegalCase]
    max_severity: str  # tinggi, sedang, rendah, tidak ada
    timestamp: str
    source: str = "mahkamah_agung"
    error: Optional[str] = None

