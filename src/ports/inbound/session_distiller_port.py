"""
Inbound Port: Session Distiller Service Interface.
"""

from typing import Protocol
from src.domain.entities import SessionState


class ISessionDistillerService(Protocol):
    """Distills long conversational histories into concise epistemic state files."""

    def distill_transcript(self, transcript_path: str, session_id: str) -> SessionState:
        """Parses transcript log and distills facts, decisions and next steps."""
        ...
