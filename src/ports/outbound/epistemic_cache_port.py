"""
Outbound Port: Epistemic Cache Interface for deterministic memoization.
"""

from typing import Optional, Protocol
from src.domain.value_objects import CacheKey, CacheEntry, CacheMetrics


class IEpistemicCache(Protocol):
    """Abstract cache port for deterministic epistemic memoization (L1/L2)."""

    def get(self, key: CacheKey) -> Optional[CacheEntry]:
        """Retrieves memoized entry by composite triple key, checking L1 then L2."""
        ...

    def put(
        self,
        key: CacheKey,
        payload: str,
        tokens_saved: int,
        computation_latency_ms: float,
    ) -> CacheEntry:
        """Stores memoized entry in L1 RAM and L2 persistent store."""
        ...

    def invalidate(self, content_sha256: str) -> int:
        """Invalidates all entries matching content_sha256."""
        ...

    def get_metrics(self) -> CacheMetrics:
        """Returns aggregated telemetry metrics."""
        ...

    def clear(self) -> None:
        """Clears L1 and L2 cache completely."""
        ...
