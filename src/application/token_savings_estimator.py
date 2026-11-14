from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class TokenSavingsReport:
    raw_tokens_projected: int
    actual_tokens_cloud_sent: int
    tokens_saved_total: int
    reduction_ratio: float
    cost_avoided_usd: float
    cloud_tier_used: str
    events_breakdown: Dict[str, int] = field(default_factory=dict)

class TokenSavingsEstimator:
    """
    Computes real-time empirical token compression and financial savings,
    recommending optimal Gemini API tiers based on prompt complexity.
    """

    PRICE_PER_1M_USD = {
        "gemini-2.0-pro": 1.50,
        "gemini-2.0-flash": 0.10,
        "gemini-2.0-flash-lite": 0.075,
        "tier_0_local": 0.00,
    }

    def __init__(self) -> None:
        self._events: List[Dict[str, int]] = []

    def record_compression_event(
        self,
        mechanism: str,
        raw_tokens: int,
        compressed_tokens: int,
        cloud_tier: str = "gemini-2.0-pro",
    ) -> None:
        saved = max(0, raw_tokens - compressed_tokens)
        self._events.append({
            "mechanism": mechanism,
            "raw": raw_tokens,
            "compressed": compressed_tokens,
            "saved": saved,
            "cloud_tier": cloud_tier,
        })

    def get_summary_report(self) -> TokenSavingsReport:
        if not self._events:
            return TokenSavingsReport(
                raw_tokens_projected=0,
                actual_tokens_cloud_sent=0,
                tokens_saved_total=0,
                reduction_ratio=1.0,
                cost_avoided_usd=0.0,
                cloud_tier_used="tier_0_local",
                events_breakdown={},
            )

        total_raw = sum(e["raw"] for e in self._events)
        total_compressed = sum(e["compressed"] for e in self._events)
        total_saved = sum(e["saved"] for e in self._events)

        breakdown: Dict[str, int] = {}
        for e in self._events:
            m = e["mechanism"]
            breakdown[m] = breakdown.get(m, 0) + e["saved"]

        reduction_ratio = round(total_raw / max(1, total_compressed), 2)
        # Cost avoided calculation based on Gemini 2.0 Pro base price
        cost_avoided = round((total_saved / 1_000_000.0) * self.PRICE_PER_1M_USD["gemini-2.0-pro"], 4)

        return TokenSavingsReport(
            raw_tokens_projected=total_raw,
            actual_tokens_cloud_sent=total_compressed,
            tokens_saved_total=total_saved,
            reduction_ratio=reduction_ratio,
            cost_avoided_usd=cost_avoided,
            cloud_tier_used="hybrid_mesh",
            events_breakdown=breakdown,
        )

    @classmethod
    def recommend_gemini_tier(cls, prompt_length: int, is_architectural: bool = False) -> str:
        """Dynamically picks lowest-cost Gemini tier capable of satisfying the cognitive task."""
        if is_architectural or prompt_length > 30_000:
            return "gemini-2.0-pro"  # Maximum depth & invariants
        if prompt_length > 5_000:
            return "gemini-2.0-flash"  # Standard code-wide search & multi-turn
        return "gemini-2.0-flash-lite"  # Micro-lint, quick checks (-95% cost vs Pro)
