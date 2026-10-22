"""
Application Use Case: Cognitive Arbiter.
Hybrid Heuristic-Semantic Classifier running in <2ms with zero cloud token cost.
Dispatches tasks between System 1 (Fast / Local Mac) and System 2 (Slow / Cloud Gemini Pro).
"""

from __future__ import annotations
import ast
import re
from src.domain.value_objects import (
    CognitiveSystem,
    TaskScope,
    TaskClassification,
    TokenBudgetEnvelope,
)
from src.ports.inbound.cognitive_arbiter_port import ICognitiveArbiter


class CognitiveArbiter(ICognitiveArbiter):
    """Evaluates task intent, file scope, and AST complexity to select cognitive system."""

    SYSTEM_2_KEYWORDS = [
        r"\barquitetura\b", r"\bredesign\b", r"\bmigra[çc][ãa]o\b", r"\bquebra\s+de\s+contrato\b",
        r"\binvariante[s]?\b", r"\bcross-module\b", r"\bmulti[- ]servi[çc]o\b", r"\bprotocolo\b",
        r"\bnovo\s+m[óo]dulo\b", r"\breestrutura[çc][ãa]o\b", r"\bdatabase\s+schema\b"
    ]

    SYSTEM_1_KEYWORDS = [
        r"\btypo\b", r"\bfix\b", r"\blint\b", r"\bformata[çc][ãa]o\b", r"\bdocstring\b",
        r"\bcoment[áa]rio\b", r"\brenomear\b", r"\badicionar\s+teste\b", r"\bboilerplate\b",
        r"\bregex\b", r"\bjson\b", r"\bassert\b", r"\bpep8\b", r"\bpequeno\s+ajuste\b"
    ]

    @staticmethod
    def calculate_cyclomatic_complexity(source_code: str) -> int:
        """Calculates McCabe cyclomatic complexity using Python ast."""
        try:
            tree = ast.parse(source_code)
        except Exception:
            return 1

        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(node, ast.IfExp):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += max(0, len(node.values) - 1)
        return complexity

    def classify_task(
        self,
        prompt: str,
        affected_files: list[str] | None = None,
        code_snippet: str | None = None
    ) -> TaskClassification:
        files = affected_files or []
        prompt_lower = prompt.lower()

        # Rule 0: Cyclomatic complexity > 10 escalates directly to System 2 Cloud
        if code_snippet:
            cc = self.calculate_cyclomatic_complexity(code_snippet)
            if cc > 10:
                return TaskClassification(
                    system=CognitiveSystem.SYSTEM_2_CLOUD_SLOW,
                    scope=TaskScope.CROSS_MODULE_ARCHITECTURE,
                    confidence=0.96,
                    rationale=f"Code cyclomatic complexity (McCabe={cc} > 10) exceeds local model capacity; escalating to System 2."
                )

        # Rule 1: Multi-file cross-module impact forces System 2
        if len(files) > 2:
            return TaskClassification(
                system=CognitiveSystem.SYSTEM_2_CLOUD_SLOW,
                scope=TaskScope.CROSS_MODULE_ARCHITECTURE,
                confidence=0.95,
                rationale=f"Task spans {len(files)} distinct files requiring cross-module architectural synthesis."
            )

        # Rule 2: Explicit System 2 architectural keywords
        for pat in self.SYSTEM_2_KEYWORDS:
            if re.search(pat, prompt_lower):
                return TaskClassification(
                    system=CognitiveSystem.SYSTEM_2_CLOUD_SLOW,
                    scope=TaskScope.CROSS_MODULE_ARCHITECTURE,
                    confidence=0.90,
                    rationale=f"Prompt matched architectural trigger pattern: '{pat}'."
                )

        # Rule 3: Explicit System 1 mechanical keywords
        for pat in self.SYSTEM_1_KEYWORDS:
            if re.search(pat, prompt_lower):
                return TaskClassification(
                    system=CognitiveSystem.SYSTEM_1_LOCAL_FAST,
                    scope=TaskScope.ISOLATED_MODULE,
                    confidence=0.92,
                    rationale=f"Prompt matched mechanical local trigger pattern: '{pat}'."
                )

        # Rule 4: Default for single file or short targeted prompt is System 1 Local First
        if len(files) <= 1:
            return TaskClassification(
                system=CognitiveSystem.SYSTEM_1_LOCAL_FAST,
                scope=TaskScope.ISOLATED_MODULE,
                confidence=0.85,
                rationale="Single isolated file scope defaulted to Local-First System 1."
            )

        # Default fallback
        return TaskClassification(
            system=CognitiveSystem.SYSTEM_2_CLOUD_SLOW,
            scope=TaskScope.CROSS_MODULE_ARCHITECTURE,
            confidence=0.75,
            rationale="Uncertain scope escalated safely to System 2 Cloud Orchestrator."
        )

    def calculate_budget(self, classification: TaskClassification) -> TokenBudgetEnvelope:
        if classification.system == CognitiveSystem.SYSTEM_1_LOCAL_FAST:
            return TokenBudgetEnvelope(
                max_system_2_tokens=0,
                blueprint_budget=0,
                audit_budget=0
            )

        return TokenBudgetEnvelope(
            max_system_2_tokens=8000,
            blueprint_budget=500,
            audit_budget=300
        )
