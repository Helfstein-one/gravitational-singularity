from typing import Dict, List, Protocol, runtime_checkable

@runtime_checkable
class IAgentGovernor(Protocol):
    """Port for managing agent concurrency and strict VRAM budget on Apple Silicon."""

    def request_model_activation(self, model_name: str, required_vram_gb: float) -> bool:
        """Requests activation of a model under strict VRAM budget limit."""
        ...

    def release_model(self, model_name: str) -> None:
        """Releases or unloads a model to free VRAM."""
        ...

    def get_vram_status(self) -> Dict[str, float]:
        """Returns current VRAM allocations and limits."""
        ...

    def get_active_models(self) -> List[str]:
        """Returns list of currently resident active models."""
        ...
