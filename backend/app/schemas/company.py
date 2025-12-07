"""
Company request/response schemas.
Field descriptions and validation messages in Bahasa Indonesia.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CompanyAnalysisRequest(BaseModel):
    """Request model for company analysis."""
    pt_name: str = Field(
        ...,
        description="Nama perusahaan (contoh: PT Maju Jaya Sentosa)",
        min_length=2,
        max_length=255
    )
    detailed: bool = Field(
        False,
        description="Apakah mengembalikan detail lengkap catatan hukum"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pt_name": "PT Maju Jaya Sentosa",
                "detailed": False
            }
        }


class CompanyAnalysisResponse(BaseModel):
    """Response model for company analysis."""
    company_name: str
    status: str
    analysis: dict
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "PT Maju Jaya Sentosa",
                "status": "success",
                "analysis": {},
                "timestamp": "2025-12-06T17:32:00"
            }
        }

