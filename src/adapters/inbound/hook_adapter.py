"""
Inbound Adapter: Antigravity PreToolUse Hook Adapter.
Reads tool invocation payload from stdin, executes GuardrailInterceptor, outputs JSON decision to stdout.
"""

from __future__ import annotations
import json
import os
import sys
import time
from src.application.guardrail_interceptor import GuardrailInterceptor
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.adapters.outbound.file_system_adapter import LocalFileSystemAdapter
from src.application.event_emitter import TelemetryEventEmitter


def _log_hook_error(stage: str, error_detail: str) -> None:
    """Safely records hook parsing/execution failures to cache log without crashing."""
    try:
        log_dir = os.path.expanduser("~/.cache/event-horizon")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "hook_errors.log")
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] stage={stage} error={error_detail[:500]}\n")
    except Exception:
        pass


def run_hook() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        _log_hook_error("stdin_json_decode", str(e))
        print(json.dumps({"decision": "allow"}))
        return

    try:
        tool_call = payload.get("toolCall", {})
        tool_name = tool_call.get("name", "")
        args = tool_call.get("args", {})

        parser = MultiLanguageAstAdapter()
        fs = LocalFileSystemAdapter()
        interceptor = GuardrailInterceptor(parser=parser, file_system=fs)

        decision = interceptor.evaluate(tool_name, args)
    except Exception as e:
        _log_hook_error("interceptor_evaluate", str(e))
        print(json.dumps({"decision": "allow"}))
        return

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
