import os
import httpx
import json
from typing import List, Optional
from .base import BaseTool, ToolParameter
from .fetch_url import FetchURLTool
import logging
import asyncio

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """Enhanced web search tool using Brave Search API with automatic content fetching"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BRAVE_SEARCH_API_KEY", "")
        if not self.api_key:
            raise ValueError("BRAVE_SEARCH_API_KEY is required")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.fetch_tool = FetchURLTool()  # Initialize fetch tool for content retrieval
        
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for current information using Brave Search API and automatically fetch full content from top results"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="The search query to look up on the web",
                required=True
            ),
            ToolParameter(
                name="count",
                type="integer",
                description="Number of results to return (default: 2, max: 5)",
                required=False
            ),
            ToolParameter(
                name="freshness",
                type="string",
                description="Filter by recency: 'day', 'week', 'month', 'year'",
                required=False,
                enum=["day", "week", "month", "year"]
            ),
            ToolParameter(
                name="fetch_content",
                type="boolean",
                description="Whether to fetch full content from top results (default: True)",
                required=False
            )
        ]
    
    async def execute(self, query: str, count: int = 2, freshness: Optional[str] = None, fetch_content: bool = True) -> str:
        """
        Execute web search and optionally fetch full content from top results
        """
        # Limit count to reasonable range
        count = min(max(count, 1), 5)
        
        try:
            # Step 1: Get search results from Brave API
            params = {
                "q": query,
                "count": count
            }
            
            if freshness:
                params["freshness"] = freshness
            
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Brave Search API error: {response.status_code} - {response.text}")
                    return f"Search API error: {response.status_code}"
                
                data = response.json()
                
                # Extract search results
                web_results = data.get("web", {}).get("results", [])
                
                if not web_results:
                    return f"No results found for: {query}"
                
                # Step 2: Format search results
                formatted_results = []
                urls_to_fetch = []
                
                for i, result in enumerate(web_results[:count], 1):
                    title = result.get("title", "No title")
                    url = result.get("url", "")
                    description = result.get("description", "No description")
                    
                    formatted_results.append({
                        "index": i,
                        "title": title,
                        "url": url,
                        "description": description
                    })
                    
                    # Collect URLs for content fetching (top 2 results only)
                    if fetch_content and i <= 2 and url:
                        urls_to_fetch.append(url)
                
                # Step 3: Fetch full content from top results
                fetched_content = []
                if fetch_content and urls_to_fetch:
                    logger.info(f"Fetching content from {len(urls_to_fetch)} URLs")
                    
                    # Fetch content from URLs concurrently
                    fetch_tasks = []
                    for url in urls_to_fetch:
                        task = asyncio.create_task(self._safe_fetch_content(url))
                        fetch_tasks.append(task)
                    
                    # Wait for all fetches to complete
                    fetch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
                    
                    for i, result in enumerate(fetch_results):
                        if isinstance(result, Exception):
                            logger.error(f"Failed to fetch content from {urls_to_fetch[i]}: {result}")
                            continue
                        
                        if result and len(result) > 100:  # Only include substantial content
                            fetched_content.append({
                                "url": urls_to_fetch[i],
                                "content": result
                            })
                
                # Step 4: Format final response
                response_parts = []
                
                # Add search results summary
                response_parts.append(f"🔍 **Search Results for '{query}'**\n")
                
                for result in formatted_results:
                    response_parts.append(f"{result['index']}. **{result['title']}**")
                    response_parts.append(f"   URL: {result['url']}")
                    response_parts.append(f"   {result['description']}\n")
                
                # Add fetched content if available
                if fetched_content:
                    response_parts.append("\n📄 **Full Article Content:**\n")
                    
                    for i, content in enumerate(fetched_content, 1):
                        response_parts.append(f"\n--- **Article {i}** ---")
                        response_parts.append(f"Source: {content['url']}")
                        response_parts.append(content['content'])
                        response_parts.append("\n" + "="*50 + "\n")
                
                # Add summary if available from Brave API
                if "summary" in data and data["summary"]:
                    response_parts.append(f"\n💡 **Search Summary:** {data['summary']}")
                
                return "\n".join(response_parts)
                
        except httpx.TimeoutException:
            return "Search request timed out. Please try again."
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            return f"Error performing search: {str(e)}"
    
    async def _safe_fetch_content(self, url: str) -> Optional[str]:
        """Safely fetch content from URL with error handling"""
        try:
            result = await self.fetch_tool.execute(url)
            
            # Extract just the content part (remove title and metadata)
            if "---" in result:
                parts = result.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2].strip()
                    # Limit content length to avoid token bloat
                    if len(content) > 8000:
                        content = content[:8000] + "\n\n[Content truncated...]"
                    return content
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {str(e)}")
            return None