"""
News analysis endpoints.
API untuk mencari dan menganalisis sentimen berita terbaru tentang perusahaan.
"""

from fastapi import APIRouter, HTTPException
from app.schemas.news import NewsAnalysisRequest, NewsAnalysisResponse, NewsArticle
from app.services.perplexity_service import PerplexityService
from app.services.sentiment_service import SentimentAnalysisService
from app.utils.logger import logger
from datetime import datetime

router = APIRouter(prefix="/api/v1/news", tags=["news"])


@router.post("/analyze", response_model=NewsAnalysisResponse, summary="Analisis sentimen berita terbaru")
async def analyze_news(request: NewsAnalysisRequest):
    """
    Mencari 10 berita terbaru tentang perusahaan dan menganalisis sentimen masing-masing.
    
    Endpoint ini:
    1. Mencari berita terbaru menggunakan Perplexity API
    2. Menganalisis sentimen setiap berita (POSITIF, NETRAL, NEGATIF)
    3. Mengembalikan hasil dengan statistik sentimen
    
    Durasi: 20-40 detik (tergantung jumlah berita)
    
    Args:
        request: NewsAnalysisRequest dengan company_name dan limit
    
    Returns:
        NewsAnalysisResponse dengan daftar artikel dan analisis sentimen
    """
    
    try:
        # Validasi input
        if not request.company_name or len(request.company_name.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Nama perusahaan tidak boleh kosong atau terlalu pendek"
            )
        
        logger.info(f"Memulai pencarian berita untuk: {request.company_name}")
        
        # 1. Search for latest news using Perplexity
        perplexity_service = PerplexityService()
        news_data = await perplexity_service.search_latest_news(
            request.company_name,
            limit=request.limit
        )
        
        logger.info(f"Ditemukan {news_data.get('total_found', 0)} artikel berita")
        
        # 2. Analyze sentiment for each news article
        sentiment_service = SentimentAnalysisService()
        articles_with_sentiment = []
        
        for article in news_data.get('news_articles', []):
            # Combine title and summary for sentiment analysis
            text_to_analyze = f"{article.get('title', '')} {article.get('summary', '')}"
            text_to_analyze = perplexity_service.extract_sentiment_text(text_to_analyze)
            
            if len(text_to_analyze.strip()) < 10:
                # Skip if text is too short
                logger.warning(f"Artikel '{article.get('title', '')}' terlalu pendek untuk dianalisis")
                continue
            
            # Analyze sentiment
            sentiment_result = sentiment_service.analyze_text(text_to_analyze)
            
            if 'error' in sentiment_result:
                logger.warning(f"Gagal menganalisis sentimen untuk artikel: {article.get('title', '')}")
                continue
            
            # Create article with sentiment
            article_with_sentiment = NewsArticle(
                title=article.get('title', 'Tidak ada judul'),
                summary=article.get('summary', 'Tidak ada ringkasan'),
                source_url=article.get('source_url', ''),
                date=article.get('date'),
                sentiment_label=sentiment_result.get('sentiment_label', 'NETRAL'),
                sentiment_score=sentiment_result.get('consensus_score', 0.5),
                confidence=sentiment_result.get('confidence', 0.0)
            )
            
            articles_with_sentiment.append(article_with_sentiment)
        
        # 3. Calculate statistics
        positive_count = sum(1 for a in articles_with_sentiment if a.sentiment_label == "POSITIF")
        neutral_count = sum(1 for a in articles_with_sentiment if a.sentiment_label == "NETRAL")
        negative_count = sum(1 for a in articles_with_sentiment if a.sentiment_label == "NEGATIF")
        
        logger.info(f"Analisis selesai: {positive_count} positif, {neutral_count} netral, {negative_count} negatif")
        
        # 4. Return response
        return NewsAnalysisResponse(
            company_name=request.company_name,
            total_articles=len(articles_with_sentiment),
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            articles=articles_with_sentiment,
            timestamp=datetime.now().isoformat(),
            status="sukses"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gagal menganalisis berita untuk {request.company_name}: {str(e)}")
        return NewsAnalysisResponse(
            company_name=request.company_name,
            total_articles=0,
            positive_count=0,
            neutral_count=0,
            negative_count=0,
            articles=[],
            timestamp=datetime.now().isoformat(),
            status="gagal",
            error=f"Gagal menganalisis berita: {str(e)}"
        )

