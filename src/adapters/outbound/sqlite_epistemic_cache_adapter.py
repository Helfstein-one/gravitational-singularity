"""
Outbound Adapter: Dual-Tier (L1 RAM LRU + L2 SQLite WAL) Epistemic Cache.
Provides sub-millisecond memoization of AST skeletons, analysis, and execution artifacts.
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import collections
import os
import sqlite3
import time
from typing import Optional

from src.domain.value_objects import CacheKey, CacheEntry, CacheMetrics
from src.ports.outbound.epistemic_cache_port import IEpistemicCache


class SqliteEpistemicCacheAdapter(IEpistemicCache):
    """
    Hybrid Epistemic Cache implementation:
    - Tier 1 (L1): In-memory OrderedDict (LRU) for <0.05ms resolution.
    - Tier 2 (L2): SQLite DB in WAL mode for persistent storage across restarts.
    """

    def __init__(
        self,
        db_path: str | None = None,
        l1_max_size: int = 500,
    ) -> None:
        self.db_path = db_path or os.path.expanduser("~/.gemini/config/cache/epistemic.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.l1_max_size = l1_max_size
        self._l1_cache: collections.OrderedDict[str, CacheEntry] = collections.OrderedDict()

        self._l1_hits: int = 0
        self._l2_hits: int = 0
        self._misses: int = 0
        self._total_tokens_saved: int = 0
        self._total_latency_saved_ms: float = 0.0

        self._init_sqlite()

    def _init_sqlite(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS epistemic_cache (
                    composite_digest TEXT PRIMARY KEY,
                    content_sha256 TEXT NOT NULL,
                    prompt_hash TEXT NOT NULL,
                    tool_spec TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    tokens_saved INTEGER NOT NULL,
                    computation_latency_ms REAL NOT NULL,
                    created_at_epoch REAL NOT NULL
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_content_sha256 ON epistemic_cache (content_sha256);"
            )

    def get(self, key: CacheKey) -> Optional[CacheEntry]:
        digest = key.composite_digest

        # 1. Check Tier 1 (L1 RAM LRU)
        if digest in self._l1_cache:
            entry = self._l1_cache[digest]
            self._l1_cache.move_to_end(digest)
            self._l1_hits += 1
            self._total_tokens_saved += entry.tokens_saved
            self._total_latency_saved_ms += entry.computation_latency_ms
            return entry

        # 2. Check Tier 2 (L2 SQLite WAL)
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT payload, tokens_saved, computation_latency_ms, created_at_epoch
                FROM epistemic_cache
                WHERE composite_digest = ?;
                """,
                (digest,),
            )
            row = cur.fetchone()

        if row:
            entry = CacheEntry(
                key=digest,
                payload=row[0],
                tokens_saved=row[1],
                computation_latency_ms=row[2],
                created_at_epoch=row[3],
            )
            # Promote to L1
            self._put_l1(digest, entry)
            self._l2_hits += 1
            self._total_tokens_saved += entry.tokens_saved
            self._total_latency_saved_ms += entry.computation_latency_ms
            return entry

        # Cache Miss
        self._misses += 1
        return None

    def put(
        self,
        key: CacheKey,
        payload: str,
        tokens_saved: int,
        computation_latency_ms: float,
    ) -> CacheEntry:
        digest = key.composite_digest
        now = time.time()
        entry = CacheEntry(
            key=digest,
            payload=payload,
            tokens_saved=tokens_saved,
            computation_latency_ms=computation_latency_ms,
            created_at_epoch=now,
        )

        # Store in L1
        self._put_l1(digest, entry)

        # Store in L2 (SQLite)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO epistemic_cache (
                    composite_digest, content_sha256, prompt_hash, tool_spec,
                    payload, tokens_saved, computation_latency_ms, created_at_epoch
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    digest,
                    key.content_sha256,
                    key.prompt_hash,
                    key.tool_spec,
                    payload,
                    tokens_saved,
                    computation_latency_ms,
                    now,
                ),
            )

        return entry

    def _put_l1(self, digest: str, entry: CacheEntry) -> None:
        if digest in self._l1_cache:
            self._l1_cache.move_to_end(digest)
        self._l1_cache[digest] = entry
        if len(self._l1_cache) > self.l1_max_size:
            self._l1_cache.popitem(last=False)

    def invalidate(self, content_sha256: str) -> int:
        # 1. Invalidate L1 keys matching content_sha256
        # Need to query L2 or purge all from L1 matching
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT composite_digest FROM epistemic_cache WHERE content_sha256 = ?;",
                (content_sha256,),
            )
            digests_to_remove = [row[0] for row in cur.fetchall()]

            for d in digests_to_remove:
                self._l1_cache.pop(d, None)

            cur.execute(
                "DELETE FROM epistemic_cache WHERE content_sha256 = ?;",
                (content_sha256,),
            )
            deleted_count = cur.rowcount

        return deleted_count

    def get_metrics(self) -> CacheMetrics:
        return CacheMetrics(
            l1_hits=self._l1_hits,
            l2_hits=self._l2_hits,
            misses=self._misses,
            total_tokens_saved=self._total_tokens_saved,
            total_latency_saved_ms=round(self._total_latency_saved_ms, 2),
        )

    def clear(self) -> None:
        self._l1_cache.clear()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM epistemic_cache;")
