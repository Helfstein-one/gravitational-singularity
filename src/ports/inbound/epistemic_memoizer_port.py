"""
Inbound Port: Epistemic Memoizer Interface.
Coordinates deterministic memoization across application use cases.
"""

from typing import Callable, Protocol, Tuple
from src.domain.value_objects import CacheMetrics


class IEpistemicMemoizer(Protocol):
    """Abstract orchestrator for memoized execution with zero-redundancy guarantee."""

    def memoized_skeletonize(
        self,
        raw_code: str,
        language: str = "python",
    ) -> Tuple[str, float, bool]:
        """
        Compresses code with transparent L1/L2 memoization.
        Returns: (compressed_code, reduction_pct, from_cache_flag)
        """
        ...

    def memoized_call(
        self,
        content: str,
        query: str,
        tool_spec: str,
        computation: Callable[[], Tuple[str, int]],
    ) -> Tuple[str, bool]:
        """
        Executes arbitrary deterministic computation if not cached.
        computation returns (payload, tokens_saved).
        Returns: (payload, from_cache_flag)
        """
        ...

    def get_metrics(self) -> CacheMetrics:
        """Returns current cache telemetry metrics."""
        ...
