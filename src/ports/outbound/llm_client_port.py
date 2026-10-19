"""
Outbound Port: LLM Client Interface (Ollama local / Cloud API).
"""

from typing import Protocol, Any


class ILLMClient(Protocol):
    """Abstract connection to LLM inference engines."""

    def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        response_format: str | None = None
    ) -> str:
        """Invokes model completion and returns string response."""
        ...

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        """Generates embedding vector for given text."""
        ...

    def list_models(self) -> list[dict[str, Any]]:
        """Lists available models and resource allocations."""
        ...
