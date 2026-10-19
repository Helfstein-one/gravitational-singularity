"""
Inbound Port: Semantic Code RAG Service Interface.
"""

from typing import Protocol
from src.domain.entities import CodeChunk


class ISemanticRagService(Protocol):
    """Indexes repository via AST chunks and retrieves exact code locations."""

    def index_repository(self, root_dir: str) -> int:
        """Indexes all code chunks in the repository; returns chunk count."""
        ...

    def query_similar_chunks(self, query: str, top_k: int = 5) -> list[tuple[CodeChunk, float]]:
        """Finds top-k semantically relevant chunks with similarity score."""
        ...
