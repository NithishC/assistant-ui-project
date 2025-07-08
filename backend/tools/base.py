from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ToolParameter(BaseModel):
    """Parameter definition for a tool"""
    name: str
    type: str
    description: str
    required: bool = True
    enum: Optional[List[str]] = None

class ToolDefinition(BaseModel):
    """OpenAI-compatible tool definition"""
    type: str = "function"
    function: Dict[str, Any]

class BaseTool(ABC):
    """Base class for all tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Tool parameters"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters"""
        pass
    
    def to_openai_tool(self) -> ToolDefinition:
        """Convert to OpenAI tool definition format"""
        properties = {}
        required = []
        
        for param in self.parameters:
            param_def = {
                "type": param.type,
                "description": param.description
            }
            if param.enum:
                param_def["enum"] = param.enum
            
            properties[param.name] = param_def
            
            if param.required:
                required.append(param.name)
        
        return ToolDefinition(
            type="function",
            function={
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        )
