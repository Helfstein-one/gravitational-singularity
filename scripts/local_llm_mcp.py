#!/usr/bin/env python3
"""
Thin Facade for Local LLM MCP Server (Stdio JSON-RPC).
Delegates to Hexagonal Architecture (src.adapters.inbound.mcp_adapter).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.inbound.mcp_adapter import run_mcp_server

if __name__ == "__main__":
    run_mcp_server()
