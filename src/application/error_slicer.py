"""
Application Layer: Smart Error Slicer.
Extracts strictly the root failure cause, failing assertion, and culprit line
from long test tracebacks (pytest/unittest), dropping payload from >2000 tokens to <80 tokens.
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import re
from typing import Optional


class SmartErrorSlicer:
    """
    Parses verbose compiler/test runner tracebacks and distills
    the exact failing assertion and culprit file/line.
    """

    FRAMEWORK_PATTERNS = [
        r"/unittest/case\.py",
        r"/_pytest/",
        r"/pytest/",
        r"/pluggy/",
    ]

    @classmethod
    def slice_traceback(cls, raw_traceback: str) -> str:
        if not raw_traceback or len(raw_traceback.splitlines()) <= 5:
            return raw_traceback

        lines = raw_traceback.splitlines()
        culprit_file_line: Optional[str] = None
        failing_code: Optional[str] = None
        assertion_msg: Optional[str] = None

        for idx, line in enumerate(lines):
            stripped = line.strip()

            # Detect file and line location
            m_file = re.search(r'File "([^"]+)", line (\d+)(?:, in (\w+))?', line)
            if m_file:
                filepath = m_file.group(1)
                line_no = m_file.group(2)
                func_name = m_file.group(3) or ""
                # Skip framework internal frames
                if not any(re.search(pat, filepath) for pat in cls.FRAMEWORK_PATTERNS):
                    culprit_file_line = f'{filepath}:{line_no} in {func_name}'.strip()
                    if idx + 1 < len(lines):
                        next_line = lines[idx + 1].strip()
                        if not next_line.startswith("File "):
                            failing_code = next_line

            # Detect assertion failure
            if stripped.startswith("assert ") or stripped.startswith("E       assert "):
                failing_code = stripped.lstrip("E ").strip()
            elif (
                "AssertionError" in stripped
                or "SyntaxError" in stripped
                or "TypeError" in stripped
                or "ValueError" in stripped
                or "AttributeError" in stripped
            ):
                assertion_msg = stripped.lstrip("E ").strip()

        output_parts: list[str] = ["=== [Smart Error Slicer: <80 tokens] ==="]
        if culprit_file_line:
            output_parts.append(f"Culprit: {culprit_file_line}")
        if failing_code:
            output_parts.append(f"Statement: {failing_code}")
        if assertion_msg:
            output_parts.append(f"Failure: {assertion_msg}")

        if len(output_parts) == 1:
            # Fallback if no specific patterns matched: take last 5 lines
            output_parts.extend([l.strip() for l in lines[-5:] if l.strip()])

        return "\n".join(output_parts)
