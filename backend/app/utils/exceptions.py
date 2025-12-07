"""
Custom exceptions with Bahasa Indonesia error messages.
All exception messages in Indonesian.
"""


class PerplexityAPIError(Exception):
    """Error API Perplexity."""
    pass


class SentimentAnalysisError(Exception):
    """Gagal menganalisis sentimen."""
    pass


class CrawlerError(Exception):
    """Gagal melakukan web scraping."""
    pass


class MahkamahCrawlerError(Exception):
    """Exception untuk kesalahan pengikisan Mahkamah Agung."""
    pass


class RiskScoringError(Exception):
    """Gagal menghitung skor risiko."""
    pass


class DatabaseError(Exception):
    """Gagal mengakses database."""
    pass

