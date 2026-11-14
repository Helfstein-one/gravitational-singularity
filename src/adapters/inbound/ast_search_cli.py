"""
Inbound Adapter: CLI entrypoint for ast-search.
Directly invokes the zero-dependency AST extractor for syntax pruning & context minimization.
"""

from __future__ import annotations
import sys
from pathlib import Path


def main() -> int:
    """Entry point for ast-search command-line interface."""
    # Locate ast_extractor.py in skills/ast-search/bin/ast_extractor.py
    # Relative to this file: src/adapters/inbound -> src -> project_root -> skills/ast-search/bin
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[3]
    candidate_paths = [
        project_root / "skills" / "ast-search" / "bin" / "ast_extractor.py",
        project_root / "skills" / "ast-search" / "ast_extractor.py",
        Path.home() / ".gemini" / "antigravity" / "skills" / "ast-search" / "bin" / "ast_extractor.py",
        Path.home() / ".gemini" / "config" / ".agents" / "skills" / "ast-search" / "bin" / "ast_extractor.py",
    ]

    extractor_script = None
    for p in candidate_paths:
        if p.exists():
            extractor_script = p
            break

    if not extractor_script:
        sys.stderr.write("Error: Could not locate ast_extractor.py in workspace skills or user skills.\n")
        return 1

    # Load and execute ast_extractor
    import runpy
    sys.argv[0] = "ast-search"
    runpy.run_path(str(extractor_script), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
