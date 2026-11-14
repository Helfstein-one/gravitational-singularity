import re
from src.ports.inbound.hybrid_routing_port import ExecutionTier, IHybridRoutingEngine, RoutingDecision

class HybridRoutingEngine(IHybridRoutingEngine):
    """
    Evaluates task entropy and complexity to decide whether to resolve locally
    at Tier 0 ($0 cloud cost) or escalate to Gemini Cloud Tiers.
    """

    DETERMINISTIC_PATTERNS = [
        r"^(format|organize imports|sort imports|rename symbol|add docstring)",
        r"^(fix lint|fix syntax|remove unused import)",
    ]

    ARCHITECTURAL_KEYWORDS = [
        "architecture", "refactor whole system", "cross-module",
        "redesign", "security audit", "protocol design", "database migration",
    ]

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
                )

        # 2. Strategic / Architectural High-Cognition Check
        for kw in self.ARCHITECTURAL_KEYWORDS:
            if kw in clean_prompt:
                return RoutingDecision(
                    tier=ExecutionTier.TIER_3_CLOUD_PRO,
                    confidence=0.92,
                    reason="High architectural complexity requiring frontier reasoning",
                    target_model="gemini-2.0-pro",
                    estimated_tokens_saved=0,
                )

        # 3. Complexity calculation on context
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
            )

        if context_lines <= 800:
            return RoutingDecision(
                tier=ExecutionTier.TIER_1_CLOUD_FLASH_LITE,
                confidence=0.85,
                reason="Moderate context size suitable for ultra-fast low-cost Flash-Lite",
                target_model="gemini-2.0-flash-lite",
                estimated_tokens_saved=500,
            )

        return RoutingDecision(
            tier=ExecutionTier.TIER_2_CLOUD_FLASH,
            confidence=0.82,
            reason="Broad context requiring large context window",
            target_model="gemini-2.0-flash",
            estimated_tokens_saved=300,
        )
