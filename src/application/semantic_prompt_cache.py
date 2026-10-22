"""
Application Use Case: Semantic Prompt Cache L0 (Cosine Cache with Scalar Quantization).
Reuses structural patch templates when an incoming prompt has >= 98% cosine similarity
to a previously resolved task, delivering instantaneous patches in 0ms without invoking LLMs.
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import json
import math
import os
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from src.adapters.outbound.accelerate_vector_adapter import AccelerateVectorAdapter


@dataclass(frozen=True)
class SemanticCacheHit:
    is_hit: bool
    similarity: float
    template_patch: Dict[str, Any]
    original_prompt: str
    tokens_saved: int
    latency_ms: float


class SemanticPromptCache:
    """
    Tier 0 Semantic Cache matching intent vectors before invoking local or cloud models.
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        similarity_threshold: float = 0.98,
    ) -> None:
        self.db_path = db_path or os.path.expanduser("~/.gemini/config/cache/semantic_cache.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.threshold = similarity_threshold
        self.accelerate = AccelerateVectorAdapter()
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS semantic_prompts (
                    prompt_hash TEXT PRIMARY KEY,
                    prompt_text TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    patch_json TEXT NOT NULL,
                    tokens_saved INTEGER NOT NULL,
                    created_at REAL NOT NULL
                );
                """
            )

    def lookup(
        self,
        prompt: str,
        prompt_embedding: Optional[List[float]] = None,
        min_similarity: Optional[float] = None,
    ) -> SemanticCacheHit:
        """
        Scans cached embeddings; returns cached patch if cosine similarity >= threshold.
        If prompt_embedding is omitted, matches against exact prompt text.
        """
        t0 = time.perf_counter()
        threshold = min_similarity if min_similarity is not None else self.threshold

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT prompt_text, embedding_json, patch_json, tokens_saved FROM semantic_prompts")
            rows = cur.fetchall()

        best_score = 0.0
        best_row = None

        for row in rows:
            p_text, emb_json, patch_str, tokens = row
            if p_text.strip().lower() == prompt.strip().lower():
                best_score = 1.0
                best_row = (p_text, patch_str, tokens)
                break
            if prompt_embedding:
                try:
                    cand_emb = json.loads(emb_json)
                    if cand_emb:
                        score = self.accelerate.cosine_similarity(prompt_embedding, cand_emb)
                        if score > best_score:
                            best_score = score
                            best_row = (p_text, patch_str, tokens)
                except Exception:
                    continue

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        if best_row and best_score >= threshold:
            p_text, patch_str, tokens = best_row
            return SemanticCacheHit(
                is_hit=True,
                similarity=round(best_score, 4),
                template_patch=json.loads(patch_str),
                original_prompt=p_text,
                tokens_saved=tokens,
                latency_ms=round(latency_ms, 3),
            )

        return SemanticCacheHit(
            is_hit=False,
            similarity=round(best_score, 4),
            template_patch={},
            original_prompt="",
            tokens_saved=0,
            latency_ms=round(latency_ms, 3),
        )

    def store(
        self,
        prompt: str,
        arg1: Any,
        arg2: Any = None,
        tokens_saved: int = 3200,
    ) -> None:
        """
        Stores resolved prompt embedding and verified patch template.
        Supports both signatures:
          store(prompt, prompt_embedding, patch, tokens_saved)
          store(prompt, patch, prompt_embedding, tokens_saved)
        """
        import hashlib
        p_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        now = time.time()

        if isinstance(arg1, list):
            prompt_embedding = arg1
            patch = arg2 if isinstance(arg2, dict) else {}
        else:
            patch = arg1 if isinstance(arg1, dict) else {}
            prompt_embedding = arg2 if isinstance(arg2, list) else None

        emb_data = prompt_embedding or []

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO semantic_prompts
                (prompt_hash, prompt_text, embedding_json, patch_json, tokens_saved, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (p_hash, prompt, json.dumps(emb_data), json.dumps(patch), tokens_saved, now),
            )
