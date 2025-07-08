#!/usr/bin/env python3
"""
MCP Server Runner for Assistant UI Tools
Usage: python run_mcp_server.py [--port PORT] [--host HOST]
"""
import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Load environment variables first
from dotenv import load_dotenv

# Load .env file from current directory
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server.mcp_server import main

def setup_logging():
    """Setup logging for MCP server"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('mcp_server.log')
        ]
    )

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run Assistant UI MCP Server')
    parser.add_argument('--port', type=int, default=8001, help='Port to run server on (default: 8001)')
    parser.add_argument('--host', type=str, default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Assistant UI MCP Server on {args.host}:{args.port}")
    
    # Set environment variables for server configuration
    os.environ['MCP_SERVER_HOST'] = args.host
    os.environ['MCP_SERVER_PORT'] = str(args.port)
    
    try:
        # Run the MCP server
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
