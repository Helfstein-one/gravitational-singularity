"""
Inbound Adapter: Antigravity PreToolUse Hook Adapter.
Reads tool invocation payload from stdin, executes GuardrailInterceptor, outputs JSON decision to stdout.
"""

from __future__ import annotations
import json
import sys
from src.application.guardrail_interceptor import GuardrailInterceptor
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.adapters.outbound.file_system_adapter import LocalFileSystemAdapter


def run_hook() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tool_call = payload.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    args = tool_call.get("args", {})

    parser = MultiLanguageAstAdapter()
    fs = LocalFileSystemAdapter()
    interceptor = GuardrailInterceptor(parser=parser, file_system=fs)

    decision = interceptor.evaluate(tool_name, args)
    print(json.dumps(decision))


if __name__ == "__main__":
    run_hook()
