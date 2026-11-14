from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

class ExecutionTier(str, Enum):
    TIER_0_LOCAL_DETERMINISTIC = "tier_0_local_deterministic"
    TIER_0_LOCAL_SLM = "tier_0_local_slm"
    TIER_1_CLOUD_FLASH_LITE = "tier_1_cloud_flash_lite"
    TIER_2_CLOUD_FLASH = "tier_2_cloud_flash"
    TIER_3_CLOUD_PRO = "tier_3_cloud_pro"

@dataclass(frozen=True)
class RoutingDecision:
    tier: ExecutionTier
    confidence: float
    reason: str
    target_model: str
    estimated_tokens_saved: int

@runtime_checkable
class IHybridRoutingEngine(Protocol):
    """Port for confidence-based hybrid routing between local edge and SaaS cloud."""

    def route_task(self, prompt: str, code_context: str = "") -> RoutingDecision:
        """Evaluates complexity and routes task to optimal tier."""
        ...
