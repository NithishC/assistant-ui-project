"""
MCP Server Implementation for Assistant UI Tools
Provides Model Context Protocol compatible interface for Case Studies and File System tools
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional, Sequence
import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.sse import SseServerTransport
from mcp.types import (
    CallToolResult, 
    ListToolsResult, 
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

from .types.mcp_types import (
    MCPToolSchema, 
    MCPTextResult, 
    MCPErrorResult,
    CASE_STUDIES_SCHEMA,
    FILE_SYSTEM_SCHEMA
)
from .tools.case_studies_mcp import MCPCaseStudiesTool
from .tools.file_system_mcp import MCPFileSystemTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssistantUIMCPServer:
    """Main MCP Server for Assistant UI Tools"""
    
    def __init__(self):
        self.server = Server("assistant-ui-tools")
        self.case_studies_tool = MCPCaseStudiesTool()
        self.file_system_tool = MCPFileSystemTool()
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Assistant UI MCP Server initialized")
    
    def _register_handlers(self):
        """Register MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools"""
            tools = [
                Tool(
                    name="case_studies_search",
                    description="Search for case studies and success stories from specific companies. Useful for competitive research, customer testimonials, and understanding how companies implement solutions.",
                    inputSchema=CASE_STUDIES_SCHEMA
                ),
                Tool(
                    name="file_system",
                    description="Perform file system operations: list directories, read files, create new files, or edit existing files. Operates within knowledge_base and output directories for secure file management.",
                    inputSchema=FILE_SYSTEM_SCHEMA
                )
            ]
            
            logger.info(f"Listed {len(tools)} tools")
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Execute tool calls"""
            logger.info(f"Tool call: {name} with args: {arguments}")
            
            try:
                if name == "case_studies_search":
                    result = await self.case_studies_tool.execute(**arguments)
                    return CallToolResult(
                        content=[TextContent(type="text", text=result)]
                    )
                
                elif name == "file_system":
                    result = await self.file_system_tool.execute(**arguments)
                    return CallToolResult(
                        content=[TextContent(type="text", text=result)]
                    )
                
                else:
                    error_msg = f"Unknown tool: {name}"
                    logger.error(error_msg)
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Error: {error_msg}")],
                        isError=True
                    )
                    
            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {error_msg}")],
                    isError=True
                )
    
    async def run_stdio(self):
        """Run MCP server with stdio transport"""
        logger.info("Starting MCP server with stdio transport")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream,
                self.server.create_initialization_options()
            )
    
    async def run_http(self, host: str = "0.0.0.0", port: int = 8001):
        """Run MCP server with HTTP transport for Docker/external access"""
        import uvicorn
        from fastapi import FastAPI
        from fastapi.responses import StreamingResponse
        from sse_starlette import EventSourceResponse
        import json
        
        logger.info(f"Starting MCP server with HTTP transport on {host}:{port}")
        
        app = FastAPI(title="Assistant UI MCP Server")
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "server": "Assistant UI MCP Server"}
        
        @app.get("/mcp/tools")
        async def list_tools_endpoint():
            """List available MCP tools"""
            try:
                # Return our tool definitions directly
                tools_data = [
                    {
                        "name": "case_studies_search",
                        "description": "Search for case studies and success stories from specific companies. Useful for competitive research, customer testimonials, and understanding how companies implement solutions.",
                        "inputSchema": CASE_STUDIES_SCHEMA
                    },
                    {
                        "name": "file_system",
                        "description": "Perform file system operations: list directories, read files, create new files, or edit existing files. Operates within knowledge_base and output directories for secure file management.",
                        "inputSchema": FILE_SYSTEM_SCHEMA
                    }
                ]
                return {"tools": tools_data}
            except Exception as e:
                logger.error(f"List tools failed: {e}", exc_info=True)
                return {"error": str(e)}
        
        @app.post("/mcp/call/{tool_name}")
        async def call_tool_endpoint(tool_name: str, arguments: dict):
            """Call an MCP tool"""
            try:
                # Call our tool instances directly
                if tool_name == "case_studies_search":
                    result_text = await self.case_studies_tool.execute(**arguments)
                    return {
                        "result": [{"type": "text", "text": result_text}],
                        "isError": False
                    }
                elif tool_name == "file_system":
                    result_text = await self.file_system_tool.execute(**arguments)
                    return {
                        "result": [{"type": "text", "text": result_text}],
                        "isError": False
                    }
                else:
                    return {
                        "result": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                        "isError": True
                    }
            except Exception as e:
                logger.error(f"Tool call failed: {e}", exc_info=True)
                return {
                    "result": [{"type": "text", "text": f"Error: {str(e)}"}],
                    "isError": True
                }
        
        @app.get("/sse/")
        async def sse_endpoint_get():
            """SSE endpoint for OpenAI Deep Research compatibility - GET for connection"""
            async def event_stream():
                # Send initial connection event
                yield {"event": "connected", "data": json.dumps({"status": "connected", "server": "assistant_ui_tools"})}
                
                # Keep connection alive
                import asyncio
                while True:
                    yield {"event": "ping", "data": json.dumps({"timestamp": asyncio.get_event_loop().time()})}
                    await asyncio.sleep(30)  # Ping every 30 seconds
            
            return EventSourceResponse(event_stream())
        
        @app.post("/sse/")
        async def sse_endpoint_post(request: dict):
            """SSE endpoint for OpenAI Deep Research - POST for MCP commands"""
            try:
                # Log the incoming request to debug
                logger.info(f"Received MCP request: {json.dumps(request, indent=2)}")
                
                # Parse MCP request
                if "method" in request:
                    method = request["method"]
                    params = request.get("params", {})
                    
                    logger.info(f"Method: {method}, Params: {params}")
                    
                    # Handle different possible method names
                    if method == "initialize":
                        # MCP initialization handshake
                        result = {
                            "jsonrpc": "2.0", 
                            "id": request.get("id"), 
                            "result": {
                                "protocolVersion": "2025-03-26",
                                "capabilities": {
                                    "tools": {},
                                    "resources": {}
                                },
                                "serverInfo": {
                                    "name": "assistant-ui-tools",
                                    "version": "1.0.0"
                                }
                            }
                        }
                        logger.info(f"MCP Initialize response: {json.dumps(result, indent=2)}")
                        return result
                    
                    elif method == "notifications/initialized":
                        # MCP notification - no response needed
                        logger.info("MCP client initialized notification received")
                        return {"jsonrpc": "2.0"}  # Just acknowledge
                    
                    elif method in ["tools/list", "list_tools", "tools.list"]:
                        # Return tools list with Deep Research required tools
                        tools_data = [
                            {
                                "name": "search",
                                "description": "Search the web for any information. Automatically detects whether to use general web search or domain-specific case studies based on query. For competitive analysis or multi-company queries, uses unrestricted web search. For single company queries, searches their specific domain.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "Search query - can be anything from competitive analysis to specific company case studies"
                                        }
                                    },
                                    "required": ["query"]
                                }
                            },
                            {
                                "name": "fetch",
                                "description": "Fetch complete document content using document ID. Retrieves detailed information for analysis.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "Document ID from search results to fetch complete content"
                                        }
                                    },
                                    "required": ["id"]
                                }
                            }
                        ]
                        result = {"jsonrpc": "2.0", "id": request.get("id"), "result": {"tools": tools_data}}
                        logger.info(f"Returning tools list: {json.dumps(result, indent=2)}")
                        return result
                    
                    elif method in ["tools/call", "call_tool", "tools.call"]:
                        # Execute tool call
                        tool_name = params.get("name")
                        arguments = params.get("arguments", {})
                        
                        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
                        
                        if tool_name == "search":
                            # Map search to case studies search OR general web search
                            query = arguments.get("query", "")
                            
                            # Check if query mentions multiple companies (competitive analysis)
                            competitive_keywords = ["competitive", "versus", "vs", "comparison", "landscape"]
                            multiple_companies = sum(1 for comp in ["salesforce", "microsoft", "amazon", "google", "oracle", "adobe"] if comp.lower() in query.lower()) > 1
                            is_competitive = any(keyword in query.lower() for keyword in competitive_keywords) or multiple_companies
                            
                            if is_competitive:
                                # For competitive analysis, use general web search
                                # Import and use the web search tool directly
                                from tools.web_search import WebSearchTool
                                web_tool = WebSearchTool(api_key=os.getenv("BRAVE_API_KEY") or os.getenv("BRAVE_SEARCH_API_KEY"))
                                result_text = await web_tool.execute(
                                    query=query,
                                    count=3,
                                    fetch_content=True
                                )
                            else:
                                # For single company queries, use case studies search
                                companies = ["salesforce", "adobe", "microsoft", "google", "amazon", "oracle"]
                                company = None
                                for comp in companies:
                                    if comp.lower() in query.lower():
                                        company = comp
                                        break
                                
                                if company:
                                    result_text = await self.case_studies_tool.execute(
                                        company=company,
                                        topic=query,
                                        count=3
                                    )
                                else:
                                    # No specific company found, use general web search
                                    from tools.web_search import WebSearchTool
                                    web_tool = WebSearchTool(api_key=os.getenv("BRAVE_API_KEY") or os.getenv("BRAVE_SEARCH_API_KEY"))
                                    result_text = await web_tool.execute(
                                        query=query,
                                        count=3,
                                        fetch_content=True
                                    )
                            result = {
                                "jsonrpc": "2.0", 
                                "id": request.get("id"), 
                                "result": {
                                    "content": [{"type": "text", "text": result_text}],
                                    "isError": False
                                }
                            }
                            logger.info(f"Search result: {result_text[:100]}...")
                            return result
                            
                        elif tool_name == "fetch":
                            # Map fetch to file system operations based on ID
                            document_id = arguments.get("id", "")
                            
                            # Simple mapping: if ID looks like a file path, read it
                            # Otherwise, treat as a company name for case studies
                            if "/" in document_id or "." in document_id:
                                # Looks like a file path
                                result_text = await self.file_system_tool.execute(
                                    operation="read",
                                    file_path=document_id
                                )
                            elif "knowledge_base" in document_id.lower():
                                # List knowledge base
                                result_text = await self.file_system_tool.execute(
                                    operation="list",
                                    directory="knowledge_base"
                                )
                            else:
                                # Treat as company name for case studies
                                result_text = await self.case_studies_tool.execute(
                                    company=document_id,
                                    count=2
                                )
                            
                            result = {
                                "jsonrpc": "2.0", 
                                "id": request.get("id"), 
                                "result": {
                                    "content": [{"type": "text", "text": result_text}],
                                    "isError": False
                                }
                            }
                            logger.info(f"Fetch result: {result_text[:100]}...")
                            return result
                        else:
                            error_result = {
                                "jsonrpc": "2.0", 
                                "id": request.get("id"), 
                                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                            }
                            logger.error(f"Unknown tool: {tool_name}")
                            return error_result
                    
                    else:
                        error_result = {
                            "jsonrpc": "2.0", 
                            "id": request.get("id"), 
                            "error": {"code": -32601, "message": f"Unknown method: {method}"}
                        }
                        logger.error(f"Unknown method: {method}")
                        return error_result
                else:
                    error_result = {
                        "jsonrpc": "2.0", 
                        "id": request.get("id"), 
                        "error": {"code": -32600, "message": "Invalid request - no method specified"}
                    }
                    logger.error("Invalid request - no method specified")
                    return error_result
                    
            except Exception as e:
                logger.error(f"SSE POST error: {e}", exc_info=True)
                error_result = {
                    "jsonrpc": "2.0", 
                    "id": request.get("id", None), 
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }
                return error_result
        
        # Keep server running
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()


async def main():
    """Main entry point for MCP server"""
    server = AssistantUIMCPServer()
    
    # Check if running in Docker or with HTTP flag
    host = os.getenv('MCP_SERVER_HOST', 'localhost')
    port = int(os.getenv('MCP_SERVER_PORT', '8001'))
    
    # Use HTTP transport if host is 0.0.0.0 (Docker) or HTTP flag is set
    if host == '0.0.0.0' or os.getenv('MCP_USE_HTTP', '').lower() == 'true':
        await server.run_http(host, port)
    else:
        await server.run_stdio()


if __name__ == "__main__":
    # Run the MCP server
    asyncio.run(main())
