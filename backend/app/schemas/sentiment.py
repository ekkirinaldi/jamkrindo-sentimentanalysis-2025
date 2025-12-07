"""
Sentiment analysis response schemas.
Sentiment labels as POSITIF, NETRAL, NEGATIF.
"""

from pydantic import BaseModel
from typing import List, Optional


class VaderScores(BaseModel):
    """VADER sentiment scores."""
    compound: float
    positive: float
    negative: float
    neutral: float


class TransformerScores(BaseModel):
    """Transformer sentiment scores."""
    label: str
    score: float
    confidence: float


class SentimentScore(BaseModel):
    """Individual sentiment score result."""
    vader_scores: VaderScores
    transformer_scores: TransformerScores
    consensus_score: float
    sentiment_label: str  # POSITIF, NETRAL, NEGATIF
    confidence: float
    text_length: int


class SentimentAnalysis(BaseModel):
    """Aggregated sentiment analysis results."""
    total_texts: int
    valid_analyses: int
    average_score: float
    std_dev: Optional[float] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    positive_count: int
    neutral_count: int
    negative_count: int
    details: List[SentimentScore]

