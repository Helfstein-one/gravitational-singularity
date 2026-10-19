"""
Inbound Port: Telemetry and Efficiency Service Interface.
"""

from typing import Protocol
from src.domain.entities import TelemetrySnapshot


class ITelemetryService(Protocol):
    """Scans execution history and produces real-time 360 telemetry."""

    def collect_snapshot(self, session_filter: str | None = None) -> TelemetrySnapshot:
        """Collects token metrics, savings, and storytelling analogies."""
        ...
