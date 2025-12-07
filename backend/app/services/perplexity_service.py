"""
Perplexity API service for company information retrieval.
Optimized for Indonesian companies with Bahasa Indonesia queries.
"""

import os
import re
from typing import Dict, Any
from datetime import datetime
import httpx
from app.config import PERPLEXITY_API_KEY


class PerplexityService:
    """Service for querying Perplexity API with Indonesian company focus."""
    
    BASE_URL = "https://api.perplexity.ai"
    MODEL = "sonar"  # Online model for current info
    
    def __init__(self):
        self.api_key = PERPLEXITY_API_KEY
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY required")
    
    async def search_company(self, company_name: str) -> Dict[str, Any]:
        """
        Search Perplexity API for company information.
        Query optimized for Indonesian companies with Bahasa Indonesia.
        
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
        # Query in Bahasa Indonesia for Indonesian companies
        query = f"""
        Cari informasi tentang "{company_name}" Indonesia.
        Sertakan: latar belakang, berita, reputasi, operasi, kontroversi.
        Fokus pada relevansi penilaian kredit.
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
            
            # Extract all possible sources from Perplexity response
            sources = []
            
            # Get citations (list of URLs)
            citations = result.get("citations", [])
            if citations:
                sources.extend([url if isinstance(url, str) else url.get('url', '') if isinstance(url, dict) else '' for url in citations])
            
            # Get search_results (may contain more detailed info)
            search_results = result.get("search_results", [])
            if search_results:
                for result_item in search_results:
                    if isinstance(result_item, dict):
                        url = result_item.get('url', '')
                        if url and url not in sources:
                            sources.append(url)
                    elif isinstance(result_item, str) and result_item not in sources:
                        sources.append(result_item)
            
            # Also extract URLs from the content itself (in case citations are missing)
            url_pattern = r'http[s]?://[^\s\)]+'
            content_urls = re.findall(url_pattern, content)
            for url in content_urls:
                if url not in sources:
                    sources.append(url)
            
            return {
                "raw_response": result,
                "extracted_text": content,
                "sources": sources,
                "query": company_name,
                "timestamp": datetime.now().isoformat()
            }
        except httpx.HTTPStatusError as e:
            raise Exception(f"Error API Perplexity: {e.response.status_code} - {str(e)}")
        except Exception as e:
            raise Exception(f"Error API Perplexity: {str(e)}")
    
    async def search_latest_news(self, company_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for latest news articles about a company using Perplexity API.
        
        Args:
            company_name: Company name (e.g., "Bank Mandiri")
            limit: Maximum number of news articles to return (default: 10)
        
        Returns:
            {
              "company_name": str,
              "news_articles": [
                {
                  "title": str,
                  "summary": str,
                  "source_url": str,
                  "date": str (if available)
                }
              ],
              "total_found": int,
              "timestamp": str
            }
        """
        query = f"""
        Cari 10 berita terbaru tentang "{company_name}" Indonesia.
        Berikan judul, ringkasan singkat, dan URL sumber untuk setiap berita.
        Fokus pada berita yang relevan dengan penilaian kredit dan reputasi perusahaan.
        Format: Judul | Ringkasan | URL
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
                        "max_tokens": 4000,
                        "temperature": 0.2
                    }
                )
            
            response.raise_for_status()
            result = response.json()
            
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Extract all possible sources from Perplexity response
            sources = []
            
            # Get citations (list of URLs)
            citations = result.get("citations", [])
            if citations:
                sources.extend([url if isinstance(url, str) else url.get('url', '') if isinstance(url, dict) else '' for url in citations])
            
            # Get search_results (may contain more detailed info)
            search_results = result.get("search_results", [])
            if search_results:
                for result_item in search_results:
                    if isinstance(result_item, dict):
                        url = result_item.get('url', '')
                        if url and url not in sources:
                            sources.append(url)
                    elif isinstance(result_item, str) and result_item not in sources:
                        sources.append(result_item)
            
            # Also extract URLs from the content itself
            url_pattern = r'http[s]?://[^\s\)]+'
            content_urls = re.findall(url_pattern, content)
            for url in content_urls:
                if url not in sources:
                    sources.append(url)
            
            # Parse news articles from the response
            news_articles = self._parse_news_articles(content, sources, limit)
            
            return {
                "company_name": company_name,
                "news_articles": news_articles,
                "total_found": len(news_articles),
                "timestamp": datetime.now().isoformat(),
                "raw_response": content,
                "sources": sources  # Include all sources found
            }
        except httpx.HTTPStatusError as e:
            raise Exception(f"Error API Perplexity: {e.response.status_code} - {str(e)}")
        except Exception as e:
            raise Exception(f"Error API Perplexity: {str(e)}")
    
    def _parse_news_articles(self, content: str, sources: list, limit: int) -> list:
        """
        Parse news articles from Perplexity response.
        Attempts to extract structured news data from the text response.
        Handles various response formats from Perplexity.
        """
        articles = []
        
        # Strategy 1: Try to split by numbered list or bullet points
        lines = content.split('\n')
        current_article = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                # Empty line might indicate article separator
                if current_article and current_article.get('title'):
                    articles.append(current_article)
                    current_article = {}
                continue
            
            # Check if line starts with a number (1., 2., etc.) or bullet
            numbered_match = re.match(r'^(\d+)[\.\)]\s+(.+)', line)
            bullet_match = re.match(r'^[-•*]\s+(.+)', line)
            
            if numbered_match or bullet_match:
                # Save previous article if exists
                if current_article and current_article.get('title'):
                    articles.append(current_article)
                    current_article = {}
                
                # Extract title
                if numbered_match:
                    title = numbered_match.group(2)
                else:
                    title = bullet_match.group(1)
                
                # Strip markdown formatting from title
                title = self._strip_markdown(title.strip())
                current_article['title'] = title
                continue
            
            # Check for URL pattern (might be on same line or separate)
            url_match = re.search(r'http[s]?://[^\s\)]+', line)
            if url_match:
                current_article['source_url'] = url_match.group(0)
                # Remove URL from line for summary
                line = re.sub(r'http[s]?://[^\s\)]+', '', line).strip()
            
            # If we have a title, accumulate summary text
            if current_article.get('title'):
                # Skip if line is too similar to title (avoid duplication)
                title_lower = current_article['title'].lower()
                line_lower = line.lower()
                
                # Skip if line is very similar to title (more than 80% match)
                if line_lower and title_lower:
                    words_in_title = set(title_lower.split())
                    words_in_line = set(line_lower.split())
                    if len(words_in_line) > 0:
                        similarity = len(words_in_title.intersection(words_in_line)) / len(words_in_line)
                        if similarity > 0.8:
                            continue  # Skip this line as it's too similar to title
                
                if 'summary' not in current_article:
                    current_article['summary'] = line
                else:
                    # Add to summary if not duplicate and not too similar to title
                    if line and line not in current_article['summary'] and line_lower != title_lower:
                        current_article['summary'] += ' ' + line
        
        # Add last article
        if current_article and current_article.get('title'):
            articles.append(current_article)
        
        # Strategy 2: If parsing failed, try to split by paragraphs and use sources
        if not articles or len(articles) < limit:
            # Split content into paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            # Match paragraphs with sources
            for i, para in enumerate(paragraphs[:limit]):
                if not para:
                    continue
                
                # Extract URL from paragraph if exists
                url_match = re.search(r'http[s]?://[^\s\)]+', para)
                source_url = url_match.group(0) if url_match else ''
                
                # Remove URL from paragraph
                para_clean = re.sub(r'http[s]?://[^\s\)]+', '', para).strip()
                
                # Extract title (first sentence or first line)
                lines_in_para = para_clean.split('\n')
                title = lines_in_para[0].strip()[:100]  # Limit title length
                
                # Strip markdown from title
                title = self._strip_markdown(title)
                
                # Get summary from remaining lines, but ensure it's different from title
                if len(lines_in_para) > 1:
                    summary = ' '.join(lines_in_para[1:])
                else:
                    # If only one line, try to extract a summary by removing title-like parts
                    summary = para_clean
                    # Remove title if it appears in summary
                    if title.lower() in summary.lower():
                        summary = summary.replace(title, '', 1).strip()
                
                # Strip markdown from summary too
                summary = self._strip_markdown(summary)
                
                # If summary is too similar to title or empty, create a generic summary
                if not summary or summary.lower() == title.lower() or len(summary) < 20:
                    summary = "Ringkasan artikel tidak tersedia."
                
                # If we don't have this article yet, add it
                if not any(a.get('title', '') == title for a in articles):
                    articles.append({
                        "title": title,
                        "summary": summary[:300] if len(summary) > 300 else summary,
                        "source_url": source_url
                    })
        
        # Strategy 3: If still no articles, create from sources
        if not articles and sources:
            # Split content into chunks
            content_chunks = [c.strip() for c in content.split('\n\n') if c.strip()]
            for i, source in enumerate(sources[:limit]):
                chunk = content_chunks[i] if i < len(content_chunks) else content[:200]
                # Try to extract a better title from chunk
                chunk_lines = chunk.split('\n')
                title = self._strip_markdown(chunk_lines[0].strip()[:100]) if chunk_lines else f"Berita {i+1}"
                summary = ' '.join(chunk_lines[1:]) if len(chunk_lines) > 1 else chunk
                articles.append({
                    "title": title if title else f"Berita {i+1}",
                    "summary": summary[:300] + "..." if len(summary) > 300 else summary,
                    "source_url": source if isinstance(source, str) else source.get('url', '') if isinstance(source, dict) else ''
                })
        
        # Limit results
        articles = articles[:limit]
        
        # Ensure all articles have required fields
        for article in articles:
            if 'source_url' not in article:
                article['source_url'] = ''
            if 'summary' not in article or not article['summary']:
                article['summary'] = article.get('title', 'Tidak ada ringkasan')
            if 'title' not in article or not article['title']:
                article['title'] = 'Tidak ada judul'
        
        return articles
    
    def _strip_markdown(self, text: str) -> str:
        """
        Strip markdown formatting from text.
        Removes **bold**, *italic*, __bold__, _italic_, and other markdown syntax.
        """
        if not text:
            return text
        
        # Remove markdown bold (**text** or __text__)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # Remove markdown italic (*text* or _text_)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        
        # Remove markdown links [text](url)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove markdown headers (# Header)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown code blocks
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_sentiment_text(self, raw_text: str) -> str:
        """
        Clean and extract text for sentiment analysis.
        Handles Indonesian text encoding (UTF-8) and preserves special characters.
        """
        if not raw_text:
            return ""
        
        # Remove URLs while keeping Indonesian text intact
        text = re.sub(r'http[s]?://\S+', '', raw_text)
        
        # Normalize whitespace patterns
        text = ' '.join(text.split())
        
        # Keep basic punctuation and Indonesian characters (é, è, ç, etc.)
        text = re.sub(r'[^\w\s.,\-]', '', text)
        
        return text.strip()

