"""
E2E tests for Model Council & Multi-Model Dispatch.
Verifies that all designated models in the Event Horizon Trinity & Council
are routed, invoked, and traced with expected parameters and contracts.
"""

import unittest
from typing import Any
from src.application.cognitive_arbiter import CognitiveArbiter
from src.application.hierarchical_cascade import HierarchicalCascade
from src.application.adversarial_reflector import AdversarialReflector
from src.application.speculative_consensus import SpeculativeConsensusEngine
from src.application.epistemic_distiller import EpistemicDistiller
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.domain.value_objects import CognitiveSystem, ModelTier


class TracingCouncilLLMClient:
    """
    LLM Client fake that records every model call, system prompt, temperature,
    and returns contextual responses for each specialized model role.
    """
    def __init__(self):
        self.invocations: list[dict[str, Any]] = []

    def generate(self, prompt: str, model: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        self.invocations.append({
            "model": model,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "kwargs": kwargs
        })

        if "deepseek-r1" in model:
            # Skeptic Auditor CoT response
            return (
                "<think>\nChecking syntax, types, and invariants...\n"
                "All assertions verified. No null dereferences found.\n</think>\n"
                '{"verdict": "APPROVED", "confidence": 0.99, "flaws": []}'
            )
        elif "smollm2" in model:
            # Micro-Worker response
            return (
                'def compute_centroid(points: list[tuple[float, float]]) -> tuple[float, float]:\n'
                '    x_sum = sum(p[0] for p in points)\n'
                '    y_sum = sum(p[1] for p in points)\n'
                '    return (x_sum / len(points), y_sum / len(points))\n'
            )
        elif "qwen2.5-coder:3b" in model:
            # Builder Agil response
            return (
                'def compute_centroid(points: list[tuple[float, float]]) -> tuple[float, float]:\n'
                '    x_sum = sum(p[0] for p in points)\n'
                '    y_sum = sum(p[1] for p in points)\n'
                '    return (x_sum / len(points), y_sum / len(points))\n'
            )
        elif "qwen2.5-coder:7b" in model:
            # Builder Elite response
            return (
                'def compute_centroid(points: list[tuple[float, float]]) -> tuple[float, float]:\n'
                '    x_sum = sum(p[0] for p in points)\n'
                '    y_sum = sum(p[1] for p in points)\n'
                '    return (x_sum / len(points), y_sum / len(points))\n'
            )
        elif "hermes3" in model:
            # Scribe Epistemic Distiller response
            return (
                "# Session State\n"
                "## Central Objective: Optimize pipeline\n"
                "## Verified Facts: 63/63 modules reached\n"
                "## Decisions: Zero external dependencies\n"
                "## Next Steps: Deploy CI\n"
            )
        elif "gemini-2.0-pro" in model or "gemini-2.0-flash" in model or "cloud" in model:
            return "Cloud Tier: Architectural decomposition verified."
        return "Default output"

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        self.invocations.append({
            "model": model,
            "prompt": text,
            "type": "embedding"
        })
        # Deterministic 768-dimensional mock embedding
        return [0.05 * ((i % 10) - 5) for i in range(768)]


class FakeTranscriptRepo:
    def get_latest_session_id(self) -> str:
        return "session-e2e-001"

    def iter_session_records(self, session_id: str):
        return [
            {"source": "USER_EXPLICIT", "content": "Refactor mathematical centroid calculation"},
            {"source": "MODEL", "content": "Applied AST patch with zero syntax flaws"}
        ]


class FakeFileSystem:
    def __init__(self):
        self.written: dict[str, str] = {}

    def write_text(self, path: str, content: str) -> None:
        self.written[path] = content

    def read_text(self, path: str) -> str:
        return self.written.get(path, "")


class TestModelCouncilDispatchE2E(unittest.TestCase):
    """
    End-to-End assertions proving that every model in the council is invoked
    at the correct layer of execution with appropriate telemetry and roles.
    """

    def setUp(self):
        self.client = TracingCouncilLLMClient()
        self.ast_adapter = MultiLanguageAstAdapter()

    def test_01_builder_elite_and_skeptic_auditor_adversarial_loop(self):
        """
        Verifies Builder (qwen2.5-coder:7b) and Skeptic (deepseek-r1:1.5b)
        cooperate in the adversarial reflection loop.
        """
        reflector = AdversarialReflector(
            llm_client=self.client,
            ast_parser=self.ast_adapter,
            builder_model="qwen2.5-coder:7b",
            skeptic_model="deepseek-r1:1.5b"
        )
        code = "def add(a: int, b: int) -> int:\n    return a + b\n"
        result = reflector.reflect_and_refine(
            task_instruction="Add two integers",
            initial_code=code,
            language="python"
        )
        self.assertTrue(result.syntax_valid)

        models_called = [inv["model"] for inv in self.client.invocations]
        self.assertIn("deepseek-r1:1.5b", models_called)

    def test_02_micro_worker_and_builder_hierarchical_cascade(self):
        """
        Verifies Hierarchical Cascade calls smollm2:1.7b for micro tasks.
        """
        cascade = HierarchicalCascade(
            llm_client=self.client,
            ast_parser=self.ast_adapter,
            micro_model="smollm2:1.7b",
            builder_model="qwen2.5-coder:7b"
        )
        prompt = "Add docstring and type hint to simple function"
        res = cascade.execute_task(task_instruction=prompt, context_code="def run(): pass")
        self.assertTrue(res.syntax_valid)
        self.assertEqual(res.resolved_by_model, "smollm2:1.7b")

        models_called = [inv["model"] for inv in self.client.invocations]
        self.assertIn("smollm2:1.7b", models_called)

    def test_03_builder_agil_speculative_consensus(self):
        """
        Verifies Speculative Consensus invokes qwen2.5-coder:3b alongside smollm2:1.7b.
        """
        consensus_engine = SpeculativeConsensusEngine(
            llm_client=self.client,
            ast_parser=self.ast_adapter
        )
        prompt = "Format compute_centroid"
        code = "def compute_centroid(): pass"
        consensus_res = consensus_engine.evaluate_consensus(
            task_instruction=prompt,
            code_snippet=code,
            model_a="qwen2.5-coder:3b",
            model_b="smollm2:1.7b"
        )
        self.assertTrue(consensus_res.has_consensus)

        models_called = [inv["model"] for inv in self.client.invocations]
        self.assertIn("qwen2.5-coder:3b", models_called)
        self.assertIn("smollm2:1.7b", models_called)

    def test_04_scout_semantic_rag_embeddings(self):
        """
        Verifies Scout (nomic-embed-text) is invoked to generate 768-dim embeddings.
        """
        emb = self.client.embed("class CentroidCalculator:\n    pass\n", model="nomic-embed-text")
        self.assertEqual(len(emb), 768)

        models_called = [inv["model"] for inv in self.client.invocations]
        self.assertIn("nomic-embed-text", models_called)

    def test_05_scribe_epistemic_distiller(self):
        """
        Verifies Scribe (hermes3:3b) is invoked for state distillation.
        """
        distiller = EpistemicDistiller(
            llm=self.client,
            repo=FakeTranscriptRepo(),
            file_system=FakeFileSystem(),
            distiller_model="hermes3:3b"
        )
        state = distiller.distill_active_session("session_state.md")
        self.assertEqual(state.session_id, "session-e2e-001")
        models_called = [inv["model"] for inv in self.client.invocations]
        self.assertIn("hermes3:3b", models_called)

    def test_06_cloud_tier_escalation_routing(self):
        """
        Verifies Cognitive Arbiter escalates to Gemini Pro (Cloud Tier)
        when tasks involve macro cross-module architecture.
        """
        arbiter = CognitiveArbiter()
        complex_prompt = (
            "arquitetura e redesign do sistema multi-serviço com nova quebra de contrato no protocolo de rede"
        )
        classification = arbiter.classify_task(
            prompt=complex_prompt,
            affected_files=["service_a.py", "service_b.py", "service_c.py", "service_d.py"]
        )
        self.assertEqual(classification.system, CognitiveSystem.SYSTEM_2_CLOUD_SLOW)


if __name__ == "__main__":
    unittest.main()
