"""
Inbound Port: Inference Optimizer.
Defines contracts for VRAM co-residence orchestration (elimination of cold-swaps)
and KV-cache preservation (elimination of redundant prefill) in local LLM inference.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from src.domain.value_objects import VramCoResidenceState, InferenceOptimizationMetrics


class IInferenceOptimizer(ABC):
    """Port for optimizing local Ollama inference requests via VRAM co-residence and num_keep."""

    @abstractmethod
    def build_request_options(
        self, model_name: str, system_prompt: str, base_options: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Injects calibrated num_keep (exact token count of system_prompt)
        and keep_alive: -1 to eliminate prefill latency and model unload.
        """
        raise NotImplementedError

    @abstractmethod
    def inspect_vram(self) -> VramCoResidenceState:
        """Inspects active models and unified memory footprint via Ollama /api/ps."""
        raise NotImplementedError

    @abstractmethod
    def warmup_core_models(self) -> Dict[str, bool]:
        """Triggers warm-up inference for smollm2:1.7b, deepseek-r1:1.5b, and qwen2.5-coder:7b."""
        raise NotImplementedError

    @abstractmethod
    def get_metrics(self) -> InferenceOptimizationMetrics:
        """Returns runtime telemetry for cold swaps prevented and prefill tokens reused."""
        raise NotImplementedError
