#!/usr/bin/env python3
"""
Thin Facade for Session Distiller CLI.
Delegates to Hexagonal Architecture (src.adapters.inbound.cli_adapters).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.inbound.cli_adapters import run_session_distiller_cli

if __name__ == "__main__":
    run_session_distiller_cli()
