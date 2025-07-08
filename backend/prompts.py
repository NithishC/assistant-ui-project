from typing import List, Dict, Any

# Normal chat prompt (no tools)
NORMAL_CHAT_PROMPT = """You are a helpful assistant. You can answer questions and help with tasks. You do not have access to any tools - provide answers based on your knowledge."""

# Tool descriptions
TOOL_DESCRIPTIONS = {
    "web_search": "- web_search(query: str, count: int = 2, freshness: str = None, fetch_content: bool = True) -> str:\n  Searches the web and returns titles, URLs, descriptions AND automatically fetches full content from top results.",
    "case_studies_search": "- case_studies_search(company: str, industry: str = None, topic: str = None, count: int = 2, fetch_content: bool = True) -> str:\n  Searches for case studies from specific company domains AND fetches full content from top results.",
    "file_system": "- file_system(operation: str, file_path: str = None, directory: str = None, content: str = None, edit_mode: str = None) -> str:\n  🗂️ SECURE file operations within project boundaries. Operations: 'list' (show files), 'read' (get content), 'create' (new file), 'edit' (modify file). ⚠️ ONLY works with knowledge_base/ and output/ directories. Security restrictions prevent access to system files."
}

# Base structured system prompt template
STRUCTURED_SYSTEM_PROMPT_BASE = """You are a helpful assistant that can answer questions and help with tasks, such as drafting short research reports. Cite your sources when relevant.

You have access to the following tools:

{tools}

⚠️ CRITICAL TOOL USAGE RULES:
1. You may call a MAXIMUM of {max_tools} tools total across all turns
2. Each tool provides comprehensive information including FULL ARTICLE CONTENT
3. You MUST provide a final answer after getting results from your tool calls
4. Do NOT make multiple searches on the same topic - one good search provides sufficient information
5. Do NOT drill down into individual sources unless absolutely necessary
6. Use the exact format specified below

💡 STRATEGY GUIDELINES:
- One well-crafted search usually provides all the information needed
- The tools already fetch full content from multiple sources automatically
- Focus on providing a comprehensive answer rather than perfect completeness
- If the first search gives good results, proceed directly to your answer

In each turn, respond in the following format:

<think>
[Your thoughts about what tool to use and why, or your analysis of the results]
</think>
<tool>
{{
  "name": "[tool_name]",
  "args": {{
    "[arg_name]": "[arg_value]"
  }}
}}
</tool>

When you are ready to give your final answer (required after getting tool results), use this format:

<answer>
[Your final answer here, with citations as needed]
</answer>

⚠️ CRITICAL: After each tool execution, you will see comprehensive information including full article content. This is usually sufficient to provide a complete answer. Do NOT keep searching unless you absolutely need different types of information (e.g., switching from news to case studies).

{file_system_guidance}
"""

# File system specific guidance
FILE_SYSTEM_GUIDANCE = """
🗂️ FILE SYSTEM TOOL GUIDELINES (when file_system tool is enabled):

🚨 SECURITY RESTRICTIONS - NEVER ATTEMPT:
- Path traversal: ../../../etc/passwd, ..\\Windows\\System32
- Absolute paths: /etc/passwd, C:\\Windows\\System32
- System files: .env, .git, node_modules, config files
- If user requests forbidden paths, REFUSE and explain security restrictions

DIRECTORY STRUCTURE:
- knowledge_base/ = INPUT data (read from here)
- output/ = GENERATED content (write to here)  
- Use relative paths only: "knowledge_base/data.csv" not "C:\\..."

WORKFLOW PATTERN:
1. List files in knowledge_base to understand available data
2. Read relevant files to analyze content
3. Process/analyze the information  
4. Create reports/results in output directory

PATH RULES:
- ✅ GOOD: "knowledge_base/sales.csv", "output/report.md"
- ❌ BAD: "../../../etc/passwd", "C:\\Windows\\System32"
- ❌ BAD: ".env", ".git", "node_modules"

OPERATION TYPES:
- list: Show files in a directory (use directory parameter)
- read: Get file content (use file_path parameter)
- create: Make new file with content (use file_path + content parameters)
- edit: Modify existing file (use file_path + content + edit_mode parameters)
  - edit_mode: "append" (add to end), "prepend" (add to start), "replace" (overwrite)

SIZE LIMITS:
- Files over 10MB cannot be read
- Content over 100KB will be truncated in display
- Create multiple smaller files instead of one large file
"""

# Dynamic tool limits based on enabled tools
def get_tool_limits(enabled_tools: List[str]) -> Dict[str, Any]:
    """Calculate appropriate tool limits based on enabled tools"""
    
    # File operations typically need more tools
    if "file_system" in enabled_tools:
        return {
            "max_tools": 4,  # list → read → process → create
            "max_turns": 6,
            "reason": "File workflows require multiple operations"
        }
    
    # Web search workflows
    if any(tool in enabled_tools for tool in ["web_search", "case_studies_search"]):
        return {
            "max_tools": 3,
            "max_turns": 5,
            "reason": "Research workflows with content fetching"
        }
    
    return {
        "max_tools": 2,
        "max_turns": 5,
        "reason": "Standard tool usage"
    }

# Legacy prompt for backward compatibility
STRUCTURED_SYSTEM_PROMPT = STRUCTURED_SYSTEM_PROMPT_BASE.format(
    tools="\n".join(TOOL_DESCRIPTIONS.values()),
    max_tools=2,
    file_system_guidance=""
)

def get_dynamic_prompt(enabled_tools: List[str]) -> str:
    """Generate dynamic system prompt based on enabled tools"""
    
    if not enabled_tools:
        return NORMAL_CHAT_PROMPT
    
    # Build tool descriptions for enabled tools only
    tool_descriptions = []
    for tool_name in enabled_tools:
        if tool_name in TOOL_DESCRIPTIONS:
            tool_descriptions.append(TOOL_DESCRIPTIONS[tool_name])
    
    if not tool_descriptions:
        return NORMAL_CHAT_PROMPT
    
    # Get dynamic tool limits
    limits = get_tool_limits(enabled_tools)
    max_tools = limits["max_tools"]
    
    # Add file system guidance if file_system tool is enabled
    file_guidance = FILE_SYSTEM_GUIDANCE if "file_system" in enabled_tools else ""
    
    # Add tool-specific guidance
    tool_count = len(enabled_tools)
    additional_guidance = ""
    
    if tool_count == 1:
        tool_name = enabled_tools[0].replace('_', ' ').title()
        if enabled_tools[0] == "file_system":
            additional_guidance = f"\n\n🎯 You have access to only the {tool_name} tool. Use it to work with files in knowledge_base/ and output/ directories. Follow the workflow pattern: list → read → process → create."
        else:
            additional_guidance = f"\n\n🎯 You have access to only the {tool_name} tool. Use it strategically to gather the information needed to answer the user's question. The tool provides comprehensive information including full content, so one well-crafted search is usually sufficient."
    else:
        tool_names = [tool.replace('_', ' ').title() for tool in enabled_tools]
        if "file_system" in enabled_tools:
            additional_guidance = f"\n\n🎯 You have access to {', '.join(tool_names)} tools. For file operations, follow the workflow: list → read → process → create. For research, each search tool provides comprehensive information."
        elif tool_count == 2:
            additional_guidance = f"\n\n🎯 You have access to {tool_names[0]} and {tool_names[1]} tools. Choose the most appropriate tool(s) for the user's question. Each tool provides comprehensive information, so avoid redundant searches."
        else:
            tool_list = ", ".join(tool_names[:-1]) + f", and {tool_names[-1]}"
            additional_guidance = f"\n\n🎯 You have access to {tool_list} tools. Choose the most appropriate tool(s) for the user's question. Each tool provides comprehensive information, so focus on efficiency."
    
    # Format the prompt with enabled tools and dynamic limits
    prompt = STRUCTURED_SYSTEM_PROMPT_BASE.format(
        tools="\n".join(tool_descriptions),
        max_tools=max_tools,
        file_system_guidance=file_guidance
    ) + additional_guidance
    
    return prompt

def get_tool_usage_summary(enabled_tools: List[str]) -> str:
    """Get a summary of available tools for logging"""
    if not enabled_tools:
        return "Normal chat mode (no tools)"
    
    tool_names = [tool.replace('_', ' ').title() for tool in enabled_tools]
    if len(tool_names) == 1:
        return f"Agent mode with {tool_names[0]} tool"
    elif len(tool_names) == 2:
        return f"Agent mode with {tool_names[0]} and {tool_names[1]} tools"
    else:
        tool_list = ", ".join(tool_names[:-1]) + f", and {tool_names[-1]}"
        return f"Agent mode with {tool_list} tools"