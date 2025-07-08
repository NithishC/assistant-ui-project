import os
import mimetypes
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FileSystemValidator:
    """Comprehensive file system security and validation"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.knowledge_base = self.project_root / "knowledge_base"
        self.output_dir = self.project_root / "output"
        
        # Security configuration
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_content_display = 100 * 1024   # 100KB for UI display
        self.allowed_extensions = {
            '.txt', '.md', '.csv', '.json', '.py', '.js', 
            '.html', '.css', '.xml', '.yaml', '.yml', '.log'
        }
        self.forbidden_paths = {
            '.env', '.git', 'node_modules', '__pycache__',
            'Dockerfile', 'docker-compose.yml', '.next',
            'package-lock.json', 'requirements.txt'
        }
        
        logger.info(f"FileSystemValidator initialized with root: {self.project_root}")
    
    def validate_path(self, file_path: str, operation: str) -> Tuple[bool, str, Optional[Path]]:
        """
        Comprehensive path validation
        Returns: (is_valid, error_message, resolved_path)
        """
        try:
            # Basic sanitization
            clean_path = file_path.strip().replace('\\', '/')
            
            # Convert to Path object
            if clean_path.startswith('/') or ':' in clean_path:
                return False, "Absolute paths not allowed. Use relative paths only.", None
            
            # Resolve relative to project root
            full_path = (self.project_root / clean_path).resolve()
            
            # Critical security check: ensure within project boundaries
            if not str(full_path).startswith(str(self.project_root)):
                return False, "Path traversal detected. Access denied.", None
            
            # Check forbidden paths
            for forbidden in self.forbidden_paths:
                if forbidden in str(full_path):
                    return False, f"Access to {forbidden} is not allowed.", None
            
            # Operation-specific validation
            if operation == 'read':
                if not full_path.exists():
                    return False, f"File not found: {clean_path}", None
                if not full_path.is_file():
                    return False, f"Path is not a file: {clean_path}", None
            
            elif operation in ['create', 'edit']:
                # Ensure parent directory exists and is valid
                parent = full_path.parent
                if not str(parent).startswith(str(self.project_root)):
                    return False, "Invalid parent directory.", None
                
                # Check file extension
                if full_path.suffix.lower() not in self.allowed_extensions:
                    return False, f"File type not allowed: {full_path.suffix}. Allowed: {', '.join(self.allowed_extensions)}", None
            
            elif operation == 'list':
                if full_path.exists() and not full_path.is_dir():
                    return False, f"Path is not a directory: {clean_path}", None
            
            return True, "Valid path", full_path
            
        except Exception as e:
            logger.error(f"Path validation error: {str(e)}")
            return False, f"Path validation error: {str(e)}", None
    
    def validate_file_size(self, file_path: Path) -> Tuple[bool, str]:
        """Check file size limits"""
        try:
            if file_path.exists():
                size = file_path.stat().st_size
                if size > self.max_file_size:
                    return False, f"File too large: {size/1024/1024:.1f}MB (max: {self.max_file_size/1024/1024}MB)"
            return True, "Size OK"
        except Exception as e:
            logger.error(f"Size check error: {str(e)}")
            return False, f"Size check error: {str(e)}"
    
    def get_safe_content(self, file_path: Path) -> Dict[str, Any]:
        """Read file content safely with truncation"""
        try:
            size = file_path.stat().st_size
            is_truncated = size > self.max_content_display
            
            # Try to detect if file is binary
            try:
                with open(file_path, 'rb') as f:
                    sample = f.read(8192)
                    if b'\x00' in sample:
                        return {
                            "content": "[BINARY FILE - Cannot display content]",
                            "truncated": False,
                            "full_size": size,
                            "displayed_size": 0,
                            "is_binary": True
                        }
            except Exception:
                pass
            
            # Read as text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                if is_truncated:
                    content = f.read(self.max_content_display)
                    return {
                        "content": content + "\n\n[TRUNCATED - File too large for display]",
                        "truncated": True,
                        "full_size": size,
                        "displayed_size": len(content)
                    }
                else:
                    content = f.read()
                    return {
                        "content": content,
                        "truncated": False,
                        "full_size": size,
                        "displayed_size": size
                    }
        except UnicodeDecodeError:
            return {
                "content": "[BINARY FILE - Cannot display content]",
                "truncated": False,
                "full_size": file_path.stat().st_size,
                "displayed_size": 0,
                "is_binary": True
            }
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return {
                "content": f"[ERROR READING FILE: {str(e)}]",
                "truncated": False,
                "full_size": 0,
                "displayed_size": 0,
                "error": str(e)
            }
    
    def ensure_directories(self) -> bool:
        """Ensure required directories exist"""
        try:
            self.knowledge_base.mkdir(exist_ok=True)
            self.output_dir.mkdir(exist_ok=True)
            logger.info("Required directories ensured")
            return True
        except Exception as e:
            logger.error(f"Error creating directories: {str(e)}")
            return False


class FileSystemError(Exception):
    """Custom file system error with user-friendly messages"""
    
    def __init__(self, message: str, error_type: str = "general", suggestions: List[str] = None):
        self.message = message
        self.error_type = error_type
        self.suggestions = suggestions or []
        super().__init__(message)
    
    def format_for_user(self) -> str:
        """Format error message for end user"""
        result = f"❌ {self.message}\n"
        
        if self.suggestions:
            result += "\n💡 Suggestions:\n"
            for suggestion in self.suggestions:
                result += f"  • {suggestion}\n"
        
        return result


# Common error patterns and suggestions
ERROR_SUGGESTIONS = {
    "file_not_found": [
        "Check if the file path is correct",
        "Use 'list' operation to see available files",
        "Ensure you're using relative paths like 'knowledge_base/file.txt'"
    ],
    "permission_denied": [
        "File might be locked by another program",
        "Check if you have write permissions",
        "Try a different filename"
    ],
    "file_too_large": [
        "Break large files into smaller chunks",
        "Use data processing tools for large datasets",
        "Consider summarizing the content instead"
    ],
    "invalid_extension": [
        "Use allowed file extensions: .txt, .md, .csv, .json, .py, .js, .html, .css, .xml, .yaml, .yml",
        "Rename your file with a supported extension",
        "Contact administrator if you need additional file types"
    ],
    "path_traversal": [
        "Use relative paths within the project directory",
        "Avoid using .. or absolute paths",
        "Work within knowledge_base/ and output/ directories"
    ]
}
