"""
Application Use Case: Semantic Code Retriever (RAG).
Indexes repository into AST chunks and retrieves exact relevant spans.
"""

from __future__ import annotations
import glob
import math
import os
from src.domain.entities import CodeChunk
from src.ports.outbound.ast_parser_port import IAstParser
from src.ports.outbound.llm_client_port import ILLMClient
from src.ports.outbound.vector_store_port import IVectorStore
from src.ports.outbound.file_system_port import IFileSystemGateway
from src.adapters.outbound.accelerate_vector_adapter import AccelerateVectorAdapter


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    return AccelerateVectorAdapter.cosine_similarity(v1, v2)


class SemanticRetriever:
    """Orchestrates AST chunking, embeddings generation and cosine similarity search."""

    def __init__(
        self,
        parser: IAstParser,
        llm: ILLMClient,
        vector_store: IVectorStore,
        file_system: IFileSystemGateway
    ):
        self.parser = parser
        self.llm = llm
        self.vector_store = vector_store
        self.fs = file_system

    def index_directory(self, root_dir: str) -> list[CodeChunk]:
        """Scans python files, partitions into AST chunks and generates embeddings."""
        pattern = os.path.join(root_dir, "**", "*.py")
        py_files = [f for f in glob.glob(pattern, recursive=True) if not "/." in f]

        cached = self.vector_store.load_chunks(root_dir)
        if cached:
            return cached

        all_chunks: list[CodeChunk] = []
        for file_path in py_files:
            try:
                code = self.fs.read_text(file_path)
                chunks = self.parser.extract_chunks(file_path, code)
                for chunk in chunks:
                    chunk.embedding = self.llm.embed(chunk.code[:2000])
                    all_chunks.append(chunk)
            except Exception:
                continue

        self.vector_store.save_chunks(root_dir, all_chunks)
        return all_chunks

    def search(self, query: str, chunks: list[CodeChunk], top_k: int = 5) -> list[tuple[CodeChunk, float]]:
        """Queries chunks using cosine similarity."""
        query_vec = self.llm.embed(query)
        if not query_vec:
            return []

        scored = []
        for chunk in chunks:
            if chunk.embedding:
                score = cosine_similarity(query_vec, chunk.embedding)
                scored.append((chunk, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
