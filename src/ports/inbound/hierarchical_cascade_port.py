"""
Inbound Port: Hierarchical Cascade Interface.
Coordinates 2-level local tiering between micro-models (smollm2:1.7b) and elite builders (qwen2.5-coder:7b).
"""

from typing import Protocol
from src.domain.value_objects import CascadeResult, CascadeMetrics


class IHierarchicalCascade(Protocol):
    """Abstract orchestrator for tiered local execution with silent promotion."""

    def execute_task(
        self,
        task_instruction: str,
        context_code: str = "",
        language: str = "python",
    ) -> CascadeResult:
        """
        Executes code generation or modification through hierarchical cascade.
        Classifies complexity -> routes to 1.7b or 7b -> performs AST validation ->
        silently promotes to 7b if 1.7b produces invalid syntax.
        """
        ...

    def get_metrics(self) -> CascadeMetrics:
        """Returns aggregated telemetry metrics for hierarchical cascade."""
        ...
