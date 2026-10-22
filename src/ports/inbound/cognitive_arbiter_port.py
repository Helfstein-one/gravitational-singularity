"""
Inbound Port: Cognitive Arbiter Interface (System 1 vs System 2 Dispatcher).
"""

from typing import Protocol
from src.domain.value_objects import TaskClassification, TokenBudgetEnvelope


class ICognitiveArbiter(Protocol):
    """Classifies prompts and file scopes into System 1 (Fast/Local) or System 2 (Slow/Cloud)."""

    def classify_task(
        self,
        prompt: str,
        affected_files: list[str] | None = None,
        code_snippet: str | None = None
    ) -> TaskClassification:
        """Classifies task intent in <2ms with zero cloud token cost, optionally evaluating cyclomatic complexity."""
        ...

    def calculate_budget(self, classification: TaskClassification) -> TokenBudgetEnvelope:
        """Determines the phase-based token budget envelope for the task."""
        ...
