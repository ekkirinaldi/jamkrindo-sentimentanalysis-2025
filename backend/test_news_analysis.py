"""
Script untuk menguji analisis berita terbaru.
Contoh penggunaan: python test_news_analysis.py
"""

import asyncio
import sys
from app.services.perplexity_service import PerplexityService
from app.services.sentiment_service import SentimentAnalysisService


async def analyze_company_news(company_name: str, limit: int = 10):
    """
    Mencari dan menganalisis sentimen berita terbaru tentang perusahaan.
    
    Args:
        company_name: Nama perusahaan (contoh: "Bank Mandiri")
        limit: Jumlah berita yang dicari (default: 10)
    """
    print("="*70)
    print(f"Analisis Berita: {company_name}")
    print("="*70)
    
    try:
        # 1. Cari berita terbaru
        perplexity = PerplexityService()
        print(f"\n1. Mencari {limit} berita terbaru tentang {company_name}...")
        news_data = await perplexity.search_latest_news(company_name, limit=limit)
        
        print(f"   ✅ Ditemukan {news_data.get('total_found', 0)} artikel berita\n")
        
        # 2. Analisis sentimen untuk setiap artikel
        sentiment_service = SentimentAnalysisService()
        articles_with_sentiment = []
        
        print("2. Menganalisis sentimen untuk setiap artikel...\n")
        
        for i, article in enumerate(news_data.get('news_articles', []), 1):
            text_to_analyze = f"{article.get('title', '')} {article.get('summary', '')}"
            text_to_analyze = perplexity.extract_sentiment_text(text_to_analyze)
            
            if len(text_to_analyze.strip()) < 10:
                print(f"   ⚠️  Artikel {i}: Teks terlalu pendek, dilewati")
                continue
            
            sentiment_result = sentiment_service.analyze_text(text_to_analyze)
            
            if 'error' in sentiment_result:
                print(f"   ❌ Artikel {i}: Error - {sentiment_result.get('error')}")
                continue
            
            sentiment_label = sentiment_result.get('sentiment_label', 'NETRAL')
            sentiment_score = sentiment_result.get('consensus_score', 0.5)
            
            emoji = "✅" if sentiment_label == "POSITIF" else "⚠️" if sentiment_label == "NETRAL" else "❌"
            print(f"   {emoji} Artikel {i}: {sentiment_label} (Skor: {sentiment_score:.3f})")
            print(f"      Judul: {article.get('title', 'N/A')[:70]}...")
            
            articles_with_sentiment.append({
                'title': article.get('title', ''),
                'sentiment': sentiment_label,
                'score': sentiment_score
            })
        
        # 3. Statistik
        positive_count = sum(1 for a in articles_with_sentiment if a['sentiment'] == "POSITIF")
        neutral_count = sum(1 for a in articles_with_sentiment if a['sentiment'] == "NETRAL")
        negative_count = sum(1 for a in articles_with_sentiment if a['sentiment'] == "NEGATIF")
        
        print(f"\n" + "="*70)
        print("RINGKASAN")
        print("="*70)
        print(f"Total Artikel Dianalisis: {len(articles_with_sentiment)}")
        print(f"✅ Positif: {positive_count}")
        print(f"⚠️  Netral:  {neutral_count}")
        print(f"❌ Negatif: {negative_count}")
        print("="*70)
        
        return articles_with_sentiment
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "Bank Mandiri"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    asyncio.run(analyze_company_news(company, limit))

