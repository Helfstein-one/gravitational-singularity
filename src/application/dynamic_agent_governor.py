import time
from typing import Dict, List, Optional
from src.ports.inbound.agent_governor_port import IAgentGovernor

class DynamicAgentGovernor(IAgentGovernor):
    """
    Governs agent concurrency and ensures local model co-residence respects
    a strict VRAM budget (8.5 GB max for 16 GB Apple Silicon Mac).
    """

    DEFAULT_MODEL_WEIGHTS_GB = {
        "smollm2:1.7b": 1.0,
        "deepseek-r1:1.5b": 1.1,
        "qwen2.5-coder:3b": 1.9,
        "hermes3:3b": 2.0,
        "qwen2.5-coder:7b": 4.5,
        "nomic-embed-text": 0.35,
    }

    def __init__(self, vram_budget_cap_gb: float = 8.5) -> None:
        self.vram_budget_cap_gb = vram_budget_cap_gb
        self._active_models: Dict[str, float] = {}  # model_name -> allocated_gb
        self._last_accessed: Dict[str, float] = {}

    @property
    def current_vram_allocated_gb(self) -> float:
        return round(sum(self._active_models.values()), 2)

    def request_model_activation(self, model_name: str, required_vram_gb: Optional[float] = None) -> bool:
        vram_needed = required_vram_gb if required_vram_gb is not None else self.DEFAULT_MODEL_WEIGHTS_GB.get(model_name, 2.0)

        if model_name in self._active_models:
            self._last_accessed[model_name] = time.time()
            return True

        # Evict least recently accessed models if budget exceeded
        while self.current_vram_allocated_gb + vram_needed > self.vram_budget_cap_gb and self._active_models:
            lru_model = min(self._last_accessed, key=self._last_accessed.get)
            self.release_model(lru_model)

        if self.current_vram_allocated_gb + vram_needed <= self.vram_budget_cap_gb:
            self._active_models[model_name] = vram_needed
            self._last_accessed[model_name] = time.time()
            return True

        return False

    def release_model(self, model_name: str) -> None:
        self._active_models.pop(model_name, None)
        self._last_accessed.pop(model_name, None)

    def get_vram_status(self) -> Dict[str, float]:
        return {
            "vram_budget_cap_gb": self.vram_budget_cap_gb,
            "vram_allocated_gb": self.current_vram_allocated_gb,
            "vram_free_gb": round(self.vram_budget_cap_gb - self.current_vram_allocated_gb, 2),
            "utilization_pct": round((self.current_vram_allocated_gb / self.vram_budget_cap_gb) * 100, 1),
        }

    def get_active_models(self) -> List[str]:
        return list(self._active_models.keys())
