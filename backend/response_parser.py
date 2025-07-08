import re
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class StructuredResponseParser:
    """Parse structured responses with think/tool/answer format"""
    
    @staticmethod
    def parse_thinking(response: str) -> Optional[str]:
        """Extract thinking section from response"""
        match = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    @staticmethod
    def parse_tool_call(response: str) -> Optional[Dict[str, Any]]:
        """Extract tool call from response"""
        match = re.search(r'<tool>(.*?)</tool>', response, re.DOTALL)
        if match:
            try:
                tool_data = json.loads(match.group(1).strip())
                # Validate structure
                if 'name' in tool_data and 'args' in tool_data:
                    return tool_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tool JSON: {e}")
        return None
    
    @staticmethod
    def parse_answer(response: str) -> Optional[str]:
        """Extract final answer from response"""
        match = re.search(r'<answer>(.*?)</answer>', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Handle truncated responses - if we see <answer> but no closing tag
        truncated_match = re.search(r'<answer>(.*?)$', response, re.DOTALL)
        if truncated_match:
            content = truncated_match.group(1).strip()
            if content:  # Only return if there's actual content
                logger.warning("Detected truncated answer response")
                return content
        
        return None
    
    @staticmethod
    def has_valid_format(response: str) -> bool:
        """Check if response has valid format"""
        has_thinking = '<think>' in response and '</think>' in response
        has_tool = '<tool>' in response and '</tool>' in response
        has_answer = '<answer>' in response  # Just check for opening tag for truncated responses
        
        # Must have thinking and either tool or answer
        return has_thinking and (has_tool or has_answer)
