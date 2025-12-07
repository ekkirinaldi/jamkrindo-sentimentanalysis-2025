# Backend Technical Specifications

## 1. Service Dependencies

### Python Packages
```
# Core Framework
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.4.2

# Database
sqlalchemy==2.0.23
# sqlite3 (built-in)

# Web Scraping
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3

# NLP & Sentiment Analysis
nltk==3.8.1
transformers==4.35.2
torch==2.1.1+cpu  # CPU-only version for on-premise
numpy==1.26.2

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.6
python-dateutil==2.8.2
```

### System Requirements
```
Python: 3.10+
pip: 23.0+
Virtual Environment: venv
Disk Space: 2GB (for ML models)
Memory: 1.5GB minimum (models + runtime)
```

---

## 2. Backend Project Structure

```
backend/
├── main.py                          # FastAPI app entry
├── requirements.txt                 # Dependencies list
├── .env.example                     # Template
├── Dockerfile                       # Container definition
│
├── app/
│   ├── __init__.py
│   ├── config.py                    # Settings & env vars
│   ├── database.py                  # SQLAlchemy setup
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── company.py               # ORM models
│   │   ├── sentiment.py
│   │   ├── legal_record.py
│   │   └── analysis_summary.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── company.py               # Request/Response models
│   │   ├── sentiment.py
│   │   ├── legal.py
│   │   └── analysis.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── perplexity_service.py    # API integration
│   │   ├── sentiment_service.py     # VADER + Transformers
│   │   ├── mahkamah_crawler.py      # Web scraper
│   │   ├── risk_scoring.py          # Risk calculation
│   │   └── data_processor.py        # Text cleaning
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── company.py           # Company endpoints
│   │       ├── analysis.py          # Analysis endpoints
│   │       └── health.py            # Health check
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                # Logging setup
│       └── exceptions.py            # Custom exceptions
│
└── tests/
    ├── test_sentiment.py
    ├── test_crawler.py
    └── test_risk_scoring.py
```

---

## 3. Core Services Implementation

### PerplexityService

```python
# app/services/perplexity_service.py

import os
import re
import asyncio
from typing import Dict, Any
import httpx
from dotenv import load_dotenv

class PerplexityService:
    BASE_URL = "https://api.perplexity.ai"
    MODEL = "pplx-7b-online"  # Online model for current info
    
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY required")
    
    async def search_company(self, company_name: str) -> Dict[str, Any]:
        """
        Search Perplexity API for company information.
        
        Args:
            company_name: PT name (e.g., "PT Maju Jaya")
        
        Returns:
            {
              "raw_response": {...},
              "extracted_text": str,
              "sources": [urls],
              "query": str,
              "timestamp": str
            }
        """
        query = f"""
        Search for information about "{company_name}" Indonesia.
        Include: background, news, reputation, operations, controversies.
        Focus on credit assessment relevance.
        """
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.MODEL,
                        "messages": [{"role": "user", "content": query}],
                        "max_tokens": 2000,
                        "temperature": 0.2
                    }
                )
            
            response.raise_for_status()
            result = response.json()
            
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            sources = result.get("citations", [])
            
            return {
                "raw_response": result,
                "extracted_text": content,
                "sources": sources,
                "query": company_name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Perplexity API error: {str(e)}")
    
    def extract_sentiment_text(self, raw_text: str) -> str:
        """Clean and extract text for sentiment analysis."""
        text = re.sub(r'http[s]?://\S+', '', raw_text)  # Remove URLs
        text = ' '.join(text.split())  # Normalize whitespace
        text = re.sub(r'[^\w\s.,-]', '', text)  # Keep basic punctuation
        return text.strip()
```

### SentimentAnalysisService

```python
# app/services/sentiment_service.py

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import numpy as np
from typing import Dict, List

nltk.download('vader_lexicon', quiet=True)

class SentimentAnalysisService:
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.transformer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-multilingual-uncased-sentiment",
            device=-1  # CPU mode
        )
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of text using VADER + Transformers.
        
        Returns:
            {
              "vader_scores": {...},
              "transformer_scores": {...},
              "consensus_score": float (0-1),
              "sentiment_label": str,
              "confidence": float,
              "text_length": int
            }
        """
        if not text or len(text.strip()) < 10:
            return {"error": "Text too short"}
        
        # VADER analysis
        vader_scores = self.vader.polarity_scores(text)
        
        # Transformer analysis
        transformer_result = self.transformer(text[:512])[0]
        transformer_label = transformer_result['label']
        transformer_score = self._transform_label_to_score(transformer_label)
        transformer_confidence = transformer_result['score']
        
        # Consensus (average of both)
        vader_normalized = (vader_scores['compound'] + 1) / 2
        consensus_score = (vader_normalized + transformer_score) / 2
        
        # Determine sentiment label
        if consensus_score >= 0.6:
            sentiment_label = "POSITIVE"
        elif consensus_score <= 0.4:
            sentiment_label = "NEGATIVE"
        else:
            sentiment_label = "NEUTRAL"
        
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
        """Analyze multiple texts and return aggregated stats."""
        results = [self.analyze_text(text) for text in texts]
        
        valid_scores = [r['consensus_score'] for r in results if 'consensus_score' in r]
        
        if not valid_scores:
            return {"error": "No valid texts"}
        
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
        """Convert label (1-5) to score (0-1)."""
        mapping = {"1": 0.0, "2": 0.25, "3": 0.5, "4": 0.75, "5": 1.0}
        return mapping.get(label, 0.5)
```

### MahkamahAgungCrawler

```python
# app/services/mahkamah_crawler.py

import asyncio
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

class MahkamahAgungCrawler:
    
    BASE_URL = "https://putusan.mahkamahagung.go.id"
    SEARCH_PATH = "/search/putusan"
    
    SEVERITY_MAP = {
        "pidana": "high",     # Criminal
        "perdata": "medium",  # Civil
        "tata": "medium",     # Administrative
        "niaga": "high",      # Commercial
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.timeout = 10
    
    async def search_company(self, company_name: str) -> Dict[str, Any]:
        """
        Search Mahkamah Agung for company legal records.
        
        Returns:
            {
              "company_name": str,
              "cases_found": int,
              "cases": [{case_data}],
              "max_severity": str,
              "timestamp": str
            }
        """
        cases = []
        
        try:
            search_url = f"{self.BASE_URL}{self.SEARCH_PATH}"
            params = {"q": company_name, "p": 1}
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            case_elements = soup.find_all('div', class_='putusan-item')
            
            for element in case_elements[:10]:  # Limit to 10 cases
                case_data = self._parse_case_element(element)
                if case_data:
                    cases.append(case_data)
                await asyncio.sleep(0.5)  # Rate limiting
            
            severities = [c.get('severity', 'low') for c in cases]
            max_severity = self._get_max_severity(severities)
            
            return {
                "company_name": company_name,
                "cases_found": len(cases),
                "cases": cases,
                "max_severity": max_severity,
                "timestamp": datetime.now().isoformat(),
                "source": "mahkamah_agung"
            }
        
        except Exception as e:
            return {
                "company_name": company_name,
                "cases_found": 0,
                "cases": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_case_element(self, element) -> Dict:
        """Parse individual case from HTML."""
        try:
            case_num = element.find('span', class_='nomor-putusan')
            case_number = case_num.text.strip() if case_num else "Unknown"
            
            date_elem = element.find('span', class_='tanggal-putusan')
            case_date = date_elem.text.strip() if date_elem else "Unknown"
            
            title = element.find('a', class_='putusan-link')
            case_title = title.text.strip() if title else "Unknown"
            case_type = self._determine_case_type(case_title)
            
            verdict = element.find('div', class_='ringkasan-putusan')
            verdict_summary = verdict.text.strip()[:200] if verdict else "No summary"
            
            source_url = title['href'] if title and title.get('href') else ""
            if source_url and not source_url.startswith('http'):
                source_url = f"{self.BASE_URL}{source_url}"
            
            severity = self.SEVERITY_MAP.get(case_type.lower(), "medium")
            
            return {
                "case_number": case_number,
                "case_date": case_date,
                "case_title": case_title,
                "case_type": case_type,
                "verdict_summary": verdict_summary,
                "severity": severity,
                "source_url": source_url
            }
        except:
            return None
    
    def _determine_case_type(self, title: str) -> str:
        """Classify case type from title."""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['pidana', 'criminal', 'penal']):
            return "pidana"
        elif any(word in title_lower for word in ['niaga', 'commercial', 'dagang']):
            return "niaga"
        elif any(word in title_lower for word in ['tata', 'administrative', 'administrasi']):
            return "tata"
        else:
            return "perdata"
    
    def _get_max_severity(self, severities: List[str]) -> str:
        """Get highest severity level."""
        severity_rank = {"high": 3, "medium": 2, "low": 1}
        if not severities:
            return "none"
        return max(severities, key=lambda x: severity_rank.get(x, 0))
```

### RiskScoringService

```python
# app/services/risk_scoring.py

from typing import Dict, Any

class RiskScoringService:
    
    SENTIMENT_WEIGHT = 0.30
    MENTIONS_WEIGHT = 0.30
    LEGAL_WEIGHT = 0.40
    
    def calculate_risk_score(
        self,
        sentiment_data: Dict[str, Any],
        legal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate final risk score from components.
        
        Formula:
        Risk = (Sentiment×0.30) + (Mentions×0.30) + (Legal×0.40)
        """
        
        sentiment_component = self._calculate_sentiment_component(sentiment_data)
        mentions_component = self._calculate_mentions_component(sentiment_data)
        legal_component = self._calculate_legal_component(legal_data)
        
        risk_score = (
            (sentiment_component * self.SENTIMENT_WEIGHT) +
            (mentions_component * self.MENTIONS_WEIGHT) +
            (legal_component * self.LEGAL_WEIGHT)
        )
        
        risk_level = self._get_risk_level(risk_score)
        recommendation = self._get_recommendation(risk_level, sentiment_component, legal_component)
        
        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "sentiment_component": round(sentiment_component, 2),
            "mentions_component": round(mentions_component, 2),
            "legal_component": round(legal_component, 2),
            "details": {
                "total_texts_analyzed": sentiment_data.get('total_texts', 0),
                "positive_texts": sentiment_data.get('positive_count', 0),
                "negative_texts": sentiment_data.get('negative_count', 0),
                "legal_cases_found": legal_data.get('cases_found', 0),
                "max_case_severity": legal_data.get('max_severity', 'none'),
            },
            "recommendation": recommendation
        }
    
    def _calculate_sentiment_component(self, sentiment_data: Dict) -> float:
        """
        Sentiment risk (0-100).
        Higher negative sentiment = higher risk.
        """
        if 'error' in sentiment_data or 'valid_analyses' not in sentiment_data:
            return 50.0
        
        avg_score = sentiment_data.get('average_score', 0.5)
        # Invert: 0.0 (negative) → 100, 0.5 (neutral) → 50, 1.0 (positive) → 0
        component = (1.0 - avg_score) * 100
        return min(100, max(0, component))
    
    def _calculate_mentions_component(self, sentiment_data: Dict) -> float:
        """
        Negative mentions risk (0-100).
        Based on ratio of negative texts.
        """
        if 'valid_analyses' not in sentiment_data or sentiment_data['valid_analyses'] == 0:
            return 50.0
        
        total = sentiment_data['valid_analyses']
        negative = sentiment_data.get('negative_count', 0)
        
        # Percentage of negative mentions
        negative_ratio = (negative / total) * 100
        return min(100, max(0, negative_ratio))
    
    def _calculate_legal_component(self, legal_data: Dict) -> float:
        """
        Legal risk (0-100).
        Cases + severity = higher risk.
        """
        cases_found = legal_data.get('cases_found', 0)
        max_severity = legal_data.get('max_severity', 'none')
        
        # Base risk from case count (max 60)
        cases_risk = min(60, (cases_found / 5) * 60) if cases_found > 0 else 0
        
        # Severity bonus
        severity_map = {
            'high': 40,
            'medium': 25,
            'low': 10,
            'none': 0
        }
        
        severity_risk = severity_map.get(max_severity, 0)
        component = min(100, cases_risk + severity_risk)
        
        return component
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Map score to risk level."""
        if risk_score <= 30:
            return "GREEN"
        elif risk_score <= 65:
            return "YELLOW"
        else:
            return "RED"
    
    def _get_recommendation(self, risk_level: str, sentiment_score: float, legal_score: float) -> str:
        """Generate recommendation text."""
        
        if risk_level == "GREEN":
            return "✅ RECOMMENDED: Positive track record. Safe for credit approval."
        
        elif risk_level == "YELLOW":
            if legal_score > 60:
                return "⚠️ REVIEW REQUIRED: Legal issues detected. Manual investigation needed."
            elif sentiment_score > 70:
                return "⚠️ REVIEW REQUIRED: Negative sentiment found. Further due diligence needed."
            else:
                return "⚠️ REVIEW REQUIRED: Mixed signals. Request additional documentation."
        
        else:  # RED
            if legal_score > 80:
                return "❌ NOT RECOMMENDED: Significant legal history. Reject application."
            else:
                return "❌ NOT RECOMMENDED: High-risk profile. Reject or require collateral."
```

---

## 4. API Endpoint Implementation

### POST `/api/v1/company/analyze`

```python
# app/api/v1/company.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/company", tags=["company"])

class CompanyAnalysisRequest(BaseModel):
    pt_name: str
    detailed: bool = False

@router.post("/analyze")
async def analyze_company(request: CompanyAnalysisRequest):
    """
    Main analysis endpoint.
    Orchestrates: Perplexity → Sentiment → Legal → Risk Score
    
    Duration: 15-30 seconds typical
    """
    
    try:
        # 1. Get company data
        perplexity_service = PerplexityService()
        company_data = await perplexity_service.search_company(request.pt_name)
        
        # 2. Sentiment analysis
        sentiment_service = SentimentAnalysisService()
        extracted_text = perplexity_service.extract_sentiment_text(
            company_data['extracted_text']
        )
        sentiment_results = sentiment_service.analyze_batch([extracted_text])
        
        # 3. Legal records crawl
        crawler = MahkamahAgungCrawler()
        legal_results = await crawler.search_company(request.pt_name)
        
        # 4. Risk calculation
        risk_scorer = RiskScoringService()
        risk_analysis = risk_scorer.calculate_risk_score(
            sentiment_results,
            legal_results
        )
        
        # Compile response
        response = {
            "company_name": request.pt_name,
            "status": "success",
            "analysis": {
                "risk_assessment": risk_analysis,
                "sentiment_analysis": sentiment_results,
                "legal_records": legal_results if request.detailed else {
                    "cases_found": legal_results.get('cases_found'),
                    "max_severity": legal_results.get('max_severity')
                }
            },
            "timestamp": company_data['timestamp']
        }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "ok"}
```

---

## 5. FastAPI Main Application

```python
# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

from app.api.v1 import company

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

app = FastAPI(
    title="Sentiment Analysis Credit Scoring API",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://backend:3000"  # Docker network
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routes
app.include_router(company.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 6. Configuration Module

```python
# app/config.py

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
```

---

## 7. Database Setup

```python
# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import DATABASE_URL

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables on startup
from app.models import company, sentiment, legal_record, analysis_summary

def init_db():
    """Initialize database tables."""
    company.Base.metadata.create_all(bind=engine)
```

---

## 8. Requirements File

```
# requirements.txt

# FastAPI & Server
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.23

# Web Scraping
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3

# NLP (CPU-only for on-premise)
nltk==3.8.1
transformers==4.35.2
torch==2.1.1+cpu
numpy==1.26.2

# Utilities
python-multipart==0.0.6
python-dateutil==2.8.2

# Optional: Async HTTP
httpx==0.25.0
```

---

## 9. Runtime Notes

### Model Initialization
- NLTK VADER: ~5MB, loaded on service init
- Transformers: ~300MB, downloaded on first run and cached
- Torch: ~200MB, CPU-only version

### Performance Characteristics
- Single company analysis: 15-30 seconds
- Perplexity API call: 5-15 seconds
- Sentiment analysis: 2-3 seconds
- Web scraping: 5-10 seconds
- Risk calculation: < 1 second

### Memory Usage
- Idle backend: ~400MB
- Active analysis: ~1.5GB peak (both models loaded)
- Data directory: ~1MB per 100 analyses

---

## 10. Deployment Checklist

- [ ] Python 3.10+ installed on server
- [ ] Docker & Docker Compose installed
- [ ] PERPLEXITY_API_KEY obtained and configured
- [ ] requirements.txt copied to backend directory
- [ ] Dockerfile builds successfully
- [ ] .env file created with API key
- [ ] docker-compose up -d runs without errors
- [ ] Backend health check responds: http://localhost:8000/health
- [ ] Sentiment model downloads on first startup (~300MB)
- [ ] Database initialized automatically on first request
