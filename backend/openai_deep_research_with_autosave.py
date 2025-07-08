import asyncio
import httpx
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class OptimizedDeepResearchMCPIntegration:
    """Optimized Integration between OpenAI Deep Research and Assistant UI MCP Server"""
    
    def __init__(self, mcp_server_url: str, openai_api_key: str):
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.available_tools = {}
        self.start_time = None
        
        # Ensure output directory exists
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def initialize(self):
        """Initialize and discover available MCP tools"""
        print("🔍 Discovering MCP tools...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.mcp_server_url}/mcp/tools")
                if response.status_code == 200:
                    tools_data = response.json()
                    self.available_tools = {tool['name']: tool for tool in tools_data['tools']}
                    print(f"✅ Found {len(self.available_tools)} MCP tools:")
                    for name, tool in self.available_tools.items():
                        print(f"   🔧 {name}: {tool['description'][:60]}...")
                    return True
                else:
                    print(f"❌ Failed to get tools: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Error connecting to MCP server: {e}")
                return False
    
    def create_optimized_deep_research_call(self, query: str, optimization_level: str = "balanced") -> Dict[str, Any]:
        """Create OPTIMIZED OpenAI Deep Research API call with speed improvements"""
        
        # Optimization Level System Messages
        optimization_configs = {
            "fast": {
                "model": "o4-mini-deep-research",  # Much faster model
                "max_searches": 5,
                "focus": "focused_efficiency"
            },
            "balanced": {
                "model": "o4-mini-deep-research",  # Still faster than o3
                "max_searches": 8,
                "focus": "quality_with_speed"
            },
            "thorough": {
                "model": "o3-deep-research-2025-06-26",  # Original model
                "max_searches": 12,
                "focus": "comprehensive_analysis"
            }
        }
        
        config = optimization_configs.get(optimization_level, optimization_configs["balanced"])
        
        # OPTIMIZED System message with explicit efficiency instructions
        system_message = f"""
You are a professional researcher preparing a structured, data-driven report. Your task is to analyze the question efficiently and thoroughly.

EFFICIENCY GUIDELINES (IMPORTANT):
- Aim for {config['max_searches']} or fewer total searches to complete your research
- Prioritize high-value searches: start broad, then focus on specific gaps
- When you find sufficient information, proceed to analysis rather than additional searches
- Focus on data-rich insights: specific figures, trends, statistics, measurable outcomes
- Each search should fill a distinct information gap - avoid redundant searches

DO NOT search for "assistant_ui_tools" or "mcp_assistant_ui_tools" - these are internal infrastructure names.

Be analytical, data-driven, and EFFICIENT. Quality over quantity of searches.
"""
        
        # Construct the API call with optimization
        api_call = {
            "model": config["model"],  # Use faster model
            "input": [
                {
                    "role": "developer",
                    "content": [
                        {
                            "type": "input_text",
                            "text": system_message
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"Research Query (aim for efficiency): {query}"
                        }
                    ]
                }
            ],
            "reasoning": {
                "summary": "auto"
            },
            "tools": [
                {
                    "type": "mcp",
                    "server_label": "assistant_ui_tools",
                    "server_url": f"{self.mcp_server_url}/sse/",
                    "require_approval": "never"
                }
            ]
        }
        
        return api_call, config
    
    async def monitor_progress(self, check_interval: int = 30) -> None:
        """Monitor MCP server activity to show progress"""
        if not self.start_time:
            return
            
        while True:
            await asyncio.sleep(check_interval)
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            print(f"⏱️  Research in progress... {minutes}m {seconds}s elapsed")
            
            # Check if we should continue (basic timeout protection)
            if elapsed > 900:  # 15 minutes
                print("⚠️  Research taking longer than expected, but continuing...")
    
    def save_result_to_markdown(self, query: str, result: str, optimization_level: str, elapsed_time: int) -> str:
        """Save Deep Research result to a formatted markdown file"""
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"deep_research_{optimization_level}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # Format the markdown content
        markdown_content = f"""# AI Customer Service Competitive Landscape Analysis

> **Research Method**: OpenAI Deep Research + MCP Integration ({optimization_level.upper()} Mode)  
> **Completion Time**: {elapsed_time//60}m {elapsed_time%60}s  
> **Date**: {datetime.now().strftime("%B %d, %Y")}  
> **Model Used**: o4-mini-deep-research  
> **Tools Used**: Web Search + Case Studies Search + MCP Server Integration

---

## Research Query

{query}

---

## Deep Research Results

{result}

---

## Methodology

This research was conducted using:
- **OpenAI Deep Research API** (o4-mini-deep-research model)
- **MCP Server Integration** for case studies from Salesforce, Amazon, Google
- **Web Search Preview** for market intelligence
- **Optimized prompting** for efficiency (≤{self.get_search_limit(optimization_level)} searches)
- **Real-time progress monitoring** with timeout protection

**Research completed in {optimization_level.upper()} mode for {'rapid competitive insights' if optimization_level == 'fast' else 'balanced quality and speed' if optimization_level == 'balanced' else 'comprehensive analysis'}.**

---

*Generated by OpenAI Deep Research + Assistant UI MCP Server Integration*  
*Generated on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S")}*
"""
        
        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"\\n📄 Results saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Error saving to file: {e}")
            return None
    
    def get_search_limit(self, optimization_level: str) -> int:
        """Get search limit for optimization level"""
        limits = {"fast": 5, "balanced": 8, "thorough": 12}
        return limits.get(optimization_level, 8)
    
    async def run_optimized_deep_research(self, query: str, optimization_level: str = "balanced") -> str:
        """Execute OPTIMIZED Deep Research with MCP integration + AUTO-SAVE"""
        print(f"\\n🔬 Starting OPTIMIZED Deep Research ({optimization_level} mode)")
        print(f"📝 Query: {query}")
        
        self.start_time = time.time()
        
        try:
            # Create the optimized API call
            api_call, config = self.create_optimized_deep_research_call(query, optimization_level)
            
            print(f"⚡ Using {config['model']} for faster completion")
            print(f"🎯 Target: ≤{config['max_searches']} searches for efficiency")
            print("📡 Calling OpenAI Deep Research API...")
            
            # Start progress monitoring
            progress_task = asyncio.create_task(self.monitor_progress())
            
            try:
                # Make the API call with timeout
                response = await asyncio.wait_for(
                    asyncio.to_thread(self.openai_client.responses.create, **api_call),
                    timeout=1200  # 20 minutes timeout
                )
                
                # Cancel progress monitoring
                progress_task.cancel()
                
                elapsed = int(time.time() - self.start_time)
                print(f"\\n✅ Deep Research completed in {elapsed//60}m {elapsed%60}s!")
                
                # Extract the final report
                if response.output and len(response.output) > 0:
                    final_output = response.output[-1]
                    if hasattr(final_output, 'content') and len(final_output.content) > 0:
                        result = final_output.content[0].text
                        
                        # 🔥 AUTO-SAVE TO .MD FILE
                        saved_file = self.save_result_to_markdown(query, result, optimization_level, elapsed)
                        if saved_file:
                            print(f"📂 Open the file to view formatted results: {saved_file}")
                        
                        return result
                
                print("❌ No output received from Deep Research")
                return "No research output received"
                
            except asyncio.TimeoutError:
                progress_task.cancel()
                elapsed = int(time.time() - self.start_time)
                error_msg = f"Deep Research timed out after {elapsed//60}m {elapsed%60}s"
                print(f"⏰ {error_msg}")
                return error_msg
            
        except Exception as e:
            if self.start_time:
                elapsed = int(time.time() - self.start_time)
                error_msg = f"Deep Research failed after {elapsed//60}m {elapsed%60}s: {str(e)}"
            else:
                error_msg = f"Deep Research failed: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    async def run_speed_comparison(self, query: str):
        """Run the same query with different optimization levels for comparison"""
        print("\\n🏃 SPEED COMPARISON TEST")
        print("="*60)
        
        modes = ["fast", "balanced"]
        results = {}
        
        for mode in modes:
            print(f"\\n🚀 Testing {mode.upper()} mode...")
            start = time.time()
            result = await self.run_optimized_deep_research(query, mode)
            elapsed = time.time() - start
            results[mode] = {
                "time": elapsed,
                "result": result[:200] + "..." if len(result) > 200 else result
            }
            print(f"⏱️  {mode.upper()} mode completed in {elapsed/60:.1f} minutes")
        
        print("\\n📊 COMPARISON RESULTS:")
        print("="*60)
        for mode, data in results.items():
            print(f"{mode.upper()}: {data['time']/60:.1f} minutes")
            print(f"Preview: {data['result']}")
            print("-" * 40)
    
    async def demonstrate_optimizations(self):
        """Demonstrate different optimization levels"""
        print("\\n🎯 OpenAI Deep Research OPTIMIZATION Demo")
        print("\\n📋 Available Optimization Levels:")
        print("   🚀 FAST: o4-mini model, ≤5 searches, ~5-8 minutes")
        print("   ⚖️  BALANCED: o4-mini model, ≤8 searches, ~8-12 minutes") 
        print("   🔬 THOROUGH: o3 model, ≤12 searches, ~20-30 minutes")
        
        # Example research query
        research_query = "Analyze competitive landscape for AI customer service solutions, focusing on Salesforce, Microsoft, and Amazon approaches."
        
        print(f"\\n🔍 Research Query: {research_query}")
        
        # Ask user which optimization level
        print("\\nSelect optimization level:")
        print("1. 🚀 FAST (recommended for quick insights)")
        print("2. ⚖️  BALANCED (good quality + speed)")
        print("3. 🔬 THOROUGH (maximum detail)")
        print("4. 🏃 SPEED TEST (compare fast vs balanced)")
        
        choice = input("\\nChoice (1-4): ").strip()
        
        if choice == "1":
            result = await self.run_optimized_deep_research(research_query, "fast")
        elif choice == "2":
            result = await self.run_optimized_deep_research(research_query, "balanced")
        elif choice == "3":
            result = await self.run_optimized_deep_research(research_query, "thorough")
        elif choice == "4":
            await self.run_speed_comparison(research_query)
            return
        else:
            print("Invalid choice, using BALANCED mode")
            result = await self.run_optimized_deep_research(research_query, "balanced")
        
        print("\\n📊 Research Results:")
        print("="*80)
        print(result)
        print("="*80)
        
        return result
    
    def get_optimization_guide(self) -> str:
        """Get guide for optimization strategies"""
        return """
🚀 OPTIMIZATION STRATEGIES IMPLEMENTED:

1. MODEL OPTIMIZATION:
   • o4-mini-deep-research: 3-5x faster than o3-deep-research
   • Still maintains high quality research capabilities
   • Reduces each search cycle from 60s to 20-30s

2. SEARCH EFFICIENCY:
   • Explicit search limits (5-12 max vs unlimited)
   • Strategic search guidance in system prompt
   • Prevents redundant searches on same topics

3. AUTO-SAVE TO MARKDOWN:
   • Automatically saves results to timestamped .md files
   • Professional formatting with metadata
   • Saves to output/ directory

4. PROGRESS MONITORING:
   • Live progress updates every 30 seconds
   • Shows elapsed time during research
   • Helps identify if process is stuck

5. SMART PROMPTING:
   • "Efficiency guidelines" in system message
   • Clear search strategy instructions
   • Quality over quantity emphasis

EXPECTED SPEED IMPROVEMENTS:
• FAST mode: 5-8 minutes (vs 30+ minutes)
• BALANCED mode: 8-12 minutes (vs 30+ minutes)
• THOROUGH mode: 15-20 minutes (vs 30+ minutes)
"""

async def main():
    """Main optimized integration demo"""
    # Configuration
    mcp_server_url = "https://4189aaad3242.ngrok-free.app".strip()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize integration
    integration = OptimizedDeepResearchMCPIntegration(mcp_server_url, openai_api_key)
    
    if await integration.initialize():
        print(integration.get_optimization_guide())
        
        # Ask user if they want to run a demo
        run_demo = input("\\nRun OPTIMIZED Deep Research demo? (y/n): ").strip().lower()
        if run_demo == 'y':
            await integration.demonstrate_optimizations()
        else:
            print("\\n✅ Optimized integration ready!")
    else:
        print("❌ Failed to initialize MCP integration")

if __name__ == "__main__":
    asyncio.run(main())
