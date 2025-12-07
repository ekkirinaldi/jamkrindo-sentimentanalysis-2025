"""
News article schemas with sentiment analysis.
All field descriptions in Bahasa Indonesia.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class NewsArticle(BaseModel):
    """Individual news article with sentiment."""
    title: str = Field(..., description="Judul berita")
    summary: str = Field(..., description="Ringkasan berita")
    source_url: str = Field(..., description="URL sumber berita")
    date: Optional[str] = Field(None, description="Tanggal berita (jika tersedia)")
    sentiment_label: str = Field(..., description="Label sentimen (POSITIF, NETRAL, NEGATIF)")
    sentiment_score: float = Field(..., description="Skor sentimen (0.0-1.0)")
    confidence: float = Field(..., description="Tingkat kepercayaan analisis")


class NewsAnalysisRequest(BaseModel):
    """Request model for news analysis."""
    company_name: str = Field(
        ...,
        description="Nama perusahaan (contoh: Bank Mandiri)",
        min_length=2,
        max_length=255
    )
    limit: int = Field(
        10,
        description="Jumlah berita terbaru yang dicari (default: 10)",
        ge=1,
        le=20
    )

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Bank Mandiri",
                "limit": 10
            }
        }


class NewsAnalysisResponse(BaseModel):
    """Response model for news analysis."""
    company_name: str = Field(..., description="Nama perusahaan yang dianalisis")
    total_articles: int = Field(..., description="Jumlah total artikel yang ditemukan")
    positive_count: int = Field(..., description="Jumlah berita positif")
    neutral_count: int = Field(..., description="Jumlah berita netral")
    negative_count: int = Field(..., description="Jumlah berita negatif")
    articles: List[NewsArticle] = Field(..., description="Daftar artikel dengan analisis sentimen")
    timestamp: str = Field(..., description="Waktu analisis")
    status: str = Field(..., description="Status analisis (sukses/gagal)")
    error: Optional[str] = Field(None, description="Pesan kesalahan jika analisis gagal")

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Bank Mandiri",
                "total_articles": 10,
                "positive_count": 6,
                "neutral_count": 2,
                "negative_count": 2,
                "articles": [],
                "timestamp": "2025-12-06T17:32:00",
                "status": "sukses"
            }
        }

