"""
Inbound Port: Syntax Compressor Interface (AST Skeletonization).
"""

from typing import Protocol


class ISyntaxCompressorService(Protocol):
    """Punes imperative method bodies, preserving signatures and docstrings."""

    def skeletonize_code(self, code: str, language: str) -> str:
        """Transforms full implementation into a compressed AST interface."""
        ...

    def calculate_compression_ratio(self, raw_code: str, skeleton_code: str) -> float:
        """Returns the percentage of token reduction achieved."""
        ...
