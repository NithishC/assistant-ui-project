"""
MCP-compatible Case Studies Tool
Converts the FastAPI CaseStudiesTool to MCP format while preserving all functionality
"""
import os
import sys
from typing import Optional, Dict, Any

# Add backend directory to path for imports
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(backend_dir)

from tools.case_studies import CaseStudiesTool
import logging

logger = logging.getLogger(__name__)


class MCPCaseStudiesTool:
    """MCP-compatible wrapper for Case Studies Tool"""
    
    def __init__(self):
        # Initialize the original tool with API key from environment
        # Try both BRAVE_API_KEY and BRAVE_SEARCH_API_KEY for compatibility
        api_key = os.getenv("BRAVE_API_KEY") or os.getenv("BRAVE_SEARCH_API_KEY")
        if not api_key:
            logger.warning("BRAVE_API_KEY or BRAVE_SEARCH_API_KEY not found - tool will use mock data")
        
        self.tool = CaseStudiesTool(api_key=api_key)
        logger.info("MCP Case Studies Tool initialized")
    
    async def execute(self, company: str, industry: Optional[str] = None, 
                     topic: Optional[str] = None, count: int = 2) -> str:
        """
        Execute case studies search with MCP-compatible interface
        
        Args:
            company: Company name to search for case studies
            industry: Industry or vertical to focus on (optional)
            topic: Specific topic or use case (optional)
            count: Number of results to return (default: 2, max: 5)
        
        Returns:
            Formatted string with case studies results
        """
        try:
            # Validate parameters
            if not company or not isinstance(company, str):
                return "❌ Error: 'company' parameter is required and must be a string"
            
            # Limit count to reasonable range for MCP usage
            count = max(1, min(count, 5))
            
            # Log the MCP call
            logger.info(f"MCP Case Studies: {company}, industry={industry}, topic={topic}, count={count}")
            
            # Execute the original tool with content fetching enabled
            result = await self.tool.execute(
                company=company,
                industry=industry,
                topic=topic,
                count=count,
                fetch_content=True  # Always fetch content for MCP consumers
            )
            
            # Add MCP-specific context
            mcp_result = f"🔍 MCP Case Studies Search Results\\n"
            mcp_result += f"📊 Query: {company}"
            if industry:
                mcp_result += f" | Industry: {industry}"
            if topic:
                mcp_result += f" | Topic: {topic}"
            mcp_result += f" | Count: {count}\\n\\n"
            
            # Append the tool results
            mcp_result += result
            
            # Add MCP footer for context
            mcp_result += "\\n\\n📡 Delivered via MCP Protocol from Assistant UI Tools"
            
            return mcp_result
            
        except Exception as e:
            error_msg = f"❌ MCP Case Studies Error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for MCP registration"""
        return {
            "name": "case_studies_search",
            "description": "Search for case studies, success stories, and customer testimonials from specific company domains. Enhanced with automatic content fetching for comprehensive analysis.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string",
                        "description": "Company name to search for case studies (e.g., 'Bloomreach', 'Salesforce')"
                    },
                    "industry": {
                        "type": "string",
                        "description": "Industry or vertical to focus on (e.g., 'retail', 'healthcare', 'finance')"
                    },
                    "topic": {
                        "type": "string",
                        "description": "Specific topic or use case (e.g., 'personalization', 'customer engagement')"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of results to return (default: 2, max: 5)",
                        "default": 2,
                        "minimum": 1,
                        "maximum": 5
                    }
                },
                "required": ["company"]
            }
        }
