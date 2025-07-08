import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class FileSystemError(Exception):
    """Enhanced file system error with contextual information"""
    
    def __init__(
        self, 
        message: str, 
        error_type: str = "general", 
        suggestions: List[str] = None,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_type = error_type
        self.suggestions = suggestions or []
        self.file_path = file_path
        self.operation = operation
        self.context = context or {}
        super().__init__(message)
    
    def format_for_user(self) -> str:
        """Format comprehensive error message for end user"""
        result = f"❌ {self.message}\\n"
        
        # Add operation context
        if self.operation and self.file_path:
            result += f"\\n📍 Context: {self.operation} operation on '{self.file_path}'\\n"
        elif self.operation:
            result += f"\\n📍 Context: {self.operation} operation\\n"
        
        # Add contextual information
        if self.context:
            result += "\\n📊 Details:\\n"
            for key, value in self.context.items():
                result += f"  • {key}: {value}\\n"
        
        # Add suggestions
        if self.suggestions:
            result += "\\n💡 Suggestions:\\n"
            for suggestion in self.suggestions:
                result += f"  • {suggestion}\\n"
        
        return result

# Enhanced error patterns and suggestions
ERROR_SUGGESTIONS = {
    "file_not_found": [
        "Check if the file path is correct",
        "Use 'list' operation to see available files",
        "Ensure you're using relative paths like 'knowledge_base/file.txt'",
        "Verify the file exists in the specified directory"
    ],
    "permission_denied": [
        "File might be locked by another program",
        "Check if you have write permissions",
        "Try a different filename",
        "Close any programs that might be using the file"
    ],
    "file_too_large": [
        "Break large files into smaller chunks",
        "Use data processing tools for large datasets",
        "Consider summarizing the content instead",
        "Files over 10MB cannot be processed"
    ],
    "invalid_extension": [
        "Use allowed file extensions: .txt, .md, .csv, .json, .py, .js, .html, .css, .xml, .yaml, .yml",
        "Rename your file with a supported extension",
        "Contact administrator if you need additional file types"
    ],
    "path_traversal": [
        "Use relative paths within the project directory",
        "Avoid using .. or absolute paths",
        "Work within knowledge_base/ and output/ directories",
        "Security restrictions prevent access outside project folder"
    ],
    "directory_not_found": [
        "Check if the directory path is correct",
        "Available directories: knowledge_base/, output/",
        "Use forward slashes in paths: 'knowledge_base/subfolder'",
        "Create subdirectories in output/ as needed"
    ],
    "file_exists": [
        "Use a different filename",
        "Use 'edit' operation to modify existing files",
        "Add timestamp or version number to filename",
        "Check if you intended to update the existing file"
    ],
    "invalid_operation": [
        "Valid operations: list, read, create, edit",
        "Check operation parameter spelling",
        "Refer to file system tool documentation"
    ],
    "content_too_large": [
        "Reduce content size for better performance",
        "Split large content into multiple files",
        "Consider using append mode for large additions"
    ]
}

class FileOperationLogger:
    """Logger for file system operations with security monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger("file_operations")
        self.security_logger = logging.getLogger("security")
    
    def log_operation(
        self, 
        operation: str, 
        file_path: str, 
        success: bool,
        user_context: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log file operation with details"""
        details = details or {}
        
        # Create log message without conflicting keys
        log_message = f"File operation {'successful' if success else 'failed'}: {operation} on {file_path}"
        
        if success:
            self.logger.info(log_message)
        else:
            self.logger.warning(log_message)
    
    def log_security_event(
        self, 
        event_type: str, 
        attempted_path: str, 
        blocked_reason: str,
        user_context: Optional[str] = None
    ):
        """Log security-related events"""
        log_message = f"Security event: {event_type} - Attempted: {attempted_path} - Reason: {blocked_reason}"
        self.security_logger.warning(log_message)

# Global logger instance
operation_logger = FileOperationLogger()

def create_contextual_error(
    error_type: str,
    message: str,
    file_path: Optional[str] = None,
    operation: Optional[str] = None,
    **context
) -> FileSystemError:
    """Create a contextual file system error with appropriate suggestions"""
    
    suggestions = ERROR_SUGGESTIONS.get(error_type, [])
    
    return FileSystemError(
        message=message,
        error_type=error_type,
        suggestions=suggestions,
        file_path=file_path,
        operation=operation,
        context=context
    )

# Utility functions for common error scenarios
def path_not_found_error(path: str, operation: str) -> FileSystemError:
    """Create error for file/directory not found"""
    return create_contextual_error(
        "file_not_found",
        f"File or directory not found: {path}",
        file_path=path,
        operation=operation,
        available_dirs="knowledge_base/, output/"
    )

def permission_error(path: str, operation: str) -> FileSystemError:
    """Create error for permission denied"""
    return create_contextual_error(
        "permission_denied",
        f"Permission denied accessing: {path}",
        file_path=path,
        operation=operation
    )

def file_too_large_error(path: str, size: int, max_size: int) -> FileSystemError:
    """Create error for file too large"""
    return create_contextual_error(
        "file_too_large",
        f"File too large: {size/1024/1024:.1f}MB (max: {max_size/1024/1024}MB)",
        file_path=path,
        operation="read",
        actual_size=f"{size/1024/1024:.1f}MB",
        max_allowed=f"{max_size/1024/1024}MB"
    )

def invalid_extension_error(path: str, allowed_extensions: List[str]) -> FileSystemError:
    """Create error for invalid file extension"""
    return create_contextual_error(
        "invalid_extension",
        f"File type not allowed: {Path(path).suffix}",
        file_path=path,
        operation="create",
        allowed_extensions=", ".join(sorted(allowed_extensions))
    )

def path_traversal_error(attempted_path: str) -> FileSystemError:
    """Create error for path traversal attempt"""
    operation_logger.log_security_event(
        "path_traversal_attempt",
        attempted_path,
        "Attempted to access outside project directory"
    )
    
    return create_contextual_error(
        "path_traversal",
        "Path traversal detected. Access denied for security reasons.",
        file_path=attempted_path,
        operation="path_validation",
        security_violation="Directory traversal attempt"
    )
