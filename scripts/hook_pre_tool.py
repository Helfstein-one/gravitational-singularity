#!/usr/bin/env python3
import sys, json, re, os, ast, subprocess

def validate_syntax(target_file: str, content: str) -> tuple:
    ext = os.path.splitext(target_file)[1].lower()

    if ext == ".py":
        try:
            ast.parse(content, filename=target_file)
        except SyntaxError as e:
            line_str = f"'{e.text.strip()}'" if e.text else ""
            return False, f"Python SyntaxError on line {e.lineno}: {e.msg} ({line_str})"

    elif ext == ".json":
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            return False, f"JSON SyntaxError on line {e.lineno}, col {e.colno}: {e.msg}"

    elif ext in [".js", ".mjs", ".cjs"]:
        try:
            res = subprocess.run(
                ["node", "--input-type=module", "--check"],
                input=content,
                text=True,
                capture_output=True,
                timeout=3
            )
            if res.returncode != 0:
                err_line = res.stderr.splitlines()[-1] if res.stderr else "Syntax error"
                return False, f"JavaScript SyntaxError: {err_line}"
        except Exception:
            pass

    elif ext in [".yaml", ".yml"]:
        try:
            import yaml
            yaml.safe_load(content)
        except Exception as e:
            if "YAMLError" in type(e).__name__ or "ScannerError" in type(e).__name__:
                return False, f"YAML SyntaxError: {str(e)}"

    return True, ""

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tool_call = payload.get("toolCall", {})
    name = tool_call.get("name", "")
    args = tool_call.get("args", {})

    # 1. Gate view_file on large / log files
    if name == "view_file":
        path = args.get("AbsolutePath", "")
        start_line = args.get("StartLine")
        end_line = args.get("EndLine")

        if path.endswith(".log"):
            # Block un-sliced reading of .log files
            if not start_line and not end_line:
                res = {
                    "decision": "deny",
                    "reason": "Event Horizon Hook: Direct view_file on *.log without slicing is denied to protect context tokens. Use tail, grep, or specify StartLine/EndLine."
                }
                print(json.dumps(res))
                return

    # 2. Gate run_command dangerous commands and auto-wrap verbose commands
    if name == "run_command":
        cmd = args.get("CommandLine", "").strip()

        # Danger checks
        if re.search(r"\brm\s+-(?:rf|fr)\s+(?:/|~|\$HOME|\.\.)", cmd) or re.search(r"\bgit\s+push\s+.*--force\b", cmd):
            res = {
                "decision": "deny",
                "reason": "Event Horizon Hook: Destructive command blocked by safety gate."
            }
            print(json.dumps(res))
            return

        # Auto-wrap test commands with test-slicer to filter passing noise
        test_triggers = [r"^pytest\b", r"^npm\s+(?:test|run\s+test)", r"^vitest\b", r"^jest\b", r"^cargo\s+test", r"^go\s+test", r"^python3?\s+-m\s+(?:unittest|pytest)"]
        is_test = any(re.search(pat, cmd) for pat in test_triggers)

        if is_test and not (cmd.startswith("test-slicer ") or cmd.startswith("rtk ")):
            res = {
                "decision": "allow",
                "overwrite": {
                    "CommandLine": f"test-slicer {cmd}"
                }
            }
            print(json.dumps(res))
            return

        # Auto-guard git log without limit
        if re.search(r"^git\s+log\b", cmd) and not re.search(r"\s+-(?:n|\d+|max-count)\b", cmd):
            cmd = f"{cmd} -n 10"

        # Auto-wrap verbose build, install, package managers and logs with rtk
        verbose_triggers = [
            r"^(?:npm|pnpm|yarn|bun)\s+(?:install|ci|add|build)",
            r"^(?:pip|pip3|poetry|uv)\s+(?:install|sync|add)",
            r"^cargo\s+(?:build|install)",
            r"^brew\s+(?:install|upgrade)",
            r"^docker\s+(?:build|logs)",
            r"^git\s+log\b"
        ]
        is_verbose = any(re.search(pat, cmd) for pat in verbose_triggers)

        if is_verbose and not cmd.startswith("rtk ") and not cmd.startswith("test-slicer "):
            res = {
                "decision": "allow",
                "overwrite": {
                    "CommandLine": f"rtk {cmd}"
                }
            }
            print(json.dumps(res))
            return

    # 3. In-memory syntax gate for replace_file_content and write_to_file
    if name in ["replace_file_content", "write_to_file"]:
        target_file = args.get("TargetFile", "")
        simulated_content = None

        if name == "write_to_file":
            code_content = args.get("CodeContent", "")
            if args.get("Append") and os.path.isfile(target_file):
                try:
                    with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                        simulated_content = f.read() + code_content
                except Exception:
                    simulated_content = code_content
            else:
                simulated_content = code_content

        elif name == "replace_file_content":
            target_content = args.get("TargetContent", "")
            replacement_content = args.get("ReplacementContent", "")
            allow_multiple = args.get("AllowMultiple", False)

            if os.path.isfile(target_file):
                try:
                    with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                        orig = f.read()
                    if target_content in orig:
                        count = -1 if allow_multiple else 1
                        simulated_content = orig.replace(target_content, replacement_content, count)
                except Exception:
                    pass

        if simulated_content is not None:
            ok, err_msg = validate_syntax(target_file, simulated_content)
            if not ok:
                res = {
                    "decision": "deny",
                    "reason": f"Event Horizon In-Memory Syntax Gate: Pre-edit dry run failed: {err_msg}. Correct syntax/indentation before applying."
                }
                print(json.dumps(res))
                return

    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
