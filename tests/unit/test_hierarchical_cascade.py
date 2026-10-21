"""
Unit tests for Hierarchical Cascade (Abstraction 18).
Verifies 2-level Tier 0 execution (smollm2:1.7b vs qwen2.5-coder:7b),
micro-task classification, silent promotion on syntax error, and metrics.
"""

import unittest
from typing import Any

from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.application.hierarchical_cascade import HierarchicalCascade
from src.domain.value_objects import CascadeTaskLevel
from src.ports.outbound.llm_client_port import ILLMClient


class CascadeFakeLLM(ILLMClient):
    """Fake LLM client simulating SmolLM2 and Qwen responses."""

    def __init__(self, micro_resp: str = "", builder_resp: str = "") -> None:
        self.micro_resp = micro_resp
        self.builder_resp = builder_resp
        self.calls: list[dict[str, Any]] = []

    def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        response_format: str | None = None,
    ) -> str:
        self.calls.append({"model": model, "prompt": prompt})
        if "smollm" in model:
            return self.micro_resp
        return self.builder_resp

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        return [0.1, 0.2]

    def list_models(self) -> list[dict[str, Any]]:
        return []


class TestHierarchicalCascade(unittest.TestCase):
    def setUp(self) -> None:
        self.ast_parser = MultiLanguageAstAdapter()

    def test_micro_task_resolved_by_smollm_successfully(self) -> None:
        smol_code = "```python\ndef format_name(first: str, last: str) -> str:\n    return f'{first} {last}'\n```"
        fake_llm = CascadeFakeLLM(micro_resp=smol_code, builder_resp="unused")
        cascade = HierarchicalCascade(llm_client=fake_llm, ast_parser=self.ast_parser)

        res = cascade.execute_task(
            task_instruction="Add docstring and typing to format_name",
            context_code="def format_name(first, last):\n    pass\n",
            language="python",
        )

        self.assertEqual(res.task_level, CascadeTaskLevel.MICRO_TASK)
        self.assertEqual(res.resolved_by_model, "smollm2:1.7b")
        self.assertFalse(res.was_promoted)
        self.assertTrue(res.syntax_valid)
        self.assertIn("format_name", res.code)

        metrics = cascade.get_metrics()
        self.assertEqual(metrics.total_cascade_requests, 1)
        self.assertEqual(metrics.smollm_micro_resolved, 1)
        self.assertEqual(metrics.promoted_to_7b, 0)
        self.assertEqual(metrics.micro_resolution_rate_pct, 100.0)

    def test_micro_task_syntax_flaw_silently_promotes_to_7b(self) -> None:
        invalid_micro_code = "```python\ndef broken_func(:\n    return 42\n```"
        valid_builder_code = "```python\ndef fixed_func() -> int:\n    return 42\n```"
        fake_llm = CascadeFakeLLM(micro_resp=invalid_micro_code, builder_resp=valid_builder_code)
        cascade = HierarchicalCascade(llm_client=fake_llm, ast_parser=self.ast_parser)

        res = cascade.execute_task(
            task_instruction="Fix one line regex format",
            context_code="regex = re.compile(r'\\d+')\n",
            language="python",
        )

        self.assertEqual(res.task_level, CascadeTaskLevel.MICRO_TASK)
        self.assertEqual(res.resolved_by_model, "qwen2.5-coder:7b")
        self.assertTrue(res.was_promoted)
        self.assertTrue(res.syntax_valid)
        self.assertIn("fixed_func", res.code)

        metrics = cascade.get_metrics()
        self.assertEqual(metrics.total_cascade_requests, 1)
        self.assertEqual(metrics.smollm_micro_resolved, 0)
        self.assertEqual(metrics.promoted_to_7b, 1)
        self.assertEqual(metrics.micro_resolution_rate_pct, 0.0)

    def test_structural_task_routed_directly_to_7b(self) -> None:
        builder_code = (
            "```python\n"
            "class ReactorEngine:\n"
            "    def __init__(self, capacity: int):\n"
            "        self.capacity = capacity\n"
            "```"
        )
        fake_llm = CascadeFakeLLM(micro_resp="unused", builder_resp=builder_code)
        cascade = HierarchicalCascade(llm_client=fake_llm, ast_parser=self.ast_parser)

        res = cascade.execute_task(
            task_instruction="Implement class ReactorEngine with database pipeline architecture",
            context_code="",
            language="python",
        )

        self.assertEqual(res.task_level, CascadeTaskLevel.STRUCTURAL_TASK)
        self.assertEqual(res.resolved_by_model, "qwen2.5-coder:7b")
        self.assertFalse(res.was_promoted)
        self.assertTrue(res.syntax_valid)
        self.assertIn("class ReactorEngine", res.code)


if __name__ == "__main__":
    unittest.main()
