"""
Inbound Port: Guardrail Service Interface for pre-execution interception.
"""

from typing import Protocol, Any
from src.domain.value_objects import SyntaxValidationResult


class IGuardrailService(Protocol):
    """Handles pre-tool validation and command truncation."""

    def evaluate_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluates a tool invocation before execution.
        Returns a gatekeeper response, e.g.:
        {"decision": "allow"} or {"decision": "deny", "explanation": "..."}
        """
        ...

    def validate_patch_in_memory(self, file_path: str, new_content: str) -> SyntaxValidationResult:
        """Validates simulated code content without disk writes."""
        ...
