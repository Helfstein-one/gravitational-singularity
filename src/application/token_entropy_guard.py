"""
Application Use Case: Token Entropy & Uncertainty Early Exit Guard.
Monitors token logprobs / entropy of early output tokens.
If perplexity exceeds threshold H > 2.8, aborts local generation early (e.g. at token 15)
and escalates immediately to Cloud Gemini Pro, preventing wasted compute on hallucinations.
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class EntropyCheckResult:
    should_early_exit: bool
    mean_entropy: float
    tokens_evaluated: int
    escalate_to_cloud: bool
    reason: str


class TokenEntropyGuard:
    """
    Evaluates early token predictability to trigger immediate silent escalation.
    """

    def __init__(self, entropy_threshold: float = 2.8, min_tokens_for_decision: int = 10) -> None:
        self.entropy_threshold = entropy_threshold
        self.min_tokens = min_tokens_for_decision

    def calculate_token_entropy(self, logprobs: List[float]) -> float:
        """
        Calculates mean negative log likelihood (NLL / perplexity proxy) from token logprobs:
        mean_nll = - sum(logprobs) / N
        """
        if not logprobs:
            return 0.0
        return -sum(logprobs) / len(logprobs)

    def evaluate_stream(self, early_logprobs: List[float]) -> EntropyCheckResult:
        """
        Evaluates early token probabilities to determine whether to abort inference.
        """
        count = len(early_logprobs)
        if count < self.min_tokens:
            return EntropyCheckResult(
                should_early_exit=False,
                mean_entropy=0.0,
                tokens_evaluated=count,
                escalate_to_cloud=False,
                reason="Collecting early tokens.",
            )

        mean_h = self.calculate_token_entropy(early_logprobs[:self.min_tokens])

        if mean_h > self.entropy_threshold:
            return EntropyCheckResult(
                should_early_exit=True,
                mean_entropy=round(mean_h, 3),
                tokens_evaluated=count,
                escalate_to_cloud=True,
                reason=f"High token entropy ({mean_h:.2f} > {self.entropy_threshold}); high model uncertainty detected. Aborting early.",
            )

        return EntropyCheckResult(
            should_early_exit=False,
            mean_entropy=round(mean_h, 3),
            tokens_evaluated=count,
            escalate_to_cloud=False,
            reason="Token entropy within confidence bounds.",
        )
