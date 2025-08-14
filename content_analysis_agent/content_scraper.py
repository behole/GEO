import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import re
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import trafilatura
from markdownify import markdownify as md

from config import get_config

logger = logging.getLogger(__name__)

@dataclass
class PageContent:
    """Represents scraped content from a single page"""
    url: str
    title: str
    meta_description: str
    headings: Dict[str, List[str]]  # h1, h2, h3, etc.
    paragraphs: List[str]
    lists: List[List[str]]
    images: List[Dict[str, str]]  # src, alt, caption
    links: List[Dict[str, str]]   # href, text, type (internal/external)
    structured_data: List[Dict]   # JSON-LD, microdata, etc.
    word_count: int
    reading_time: int  # estimated minutes
    last_modified: Optional[str]
    content_type: str  # product_page, faq, blog_post, etc.
    raw_html: str
    clean_text: str
    markdown: str
    scrape_timestamp: str
    scrape_success: bool
    error_message: Optional[str]

@dataclass
class SiteAnalysis:
    """Complete analysis of a website"""
    domain: str
    total_pages: int
    successful_scrapes: int
    failed_scrapes: int
    pages: List[PageContent]
    site_structure: Dict[str, Any]
    robots_txt: str
    sitemap_urls: List[str]
    crawl_duration: float
    analysis_timestamp: str

class ContentScraper:
    """Advanced content scraper for website analysis"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.session = None
        self.scraped_urls = set()
        self.failed_urls = set()
        self.skipped_urls = set()
        
        # Domain blocklist for GEO optimization focus
        self.blocked_domains = {
            # Shipping and logistics
            'ups.com', 'fedex.com', 'usps.com', 'dhl.com', 'shippo.com',
            # Social media platforms
            'facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com', 
            'youtube.com', 'tiktok.com', 'pinterest.com', 'snapchat.com',
            # Payment processors
            'paypal.com', 'stripe.com', 'square.com', 'shopify.com',
            # Analytics and tracking
            'google-analytics.com', 'googletagmanager.com', 'hotjar.com',
            'mixpanel.com', 'segment.com', 'amplitude.com',
            # Ad networks and widgets
            'googleadservices.com', 'doubleclick.net', 'adsystem.com',
            'amazon-adsystem.com', 'googlesyndication.com',
            # Other non-content domains
            'cdnjs.cloudflare.com', 'jsdelivr.net', 'unpkg.com',
            'fonts.googleapis.com', 'gravatar.com'
        }
        
        # GEO-relevant content patterns (higher priority)
        self.geo_priority_keywords = [
            # Product-focused
            'product', 'sunscreen', 'spf', 'mineral', 'zinc', 'titanium',
            # Information content
            'ingredient', 'guide', 'how-to', 'application', 'use', 'apply',
            'faq', 'question', 'about', 'story', 'science', 'research',
            # Skin-related content
            'skin', 'face', 'sensitive', 'acne', 'dry', 'oily', 'care',
            # Educational content
            'learn', 'education', 'tips', 'advice', 'benefit', 'protection'
        ]
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=self.config.MAX_CONCURRENT_REQUESTS)
        timeout = aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_website(self, website_url: str, max_pages: Optional[int] = None) -> SiteAnalysis:
        """Scrape entire website with intelligent crawling"""
        start_time = time.time()
        max_pages = max_pages or self.config.MAX_PAGES_PER_SITE
        
        logger.info(f"Starting website scrape for {website_url}")
        
        # Get site structure and important URLs
        site_structure = await self._analyze_site_structure(website_url)
        important_urls = await self._discover_important_urls(website_url, site_structure)
        
        # Limit URLs based on priority and max_pages
        urls_to_scrape = self._prioritize_urls(important_urls, max_pages)
        
        logger.info(f"Found {len(urls_to_scrape)} URLs to scrape")
        
        # Create semaphore for concurrent requests
        semaphore = asyncio.Semaphore(self.config.MAX_CONCURRENT_REQUESTS)
        
        # Scrape pages concurrently
        scrape_tasks = [
            self._scrape_single_page_with_semaphore(semaphore, url)
            for url in urls_to_scrape
        ]
        
        pages = await asyncio.gather(*scrape_tasks, return_exceptions=True)
        
        # Process results
        successful_pages = []
        failed_count = 0
        
        for i, result in enumerate(pages):
            if isinstance(result, Exception):
                logger.error(f"Exception scraping {urls_to_scrape[i]}: {str(result)}")
                failed_count += 1
            elif result and result.scrape_success:
                successful_pages.append(result)
            else:
                failed_count += 1
        
        crawl_duration = time.time() - start_time
        
        # Enhanced logging with skipped URL reporting
        logger.info(f"Scraping completed: {len(successful_pages)} successful, {failed_count} failed, {len(self.skipped_urls)} skipped")
        
        if self.skipped_urls:
            logger.info(f"Skipped URLs summary:")
            skipped_by_reason = {}
            for url in self.skipped_urls:
                if any(blocked in url.lower() for blocked in self.blocked_domains):
                    reason = "Blocked domain"
                elif urlparse(url).netloc.lower() != urlparse(website_url).netloc.lower():
                    reason = "External domain"
                else:
                    reason = "Other filter"
                    
                if reason not in skipped_by_reason:
                    skipped_by_reason[reason] = []
                skipped_by_reason[reason].append(url)
            
            for reason, urls in skipped_by_reason.items():
                logger.info(f"  {reason}: {len(urls)} URLs")
                # Log first few examples
                for url in urls[:3]:
                    logger.info(f"    - {url}")
                if len(urls) > 3:
                    logger.info(f"    ... and {len(urls) - 3} more")
        
        return SiteAnalysis(
            domain=urlparse(website_url).netloc,
            total_pages=len(urls_to_scrape),
            successful_scrapes=len(successful_pages),
            failed_scrapes=failed_count,
            pages=successful_pages,
            site_structure=site_structure,
            robots_txt=site_structure.get('robots_txt', ''),
            sitemap_urls=site_structure.get('sitemap_urls', []),
            crawl_duration=crawl_duration,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    async def _scrape_single_page_with_semaphore(self, semaphore: asyncio.Semaphore, url: str) -> Optional[PageContent]:
        """Scrape single page with rate limiting"""
        async with semaphore:
            return await self.scrape_single_page(url)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def scrape_single_page(self, url: str) -> Optional[PageContent]:
        """Scrape a single page and extract structured content"""
        try:
            logger.debug(f"Scraping page: {url}")
            
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
            
            async with self.session.get(url) as response:
                # Improved error handling for different status codes
                if response.status >= 400:
                    if response.status == 403:
                        logger.warning(f"Access forbidden for {url} - likely blocked by site")
                        return self._create_failed_page_content(url, f"Access forbidden (403)")
                    elif response.status == 404:
                        logger.warning(f"Page not found: {url}")
                        return self._create_failed_page_content(url, f"Page not found (404)")
                    elif response.status >= 500:
                        logger.warning(f"Server error for {url}: HTTP {response.status}")
                        return self._create_failed_page_content(url, f"Server error ({response.status})")
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return self._create_failed_page_content(url, f"HTTP {response.status}")
                
                # Handle redirects to external domains
                if str(response.url) != url:
                    redirect_domain = urlparse(str(response.url)).netloc.lower()
                    target_domain = urlparse(url).netloc.lower()
                    if redirect_domain != target_domain:
                        logger.warning(f"External redirect detected: {url} -> {response.url}")
                        self.skipped_urls.add(url)
                        return self._create_failed_page_content(url, "Redirected to external domain")
                
                # Get content with size limits
                try:
                    html_content = await response.text(encoding='utf-8', errors='ignore')
                except UnicodeDecodeError:
                    html_content = await response.text(encoding='latin-1', errors='ignore')
                
                # Check content size (avoid processing extremely large pages)
                if len(html_content) > 5 * 1024 * 1024:  # 5MB limit
                    logger.warning(f"Page too large ({len(html_content)} bytes): {url}")
                    return self._create_failed_page_content(url, "Page too large")
                
                content_type = response.headers.get('content-type', '').lower()
                
                if 'text/html' not in content_type:
                    logger.warning(f"Non-HTML content type for {url}: {content_type}")
                    return self._create_failed_page_content(url, f"Non-HTML content: {content_type}")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract clean text using trafilatura
                clean_text = trafilatura.extract(html_content) or ""
                
                # Convert to markdown
                markdown_content = md(html_content, heading_style="ATX")
                
                # Extract structured content
                page_content = PageContent(
                    url=url,
                    title=self._extract_title(soup),
                    meta_description=self._extract_meta_description(soup),
                    headings=self._extract_headings(soup),
                    paragraphs=self._extract_paragraphs(soup),
                    lists=self._extract_lists(soup),
                    images=self._extract_images(soup, url),
                    links=self._extract_links(soup, url),
                    structured_data=self._extract_structured_data(soup),
                    word_count=len(clean_text.split()) if clean_text else 0,
                    reading_time=self._calculate_reading_time(clean_text),
                    last_modified=self._extract_last_modified(soup, response.headers),
                    content_type=self._classify_content_type(url, soup, clean_text),
                    raw_html=html_content if self.config.SAVE_HTML_CONTENT else "",
                    clean_text=clean_text,
                    markdown=markdown_content,
                    scrape_timestamp=datetime.now().isoformat(),
                    scrape_success=True,
                    error_message=None
                )
                
                self.scraped_urls.add(url)
                return page_content
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            self.failed_urls.add(url)
            return self._create_failed_page_content(url, str(e))
    
    def _create_failed_page_content(self, url: str, error_msg: str) -> PageContent:
        """Create a failed page content object"""
        return PageContent(
            url=url,
            title="",
            meta_description="",
            headings={},
            paragraphs=[],
            lists=[],
            images=[],
            links=[],
            structured_data=[],
            word_count=0,
            reading_time=0,
            last_modified=None,
            content_type="unknown",
            raw_html="",
            clean_text="",
            markdown="",
            scrape_timestamp=datetime.now().isoformat(),
            scrape_success=False,
            error_message=error_msg
        )
    
    async def _analyze_site_structure(self, website_url: str) -> Dict[str, Any]:
        """Analyze site structure, robots.txt, sitemap, etc."""
        domain = urlparse(website_url).netloc
        structure = {
            'domain': domain,
            'robots_txt': '',
            'sitemap_urls': [],
            'navigation_structure': {},
            'page_types': set()
        }
        
        # Get robots.txt
        try:
            robots_url = f"https://{domain}/robots.txt"
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    structure['robots_txt'] = await response.text()
                    # Extract sitemap URLs from robots.txt
                    sitemap_matches = re.findall(r'sitemap:\s*(.+)', structure['robots_txt'], re.IGNORECASE)
                    structure['sitemap_urls'].extend(sitemap_matches)
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt for {domain}: {str(e)}")
        
        # Try common sitemap locations
        common_sitemaps = ['/sitemap.xml', '/sitemap_index.xml', '/sitemap.txt']
        for sitemap_path in common_sitemaps:
            try:
                sitemap_url = f"https://{domain}{sitemap_path}"
                async with self.session.get(sitemap_url) as response:
                    if response.status == 200 and sitemap_url not in structure['sitemap_urls']:
                        structure['sitemap_urls'].append(sitemap_url)
            except Exception:
                continue
        
        return structure
    
    async def _discover_important_urls(self, website_url: str, site_structure: Dict) -> List[str]:
        """Discover important URLs using multiple strategies"""
        urls = set()
        
        # Add the homepage
        urls.add(website_url)
        
        # Parse sitemaps
        for sitemap_url in site_structure.get('sitemap_urls', []):
            sitemap_urls = await self._parse_sitemap(sitemap_url)
            urls.update(sitemap_urls)
        
        # Crawl from homepage to discover more URLs
        homepage_urls = await self._crawl_from_page(website_url, depth=0)
        urls.update(homepage_urls)
        
        # Filter to same domain
        domain = urlparse(website_url).netloc
        filtered_urls = [
            url for url in urls 
            if urlparse(url).netloc == domain or urlparse(url).netloc == f"www.{domain}"
        ]
        
        return list(set(filtered_urls))
    
    async def _parse_sitemap(self, sitemap_url: str) -> List[str]:
        """Parse XML sitemap to extract URLs"""
        urls = []
        try:
            async with self.session.get(sitemap_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse XML sitemap
                    soup = BeautifulSoup(content, 'xml')
                    
                    # Handle sitemap index
                    sitemap_tags = soup.find_all('sitemap')
                    if sitemap_tags:
                        for sitemap_tag in sitemap_tags:
                            loc_tag = sitemap_tag.find('loc')
                            if loc_tag:
                                nested_urls = await self._parse_sitemap(loc_tag.text)
                                urls.extend(nested_urls)
                    
                    # Handle URL set
                    url_tags = soup.find_all('url')
                    for url_tag in url_tags:
                        loc_tag = url_tag.find('loc')
                        if loc_tag:
                            urls.append(loc_tag.text)
        
        except Exception as e:
            logger.warning(f"Error parsing sitemap {sitemap_url}: {str(e)}")
        
        return urls
    
    async def _crawl_from_page(self, url: str, depth: int) -> List[str]:
        """Crawl URLs from a single page"""
        if depth >= self.config.CRAWL_DEPTH:
            return []
        
        urls = set()
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract all links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(url, href)
                        
                        # Basic URL filtering
                        if self._should_include_url(full_url):
                            urls.add(full_url)
                            
                            # Recursively crawl if depth allows
                            if depth < self.config.CRAWL_DEPTH - 1:
                                nested_urls = await self._crawl_from_page(full_url, depth + 1)
                                urls.update(nested_urls)
        
        except Exception as e:
            logger.warning(f"Error crawling from {url}: {str(e)}")
        
        return list(urls)
    
    def _should_include_url(self, url: str) -> bool:
        """Determine if URL should be included in crawl - GEO-focused filtering"""
        parsed = urlparse(url)
        
        # Check if domain is in blocklist
        domain = parsed.netloc.lower()
        # Remove www. prefix for matching
        domain = domain.replace('www.', '') if domain.startswith('www.') else domain
        
        if any(blocked in domain for blocked in self.blocked_domains):
            logger.debug(f"Skipping blocked domain: {url}")
            self.skipped_urls.add(url)
            return False
        
        # Skip certain file types (expanded list)
        skip_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  # Documents
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico',   # Images
            '.css', '.js', '.json', '.xml', '.txt',                     # Web assets
            '.zip', '.rar', '.tar', '.gz',                              # Archives
            '.mp4', '.avi', '.mov', '.wmv', '.mp3', '.wav'              # Media
        }
        if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
            logger.debug(f"Skipping file extension: {url}")
            return False
        
        # Skip certain URL patterns (expanded)
        skip_patterns = [
            '#', 'mailto:', 'tel:', 'javascript:', 'data:',
            '/wp-admin', '/admin', '/login', '/register', '/checkout',  # Admin/commerce
            '/cart', '/account', '/profile', '/settings',              # User areas
            '/search', '/filter', '?search=', '?filter=',              # Search/filter URLs
            '/api/', '/ajax/', '/webhook/',                            # API endpoints
            '?utm_', '?ref=', '?fb', '?gclid',                        # Tracking params
        ]
        url_lower = url.lower()
        for pattern in skip_patterns:
            if pattern in url_lower:
                logger.debug(f"Skipping URL pattern {pattern}: {url}")
                return False
        
        # Additional domain validation - only include same domain or subdomain
        target_domain = urlparse(self.config.BRAND_WEBSITE).netloc.lower()
        target_domain = target_domain.replace('www.', '') if target_domain.startswith('www.') else target_domain
        
        if not (domain == target_domain or domain.endswith(f'.{target_domain}')):
            logger.debug(f"Skipping external domain: {url}")
            self.skipped_urls.add(url)
            return False
        
        return True
    
    def _prioritize_urls(self, urls: List[str], max_pages: int) -> List[str]:
        """Prioritize URLs based on GEO relevance and content importance"""
        priority_scores = {}
        
        # Critical GEO content (highest priority)
        critical_keywords = [
            'product', 'sunscreen', 'spf', 'mineral', 'zinc', 'titanium',
            'ingredient', 'faq', 'about'
        ]
        
        # High-value content
        high_priority_keywords = [
            'how-to', 'guide', 'application', 'use', 'apply', 'tutorial',
            'science', 'research', 'benefit', 'protection', 'safety'
        ]
        
        # Medium-value content
        medium_priority_keywords = [
            'skin', 'face', 'care', 'sensitive', 'tips', 'advice',
            'blog', 'news', 'story', 'learn', 'education'
        ]
        
        # Lower priority but still relevant
        low_priority_keywords = [
            'support', 'help', 'contact', 'shipping', 'return'
        ]
        
        for url in urls:
            score = 1  # Base score
            url_lower = url.lower()
            path = urlparse(url).path.lower()
            
            # Critical content gets highest boost
            for keyword in critical_keywords:
                if keyword in url_lower:
                    score += 10  # Major boost
            
            # High priority content
            for keyword in high_priority_keywords:
                if keyword in url_lower:
                    score += 5
            
            # Medium priority content
            for keyword in medium_priority_keywords:
                if keyword in url_lower:
                    score += 3
            
            # Low priority content
            for keyword in low_priority_keywords:
                if keyword in url_lower:
                    score += 1
            
            # Boost for likely product/category pages
            if any(pattern in path for pattern in ['/products/', '/collections/', '/categories/']):
                score += 8
            
            # Boost for educational content
            if any(pattern in path for pattern in ['/learn/', '/education/', '/guides/', '/how-to/']):
                score += 7
            
            # Boost for brand story content
            if any(pattern in path for pattern in ['/about', '/story', '/mission', '/science']):
                score += 6
            
            # Boost for homepage and main pages
            if path in ['/', '/home', '/index']:
                score += 5
            
            # Boost for shorter, cleaner URLs (usually more important pages)
            if len(url) < 80:
                score += 2
            elif len(url) < 120:
                score += 1
            
            # Penalize very deep URLs (often less important)
            path_depth = url.count('/') - 2  # Account for protocol
            if path_depth > 4:
                score -= (path_depth - 4) * 2
            
            # Penalize URLs with many parameters (often filters/searches)
            if url.count('?') > 0 and url.count('=') > 2:
                score -= 3
            
            # Ensure minimum score
            priority_scores[url] = max(1, score)
        
        # Sort by priority and return top URLs
        sorted_urls = sorted(urls, key=lambda x: priority_scores.get(x, 1), reverse=True)
        
        # Log top URLs for debugging
        logger.info(f"Top 10 prioritized URLs:")
        for i, url in enumerate(sorted_urls[:10], 1):
            logger.info(f"  {i}. [{priority_scores.get(url, 1)}] {url}")
        
        return sorted_urls[:max_pages]
    
    # Content extraction methods
    def _extract_title(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        headings = {}
        for level in range(1, 7):  # h1 to h6
            tag_name = f'h{level}'
            heading_tags = soup.find_all(tag_name)
            headings[tag_name] = [tag.get_text(strip=True) for tag in heading_tags]
        return headings
    
    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        paragraphs = soup.find_all('p')
        return [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    
    def _extract_lists(self, soup: BeautifulSoup) -> List[List[str]]:
        lists = []
        for list_tag in soup.find_all(['ul', 'ol']):
            items = [li.get_text(strip=True) for li in list_tag.find_all('li')]
            if items:
                lists.append(items)
        return lists
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                src = urljoin(base_url, src)
                images.append({
                    'src': src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
        return images
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = urljoin(base_url, link['href'])
            link_domain = urlparse(href).netloc
            
            links.append({
                'href': href,
                'text': link.get_text(strip=True),
                'type': 'internal' if link_domain == base_domain else 'external'
            })
        
        return links
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        structured_data = []
        
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = script.string
                if data:
                    structured_data.append({
                        'type': 'json-ld',
                        'data': data.strip()
                    })
            except Exception:
                continue
        
        # Microdata (basic extraction)
        for elem in soup.find_all(attrs={'itemscope': True}):
            try:
                structured_data.append({
                    'type': 'microdata',
                    'itemtype': elem.get('itemtype', ''),
                    'content': elem.get_text(strip=True)[:200]  # First 200 chars
                })
            except Exception:
                continue
        
        return structured_data
    
    def _calculate_reading_time(self, text: str, wpm: int = 200) -> int:
        """Calculate estimated reading time in minutes"""
        if not text:
            return 0
        word_count = len(text.split())
        return max(1, round(word_count / wpm))
    
    def _extract_last_modified(self, soup: BeautifulSoup, headers: Dict) -> Optional[str]:
        """Extract last modified date from headers or meta tags"""
        # Check HTTP headers
        last_modified = headers.get('last-modified')
        if last_modified:
            return last_modified
        
        # Check meta tags
        meta_modified = soup.find('meta', attrs={'name': 'last-modified'})
        if meta_modified and meta_modified.get('content'):
            return meta_modified['content']
        
        # Check article published/modified dates
        for attr in ['dateModified', 'datePublished']:
            date_elem = soup.find(attrs={'property': attr}) or soup.find(attrs={'itemprop': attr})
            if date_elem and date_elem.get('content'):
                return date_elem['content']
        
        return None
    
    def _classify_content_type(self, url: str, soup: BeautifulSoup, text: str) -> str:
        """Classify the type of content on the page"""
        url_lower = url.lower()
        text_lower = text.lower()
        
        # URL-based classification
        if any(keyword in url_lower for keyword in ['product', 'sunscreen']):
            return 'product_page'
        elif any(keyword in url_lower for keyword in ['faq', 'frequently-asked']):
            return 'faq_page'
        elif any(keyword in url_lower for keyword in ['blog', 'news', 'article']):
            return 'blog_post'
        elif any(keyword in url_lower for keyword in ['about', 'company', 'story']):
            return 'about_page'
        elif any(keyword in url_lower for keyword in ['contact', 'support']):
            return 'contact_page'
        elif any(keyword in url_lower for keyword in ['ingredient', 'guide', 'how-to']):
            return 'guide_page'
        
        # Content-based classification
        if 'ingredients' in text_lower and ('zinc' in text_lower or 'titanium' in text_lower):
            return 'ingredient_guide'
        elif 'application' in text_lower and ('apply' in text_lower or 'use' in text_lower):
            return 'application_guide'
        elif text_lower.count('?') > 5:  # Lots of questions
            return 'faq_page'
        
        # Check structured data for more specific types
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                if script.string and 'Product' in script.string:
                    return 'product_page'
                elif script.string and 'Article' in script.string:
                    return 'blog_post'
            except Exception:
                continue
        
        return 'general_page'