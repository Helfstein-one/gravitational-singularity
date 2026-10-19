"""
Outbound Port: Multi-Language AST Parser Interface.
"""

from typing import Protocol
from src.domain.value_objects import SyntaxValidationResult
from src.domain.entities import CodeChunk


class IAstParser(Protocol):
    """Abstract parser for syntax validation, chunking, and skeletonization."""

    def validate_syntax(self, code: str, language: str) -> SyntaxValidationResult:
        """Validates code syntax in memory."""
        ...

    def extract_chunks(self, file_path: str, code: str) -> list[CodeChunk]:
        """Partitions code into semantic AST chunks (functions, classes)."""
        ...

    def skeletonize(self, code: str, language: str) -> str:
        """Compresses code by replacing imperative bodies with ellipsis."""
        ...
