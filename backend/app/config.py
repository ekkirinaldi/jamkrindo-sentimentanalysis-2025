"""
Configuration module for the application.
Loads environment variables and defines configuration constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Perplexity API
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MAX_REQUESTS_PER_DAY = int(os.getenv("PERPLEXITY_MAX_REQUESTS_PER_DAY", "100"))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/credit_scoring.db")

# Server
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Crawling
MAHKAMAH_CRAWL_DELAY = float(os.getenv("MAHKAMAH_CRAWL_DELAY_SECONDS", "0.5"))

# NLP Model
SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "distilbert-base-multilingual-uncased-sentiment")
TORCH_DEVICE = os.getenv("TORCH_DEVICE", "cpu")  # Always CPU for on-premise

