import os
from typing import List, Optional
from .web_search import WebSearchTool
from .base import ToolParameter
import logging

logger = logging.getLogger(__name__)

class CaseStudiesTool(WebSearchTool):
    """
    Case studies search tool that constrains searches to specific domains.
    Useful for finding customer case studies, success stories, and testimonials.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        # Default domains for case studies
        self.case_study_domains = [
            "bloomreach.com",
            "salesforce.com", 
            "hubspot.com",
            "adobe.com",
            "oracle.com",
            "sap.com",
            "microsoft.com",
            "aws.amazon.com",
            "cloud.google.com"
        ]
    
    @property
    def name(self) -> str:
        return "case_studies_search"
    
    @property
    def description(self) -> str:
        return "Search for case studies, success stories, and customer testimonials from specific company domains"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="company",
                type="string",
                description="The company whose case studies to search for (e.g., 'Bloomreach', 'Salesforce')",
                required=True
            ),
            ToolParameter(
                name="industry",
                type="string",
                description="Industry or vertical to focus on (e.g., 'retail', 'healthcare', 'finance')",
                required=False
            ),
            ToolParameter(
                name="topic",
                type="string",
                description="Specific topic or use case (e.g., 'personalization', 'customer engagement')",
                required=False
            ),
            ToolParameter(
                name="count",
                type="integer",
                description="Number of results to return (default: 2, max: 10)",
                required=False
            ),
            ToolParameter(
                name="fetch_content",
                type="boolean",
                description="Whether to fetch full content from top results (default: True)",
                required=False
            )
        ]
    
    def _get_company_domain(self, company: str) -> Optional[str]:
        """Get the domain for a given company name"""
        company_lower = company.lower().replace(" ", "")
        
        # Direct domain mappings
        domain_map = {
            "bloomreach": "bloomreach.com",
            "salesforce": "salesforce.com",
            "hubspot": "hubspot.com",
            "adobe": "adobe.com",
            "oracle": "oracle.com",
            "sap": "sap.com",
            "microsoft": "microsoft.com",
            "aws": "aws.amazon.com",
            "amazon": "aws.amazon.com",
            "google": "cloud.google.com",
            "googlecloud": "cloud.google.com"
        }
        
        return domain_map.get(company_lower)
    
    async def execute(self, company: str, industry: Optional[str] = None, 
                     topic: Optional[str] = None, count: int = 2, fetch_content: bool = True) -> str:
        """
        Search for case studies with domain constraints
        """
        # Get company domain
        domain = self._get_company_domain(company)
        if not domain:
            # If domain not found, try searching with company name
            domain = f"{company.lower()}.com"
        
        # Build search query
        query_parts = [f"site:{domain}"]
        
        # Add case study keywords
        query_parts.append("(case study OR success story OR customer story OR testimonial)")
        
        # Add industry filter if specified
        if industry:
            query_parts.append(f'"{industry}"')
        
        # Add topic filter if specified
        if topic:
            query_parts.append(f'"{topic}"')
        
        # Combine query parts
        search_query = " ".join(query_parts)
        
        # Log the constructed query
        logger.info(f"Case studies search query: {search_query}")
        
        # Execute search using parent class with content fetching
        results = await super().execute(
            query=search_query,
            count=min(count, 10),  # Limit to 10 for case studies
            freshness="year",  # Focus on recent case studies
            fetch_content=fetch_content
        )
        
        # Add context to results
        context = f"Case studies from {company}"
        if industry:
            context += f" in {industry}"
        if topic:
            context += f" about {topic}"
        
        # Replace the generic header with specific context
        if results.startswith("Search results for"):
            lines = results.split("\n")
            lines[0] = f"{context}:"
            results = "\n".join(lines)
        
        return results
