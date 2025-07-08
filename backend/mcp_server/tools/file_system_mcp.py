"""
MCP-compatible File System Tool
Converts the FastAPI FileSystemTool to MCP format while preserving all functionality
"""
import os
import sys
from typing import Optional, Dict, Any

# Add backend directory to path for imports
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(backend_dir)

from tools.file_system import FileSystemTool
import logging

logger = logging.getLogger(__name__)


class MCPFileSystemTool:
    """MCP-compatible wrapper for File System Tool"""
    
    def __init__(self):
        # Initialize with current directory as project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.tool = FileSystemTool(project_root=project_root)
        logger.info(f"MCP File System Tool initialized with root: {project_root}")
    
    async def execute(self, operation: str, path: str, content: Optional[str] = None) -> str:
        """
        Execute file system operation with MCP-compatible interface
        
        Args:
            operation: File operation to perform (list, read, create, edit)
            path: File or directory path (relative to knowledge_base or output)
            content: Content for create/edit operations (optional)
        
        Returns:
            Formatted string with operation results
        """
        try:
            # Validate operation
            valid_operations = ["list", "read", "create", "edit"]
            if operation not in valid_operations:
                return f"❌ Error: Invalid operation '{operation}'. Valid operations: {', '.join(valid_operations)}"
            
            # Log the MCP call
            logger.info(f"MCP File System: {operation} on {path}")
            
            # Map MCP parameters to original tool parameters
            kwargs = {"operation": operation}
            
            if operation == "list":
                kwargs["directory"] = path if path else ""
            else:
                kwargs["file_path"] = path
            
            if content is not None:
                kwargs["content"] = content
                if operation == "edit":
                    # Default to append mode for MCP
                    kwargs["edit_mode"] = "append"
            
            # Execute the original tool
            result = await self.tool.execute(**kwargs)
            
            # Add MCP-specific context
            mcp_result = f"🗂️ MCP File System Operation\\n"
            mcp_result += f"⚙️ Operation: {operation.upper()}"
            if path:
                mcp_result += f" | Path: {path}"
            mcp_result += "\\n\\n"
            
            # Append the tool results
            mcp_result += result
            
            # Add MCP footer for context
            mcp_result += "\\n\\n📡 Delivered via MCP Protocol from Assistant UI Tools"
            
            return mcp_result
            
        except Exception as e:
            error_msg = f"❌ MCP File System Error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for MCP registration"""
        return {
            "name": "file_system",
            "description": "Perform secure file system operations: list directories, read files, create new files, or edit existing files. Operates within knowledge_base and output directories with comprehensive security validation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["list", "read", "create", "edit"],
                        "description": "File system operation to perform"
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory path (relative to knowledge_base or output directories)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content for create/edit operations (optional)"
                    }
                },
                "required": ["operation", "path"]
            }
        }
