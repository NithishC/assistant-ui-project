from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, AsyncGenerator
import os
from dotenv import load_dotenv
import openai
import logging
import json

# Import tools and utilities
from tools import get_tool_registry
from prompts import STRUCTURED_SYSTEM_PROMPT, get_dynamic_prompt, get_tool_limits
from response_parser import StructuredResponseParser

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate required environment variables
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is required in environment variables")
# Note: BRAVE_SEARCH_API_KEY is optional - file system tools work without it

# Initialize FastAPI app
app = FastAPI(title="Assistant UI Backend", version="4.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize tool registry
tool_registry = get_tool_registry()

# Pydantic models
class Message(BaseModel):
    role: str
    content: Any

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gpt-4o-mini"
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 16000
    stream: Optional[bool] = True
    tools_enabled: Optional[bool] = True  # Legacy field
    enabled_tools: Optional[List[str]] = []

class ChatResponse(BaseModel):
    text: str

@app.get("/")
async def root():
    return {
        "message": "Assistant UI Backend",
        "version": "4.0.0",
        "tools": tool_registry.get_tool_names(),
        "features": ["Agent Mode", "Tool Toggles", "Dynamic Prompts", "File System"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "tools_available": len(tool_registry.get_all_tools()),
        "tool_names": tool_registry.get_tool_names(),
        "phase": "File System Tools"
    }

@app.get("/tools")
async def list_tools():
    """List all available tools and their definitions"""
    tools = []
    for tool in tool_registry.get_all_tools():
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": [p.dict() for p in tool.parameters]
        })
    return {"tools": tools}

async def generate_normal_chat_response(request: ChatRequest) -> AsyncGenerator[str, None]:
    """Generate normal chat response without tools"""
    try:
        messages = []
        
        # Add system prompt for normal chat
        messages.append({
            "role": "system", 
            "content": "You are a helpful assistant. You can answer questions and help with tasks. You do not have access to any tools - provide answers based on your knowledge."
        })
        
        # Add user messages
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})
        
        logger.info("Normal chat mode - no tools")
        
        # Get response from LLM without tools
        response = openai_client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False
        )
        
        assistant_response = response.choices[0].message.content
        
        # Stream the response as content
        yield f"data: {json.dumps({'type': 'content', 'text': assistant_response})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in normal chat generation: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

async def generate_agent_mode_response(request: ChatRequest, enabled_tools: List[str]) -> AsyncGenerator[str, None]:
    """Generate agent mode response with enabled tools"""
    try:
        messages = []
        
        # Get dynamic prompt based on enabled tools
        system_prompt = get_dynamic_prompt(enabled_tools)
        messages.append({"role": "system", "content": system_prompt})
        
        # Add user messages
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})
        
        logger.info(f"Agent mode with enabled tools: {enabled_tools}")
        
        # Get dynamic tool limits based on enabled tools
        limits = get_tool_limits(enabled_tools)
        max_tools = limits["max_tools"]
        max_turns = limits["max_turns"]
        
        logger.info(f"Using dynamic limits: {max_tools} tools, {max_turns} turns ({limits['reason']})")
        
        parser = StructuredResponseParser()
        turn_count = 0
        tools_used = 0
        previous_tool_calls = set()
        
        while turn_count < max_turns:
            turn_count += 1
            
            # Get response from LLM
            response = openai_client.chat.completions.create(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=False
            )
            
            assistant_response = response.choices[0].message.content
            
            # Log the AI response for debugging
            logger.info(f"AI Response Turn {turn_count}: {assistant_response[:200]}...")
            
            # Parse the response
            thinking = parser.parse_thinking(assistant_response)
            tool_call = parser.parse_tool_call(assistant_response)
            answer = parser.parse_answer(assistant_response)
            
            # Stream the thinking
            if thinking:
                yield f"data: {json.dumps({'type': 'thinking', 'text': thinking})}\n\n"
            
            # Check for tool call
            if tool_call:
                # Check if tool is enabled
                if tool_call['name'] not in enabled_tools:
                    logger.warning(f"AI tried to use disabled tool: {tool_call['name']}")
                    msg = f"I cannot use the {tool_call['name']} tool as it is not currently enabled. Let me answer based on my knowledge instead."
                    yield f"data: {json.dumps({'type': 'content', 'text': msg})}\n\n"
                    break
                
                # Check if we've reached the tool limit
                if tools_used >= max_tools:
                    logger.warning(f"Tool limit reached ({max_tools}). Forcing final answer.")
                    yield f"data: {json.dumps({'type': 'content', 'text': 'I have reached the maximum number of tool calls allowed. Based on the information I have gathered, let me provide you with an answer.'})}\n\n"
                    break
                
                # Check for tool call loops
                tool_signature = f"{tool_call['name']}:{json.dumps(tool_call['args'], sort_keys=True)}"
                if tool_signature in previous_tool_calls:
                    logger.warning(f"Tool loop detected at turn {turn_count}! Same tool call repeated.")
                    yield f"data: {json.dumps({'type': 'content', 'text': 'I detected that I was about to repeat the same tool call. Let me provide an answer based on the information I have already gathered.'})}\n\n"
                    break
                
                previous_tool_calls.add(tool_signature)
                tools_used += 1
                
                # Stream tool call info
                tool_id = f"call_{turn_count}"
                yield f"data: {json.dumps({'type': 'tool_calls', 'tool_calls': [{'id': tool_id, 'function': {'name': tool_call['name'], 'arguments': json.dumps(tool_call['args'])}}]})}\n\n"
                
                # Execute the tool
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                # Additional security check for file_system tool
                if tool_name == 'file_system':
                    file_path = tool_args.get('file_path', '')
                    if file_path:
                        # Check for obvious security violations
                        if '../' in file_path or '..\\' in file_path or file_path.startswith('/') or ':' in file_path:
                            logger.warning(f"Security violation blocked: {file_path}")
                            security_msg = '🚨 Security restriction: I cannot access files outside the project directory. Please use relative paths within knowledge_base/ or output/ directories only.'
                            yield f"data: {json.dumps({'type': 'content', 'text': security_msg})}\n\n"
                            break
                
                logger.info(f"Executing enabled tool: {tool_name} with args: {tool_args}")
                
                try:
                    # Send tool start notification
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool_name': tool_name, 'args': tool_args})}\n\n"
                    
                    result = await tool_registry.execute_tool(tool_name, **tool_args)
                    
                    # Send the complete result
                    yield f"data: {json.dumps({'type': 'tool_result', 'tool_name': tool_name, 'result': result})}\n\n"
                    
                    # Add to conversation with strong instruction based on tool count
                    messages.append({"role": "assistant", "content": assistant_response})
                    
                    if tools_used >= max_tools:
                        messages.append({"role": "user", "content": f"✅ Tool '{tool_name}' completed successfully. Result:\n{result}\n\n🚫 CRITICAL: You have now used {tools_used} tools (maximum allowed). You MUST provide your final answer using the <answer></answer> format. Do NOT call any more tools. Analyze all the results and give a comprehensive response."})
                    else:
                        messages.append({"role": "user", "content": f"✅ Tool '{tool_name}' completed successfully. Result:\n{result}\n\n📊 You have used {tools_used} of {max_tools} allowed tools. You can either use another enabled tool if needed or provide your final answer using <answer></answer> format."})
                    
                except Exception as e:
                    error_msg = f"Error executing tool: {str(e)}"
                    yield f"data: {json.dumps({'type': 'tool_error', 'tool_name': tool_name, 'error': error_msg})}\n\n"
                    messages.append({"role": "assistant", "content": assistant_response})
                    messages.append({"role": "user", "content": f"❌ Tool '{tool_name}' failed: {error_msg}\n\n🚫 CRITICAL: Provide your final answer using the <answer></answer> format with whatever information you have."})
            
            elif answer:
                # Stream the final answer
                yield f"data: {json.dumps({'type': 'content', 'text': answer})}\n\n"
                break
            
            else:
                # Invalid format - ask for proper format
                error_msg = "Please respond using the required format with <think>, <tool>, or <answer> tags."
                yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"
                messages.append({"role": "assistant", "content": assistant_response})
                messages.append({"role": "user", "content": error_msg})
        
        # Check if we hit max turns without a final answer
        if turn_count >= max_turns:
            logger.warning(f"Maximum turns ({max_turns}) reached without final answer")
            yield f"data: {json.dumps({'type': 'content', 'text': 'I have reached the maximum number of conversation turns. Let me provide you with the best answer I can based on the information available.'})}\n\n"
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error in agent mode generation: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with dual-mode support"""
    try:
        enabled_tools = request.enabled_tools or []
        
        logger.info(f"Chat request with {len(request.messages)} messages, enabled tools: {enabled_tools}")
        
        if request.stream:
            if not enabled_tools:
                # Normal chat mode
                return StreamingResponse(
                    generate_normal_chat_response(request),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                    }
                )
            else:
                # Agent mode with enabled tools
                return StreamingResponse(
                    generate_agent_mode_response(request, enabled_tools),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                    }
                )
        else:
            # For non-streaming, collect all events and return final answer
            if not enabled_tools:
                events = []
                async for event in generate_normal_chat_response(request):
                    events.append(event)
            else:
                events = []
                async for event in generate_agent_mode_response(request, enabled_tools):
                    events.append(event)
            
            # Extract final answer from events
            final_text = ""
            for event in events:
                if "data: " in event:
                    try:
                        data = json.loads(event.split("data: ")[1])
                        if data.get("type") == "content":
                            final_text = data.get("text", "")
                    except:
                        pass
            
            return ChatResponse(text=final_text or "No response generated")
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting backend with {len(tool_registry.get_all_tools())} tools")
    logger.info(f"Available tools: {', '.join(tool_registry.get_tool_names())}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)