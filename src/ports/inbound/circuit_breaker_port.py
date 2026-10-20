"""
Inbound Port: Circuit Breaker Interface for System 1 Escalation.
"""

from typing import Protocol
from src.domain.value_objects import EscalationPayload


class ICircuitBreaker(Protocol):
    """Monitors local execution attempts and manages clean handoff to System 2."""

    def record_attempt(self, file_path: str, is_success: bool, error_msg: str = "") -> bool:
        """Records attempt. Returns True if retry is permitted, False if circuit is tripped."""
        ...

    def build_escalation_handoff(self, file_path: str, instruction: str) -> EscalationPayload:
        """Synthesizes a minimal (<100 tokens) surgical handoff payload for System 2."""
        ...

    def reset(self, file_path: str) -> None:
        """Resets circuit state for the target file."""
        ...
