"""
Application Use Case: Epistemic Memoizer.
Decorator / Orchestrator for deterministic sub-millisecond memoization (L1 RAM + L2 SQLite).
Eliminates duplicate inference, skeletonization, and AST parsing with 0ms and $0.00 cloud cost.
"""

from __future__ import annotations
import hashlib
import json
import time
from typing import Callable, Optional, Tuple

from src.domain.value_objects import CacheKey, CacheMetrics
from src.ports.inbound.epistemic_memoizer_port import IEpistemicMemoizer
from src.ports.outbound.epistemic_cache_port import IEpistemicCache
from src.application.code_skeletonizer import CodeSkeletonizer


class EpistemicMemoizer(IEpistemicMemoizer):
    """
    Coordinates L1 RAM and L2 SQLite caching for zero-waste agentic operations.
    """

    def __init__(
        self,
        cache: IEpistemicCache,
        skeletonizer: Optional[CodeSkeletonizer] = None,
    ) -> None:
        self.cache = cache
        self.skeletonizer = skeletonizer

    def memoized_skeletonize(
        self,
        raw_code: str,
        language: str = "python",
    ) -> Tuple[str, float, bool]:
        """
        Compresses code with transparent L1/L2 memoization.
        Returns: (compressed_code, reduction_pct, from_cache_flag)
        """
        content_sha256 = hashlib.sha256(raw_code.encode("utf-8")).hexdigest()
        key = CacheKey(
            content_sha256=content_sha256,
            prompt_hash="ast_skeletonize",
            tool_spec=f"ast_parser:{language}",
        )

        cached_entry = self.cache.get(key)
        if cached_entry:
            data = json.loads(cached_entry.payload)
            return data["compressed"], data["reduction"], True

        if not self.skeletonizer:
            raise RuntimeError("CodeSkeletonizer must be provided to compute unmemoized skeleton.")

        t0 = time.perf_counter()
        compressed, reduction = self.skeletonizer.skeletonize(raw_code, language)
        duration_ms = (time.perf_counter() - t0) * 1000.0

        # Calculate tokens saved
        orig_tokens = len(raw_code.split())
        comp_tokens = len(compressed.split())
        tokens_saved = max(0, orig_tokens - comp_tokens)

        payload = json.dumps({"compressed": compressed, "reduction": reduction})
        self.cache.put(
            key=key,
            payload=payload,
            tokens_saved=tokens_saved,
            computation_latency_ms=duration_ms,
        )

        return compressed, reduction, False

    def memoized_call(
        self,
        content: str,
        query: str,
        tool_spec: str,
        computation: Callable[[], Tuple[str, int]],
    ) -> Tuple[str, bool]:
        """
        Executes arbitrary deterministic computation if not cached.
        computation callback must return (payload_str, tokens_saved).
        Returns: (payload, from_cache_flag)
        """
        content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        prompt_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()
        key = CacheKey(
            content_sha256=content_sha256,
            prompt_hash=prompt_hash,
            tool_spec=tool_spec,
        )

        cached_entry = self.cache.get(key)
        if cached_entry:
            return cached_entry.payload, True

        t0 = time.perf_counter()
        result_payload, tokens_saved = computation()
        duration_ms = (time.perf_counter() - t0) * 1000.0

        self.cache.put(
            key=key,
            payload=result_payload,
            tokens_saved=tokens_saved,
            computation_latency_ms=duration_ms,
        )
        return result_payload, False

    def get_metrics(self) -> CacheMetrics:
        return self.cache.get_metrics()
