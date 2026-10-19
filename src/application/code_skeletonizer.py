"""
Application Use Case: Code Skeletonizer.
Punes imperative logic while preserving class and function signatures.
"""

from __future__ import annotations
import re
from src.ports.outbound.ast_parser_port import IAstParser


class CodeSkeletonizer:
    """Use case coordinating AST skeletonization and compression metrics."""

    def __init__(self, parser: IAstParser):
        self.parser = parser

    def skeletonize(self, raw_code: str, language: str = "python") -> tuple[str, float]:
        """Returns compressed code skeleton and token reduction percentage."""
        compressed = self.parser.skeletonize(raw_code, language)
        reduction = self._estimate_token_reduction(raw_code, compressed)
        return compressed, reduction

    def _estimate_token_reduction(self, original: str, compressed: str) -> float:
        orig_tokens = len(re.findall(r"\w+|[^\w\s]", original))
        comp_tokens = len(re.findall(r"\w+|[^\w\s]", compressed))
        if orig_tokens == 0:
            return 0.0
        return round((1.0 - (comp_tokens / orig_tokens)) * 100.0, 1)
