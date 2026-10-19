#!/usr/bin/env python3
"""
Thin Facade for Semantic Code RAG CLI.
Delegates to Hexagonal Architecture (src.adapters.inbound.cli_adapters).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.inbound.cli_adapters import run_code_rag_cli

if __name__ == "__main__":
    run_code_rag_cli()
