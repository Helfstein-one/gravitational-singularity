import os
import re
from src.ports.inbound.hybrid_routing_port import ExecutionTier, IHybridRoutingEngine, RoutingDecision

class HybridRoutingEngine(IHybridRoutingEngine):
    """
    Evaluates task entropy and complexity to decide whether to resolve locally
    at Tier 0 ($0 cloud cost) or escalate to Gemini Cloud Tiers (Flash-Lite, Flash,
    Flash Thinking, Pro).
    """

    DETERMINISTIC_PATTERNS = [
        r"^(format|organize imports|sort imports|rename symbol|add docstring)",
        r"^(fix lint|fix syntax|remove unused import)",
    ]

    THINKING_KEYWORDS = [
        "debug concurrency", "prove invariant", "algorithmic proof",
        "complex race condition", "formal logic", "memory leak", "deadlock analysis",
    ]

    ARCHITECTURAL_KEYWORDS = [
        "architecture", "refactor whole system", "cross-module",
        "redesign", "security audit", "protocol design", "database migration",
    ]

    def __init__(self):
        # Configurable model mapping supporting newest Google SaaS Gemini versions (2.0 / 2.5)
        self.model_pro = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")
        self.model_flash_thinking = os.getenv("GEMINI_FLASH_THINKING_MODEL", "gemini-2.0-flash-thinking-exp")
        self.model_flash = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")
        self.model_flash_lite = os.getenv("GEMINI_FLASH_LITE_MODEL", "gemini-2.0-flash-lite")

    def route_task(self, prompt: str, code_context: str = "") -> RoutingDecision:
        clean_prompt = prompt.strip().lower()

        # 1. Deterministic System 0 bypass
        for pattern in self.DETERMINISTIC_PATTERNS:
            if re.search(pattern, clean_prompt):
                return RoutingDecision(
                    tier=ExecutionTier.TIER_0_LOCAL_DETERMINISTIC,
                    confidence=0.98,
                    reason="Deterministic task resolvable via AST / libcst in RAM",
                    target_model="ast.NodeTransformer",
                    estimated_tokens_saved=2500,
                    thinking_budget=0,
                    supports_context_caching=False,
                )

        # 2. Strategic / Architectural High-Cognition Check
        for kw in self.ARCHITECTURAL_KEYWORDS:
            if kw in clean_prompt:
                return RoutingDecision(
                    tier=ExecutionTier.TIER_3_CLOUD_PRO,
                    confidence=0.92,
                    reason="High architectural complexity requiring frontier reasoning",
                    target_model=self.model_pro,
                    estimated_tokens_saved=0,
                    thinking_budget=4096,
                    supports_context_caching=True,
                )

        # 3. Deep Algorithmic Reasoning / Thinking Check (Flash Thinking Tier)
        for kw in self.THINKING_KEYWORDS:
            if kw in clean_prompt:
                return RoutingDecision(
                    tier=ExecutionTier.TIER_2_5_CLOUD_FLASH_THINKING,
                    confidence=0.90,
                    reason="Deep algorithmic reasoning requiring CoT thinking tokens without Pro price",
                    target_model=self.model_flash_thinking,
                    estimated_tokens_saved=1200,
                    thinking_budget=2048,
                    supports_context_caching=True,
                )

        # 4. Complexity calculation on context
        context_lines = len(code_context.splitlines()) if code_context else 0
        cyclomatic_signals = sum(code_context.count(k) for k in ["if ", "for ", "while ", "def ", "class ", "try:"])

        # Local Small Language Model routing
        if context_lines <= 250 and cyclomatic_signals < 15:
            return RoutingDecision(
                tier=ExecutionTier.TIER_0_LOCAL_SLM,
                confidence=0.88,
                reason="Bounded single-file modification well suited for local 7B SLM",
                target_model="qwen2.5-coder:7b",
                estimated_tokens_saved=min(1800 + context_lines * 4, 8000),
                thinking_budget=0,
                supports_context_caching=False,
            )

        if context_lines <= 800:
            return RoutingDecision(
                tier=ExecutionTier.TIER_1_CLOUD_FLASH_LITE,
                confidence=0.85,
                reason="Moderate context size suitable for ultra-fast low-cost Flash-Lite",
                target_model=self.model_flash_lite,
                estimated_tokens_saved=500,
                thinking_budget=0,
                supports_context_caching=False,
            )

        return RoutingDecision(
            tier=ExecutionTier.TIER_2_CLOUD_FLASH,
            confidence=0.82,
            reason="Broad context requiring large context window",
            target_model=self.model_flash,
            estimated_tokens_saved=300,
            thinking_budget=0,
            supports_context_caching=context_lines > 500,
        )
