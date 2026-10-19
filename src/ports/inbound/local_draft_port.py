"""
Inbound Port: Local-First Speculative Draft Interface (Qwen 7B + AST self-refine).
"""

from typing import Protocol, Any


class ILocalDraftService(Protocol):
    """Generates local-first zero-cloud patches with self-healing retry."""

    def draft_and_apply_patch(
        self,
        file_path: str,
        instruction: str,
        target_lines: str | None = None
    ) -> dict[str, Any]:
        """
        Generates local diff, validates in-memory AST.
        Returns execution report with cost $0.00 or escalate_to_cloud signal.
        """
        ...
