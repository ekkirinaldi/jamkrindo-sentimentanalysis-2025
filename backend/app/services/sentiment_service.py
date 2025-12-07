"""
Sentiment analysis service using VADER and Transformers.
Optimized for Indonesian text processing with Bahasa Indonesia labels.
"""

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import numpy as np
from typing import Dict, List, Optional
from app.config import TORCH_DEVICE
from app.utils.logger import logger

# Download NLTK data (will be cached)
try:
    nltk.download('vader_lexicon', quiet=True)
except:
    pass  # Already downloaded


class SentimentAnalysisService:
    """Service for sentiment analysis with Indonesian language support."""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self._transformer = None  # Lazy loading
    
    def _get_transformer(self):
        """Lazy load transformer model only when needed."""
        if self._transformer is None:
            # Multilingual model specifically supports Indonesian language
            # Using a valid multilingual sentiment model
            try:
                logger.info("Loading sentiment analysis model (first time, may take a moment)...")
                self._transformer = pipeline(
                    "sentiment-analysis",
                    model="nlptown/bert-base-multilingual-uncased-sentiment",
                    device=-1 if TORCH_DEVICE == "cpu" else 0  # CPU mode for on-premise
                )
                logger.info("Sentiment model loaded successfully")
            except Exception as e:
                # Fallback to a simpler model if the above fails
                logger.warning(f"Failed to load primary model, using fallback: {str(e)}")
                try:
                    self._transformer = pipeline(
                        "sentiment-analysis",
                        model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
                        device=-1 if TORCH_DEVICE == "cpu" else 0
                    )
                    logger.info("Fallback sentiment model loaded successfully")
                except Exception as e2:
                    logger.error(f"Failed to load fallback model: {str(e2)}")
                    # Use default model as last resort
                    self._transformer = pipeline(
                        "sentiment-analysis",
                        device=-1 if TORCH_DEVICE == "cpu" else 0
                    )
        return self._transformer
    
    @property
    def transformer(self):
        """Property to access transformer with lazy loading."""
        return self._get_transformer()
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of text using VADER + Transformers.
        Optimized for Indonesian text patterns.
        
        Returns:
            {
              "vader_scores": {...},
              "transformer_scores": {...},
              "consensus_score": float (0-1),
              "sentiment_label": str (POSITIF, NETRAL, NEGATIF),
              "confidence": float,
              "text_length": int
            }
        """
        if not text or len(text.strip()) < 10:
            return {"error": "Text terlalu pendek"}
        
        # VADER analysis (works with English, multilingual model handles Indonesian better)
        vader_scores = self.vader.polarity_scores(text)
        
        # Transformer analysis (handles Indonesian text)
        # Limit to 512 tokens for transformer model
        transformer_result = self.transformer(text[:512])[0]
        transformer_label = transformer_result['label']
        transformer_score = self._transform_label_to_score(transformer_label)
        transformer_confidence = transformer_result['score']
        
        # Consensus (average of both)
        vader_normalized = (vader_scores['compound'] + 1) / 2
        consensus_score = (vader_normalized + transformer_score) / 2
        
        # Determine sentiment label in Bahasa Indonesia
        if consensus_score >= 0.6:
            sentiment_label = "POSITIF"
        elif consensus_score <= 0.4:
            sentiment_label = "NEGATIF"
        else:
            sentiment_label = "NETRAL"
        
        return {
            "vader_scores": {
                "compound": vader_scores['compound'],
                "positive": vader_scores['pos'],
                "negative": vader_scores['neg'],
                "neutral": vader_scores['neu']
            },
            "transformer_scores": {
                "label": transformer_label,
                "score": transformer_score,
                "confidence": transformer_confidence
            },
            "consensus_score": round(consensus_score, 3),
            "sentiment_label": sentiment_label,
            "confidence": min(transformer_confidence, abs(vader_scores['compound'])),
            "text_length": len(text.split())
        }
    
    def analyze_batch(self, texts: List[str]) -> Dict:
        """Analyze multiple texts and return aggregated statistics."""
        results = [self.analyze_text(text) for text in texts]
        
        valid_scores = [r['consensus_score'] for r in results if 'consensus_score' in r]
        
        if not valid_scores:
            return {"error": "Tidak ada teks yang valid"}
        
        return {
            "total_texts": len(texts),
            "valid_analyses": len(valid_scores),
            "average_score": round(np.mean(valid_scores), 3),
            "std_dev": round(np.std(valid_scores), 3),
            "min_score": min(valid_scores),
            "max_score": max(valid_scores),
            "positive_count": sum(1 for s in valid_scores if s >= 0.6),
            "neutral_count": sum(1 for s in valid_scores if 0.4 < s < 0.6),
            "negative_count": sum(1 for s in valid_scores if s <= 0.4),
            "details": results
        }
    
    def _transform_label_to_score(self, label: str) -> float:
        """Convert transformer label (1-5) to score (0-1)."""
        mapping = {
            "1 star": 0.0,
            "2 stars": 0.25,
            "3 stars": 0.5,
            "4 stars": 0.75,
            "5 stars": 1.0,
            "1": 0.0,
            "2": 0.25,
            "3": 0.5,
            "4": 0.75,
            "5": 1.0,
            "POSITIVE": 0.75,
            "NEGATIVE": 0.25,
            "NEUTRAL": 0.5
        }
        return mapping.get(label, 0.5)

