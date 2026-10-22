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
from typing import Optional


class GuardrailInterceptor:
    """Interception engine enforcing pre-tool safety and in-memory AST validation."""

    def __init__(
        self,
        parser: IAstParser,
        file_system: IFileSystemGateway,
        merkle_engine: Optional[Any] = None,
        arbiter: Optional[Any] = None,
    ):
        self.parser = parser
        self.fs = file_system
        self.merkle_engine = merkle_engine
        self.arbiter = arbiter

    def evaluate(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Evaluates tool invocation and returns decision dictionary."""
        # 1. Gate view_file on large / log files and un-sliced code files
        if tool_name == "view_file":
            path = args.get("AbsolutePath", "")
            start_line = args.get("StartLine")
            end_line = args.get("EndLine")

            if path.endswith(".log") and not start_line and not end_line:
                return {
                    "decision": "deny",
                    "reason": "Event Horizon Hook: Direct view_file on *.log without slicing is denied to protect context tokens. Use tail, grep, or specify StartLine/EndLine."
                }

            # Proactive AST context guard on long source files
            if not start_line and not end_line and self.fs.exists(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in [".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"]:
                    try:
                        content = self.fs.read_text(path)
                        lines = content.splitlines()
                        if len(lines) > 120:
                            chunks = self.parser.extract_chunks(path, content)
                            symbols_summary = ", ".join([f"{c.name} (L{c.start_line}-L{c.end_line})" for c in chunks[:8]])
                            more = f" ... and {len(chunks)-8} more" if len(chunks) > 8 else ""
                            return {
                                "decision": "deny",
                                "reason": (
                                    f"Event Horizon AST Guard: {os.path.basename(path)} has {len(lines)} lines (>120). "
                                    f"Un-sliced view_file is blocked to prevent context token bloat. "
                                    f"Key symbols: [{symbols_summary}{more}]. "
                                    f"Please specify StartLine and EndLine to view a surgical slice."
                                )
                            }
                    except Exception:
                        pass

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

        # 3. In-memory syntax gate for file editing and writing tools
        if tool_name in ["replace_file_content", "write_to_file", "edit_file", "write_file"]:
            target_file = (
                args.get("TargetFile")
                or args.get("Path")
                or args.get("file_path")
                or ""
            )
            simulated_content: str | None = None

            if tool_name in ["write_to_file", "write_file"]:
                code_content = (
                    args.get("CodeContent")
                    or args.get("Content")
                    or args.get("code_content")
                    or ""
                )
                if args.get("Append") and self.fs.exists(target_file):
                    try:
                        orig = self.fs.read_text(target_file)
                        simulated_content = orig + code_content
                    except Exception:
                        simulated_content = code_content
                else:
                    simulated_content = code_content

            elif tool_name in ["replace_file_content", "edit_file"]:
                target_content = (
                    args.get("TargetContent")
                    or args.get("Target")
                    or args.get("target_content")
                    or ""
                )
                replacement_content = (
                    args.get("ReplacementContent")
                    or args.get("Replacement")
                    or args.get("replacement_content")
                    or ""
                )
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
                lang = "python" if ext == ".py" else "javascript" if ext in [".js", ".mjs", ".cjs", ".ts", ".tsx"] else "json" if ext == ".json" else "unknown"
                result: SyntaxValidationResult = self.parser.validate_syntax(simulated_content, lang)
                if not result.is_valid:
                    return {
                        "decision": "deny",
                        "reason": f"Event Horizon In-Memory Syntax Gate: Pre-edit dry run failed: {result.error_message}. Correct syntax/indentation before applying."
                    }

                # Formal Verification Gate: Type & Signature Invariants Check
                if lang == "python" and self.fs.exists(target_file):
                    try:
                        orig_code = self.fs.read_text(target_file)
                        inv_err = self._check_type_invariants(orig_code, simulated_content)
                        if inv_err:
                            return {
                                "decision": "deny",
                                "reason": f"Event Horizon Formal Verification Gate: {inv_err}"
                            }
                    except Exception:
                        pass

                # Optional: Reconcile with Merkle engine and check McCabe complexity
                if self.merkle_engine and hasattr(self.merkle_engine, "reconcile_and_assemble"):
                    try:
                        self.merkle_engine.reconcile_and_assemble(target_file, simulated_content)
                    except Exception:
                        pass

        return {"decision": "allow"}

    def _check_type_invariants(self, original_code: str, new_code: str) -> Optional[str]:
        """
        Formal Verification Gate: Checks that patch does not drop required parameters
        or break function signature contracts.
        """
        import ast
        try:
            tree_orig = ast.parse(original_code)
            tree_new = ast.parse(new_code)
        except Exception:
            return None

        orig_funcs = {
            n.name: n for n in ast.walk(tree_orig)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        new_funcs = {
            n.name: n for n in ast.walk(tree_new)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        for fname, orig_f in orig_funcs.items():
            if fname in new_funcs:
                new_f = new_funcs[fname]
                orig_args = [a.arg for a in orig_f.args.args if a.arg != "self"]
                new_args = [a.arg for a in new_f.args.args if a.arg != "self"]
                orig_non_defaults = orig_args[:len(orig_args) - len(orig_f.args.defaults)]
                new_non_defaults = new_args[:len(new_args) - len(new_f.args.defaults)]
                if len(new_non_defaults) < len(orig_non_defaults):
                    return f"Signature invariant violation in '{fname}': required parameter count dropped from {len(orig_non_defaults)} to {len(new_non_defaults)}."
        return None
