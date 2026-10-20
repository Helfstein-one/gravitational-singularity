"""
Inbound Port: Predictive AST Pre-Warmer Interface.
Defines contracts for background file system monitoring and proactive cache warming.
"""

from typing import List, Protocol
from src.domain.value_objects import PreWarmMetrics


class IPreWarmer(Protocol):
    """Abstract orchestrator for proactive AST cache pre-warming."""

    def start(self, watch_dirs: List[str] | None = None) -> None:
        """Starts background file watcher and pre-warming thread."""
        ...

    def stop(self) -> None:
        """Stops background file watcher and pre-warming thread."""
        ...

    def prewarm_file(self, file_path: str) -> bool:
        """Synchronously prewarms a single file into Epistemic Cache."""
        ...

    def get_metrics(self) -> PreWarmMetrics:
        """Returns real-time telemetry metrics of pre-warmed files."""
        ...
