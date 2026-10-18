#!/usr/bin/env python3
"""
Smart Test Slicer - Filters test execution output to retain only failures,
errors, and summary metrics, discarding passing noise to preserve LLM tokens.
"""

import sys
import subprocess
import re

def slice_output(raw_output: str, exit_code: int) -> str:
    lines = raw_output.splitlines()
    if len(lines) <= 60:
        return raw_output

    if exit_code == 0:
        # Success case: keep header and summary
        header = lines[:10]
        tail = lines[-15:]
        return "\n".join(header) + f"\n\n... [Smart Test Slicer: {len(lines) - 25} lines of passing tests truncated] ...\n\n" + "\n".join(tail)

    # Failure case: identify lines with failure indicators
    failure_blocks = []
    in_failure = False
    current_block = []

    fail_triggers = re.compile(r"(FAIL|FAILED|ERROR|ERRORS|Traceback|AssertionError|assert |Exception|failure:)", re.IGNORECASE)

    for line in lines:
        if fail_triggers.search(line):
            in_failure = True
            current_block.append(line)
        elif in_failure:
            current_block.append(line)
            # End block if separator or empty line sequence
            if re.match(r"^(=+|-{3,}|_{3,})\s*$", line.strip()) and len(current_block) > 5:
                failure_blocks.extend(current_block)
                current_block = []
                in_failure = False

    if current_block:
        failure_blocks.extend(current_block)

    summary = lines[-20:]
    result = []
    result.append(f"=== [Smart Test Slicer: Truncated {len(lines)} lines -> Highlighting Failures & Summary] ===")
    if failure_blocks:
        result.append("\n--- Failure Traces ---")
        result.append("\n".join(failure_blocks[:100]))
    result.append("\n--- Final Test Summary ---")
    result.append("\n".join(summary))

    return "\n".join(result)

def main():
    if len(sys.argv) < 2:
        print("Usage: test-slicer <test command...>")
        sys.exit(1)

    cmd = sys.argv[1:]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    sliced = slice_output(proc.stdout, proc.returncode)
    print(sliced)
    sys.exit(proc.returncode)

if __name__ == "__main__":
    main()
