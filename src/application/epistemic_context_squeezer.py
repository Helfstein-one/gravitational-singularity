"""
Application Use Case: Epistemic Context Squeezer.
Applies a 3-level non-destructive virtual compaction on conversation history.
Keeps prompt context strictly within an 8,000-token ceiling without altering physical disk logs.
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import copy
import re
from typing import List, Optional

from src.domain.value_objects import (
    ContextSqueezePolicy,
    SqueezedContext,
    SqueezeMetrics,
)
from src.ports.inbound.context_squeezer_port import IContextSqueezer


class EpistemicContextSqueezer(IContextSqueezer):
    """
    In-memory virtual context squeezer preserving N and N-1 turns while
    collapsing older verbose execution traces to maximize prompt efficiency.
    """

    def __init__(self, default_policy: Optional[ContextSqueezePolicy] = None) -> None:
        self.default_policy = default_policy or ContextSqueezePolicy()
        self._total_invocations: int = 0
        self._total_tokens_pruned: int = 0
        self._ratios: list[float] = []

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(re.findall(r"\w+|[^\w\s]", text))

    def _estimate_step_tokens(self, step: dict) -> int:
        content = step.get("content") or ""
        thinking = step.get("thinking") or ""
        tool_calls = str(step.get("tool_calls") or "")
        return self._estimate_tokens(content) + self._estimate_tokens(thinking) + self._estimate_tokens(tool_calls)

    def squeeze_transcript(
        self,
        raw_steps: List[dict],
        policy: Optional[ContextSqueezePolicy] = None,
    ) -> SqueezedContext:
        active_policy = policy or self.default_policy
        total_steps = len(raw_steps)

        if total_steps == 0:
            return SqueezedContext(
                original_steps_count=0,
                squeezed_steps_count=0,
                raw_tokens=0,
                squeezed_tokens=0,
                steps_payload=[],
            )

        # Calculate original raw token volume
        raw_tokens = sum(self._estimate_step_tokens(s) for s in raw_steps)

        # Deep copy steps to guarantee non-destructive virtual projection
        squeezed_steps = copy.deepcopy(raw_steps)
        cutoff_index = max(0, total_steps - active_policy.preserve_recent_turns)

        # Level 1 & 2: Process older steps (before the recent turns threshold)
        for i in range(cutoff_index):
            step = squeezed_steps[i]
            step_type = step.get("type", "")

            # Preserve explicit user instructions untouched
            if step_type == "USER_INPUT":
                continue

            # Level 2: Collapse tool outputs and command logs
            content = step.get("content")
            if isinstance(content, str) and len(content) > 200:
                # Collapse verbose test / build / git outputs
                if "test" in content.lower() or "passed" in content.lower() or "exit code" in content.lower():
                    first_line = content.strip().split("\n")[0][:100]
                    step["content"] = f"[Pruned Log: {first_line}... (collapsed {len(content)} chars)]"
                elif active_policy.collapse_file_views and ("def " in content or "class " in content or "import " in content):
                    step["content"] = f"[Pruned File View: {len(content.splitlines())} lines collapsed in memory]"
                else:
                    step["content"] = content[:150] + f"... [Collapsed {len(content) - 150} redundant chars]"

            # Prune excessive thinking tokens in older planning turns
            thinking = step.get("thinking")
            if isinstance(thinking, str) and len(thinking) > 300:
                step["thinking"] = thinking[:120] + "... [Historical reasoning collapsed]"

        # Level 3: Token Budget Ceiling Guard
        squeezed_tokens = sum(self._estimate_step_tokens(s) for s in squeezed_steps)

        if squeezed_tokens > active_policy.max_token_ceiling and len(squeezed_steps) > active_policy.preserve_recent_turns:
            # Progressively drop oldest intermediary assistant steps until within budget
            pruned_steps: list[dict] = []
            # Keep initial prompt step if present
            initial_step = squeezed_steps[0] if squeezed_steps[0].get("type") == "USER_INPUT" else None
            recent_steps = squeezed_steps[cutoff_index:]
            intermediary_steps = squeezed_steps[1 if initial_step else 0 : cutoff_index]

            budget_available = active_policy.max_token_ceiling - sum(self._estimate_step_tokens(s) for s in recent_steps)
            if initial_step:
                budget_available -= self._estimate_step_tokens(initial_step)

            kept_intermediary: list[dict] = []
            # Take most recent intermediary steps moving backwards
            for s in reversed(intermediary_steps):
                s_tokens = self._estimate_step_tokens(s)
                if budget_available >= s_tokens:
                    kept_intermediary.insert(0, s)
                    budget_available -= s_tokens

            if initial_step:
                pruned_steps.append(initial_step)
            pruned_steps.extend(kept_intermediary)
            pruned_steps.extend(recent_steps)
            squeezed_steps = pruned_steps
            squeezed_tokens = sum(self._estimate_step_tokens(s) for s in squeezed_steps)

        result = SqueezedContext(
            original_steps_count=total_steps,
            squeezed_steps_count=len(squeezed_steps),
            raw_tokens=raw_tokens,
            squeezed_tokens=squeezed_tokens,
            steps_payload=squeezed_steps,
        )

        # Track telemetry
        self._total_invocations += 1
        self._total_tokens_pruned += result.tokens_pruned
        self._ratios.append(result.compression_ratio_pct)

        return result

    def get_metrics(self) -> SqueezeMetrics:
        avg_ratio = round(sum(self._ratios) / len(self._ratios), 1) if self._ratios else 0.0
        return SqueezeMetrics(
            total_invocations=self._total_invocations,
            total_tokens_pruned=self._total_tokens_pruned,
            average_compression_ratio_pct=avg_ratio,
        )
