"""
MCP-specific type definitions for tool schemas and responses
"""
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel


class MCPToolSchema(BaseModel):
    """Schema definition for MCP tools"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPToolResult(BaseModel):
    """Result format for MCP tool execution"""
    content: List[Dict[str, Any]]
    isError: bool = False


class MCPErrorResult(MCPToolResult):
    """Error result for MCP tool execution"""
    def __init__(self, error_message: str, error_code: str = "TOOL_ERROR"):
        super().__init__(
            content=[{
                "type": "text",
                "text": f"Error: {error_message}"
            }],
            isError=True
        )


class MCPTextResult(MCPToolResult):
    """Text result for MCP tool execution"""
    def __init__(self, text: str):
        super().__init__(
            content=[{
                "type": "text", 
                "text": text
            }],
            isError=False
        )


# Tool argument schemas
CASE_STUDIES_SCHEMA = {
    "type": "object",
    "properties": {
        "company": {
            "type": "string",
            "description": "Company name to search for case studies"
        },
        "industry": {
            "type": "string", 
            "description": "Industry to filter case studies (optional)"
        },
        "topic": {
            "type": "string",
            "description": "Specific topic to search for (optional)"
        },
        "count": {
            "type": "integer",
            "description": "Number of case studies to retrieve (default: 2)",
            "default": 2,
            "minimum": 1,
            "maximum": 5
        }
    },
    "required": ["company"]
}

FILE_SYSTEM_SCHEMA = {
    "type": "object", 
    "properties": {
        "operation": {
            "type": "string",
            "enum": ["list", "read", "create", "edit"],
            "description": "File system operation to perform"
        },
        "path": {
            "type": "string",
            "description": "File or directory path (relative to knowledge_base or output)"
        },
        "content": {
            "type": "string", 
            "description": "Content for create/edit operations (optional)"
        }
    },
    "required": ["operation", "path"]
}
