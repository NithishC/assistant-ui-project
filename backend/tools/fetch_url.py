import httpx
from typing import Optional
from .base import BaseTool, ToolParameter
import logging
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
import os

logger = logging.getLogger(__name__)

class FetchURLTool(BaseTool):
    """Web scraping tool using ScraperAPI service"""
    
    def __init__(self):
        self.api_key = os.getenv("SCRAPERAPI_KEY", "")
        self.scraper_url = "https://api.scraperapi.com/"
        self.timeout = 30.0
        self.max_content_length = 50000  # ~12k tokens
        
    @property
    def name(self) -> str:
        return "fetch_url"
    
    @property
    def description(self) -> str:
        return "Fetches webpage content using ScraperAPI service to bypass blocks and JavaScript rendering"
    
    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="url",
                type="string",
                description="The URL to fetch content from",
                required=True
            )
        ]
    
    def _clean_html_content(self, html: str) -> str:
        """Clean HTML and convert to markdown"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header', 
                           'noscript', 'iframe', 'form', 'button', 'input', 'svg']):
            element.decompose()
        
        # Remove elements with common ad/tracking classes
        unwanted_patterns = [
            r'ad[s]?', r'advertisement', r'promo', r'popup', r'modal', r'cookie',
            r'tracking', r'analytics', r'social', r'share', r'comment', r'sidebar',
            r'widget', r'banner', r'menu', r'navigation'
        ]
        
        for pattern in unwanted_patterns:
            for element in soup.find_all(class_=re.compile(pattern, re.I)):
                element.decompose()
            for element in soup.find_all(id=re.compile(pattern, re.I)):
                element.decompose()
        
        # Try to find main content
        main_content = None
        content_selectors = [
            'main', 'article', '[role="main"]', '.content', '#content',
            '.post-content', '.entry-content', '.article-content',
            '.story-body', '.article-body', '.content-body',
            '.post-body', '.entry-body', '.main-content', '.page-content'
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content and len(main_content.get_text().strip()) > 100:
                break
        
        # Fallback to body if no main content found
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return ""
        
        # Convert to markdown
        markdown_content = md(str(main_content), heading_style="ATX")
        
        # Clean up markdown
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        markdown_content = re.sub(r'[ \t]+', ' ', markdown_content)
        markdown_content = re.sub(r'^\s*$\n', '', markdown_content, flags=re.MULTILINE)
        
        return markdown_content.strip()
    
    async def execute(self, url: str) -> str:
        """Fetch URL content using ScraperAPI"""
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                return f"Error: Invalid URL. Must start with http:// or https://"
            
            logger.info(f"Fetching URL with ScraperAPI: {url}")
            
            # Prepare ScraperAPI request
            payload = {
                'api_key': self.api_key,
                'url': url,
                'render': 'true',  # Enable JavaScript rendering
                'wait': 2000,      # Wait 2 seconds for page to load
                'format': 'html'   # Return HTML content
            }
            
            # Make request to ScraperAPI
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.scraper_url, params=payload)
                
                if response.status_code != 200:
                    return f"Error: ScraperAPI returned status {response.status_code}. Response: {response.text}"
                
                html_content = response.text
                
                if not html_content or len(html_content) < 100:
                    return f"Error: No content received from ScraperAPI for {url}"
                
                # Extract and clean content
                markdown_content = self._clean_html_content(html_content)
                
                if not markdown_content:
                    return f"Error: No meaningful content could be extracted from {url}"
                
                # Get page title
                soup = BeautifulSoup(html_content, 'html.parser')
                title = soup.find('title')
                title_text = title.get_text().strip() if title else "Untitled"
                
                # Truncate if too long
                if len(markdown_content) > self.max_content_length:
                    markdown_content = markdown_content[:self.max_content_length] + "\n\n[Content truncated...]"
                
                # Format result
                result = f"# {title_text}\n\n"
                result += f"Source: {url}\n"
                result += f"Method: ScraperAPI\n\n"
                result += "---\n\n"
                result += markdown_content
                
                logger.info(f"Successfully fetched and processed content from {url}")
                return result
                
        except httpx.TimeoutException:
            return f"Error: Request timed out after {self.timeout} seconds"
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return f"Error: Failed to fetch content - {str(e)}"
