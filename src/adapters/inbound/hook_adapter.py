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


WRITE_TOOLS = {"replace_file_content", "write_to_file", "edit_file", "write_file"}


def run_hook() -> None:
    raw_input = ""
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input)
    except Exception as e:
        _log_hook_error("stdin_json_decode", str(e))
        # Fail-closed: If raw stdin contains any write tool invocations, deny to prevent corrupted writes
        if any(w in raw_input for w in WRITE_TOOLS):
            print(json.dumps({
                "decision": "deny",
                "reason": "Event Horizon Fail-Closed Safety Gate: Corrupted JSON payload on write tool call. Blocked to prevent file corruption."
            }))
            return
        print(json.dumps({"decision": "allow"}))
        return

    tool_name = ""
    args = {}
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
        # Fail-closed for all write operations, fail-open for read-only tools
        if tool_name in WRITE_TOOLS:
            decision = {
                "decision": "deny",
                "reason": f"Event Horizon Fail-Closed Safety Gate: Pre-write inspection failed unexpectedly ({type(e).__name__}: {str(e)[:200]}). Blocked for file safety."
            }
        else:
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
