"""
Application Use Case: Hierarchical Cascade.
Orchestrates 2-level Tier 0 local execution between ultra-fast micro-models (smollm2:1.7b)
and elite builders (qwen2.5-coder:7b) with silent promotion on syntax flaws.
Follows Single Responsibility (SRP) and Dependency Inversion (DIP).
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import re
import time
from typing import List

from src.domain.value_objects import (
    CascadeTaskLevel,
    CascadeResult,
    CascadeMetrics,
)
from src.ports.inbound.hierarchical_cascade_port import IHierarchicalCascade
from src.ports.outbound.llm_client_port import ILLMClient
from src.ports.outbound.ast_parser_port import IAstParser
from src.application.speculative_consensus import SpeculativeConsensusEngine
from src.application.asymmetric_speculative_decoder import AsymmetricSpeculativeDecoder
from src.application.tree_speculative_decoder import TreeSpeculativeDecoder


class HierarchicalCascade(IHierarchicalCascade):
    """
    Routes code generation tasks hierarchically: micro-tasks resolve in ~50ms
    on smollm2:1.7b, with automatic silent promotion to qwen2.5-coder:7b.
    """

    MICRO_PATTERNS = re.compile(
        r"\b(docstring|type hint|typing|format|regex|json schema|simple function|rename|one line|fix typo|single line|linter)\b",
        re.IGNORECASE,
    )
    STRUCTURAL_PATTERNS = re.compile(
        r"\b(class |architect|multiple methods|database|engine|concurrency|pipeline|framework)\b",
        re.IGNORECASE,
    )

    def __init__(
        self,
        llm_client: ILLMClient,
        ast_parser: IAstParser,
        micro_model: str = "smollm2:1.7b",
        builder_model: str = "qwen2.5-coder:7b",
        consensus_engine: SpeculativeConsensusEngine | None = None,
        speculative_decoder: AsymmetricSpeculativeDecoder | None = None,
        tree_decoder: TreeSpeculativeDecoder | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.ast_parser = ast_parser
        self.micro_model = micro_model
        self.builder_model = builder_model
        self.consensus_engine = consensus_engine or SpeculativeConsensusEngine(llm_client, ast_parser)
        self.speculative_decoder = speculative_decoder or AsymmetricSpeculativeDecoder(llm_client=llm_client)
        self.tree_decoder = tree_decoder or TreeSpeculativeDecoder()

        self._total_requests: int = 0
        self._smollm_micro_resolved: int = 0
        self._promoted_to_7b: int = 0
        self._latencies_ms: List[float] = []

    def classify_task_level(self, instruction: str, context_code: str = "") -> CascadeTaskLevel:
        lines_count = len(context_code.splitlines()) if context_code else 0
        has_micro_match = bool(self.MICRO_PATTERNS.search(instruction))
        has_structural_match = bool(self.STRUCTURAL_PATTERNS.search(instruction))

        if has_micro_match and not has_structural_match and lines_count < 40:
            return CascadeTaskLevel.MICRO_TASK
        return CascadeTaskLevel.STRUCTURAL_TASK

    def _extract_code(self, raw_resp: str, language: str) -> str:
        pattern = rf"```{language}\n(.*?)\n```"
        match = re.search(pattern, raw_resp, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        generic_match = re.search(r"```(?:\w+)?\n(.*?)\n```", raw_resp, re.DOTALL)
        if generic_match:
            return generic_match.group(1).strip()
        return raw_resp.strip()

    def execute_task(
        self,
        task_instruction: str,
        context_code: str = "",
        language: str = "python",
    ) -> CascadeResult:
        t0 = time.perf_counter()
        self._total_requests += 1

        level = self.classify_task_level(task_instruction, context_code)

        if level == CascadeTaskLevel.MICRO_TASK:
            # Level 0: Try ultra-fast resolution on micro-model (1.7B)
            micro_prompt = (
                f"Task: {task_instruction}\n"
                f"Context Code:\n{context_code}\n\n"
                f"Return ONLY the valid {language} code inside ```{language} ... ```."
            )
            raw_resp = self.llm_client.generate(
                prompt=micro_prompt,
                model=self.micro_model,
                temperature=0.0,
            )
            code = self._extract_code(raw_resp, language)
            validation = self.ast_parser.validate_syntax(code, language)

            if validation.is_valid:
                duration_ms = (time.perf_counter() - t0) * 1000.0
                self._smollm_micro_resolved += 1
                self._latencies_ms.append(duration_ms)
                return CascadeResult(
                    task_level=CascadeTaskLevel.MICRO_TASK,
                    resolved_by_model=self.micro_model,
                    was_promoted=False,
                    code=code,
                    syntax_valid=True,
                    latency_ms=round(duration_ms, 2),
                )

            # Syntax failure in micro-model: Silent Promotion to Builder 7B
            self._promoted_to_7b += 1
            builder_prompt = (
                f"Task: {task_instruction}\n"
                f"Context Code:\n{context_code}\n"
                f"Note: Previous micro-draft had syntax errors: {validation.error_message}\n\n"
                f"Provide robust, clean {language} code inside ```{language} ... ```."
            )
            promoted_raw = self.llm_client.generate(
                prompt=builder_prompt,
                model=self.builder_model,
                temperature=0.0,
            )
            promoted_code = self._extract_code(promoted_raw, language)
            promoted_val = self.ast_parser.validate_syntax(promoted_code, language)
            duration_ms = (time.perf_counter() - t0) * 1000.0
            self._latencies_ms.append(duration_ms)

            return CascadeResult(
                task_level=CascadeTaskLevel.MICRO_TASK,
                resolved_by_model=self.builder_model,
                was_promoted=True,
                code=promoted_code,
                syntax_valid=promoted_val.is_valid,
                latency_ms=round(duration_ms, 2),
            )

        # Level 1: Structural task routed directly to Builder 7B
        structural_prompt = (
            f"Task: {task_instruction}\n"
            f"Context Code:\n{context_code}\n\n"
            f"Implement clean, architectural {language} code inside ```{language} ... ```."
        )
        resp = self.llm_client.generate(
            prompt=structural_prompt,
            model=self.builder_model,
            temperature=0.0,
        )
        struct_code = self._extract_code(resp, language)
        struct_val = self.ast_parser.validate_syntax(struct_code, language)
        duration_ms = (time.perf_counter() - t0) * 1000.0
        self._latencies_ms.append(duration_ms)

        return CascadeResult(
            task_level=CascadeTaskLevel.STRUCTURAL_TASK,
            resolved_by_model=self.builder_model,
            was_promoted=False,
            code=struct_code,
            syntax_valid=struct_val.is_valid,
            latency_ms=round(duration_ms, 2),
        )

    def get_metrics(self) -> CascadeMetrics:
        avg_lat = (
            round(sum(self._latencies_ms) / len(self._latencies_ms), 2)
            if self._latencies_ms
            else 0.0
        )
        return CascadeMetrics(
            total_cascade_requests=self._total_requests,
            smollm_micro_resolved=self._smollm_micro_resolved,
            promoted_to_7b=self._promoted_to_7b,
            avg_cascade_latency_ms=avg_lat,
        )
