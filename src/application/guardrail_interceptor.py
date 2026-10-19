"""
Application Use Case: Guardrail Interceptor.
Evaluates PreToolUse calls, enforces syntax validity in RAM and rewrites noisy commands.
"""

from __future__ import annotations
import os
import re
from typing import Any
from src.ports.outbound.ast_parser_port import IAstParser
from src.ports.outbound.file_system_port import IFileSystemGateway
from src.domain.value_objects import SyntaxValidationResult


class GuardrailInterceptor:
    """Interception engine enforcing pre-tool safety and in-memory AST validation."""

    def __init__(self, parser: IAstParser, file_system: IFileSystemGateway):
        self.parser = parser
        self.fs = file_system

    def evaluate(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Evaluates tool invocation and returns decision dictionary."""
        # 1. Gate view_file on large / log files
        if tool_name == "view_file":
            path = args.get("AbsolutePath", "")
            start_line = args.get("StartLine")
            end_line = args.get("EndLine")
            if path.endswith(".log") and not start_line and not end_line:
                return {
                    "decision": "deny",
                    "reason": "Event Horizon Hook: Direct view_file on *.log without slicing is denied to protect context tokens. Use tail, grep, or specify StartLine/EndLine."
                }

        # 2. Gate run_command dangerous commands and auto-wrap verbose commands
        if tool_name == "run_command":
            cmd = args.get("CommandLine", "").strip()

            # Dangerous command blocks
            if re.search(r"\brm\s+-(?:rf|fr)\s+(?:/|~|\$HOME|\.\.)", cmd) or re.search(r"\bgit\s+push\s+.*--force\b", cmd):
                return {
                    "decision": "deny",
                    "reason": "Event Horizon Hook: Destructive command blocked by safety gate."
                }

            # Auto-wrap test commands
            test_triggers = [
                r"^pytest\b", r"^npm\s+(?:test|run\s+test)", r"^vitest\b",
                r"^jest\b", r"^cargo\s+test", r"^go\s+test",
                r"^python3?\s+-m\s+(?:unittest|pytest)"
            ]
            if any(re.search(pat, cmd) for pat in test_triggers) and not (cmd.startswith("test-slicer ") or cmd.startswith("rtk ")):
                return {
                    "decision": "allow",
                    "overwrite": {"CommandLine": f"test-slicer {cmd}"}
                }

            # Auto-guard git log without limit
            if re.search(r"^git\s+log\b", cmd) and not re.search(r"\s+-(?:n|\d+|max-count)\b", cmd):
                cmd = f"{cmd} -n 10"

            # Auto-wrap verbose build and install commands with RTK
            verbose_triggers = [
                r"^(?:npm|pnpm|yarn|bun)\s+(?:install|ci|add|build)",
                r"^(?:pip|pip3|poetry|uv)\s+(?:install|sync|add)",
                r"^cargo\s+(?:build|install)",
                r"^brew\s+(?:install|upgrade)",
                r"^docker\s+(?:build|logs)",
                r"^git\s+log\b"
            ]
            if any(re.search(pat, cmd) for pat in verbose_triggers) and not cmd.startswith("rtk ") and not cmd.startswith("test-slicer "):
                return {
                    "decision": "allow",
                    "overwrite": {"CommandLine": f"rtk {cmd}"}
                }

        # 3. In-memory syntax gate for replace_file_content and write_to_file
        if tool_name in ["replace_file_content", "write_to_file"]:
            target_file = args.get("TargetFile", "")
            simulated_content: str | None = None

            if tool_name == "write_to_file":
                code_content = args.get("CodeContent", "")
                if args.get("Append") and self.fs.exists(target_file):
                    try:
                        orig = self.fs.read_text(target_file)
                        simulated_content = orig + code_content
                    except Exception:
                        simulated_content = code_content
                else:
                    simulated_content = code_content

            elif tool_name == "replace_file_content":
                target_content = args.get("TargetContent", "")
                replacement_content = args.get("ReplacementContent", "")
                allow_multiple = args.get("AllowMultiple", False)

                if self.fs.exists(target_file):
                    try:
                        orig = self.fs.read_text(target_file)
                        if target_content in orig:
                            count = -1 if allow_multiple else 1
                            simulated_content = orig.replace(target_content, replacement_content, count)
                    except Exception:
                        pass

            if simulated_content is not None:
                ext = os.path.splitext(target_file)[1].lower()
                lang = "python" if ext == ".py" else "javascript" if ext in [".js", ".mjs", ".cjs"] else "json" if ext == ".json" else "unknown"
                result: SyntaxValidationResult = self.parser.validate_syntax(simulated_content, lang)
                if not result.is_valid:
                    return {
                        "decision": "deny",
                        "reason": f"Event Horizon In-Memory Syntax Gate: Pre-edit dry run failed: {result.error_message}. Correct syntax/indentation before applying."
                    }

        return {"decision": "allow"}
