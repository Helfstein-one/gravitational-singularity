#!/usr/bin/env python3
"""
Thin Facade for Antigravity Live Telemetry Daemon :7890.
Delegates to Hexagonal Architecture (src.adapters.inbound.http_telemetry_adapter).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.adapters.inbound.http_telemetry_adapter import main

if __name__ == "__main__":
    main()
