"""
Unit tests for Local Adversarial Reflector (Abstraction 17).
Verifies 1-shot reflection cycles between Builder and Skeptic, flaw interception,
self-refinement, and telemetry metrics without external dependencies.
"""

import unittest
from typing import Any

from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.application.adversarial_reflector import AdversarialReflector
from src.ports.outbound.llm_client_port import ILLMClient


class FakeLLMClient(ILLMClient):
    """Fake LLM client simulating Builder and Skeptic responses."""

    def __init__(self, skeptic_response: str, builder_response: str = "") -> None:
        self.skeptic_response = skeptic_response
        self.builder_response = builder_response
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
        if "deepseek" in model or "skeptic" in model.lower():
            return self.skeptic_response
        return self.builder_response

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        return [0.1, 0.2, 0.3]

    def list_models(self) -> list[dict[str, Any]]:
        return []


class TestAdversarialReflector(unittest.TestCase):
    def setUp(self) -> None:
        self.ast_parser = MultiLanguageAstAdapter()

    def test_clean_code_approved_directly_without_refinement(self) -> None:
        skeptic_json = '{"has_flaws": false, "flaw_category": "none", "critique": "Optimal time complexity, no bugs."}'
        fake_client = FakeLLMClient(skeptic_response=skeptic_json)
        reflector = AdversarialReflector(llm_client=fake_client, ast_parser=self.ast_parser)

        code = "def add(a: int, b: int) -> int:\n    return a + b\n"
        res = reflector.reflect_and_refine(
            task_instruction="Implement integer addition",
            initial_code=code,
            language="python",
        )

        self.assertFalse(res.was_refined)
        self.assertEqual(res.final_code, code)
        self.assertTrue(res.syntax_valid)
        self.assertFalse(res.critique.has_flaws)

        metrics = reflector.get_metrics()
        self.assertEqual(metrics.total_reflection_cycles, 1)
        self.assertEqual(metrics.skeptic_flaws_intercepted, 0)
        self.assertEqual(metrics.self_refine_success_pct, 100.0)

    def test_flawed_code_intercepted_and_self_refined(self) -> None:
        skeptic_json = (
            '{"has_flaws": true, "flaw_category": "boundary_value", '
            '"critique": "Division by zero if divisor is 0."}'
        )
        builder_code = (
            "```python\n"
            "def safe_divide(a: float, b: float) -> float | None:\n"
            "    if b == 0:\n"
            "        return None\n"
            "    return a / b\n"
            "```"
        )
        fake_client = FakeLLMClient(
            skeptic_response=skeptic_json,
            builder_response=builder_code,
        )
        reflector = AdversarialReflector(llm_client=fake_client, ast_parser=self.ast_parser)

        initial = "def safe_divide(a: float, b: float) -> float:\n    return a / b\n"
        res = reflector.reflect_and_refine(
            task_instruction="Safe division handling zero",
            initial_code=initial,
            language="python",
        )

        self.assertTrue(res.was_refined)
        self.assertIn("if b == 0:", res.final_code)
        self.assertTrue(res.syntax_valid)
        self.assertTrue(res.critique.has_flaws)

        metrics = reflector.get_metrics()
        self.assertEqual(metrics.total_reflection_cycles, 1)
        self.assertEqual(metrics.skeptic_flaws_intercepted, 1)
        self.assertEqual(metrics.successful_self_refinements, 1)
        self.assertEqual(metrics.self_refine_success_pct, 100.0)
        self.assertGreater(metrics.zero_cloud_cost_saved_usd, 0.0)

    def test_fallback_heuristic_parsing_when_skeptic_not_json(self) -> None:
        raw_critique = "Wait, there is a severe bug with index bounds!"
        builder_fixed = "def get_item(lst):\n    return lst[0] if lst else None\n"
        fake_client = FakeLLMClient(
            skeptic_response=raw_critique,
            builder_response=builder_fixed,
        )
        reflector = AdversarialReflector(llm_client=fake_client, ast_parser=self.ast_parser)

        initial = "def get_item(lst):\n    return lst[0]\n"
        res = reflector.reflect_and_refine(
            task_instruction="Safe array get",
            initial_code=initial,
            language="python",
        )

        self.assertTrue(res.was_refined)
        self.assertTrue(res.critique.has_flaws)
        self.assertTrue(res.syntax_valid)


if __name__ == "__main__":
    unittest.main()
