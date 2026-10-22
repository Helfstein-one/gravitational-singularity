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
from src.application.event_emitter import TelemetryEventEmitter


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

    # Reactive event emission to shared memory ring buffer
    try:
        events = TelemetryEventEmitter.get_instance()
        if decision.get("decision") == "deny":
            events.on_syntax_blocked(
                file_path=args.get("TargetFile") or args.get("Path") or args.get("AbsolutePath") or tool_name,
                tool_name=tool_name,
                error_message=decision.get("reason", "blocked by guardrail"),
            )
        else:
            events.emit("on_hook_allowed", {"tool": tool_name})
    except Exception:
        pass

    print(json.dumps(decision))


if __name__ == "__main__":
    run_hook()
