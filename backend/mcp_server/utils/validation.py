"""
MCP Server Validation Utilities
"""
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class MCPValidator:
    """Validation utilities for MCP server operations"""
    
    @staticmethod
    def validate_case_studies_args(args: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate case studies tool arguments"""
        # Check required arguments
        if "company" not in args:
            return False, "Missing required argument: company"
        
        if not isinstance(args["company"], str) or not args["company"].strip():
            return False, "Argument 'company' must be a non-empty string"
        
        # Validate optional arguments
        if "industry" in args and not isinstance(args["industry"], str):
            return False, "Argument 'industry' must be a string"
        
        if "topic" in args and not isinstance(args["topic"], str):
            return False, "Argument 'topic' must be a string"
        
        if "count" in args:
            if not isinstance(args["count"], int):
                return False, "Argument 'count' must be an integer"
            if args["count"] < 1 or args["count"] > 5:
                return False, "Argument 'count' must be between 1 and 5"
        
        return True, None
    
    @staticmethod
    def validate_file_system_args(args: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate file system tool arguments"""
        # Check required arguments
        if "operation" not in args:
            return False, "Missing required argument: operation"
        
        valid_operations = ["list", "read", "create", "edit"]
        if args["operation"] not in valid_operations:
            return False, f"Invalid operation. Must be one of: {', '.join(valid_operations)}"
        
        if "path" not in args:
            return False, "Missing required argument: path"
        
        if not isinstance(args["path"], str):
            return False, "Argument 'path' must be a string"
        
        # Validate content for operations that need it
        operation = args["operation"]
        if operation in ["create", "edit"]:
            if "content" not in args:
                return False, f"Argument 'content' is required for {operation} operation"
            if not isinstance(args["content"], str):
                return False, "Argument 'content' must be a string"
        
        return True, None
    
    @staticmethod
    def sanitize_args(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize and clean tool arguments"""
        sanitized = {}
        
        if tool_name == "case_studies_search":
            sanitized["company"] = args.get("company", "").strip()
            
            if "industry" in args and args["industry"]:
                sanitized["industry"] = args["industry"].strip()
            
            if "topic" in args and args["topic"]:
                sanitized["topic"] = args["topic"].strip()
            
            # Set default count if not provided
            sanitized["count"] = args.get("count", 2)
            
        elif tool_name == "file_system":
            sanitized["operation"] = args.get("operation", "").strip()
            sanitized["path"] = args.get("path", "").strip()
            
            if "content" in args:
                sanitized["content"] = args["content"]
        
        return sanitized
    
    @staticmethod
    def log_tool_call(tool_name: str, args: Dict[str, Any], success: bool, error: Optional[str] = None):
        """Log tool execution for debugging"""
        if success:
            logger.info(f"MCP Tool Success: {tool_name} with args {args}")
        else:
            logger.error(f"MCP Tool Failed: {tool_name} with args {args} - Error: {error}")
