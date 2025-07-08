from typing import Dict, List, Optional
from .base import BaseTool, ToolDefinition
from .web_search import WebSearchTool
from .case_studies import CaseStudiesTool
from .fetch_url import FetchURLTool
from .file_system import FileSystemTool
import os
import logging

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available tools"""
        try:
            # Initialize web search tools (require API key)
            api_key = os.getenv("BRAVE_SEARCH_API_KEY")
            if api_key:
                logger.info("Initializing web search tools with Brave Search API")
                self.register_tool(WebSearchTool(api_key))
                self.register_tool(CaseStudiesTool(api_key))
                self.register_tool(FetchURLTool())
            else:
                logger.warning("BRAVE_SEARCH_API_KEY not found - web search tools disabled")
            
            # Initialize file system tool (no API key needed)
            project_root = os.getenv("PROJECT_ROOT", os.getcwd())
            logger.info("Initializing file system tool")
            self.register_tool(FileSystemTool(project_root))
            
            logger.info(f"Tool registry initialized with {len(self.tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize tools: {str(e)}")
            raise
    
    def register_tool(self, tool: BaseTool):
        """Register a tool in the registry"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """Get OpenAI-compatible tool definitions"""
        return [tool.to_openai_tool() for tool in self.tools.values()]
    
    def get_tool_names(self) -> List[str]:
        """Get list of tool names"""
        return list(self.tools.keys())
    
    async def execute_tool(self, name: str, **kwargs) -> str:
        """Execute a tool by name with given parameters"""
        tool = self.get_tool(name)
        if not tool:
            return f"Error: Tool '{name}' not found. Available tools: {', '.join(self.get_tool_names())}"
        
        try:
            result = await tool.execute(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            return f"Error executing tool: {str(e)}"


# Global registry instance
_registry: Optional[ToolRegistry] = None

def get_tool_registry() -> ToolRegistry:
    """Get or create the global tool registry"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
