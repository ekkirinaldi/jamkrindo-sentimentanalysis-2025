"""
Mahkamah Agung web crawler using Crawl4AI.
Handles Indonesian legal database with Bahasa Indonesia case types and severity.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import MAHKAMAH_CRAWL_DELAY
from app.utils.logger import logger
from app.utils.exceptions import CrawlerError

class MahkamahCrawlerError(CrawlerError):
    """Exception khusus untuk kesalahan pengikisan Mahkamah Agung."""
    pass

try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    logger.warning("Crawl4AI not available, falling back to requests")


class MahkamahAgungCrawler:
    """Crawler for Indonesian legal database (Mahkamah Agung) using Crawl4AI."""
    
    BASE_URL = "https://putusan3.mahkamahagung.go.id"
    SEARCH_URL = f"{BASE_URL}/search.html"
    
    # Severity mapping to Bahasa Indonesia
    SEVERITY_MAP = {
        "pidana": "tinggi",      # Criminal - high severity
        "perdata": "sedang",      # Civil - medium severity
        "tata usaha negara": "sedang",  # Administrative - medium severity
        "tata": "sedang",         # Administrative - medium severity
        "niaga": "tinggi",        # Commercial - high severity
        "pajak": "sedang",        # Tax - medium severity
        "pidana umum": "tinggi",  # General criminal - high severity
        "pidana khusus": "tinggi", # Special criminal - high severity
    }
    
    def __init__(self):
        self.timeout = 15  # Reduced timeout to fail faster
        self.page_timeout = 20000  # 20 seconds for page load (in milliseconds)
        self.use_crawl4ai = CRAWL4AI_AVAILABLE
    
    async def search_company(self, company_name: str) -> Dict[str, Any]:
        """
        Search Mahkamah Agung for company legal records using Crawl4AI.
        Handles Indonesian company name formats (PT, CV, UD, etc.).
        
        Returns:
            {
              "company_name": str,
              "cases_found": int,
              "cases": [{case_data}],
              "max_severity": str (tinggi, sedang, rendah, tidak ada),
              "timestamp": str
            }
        """
        cases = []
        
        try:
            if self.use_crawl4ai:
                cases = await self._search_with_crawl4ai(company_name)
            else:
                logger.warning("Crawl4AI not available, using fallback method")
                cases = await self._search_fallback(company_name)
            
            severities = [c.get('severity', 'rendah') for c in cases]
            max_severity = self._get_max_severity(severities)
            
            return {
                "company_name": company_name,
                "cases_found": len(cases),
                "cases": cases[:10],  # Limit to 10 cases
                "max_severity": max_severity,
                "timestamp": datetime.now().isoformat(),
                "source": "mahkamah_agung"
            }
        
        except Exception as e:
            logger.error(f"Error crawling Mahkamah Agung: {str(e)}")
            return {
                "company_name": company_name,
                "cases_found": 0,
                "cases": [],
                "error": f"Error crawling: {str(e)}",
                "max_severity": "tidak ada",
                "timestamp": datetime.now().isoformat(),
                "source": "mahkamah_agung"
            }
    
    async def _search_with_crawl4ai(self, company_name: str) -> List[Dict]:
        """Search using Crawl4AI for better JavaScript handling."""
        cases = []
        
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                # Construct search URL with query parameters
                search_params = {
                    "jenis_doc": "putusan",
                    "q": company_name,
                    "p": 1
                }
                
                # Build URL with query string
                query_string = "&".join([f"{k}={v}" for k, v in search_params.items()])
                search_url = f"{self.SEARCH_URL}?{query_string}"
                
                logger.info(f"Crawling: {search_url}")
                
                result = await asyncio.wait_for(
                    crawler.arun(
                        url=search_url,
                        wait_for="css:div.entry-c",
                        page_timeout=self.page_timeout,
                        bypass_cache=True
                    ),
                    timeout=self.timeout  # 15 seconds total timeout
                )
                
                if not result.success:
                    logger.warning(f"Crawl4AI crawl failed: {result.error_message}")
                    return cases
                
                # Parse the cleaned HTML or markdown
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(result.html, 'html.parser')
                
                # Find case containers - they are in div.entry-c
                case_elements = soup.find_all('div', class_='entry-c')
                
                # If not found, try alternative selectors
                if not case_elements:
                    case_elements = (
                        soup.find_all('div', class_='putusan-item') or
                        soup.find_all('div', class_='case-item') or
                        soup.find_all('div', class_=lambda x: x and 'entry' in str(x).lower()) or
                        []
                    )
                
                logger.info(f"Found {len(case_elements)} potential case elements")
                
                for element in case_elements[:10]:  # Limit to 10 cases
                    case_data = self._parse_case_element(element)
                    if case_data:
                        cases.append(case_data)
                    await asyncio.sleep(MAHKAMAH_CRAWL_DELAY)  # Rate limiting
                
        except asyncio.TimeoutError:
            logger.warning(f"Crawl4AI timeout untuk {company_name}, menggunakan fallback")
            return await self._search_fallback(company_name)
        except Exception as e:
            logger.warning(f"Crawl4AI error: {str(e)}, menggunakan fallback")
            # Try fallback instead of failing completely
            try:
                return await self._search_fallback(company_name)
            except Exception as e2:
                logger.error(f"Fallback juga gagal: {str(e2)}")
                # Return empty results instead of raising error
                return []
        
        return cases
    
    async def _search_fallback(self, company_name: str) -> List[Dict]:
        """Fallback search method using requests (if Crawl4AI unavailable)."""
        import requests
        from bs4 import BeautifulSoup
        
        cases = []
        
        try:
            search_url = self.SEARCH_URL
            params = {
                "jenis_doc": "putusan",
                "q": company_name,
                "p": 1
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            case_elements = (
                soup.find_all('div', class_='putusan-item') or
                soup.find_all('div', class_='case-item') or
                soup.select('table tbody tr') or
                []
            )
            
            for element in case_elements[:10]:
                case_data = self._parse_case_element(element)
                if case_data:
                    cases.append(case_data)
                await asyncio.sleep(MAHKAMAH_CRAWL_DELAY)
                
        except Exception as e:
            logger.error(f"Fallback search error: {str(e)}")
            raise MahkamahCrawlerError(f"Kesalahan pencarian fallback: {str(e)}")
        
        return cases
    
    def _parse_case_element(self, element) -> Optional[Dict]:
        """Parse individual case from HTML. Handles Indonesian date formats."""
        try:
            # Structure: div.entry-c contains:
            # 1. Breadcrumb navigation (div.small with links)
            # 2. Date info (div.small with Register/Putus/Upload)
            # 3. Case number link (strong > a)
            # 4. Case title/description (div after case number)
            # 5. Summary (list > blockquote)
            
            # 1. Find case number - it's in a strong > a link with "Putusan MAHKAMAH AGUNG Nomor" pattern
            case_number = "Tidak diketahui"
            source_url = ""
            
            # Look for strong element containing a link to putusan detail page
            all_strong = element.find_all('strong')
            for strong_elem in all_strong:
                case_num_a = strong_elem.find('a', href=lambda x: x and 'direktori/putusan' in x.lower())
                if case_num_a:
                    case_number = case_num_a.get_text(strip=True)
                    source_url = case_num_a.get('href', '')
                    if source_url and not source_url.startswith('http'):
                        source_url = f"{self.BASE_URL}{source_url}"
                    break
            
            # Fallback: look for any link with "Putusan" and "Nomor" in text
            if case_number == "Tidak diketahui":
                putusan_links = element.find_all('a', href=lambda x: x and 'putusan' in x.lower())
                for link in putusan_links:
                    link_text = link.get_text(strip=True)
                    if 'Putusan' in link_text and 'Nomor' in link_text:
                        case_number = link_text
                        source_url = link.get('href', '')
                        if source_url and not source_url.startswith('http'):
                            source_url = f"{self.BASE_URL}{source_url}"
                        break
            
            # 2. Find date information - in div.small with strong tags
            case_date = "Tidak diketahui"
            date_divs = element.find_all('div', class_='small')
            for date_div in date_divs:
                # Look for div containing date information (has "Register", "Putus", "Upload")
                date_text = date_div.get_text(separator=' ', strip=True)
                if 'Putus' in date_text or 'Register' in date_text:
                    # Extract date pattern DD-MM-YYYY after "Putus :"
                    import re
                    # Look for date after "Putus :"
                    putus_match = re.search(r'Putus\s*:\s*(\d{2}-\d{2}-\d{4})', date_text)
                    if putus_match:
                        case_date = putus_match.group(1)
                        break
                    # Fallback: find any date pattern
                    date_match = re.search(r'(\d{2}-\d{2}-\d{4})', date_text)
                    if date_match:
                        case_date = date_match.group(1)
                        break
            
            # 3. Find case title/description - it's in a div after the case number link
            case_title = "Tidak diketahui"
            
            # Find the div that comes after the strong case number link
            # Look for div that contains "Tanggal" (date) pattern
            all_divs = element.find_all('div')
            for div in all_divs:
                div_text = div.get_text(strip=True)
                # Look for div with "Tanggal" pattern (case description)
                if 'Tanggal' in div_text and len(div_text) > 20:
                    # Remove mark tags (highlighted search terms) first
                    for mark in div.find_all('mark'):
                        mark.unwrap()
                    
                    # Get cleaned text
                    case_title = div.get_text(separator=' ', strip=True)
                    
                    # Clean up: remove metadata like view counts, download counts, status
                    import re
                    # Remove patterns like "132 — 68 — Berkekuatan Hukum Tetap" or "90 — 0 — Berkekuatan Hukum Tetap"
                    case_title = re.sub(r'\s*\d+\s*—\s*\d+\s*—\s*Berkekuatan.*$', '', case_title, flags=re.IGNORECASE).strip()
                    # Remove trailing dashes and extra spaces
                    case_title = re.sub(r'\s*—\s*$', '', case_title).strip()
                    # Remove multiple spaces
                    case_title = re.sub(r'\s+', ' ', case_title).strip()
                    break
            
            # If no title found, try to extract from case number
            if case_title == "Tidak diketahui" and case_number != "Tidak diketahui":
                case_title = case_number
            
            case_type = self._determine_case_type(case_title)
            
            # 4. Find verdict summary - in blockquote elements
            verdict_summary = ""
            blockquotes = element.find_all('blockquote')
            if blockquotes:
                # Combine all blockquote text
                summary_parts = []
                for bq in blockquotes[:3]:  # Limit to first 3 blockquotes
                    text = bq.get_text(separator=' ', strip=True)
                    if text and len(text) > 20:  # Only include substantial text
                        summary_parts.append(text)
                
                if summary_parts:
                    verdict_summary = ' '.join(summary_parts)
                    # Limit to 500 characters
                    if len(verdict_summary) > 500:
                        verdict_summary = verdict_summary[:500] + "..."
            
            # If no summary from blockquotes, try to get from element text
            if not verdict_summary:
                all_text = element.get_text(separator=' ', strip=True)
                # Remove case number and title from text
                if case_number in all_text:
                    all_text = all_text.replace(case_number, '', 1)
                if case_title in all_text:
                    all_text = all_text.replace(case_title, '', 1)
                # Get a reasonable chunk
                if len(all_text) > 100:
                    verdict_summary = all_text[:300].strip()
                else:
                    verdict_summary = "Tidak ada ringkasan"
            
            severity = self.SEVERITY_MAP.get(case_type.lower(), "sedang")
            
            return {
                "case_number": case_number,
                "case_date": case_date,
                "case_title": case_title,
                "case_type": case_type,
                "verdict_summary": verdict_summary,
                "severity": severity,
                "source_url": source_url
            }
        except Exception as e:
            logger.warning(f"Error parsing case element: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _determine_case_type(self, title: str) -> str:
        """
        Classify case type from title.
        Returns Indonesian case types: pidana, perdata, tata usaha negara, niaga
        """
        if not title:
            return "perdata"
            
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['pidana', 'criminal', 'penal', 'kriminal', '/pid']):
            if 'khusus' in title_lower or '/pid.sus' in title_lower:
                return "pidana khusus"
            return "pidana"
        elif any(word in title_lower for word in ['niaga', 'commercial', 'dagang', 'perdagangan', '/pdt.sus']):
            return "niaga"
        elif any(word in title_lower for word in ['tata usaha negara', 'administrative', 'administrasi', 'tata usaha', '/tun']):
            return "tata usaha negara"
        elif any(word in title_lower for word in ['pajak', 'tax', '/pjk']):
            return "pajak"
        else:
            return "perdata"
    
    def _get_max_severity(self, severities: List[str]) -> str:
        """
        Get highest severity level.
        Returns Bahasa Indonesia: tinggi, sedang, rendah, tidak ada
        """
        severity_rank = {"tinggi": 3, "sedang": 2, "rendah": 1, "tidak ada": 0}
        if not severities:
            return "tidak ada"
        return max(severities, key=lambda x: severity_rank.get(x, 0))
