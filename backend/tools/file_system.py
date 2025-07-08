import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseTool, ToolParameter
import logging

# Import security validator and enhanced error handling
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from security.file_validator import FileSystemValidator
from security.error_handler import (
    FileSystemError, operation_logger, create_contextual_error,
    path_not_found_error, permission_error, file_too_large_error,
    invalid_extension_error, path_traversal_error
)

logger = logging.getLogger(__name__)

class FileSystemTool(BaseTool):
    """Secure file system operations tool"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            project_root = os.getenv("PROJECT_ROOT", os.getcwd())
        
        self.validator = FileSystemValidator(project_root)
        self.project_root = Path(project_root)
        
        # Ensure required directories exist
        success = self.validator.ensure_directories()
        if not success:
            logger.error("Failed to create required directories")
        
        logger.info(f"FileSystemTool initialized with root: {self.project_root}")
    
    @property
    def name(self) -> str:
        return "file_system"
    
    @property
    def description(self) -> str:
        return "Perform file system operations: list, read, create, and edit files in knowledge_base and output directories"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="File operation to perform",
                required=True,
                enum=["list", "read", "create", "edit"]
            ),
            ToolParameter(
                name="file_path",
                type="string", 
                description="Relative file path (e.g., 'knowledge_base/data.csv', 'output/report.md')",
                required=False
            ),
            ToolParameter(
                name="directory",
                type="string",
                description="Directory to list (for list operation)",
                required=False
            ),
            ToolParameter(
                name="content",
                type="string",
                description="File content (for create/edit operations)",
                required=False
            ),
            ToolParameter(
                name="edit_mode",
                type="string",
                description="Edit mode: append, prepend, replace",
                required=False,
                enum=["append", "prepend", "replace"]
            )
        ]
    
    async def execute(self, **kwargs) -> str:
        """Execute file system operation with comprehensive error handling"""
        operation = kwargs.get("operation")
        file_path = kwargs.get("file_path")
        
        # Note: Will log success/failure after operation completes
        
        try:
            if operation == "list":
                result = await self._list_files(kwargs)
            elif operation == "read":
                result = await self._read_file(kwargs)
            elif operation == "create":
                result = await self._create_file(kwargs)
            elif operation == "edit":
                result = await self._edit_file(kwargs)
            else:
                error = create_contextual_error(
                    "invalid_operation",
                    f"Unknown operation: {operation}",
                    operation=operation
                )
                return error.format_for_user()
            
            # Log successful operation
            operation_logger.log_operation(
                operation=operation,
                file_path=file_path or kwargs.get("directory", "N/A"),
                success=True,
                details={"result_length": len(result)}
            )
            
            return result
                
        except FileSystemError as e:
            return e.format_for_user()
        except Exception as e:
            logger.error(f"FileSystem operation failed: {str(e)}")
            error = create_contextual_error(
                "general",
                f"Unexpected error: {str(e)}",
                operation=operation,
                file_path=file_path
            )
            return error.format_for_user()
    
    async def _list_files(self, kwargs: dict) -> str:
        """List files in directory"""
        directory = kwargs.get("directory", "")
        
        # Default to listing both main directories if no directory specified
        if not directory:
            try:
                result = "📂 Project Directory Structure\\n\\n"
                
                # List knowledge_base
                kb_path = self.validator.knowledge_base
                if kb_path.exists():
                    result += "📁 knowledge_base/ (input data)\\n"
                    for item in sorted(kb_path.iterdir()):
                        if item.is_file():
                            size = item.stat().st_size
                            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                            result += f"  📄 {item.name} ({size_str})\\n"
                
                result += "\\n"
                
                # List output
                output_path = self.validator.output_dir
                if output_path.exists():
                    result += "📁 output/ (generated content)\\n"
                    files_found = False
                    for item in sorted(output_path.iterdir()):
                        if item.is_file():
                            size = item.stat().st_size
                            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                            result += f"  📄 {item.name} ({size_str})\\n"
                            files_found = True
                    if not files_found:
                        result += "  (empty - ready for generated content)\\n"
                
                return result
                
            except Exception as e:
                return f"❌ Error listing directories: {str(e)}"
        
        # Validate directory path
        is_valid, error_msg, dir_path = self.validator.validate_path(
            directory, "list"
        )
        
        if not is_valid:
            return f"❌ {error_msg}"
        
        try:
            if not dir_path.exists():
                return f"📂 Directory not found: {directory}\\n\\nAvailable directories:\\n- knowledge_base/\\n- output/"
            
            files = []
            directories = []
            
            for item in sorted(dir_path.iterdir()):
                if item.is_file():
                    size = item.stat().st_size
                    size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                    files.append(f"📄 {item.name} ({size_str})")
                elif item.is_dir():
                    directories.append(f"📁 {item.name}/")
            
            result = f"📂 Directory: {directory}\\n\\n"
            
            if directories:
                result += "📁 Subdirectories:\\n" + "\\n".join(directories) + "\\n\\n"
            
            if files:
                result += "📄 Files:\\n" + "\\n".join(files)
            else:
                result += "No files found."
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing directory {directory}: {str(e)}")
            return f"❌ Error listing directory: {str(e)}"
    
    async def _read_file(self, kwargs: dict) -> str:
        """Read file content safely"""
        file_path = kwargs.get("file_path")
        
        if not file_path:
            return "❌ file_path parameter required for read operation"
        
        # Validate file path
        is_valid, error_msg, full_path = self.validator.validate_path(file_path, "read")
        if not is_valid:
            if "not found" in error_msg.lower():
                raise path_not_found_error(file_path, "read")
            elif "traversal" in error_msg.lower():
                raise path_traversal_error(file_path)
            else:
                raise create_contextual_error("validation_error", error_msg, file_path, "read")
        
        # Check file size
        size_valid, size_msg = self.validator.validate_file_size(full_path)
        if not size_valid:
            # Extract size information for better error
            try:
                size = full_path.stat().st_size
                raise file_too_large_error(file_path, size, self.validator.max_file_size)
            except:
                raise create_contextual_error("file_too_large", size_msg, file_path, "read")
        
        # Read content safely
        content_data = self.validator.get_safe_content(full_path)
        
        result = f"📄 File: {file_path}\\n"
        result += f"📊 Size: {content_data['full_size']:,} bytes\\n"
        
        if content_data.get('is_binary'):
            result += f"⚠️ Binary file detected - cannot display content\\n"
            return result
        
        if content_data.get('error'):
            result += f"❌ Error: {content_data['error']}\\n"
            return result
        
        if content_data['truncated']:
            result += f"⚠️ Content truncated (showing {content_data['displayed_size']:,} of {content_data['full_size']:,} bytes)\\n"
        
        result += f"\\n📝 Content:\\n{'-' * 40}\\n{content_data['content']}"
        
        return result
    
    async def _create_file(self, kwargs: dict) -> str:
        """Create new file"""
        file_path = kwargs.get("file_path")
        content = kwargs.get("content", "")
        
        if not file_path:
            return "❌ file_path parameter required for create operation"
        
        # Validate file path
        is_valid, error_msg, full_path = self.validator.validate_path(file_path, "create")
        if not is_valid:
            if "not allowed" in error_msg.lower() and "type" in error_msg.lower():
                error = FileSystemError(error_msg, "invalid_extension", ERROR_SUGGESTIONS["invalid_extension"])
                return error.format_for_user()
            return f"❌ {error_msg}"
        
        try:
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file already exists
            if full_path.exists():
                return f"❌ File already exists: {file_path}\\nUse edit operation to modify existing files."
            
            # Write content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Verify creation
            size = full_path.stat().st_size
            
            result = f"✅ File created successfully: {file_path}\\n"
            result += f"📊 Size: {size:,} bytes\\n"
            result += f"📝 Content length: {len(content):,} characters"
            
            return result
            
        except PermissionError:
            error = FileSystemError(f"Permission denied creating file: {file_path}", "permission_denied", ERROR_SUGGESTIONS["permission_denied"])
            return error.format_for_user()
        except Exception as e:
            logger.error(f"Error creating file {file_path}: {str(e)}")
            return f"❌ Error creating file: {str(e)}"
    
    async def _edit_file(self, kwargs: dict) -> str:
        """Edit existing file"""
        file_path = kwargs.get("file_path")
        content = kwargs.get("content", "")
        edit_mode = kwargs.get("edit_mode", "append")
        
        if not file_path:
            return "❌ file_path parameter required for edit operation"
        
        if edit_mode not in ["append", "prepend", "replace"]:
            return f"❌ Invalid edit_mode: {edit_mode}. Use: append, prepend, or replace"
        
        # Validate file path
        is_valid, error_msg, full_path = self.validator.validate_path(file_path, "edit")
        if not is_valid:
            return f"❌ {error_msg}"
        
        try:
            if not full_path.exists():
                return f"❌ File not found: {file_path}\\nUse create operation to make new files."
            
            # Read existing content
            with open(full_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Apply edit based on mode
            if edit_mode == "append":
                new_content = existing_content + content
            elif edit_mode == "prepend":
                new_content = content + existing_content
            elif edit_mode == "replace":
                new_content = content
            
            # Write updated content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Report results
            old_size = len(existing_content)
            new_size = len(new_content)
            
            result = f"✅ File edited successfully: {file_path}\\n"
            result += f"📊 Mode: {edit_mode}\\n"
            result += f"📊 Size change: {old_size:,} → {new_size:,} characters\\n"
            result += f"📝 Added: {len(content):,} characters"
            
            return result
            
        except PermissionError:
            error = FileSystemError(f"Permission denied editing file: {file_path}", "permission_denied", ERROR_SUGGESTIONS["permission_denied"])
            return error.format_for_user()
        except Exception as e:
            logger.error(f"Error editing file {file_path}: {str(e)}")
            return f"❌ Error editing file: {str(e)}"
