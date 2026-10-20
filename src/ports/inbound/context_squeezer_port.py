"""
Inbound Port: Epistemic Context Squeezer Interface.
Defines contracts for non-destructive in-memory context compaction.
"""

from typing import List, Protocol
from src.domain.value_objects import (
    ContextSqueezePolicy,
    SqueezedContext,
    SqueezeMetrics,
)


class IContextSqueezer(Protocol):
    """Abstract orchestrator for virtual 3-level context compression."""

    def squeeze_transcript(
        self,
        raw_steps: List[dict],
        policy: ContextSqueezePolicy | None = None,
    ) -> SqueezedContext:
        """
        Compresses raw transcript steps into a pruned, token-bounded projection.
        Guarantees that raw_steps is not modified in-place.
        """
        ...

    def get_metrics(self) -> SqueezeMetrics:
        """Returns aggregated telemetry metrics for context pruning."""
        ...
