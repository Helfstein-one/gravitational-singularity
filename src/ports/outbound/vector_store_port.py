"""
Outbound Port: Vector Store and Embedding Cache Interface.
"""

from typing import Protocol
from src.domain.entities import CodeChunk


class IVectorStore(Protocol):
    """Abstract persistence for embeddings and deterministic chunk caches."""

    def save_chunks(self, repo_key: str, chunks: list[CodeChunk]) -> None:
        """Stores indexed chunks with embeddings."""
        ...

    def load_chunks(self, repo_key: str) -> list[CodeChunk] | None:
        """Retrieves cached chunks if available."""
        ...

    def get_file_hash(self, file_path: str) -> str:
        """Returns deterministic content hash (e.g. SHA-256) of file."""
        ...
