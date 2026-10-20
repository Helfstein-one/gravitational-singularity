"""
Inbound Port: Local Adversarial Reflector Interface.
Coordinates Builder vs Skeptic reflection cycles in local RAM with zero cloud cost.
"""

from typing import Protocol
from src.domain.value_objects import ReflectionResult, AdversarialMetrics


class IAdversarialReflector(Protocol):
    """Abstract orchestrator for 1-shot Builder vs Skeptic local reflection."""

    def reflect_and_refine(
        self,
        task_instruction: str,
        initial_code: str,
        language: str = "python",
    ) -> ReflectionResult:
        """
        Executes a 1-shot adversarial reflection cycle.
        1. Skeptic audits initial_code.
        2. If flaws found, Builder refines with the critique.
        3. Validates syntax in memory.
        """
        ...

    def get_metrics(self) -> AdversarialMetrics:
        """Returns aggregated telemetry metrics for adversarial reflections."""
        ...
