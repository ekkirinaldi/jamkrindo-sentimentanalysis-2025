"""
Company analysis endpoints.
API documentation and descriptions in Bahasa Indonesia.
"""

from fastapi import APIRouter, HTTPException
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from app.schemas.company import CompanyAnalysisRequest, CompanyAnalysisResponse
from app.schemas.news import NewsAnalysisResponse
from app.services.perplexity_service import PerplexityService
from app.services.sentiment_service import SentimentAnalysisService
from app.services.mahkamah_crawler import MahkamahAgungCrawler
from app.services.risk_scoring import RiskScoringService
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1/company", tags=["company"])


@router.post("/analyze", response_model=CompanyAnalysisResponse)
async def analyze_company(request: CompanyAnalysisRequest):
    """
    Endpoint utama untuk menganalisis perusahaan.
    Mengorchestrasi: Perplexity → Sentiment → Legal → Risk Score
    
    Durasi: 15-30 detik (khas)
    
    Args:
        request: CompanyAnalysisRequest dengan pt_name dan detailed flag
    
    Returns:
        CompanyAnalysisResponse dengan hasil analisis lengkap
    """
    
    try:
        # Validasi input
        if not request.pt_name or len(request.pt_name.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Nama perusahaan tidak boleh kosong atau terlalu pendek"
            )
        
        logger.info(f"Memulai analisis untuk: {request.pt_name}")
        
        # 1. Get company data from Perplexity
        perplexity_service = PerplexityService()
        company_data = await perplexity_service.search_company(request.pt_name)
        
        # 2. Sentiment analysis
        sentiment_service = SentimentAnalysisService()
        extracted_text = perplexity_service.extract_sentiment_text(
            company_data['extracted_text']
        )
        sentiment_results = sentiment_service.analyze_batch([extracted_text])
        
        # 3. Legal records crawl (with timeout protection)
        try:
            crawler = MahkamahAgungCrawler()
            legal_results = await asyncio.wait_for(
                crawler.search_company(request.pt_name),
                timeout=45.0  # Max 45 seconds for crawler
            )
        except asyncio.TimeoutError:
            logger.warning(f"Timeout saat crawling Mahkamah Agung untuk {request.pt_name}")
            legal_results = {
                "company_name": request.pt_name,
                "cases_found": 0,
                "cases": [],
                "max_severity": "tidak ada",
                "timestamp": datetime.now().isoformat(),
                "source": "mahkamah_agung",
                "error": "Timeout saat mengakses database Mahkamah Agung"
            }
        except Exception as e:
            logger.error(f"Error crawling Mahkamah Agung: {str(e)}")
            legal_results = {
                "company_name": request.pt_name,
                "cases_found": 0,
                "cases": [],
                "max_severity": "tidak ada",
                "timestamp": datetime.now().isoformat(),
                "source": "mahkamah_agung",
                "error": f"Kesalahan crawler: {str(e)}"
            }
        
        # 4. News analysis (optional, run in parallel or after main analysis)
        news_analysis: Optional[Dict[str, Any]] = None
        news_sources: list = []
        try:
            logger.info(f"Memulai analisis berita untuk: {request.pt_name}")
            news_data = await perplexity_service.search_latest_news(request.pt_name, limit=10)
            # Collect sources from news search
            news_sources = news_data.get('sources', [])
            
            # Analyze sentiment for each news article
            articles_with_sentiment = []
            for article in news_data.get('news_articles', []):
                text_to_analyze = f"{article.get('title', '')} {article.get('summary', '')}"
                text_to_analyze = perplexity_service.extract_sentiment_text(text_to_analyze)
                
                if len(text_to_analyze.strip()) < 10:
                    continue
                
                sentiment_result = sentiment_service.analyze_text(text_to_analyze)
                if 'error' in sentiment_result:
                    continue
                
                articles_with_sentiment.append({
                    "title": article.get('title', 'Tidak ada judul'),
                    "summary": article.get('summary', 'Tidak ada ringkasan'),
                    "source_url": article.get('source_url', ''),
                    "date": article.get('date'),
                    "sentiment_label": sentiment_result.get('sentiment_label', 'NETRAL'),
                    "sentiment_score": sentiment_result.get('consensus_score', 0.5),
                    "confidence": sentiment_result.get('confidence', 0.0)
                })
            
            # Calculate statistics
            positive_count = sum(1 for a in articles_with_sentiment if a['sentiment_label'] == "POSITIF")
            neutral_count = sum(1 for a in articles_with_sentiment if a['sentiment_label'] == "NETRAL")
            negative_count = sum(1 for a in articles_with_sentiment if a['sentiment_label'] == "NEGATIF")
            
            news_analysis = {
                "company_name": request.pt_name,
                "total_articles": len(articles_with_sentiment),
                "positive_count": positive_count,
                "neutral_count": neutral_count,
                "negative_count": negative_count,
                "articles": articles_with_sentiment,
                "timestamp": datetime.now().isoformat(),
                "status": "sukses"
            }
            logger.info(f"Analisis berita selesai: {positive_count} positif, {neutral_count} netral, {negative_count} negatif")
        except Exception as e:
            logger.warning(f"Gagal menganalisis berita untuk {request.pt_name}: {str(e)}")
            news_analysis = {
                "company_name": request.pt_name,
                "total_articles": 0,
                "positive_count": 0,
                "neutral_count": 0,
                "negative_count": 0,
                "articles": [],
                "timestamp": datetime.now().isoformat(),
                "status": "gagal",
                "error": f"Gagal menganalisis berita: {str(e)}"
            }
        
        # 5. Risk calculation
        risk_scorer = RiskScoringService()
        risk_analysis = risk_scorer.calculate_risk_score(
            sentiment_results,
            legal_results
        )
        
        # 6. Compile response with all evidence
        response_data = {
            "company_name": request.pt_name,
            "status": "success",
            "analysis": {
                "risk_assessment": risk_analysis,
                "sentiment_analysis": sentiment_results,
                "legal_records": legal_results if request.detailed else {
                    "company_name": legal_results.get('company_name'),
                    "cases_found": legal_results.get('cases_found'),
                    "max_severity": legal_results.get('max_severity'),
                    "timestamp": legal_results.get('timestamp')
                },
                "news_analysis": news_analysis,  # Add news analysis
                "perplexity_sources": company_data.get('sources', []),  # Add Perplexity sources from company search
                "perplexity_news_sources": news_sources  # Add Perplexity sources from news search
            },
            "timestamp": company_data['timestamp']
        }
        
        logger.info(f"Analisis selesai untuk: {request.pt_name}")
        return response_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gagal menganalisis perusahaan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menganalisis perusahaan: {str(e)}"
        )

