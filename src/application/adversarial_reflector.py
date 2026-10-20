"""
Application Use Case: Local Adversarial Reflector.
Orchestrates a 1-shot reflection cycle between Builder (qwen2.5-coder:7b) and
Skeptic (deepseek-r1:1.5b) in RAM with $0.00 cloud cost and sub-3-second latency.
Follows Single Responsibility (SRP) and Dependency Inversion (DIP).
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import json
import re
import time
from typing import Optional

from src.domain.value_objects import (
    ReflectionCritique,
    ReflectionResult,
    AdversarialMetrics,
)
from src.ports.inbound.adversarial_reflector_port import IAdversarialReflector
from src.ports.outbound.llm_client_port import ILLMClient
from src.ports.outbound.ast_parser_port import IAstParser


class AdversarialReflector(IAdversarialReflector):
    """
    Coordinates double-check adversarial audits between local Ollama models.
    """

    def __init__(
        self,
        llm_client: ILLMClient,
        ast_parser: IAstParser,
        builder_model: str = "qwen2.5-coder:7b",
        skeptic_model: str = "deepseek-r1:1.5b",
    ) -> None:
        self.llm_client = llm_client
        self.ast_parser = ast_parser
        self.builder_model = builder_model
        self.skeptic_model = skeptic_model

        self._total_reflection_cycles: int = 0
        self._skeptic_flaws_intercepted: int = 0
        self._successful_self_refinements: int = 0
        self._zero_cloud_cost_saved_usd: float = 0.0

    def _parse_critique_json(self, raw_resp: str) -> ReflectionCritique:
        # Strip potential markdown code blocks or reasoning traces
        clean = re.sub(r"<think>.*?</think>", "", raw_resp, flags=re.DOTALL).strip()
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return ReflectionCritique(
                    has_flaws=bool(data.get("has_flaws", False)),
                    flaw_category=str(data.get("flaw_category", "none")),
                    critique_details=str(data.get("critique", data.get("critique_details", ""))),
                    confidence_score=float(data.get("confidence_score", 1.0)),
                )
            except Exception:
                pass

        # Fallback heuristic if not strictly JSON formatted
        has_flaws = any(
            w in raw_resp.lower()
            for w in ["bug", "flaw", "vulnerability", "infinite loop", "error", "missing", "fails"]
        )
        return ReflectionCritique(
            has_flaws=has_flaws,
            flaw_category="heuristic_audit" if has_flaws else "clean",
            critique_details=clean[:300],
            confidence_score=0.85,
        )

    def _extract_code_block(self, text: str, language: str) -> str:
        pattern = rf"```{language}\n(.*?)\n```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        generic_match = re.search(r"```(?:\w+)?\n(.*?)\n```", text, re.DOTALL)
        if generic_match:
            return generic_match.group(1).strip()
        return text.strip()

    def reflect_and_refine(
        self,
        task_instruction: str,
        initial_code: str,
        language: str = "python",
    ) -> ReflectionResult:
        t0 = time.perf_counter()
        self._total_reflection_cycles += 1

        # Turn 1: Skeptic Audits Code
        skeptic_prompt = (
            f"You are the Skeptic Auditor (deepseek-r1). Audit this {language} implementation:\n"
            f"Task: {task_instruction}\n\n"
            f"Code to Audit:\n{initial_code}\n\n"
            "Analyze for edge cases, null pointers, off-by-one errors, infinite loops, or broken contracts.\n"
            "Return JSON format:\n"
            '{"has_flaws": boolean, "flaw_category": "logic_bug|boundary_value|syntax|none", "critique": "concise description"}'
        )

        skeptic_raw = self.llm_client.generate(
            prompt=skeptic_prompt,
            model=self.skeptic_model,
            system_prompt="You are a rigorous code auditor. Output JSON.",
            temperature=0.0,
            response_format="json",
        )
        critique = self._parse_critique_json(skeptic_raw)

        final_code = initial_code
        was_refined = False

        if critique.has_flaws:
            self._skeptic_flaws_intercepted += 1

            # Turn 2: Builder Refines with Critique
            builder_prompt = (
                f"You are the Builder Elite (qwen2.5-coder). Refine and fix this {language} code:\n"
                f"Task: {task_instruction}\n"
                f"Initial Code:\n{initial_code}\n"
                f"Skeptic Audit Critique:\n{critique.critique_details}\n\n"
                f"Address all flaws. Output ONLY the fixed {language} code inside ```{language} ... ```."
            )

            builder_raw = self.llm_client.generate(
                prompt=builder_prompt,
                model=self.builder_model,
                temperature=0.0,
            )
            refined_code = self._extract_code_block(builder_raw, language)
            final_code = refined_code
            was_refined = True

        # Validation Step: In-memory AST check
        validation = self.ast_parser.validate_syntax(final_code, language)
        if was_refined and validation.is_valid:
            self._successful_self_refinements += 1

        duration_ms = (time.perf_counter() - t0) * 1000.0

        # Poupando 1.500 tokens de nuvem por ciclo reflexivo local (~$0.00225 USD)
        self._zero_cloud_cost_saved_usd += 0.00225

        return ReflectionResult(
            original_code=initial_code,
            final_code=final_code,
            critique=critique,
            was_refined=was_refined,
            syntax_valid=validation.is_valid,
            latency_ms=round(duration_ms, 2),
        )

    def get_metrics(self) -> AdversarialMetrics:
        return AdversarialMetrics(
            total_reflection_cycles=self._total_reflection_cycles,
            skeptic_flaws_intercepted=self._skeptic_flaws_intercepted,
            successful_self_refinements=self._successful_self_refinements,
            zero_cloud_cost_saved_usd=round(self._zero_cloud_cost_saved_usd, 4),
        )
