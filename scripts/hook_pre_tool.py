#!/usr/bin/env python3
"""
Thin Facade for Antigravity PreToolUse Hook.
Delegates to Hexagonal Architecture (src.adapters.inbound.hook_adapter).
Includes bulletproof fallback to prevent blocking tools if environment paths change.
"""
import json
import os
import sys

# Priority 1: Check standard repository path
REPO_PATH = "/Users/mauriciohelfstein/dev/gravitational-singularity"
if os.path.isdir(os.path.join(REPO_PATH, "src")) and REPO_PATH not in sys.path:
    sys.path.insert(0, REPO_PATH)

# Priority 2: Check relative parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from src.adapters.inbound.hook_adapter import run_hook
    if __name__ == "__main__":
        run_hook()
except Exception:
    # Bulletproof fallback: Never block tool execution if imports fail
    print(json.dumps({"decision": "allow"}))
