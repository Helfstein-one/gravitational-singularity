"""
Outbound Adapter: Deterministic File Cache for Vector Embeddings.
Implements IVectorStore using JSON on disk and SHA-256 hashes.
"""

from __future__ import annotations
import hashlib
import json
import os
from src.ports.outbound.vector_store_port import IVectorStore
from src.domain.entities import CodeChunk


class JsonFileCacheAdapter(IVectorStore):
    """Stores and retrieves precomputed embeddings based on content hashes."""

    def __init__(self, cache_dir: str | None = None):
        self.cache_dir = cache_dir or os.path.expanduser("~/.gemini/config/cache/code_rag")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, repo_key: str) -> str:
        safe_key = hashlib.sha256(repo_key.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.json")

    def get_file_hash(self, file_path: str) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    def save_chunks(self, repo_key: str, chunks: list[CodeChunk]) -> None:
        path = self._get_cache_path(repo_key)
        data = [
            {
                "file_path": c.file_path,
                "start_line": c.start_line,
                "end_line": c.end_line,
                "node_type": c.node_type,
                "name": c.name,
                "code": c.code,
                "embedding": c.embedding
            }
            for c in chunks
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_chunks(self, repo_key: str) -> list[CodeChunk] | None:
        path = self._get_cache_path(repo_key)
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            chunks: list[CodeChunk] = []
            for item in raw_list:
                chunks.append(CodeChunk(
                    file_path=item["file_path"],
                    start_line=item["start_line"],
                    end_line=item["end_line"],
                    node_type=item["node_type"],
                    name=item["name"],
                    code=item["code"],
                    embedding=item.get("embedding", [])
                ))
            return chunks
        except Exception:
            return None
