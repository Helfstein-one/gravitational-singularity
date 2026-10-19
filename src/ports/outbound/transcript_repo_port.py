"""
Outbound Port: Transcript Log Repository Interface.
"""

from typing import Protocol, Iterator, Any


class ITranscriptRepository(Protocol):
    """Abstract interface to read Antigravity execution transcripts."""

    def get_latest_session_id(self) -> str:
        """Returns the ID of the current active session."""
        ...

    def iter_session_records(self, session_id: str | None = None) -> Iterator[dict[str, Any]]:
        """Streams JSON step records from transcript logs."""
        ...

    def get_all_transcript_paths(self) -> list[str]:
        """Returns all discovered transcript.jsonl file paths."""
        ...
