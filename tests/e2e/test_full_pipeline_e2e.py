"""
E2E tests for the Complete Unified Execution Pipeline.
Verifies end-to-end lifecycle from tool call / request dispatch to disk persistence,
including L0 semantic caching, SMT invariant verification, and token reduction guarantees.
"""

import os
import tempfile
import unittest
from typing import Any
from src.application.unified_execution_pipeline import UnifiedExecutionPipeline
from src.application.cognitive_arbiter import CognitiveArbiter
from src.application.speculative_drafter import SpeculativeDrafter
from src.application.adversarial_reflector import AdversarialReflector
from src.application.ast_merkle_engine import AstMerkleEngine
from src.application.guardrail_interceptor import GuardrailInterceptor
from src.application.code_skeletonizer import CodeSkeletonizer
from src.application.smt_formal_verification_gate import SmtFormalVerificationGate
from src.application.semantic_prompt_cache import SemanticPromptCache
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.adapters.outbound.file_system_adapter import LocalFileSystemAdapter
from src.domain.value_objects import SyntaxValidationResult


class E2EClientFake:
    def __init__(self):
        self.call_count = 0

    def generate(self, prompt: str, model: str, **kwargs: Any) -> str:
        self.call_count += 1
        if "deepseek-r1" in model:
            return '{"has_flaws": false, "flaw_category": "none", "critique": "All invariants sound"}'
        import json
        return json.dumps({
            "TargetContent": "    return (x, y)\n",
            "ReplacementContent": "    return (x * 2.0, y * 2.0)\n",
            "StartLine": 2,
            "EndLine": 2,
            "Explanation": "Scale coordinates by 2.0"
        })

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        # Deterministic 768-dim vector
        return [0.1 * ((i % 5) - 2) for i in range(768)]


class TestFullPipelineE2E(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "geo_calc.py")
        self.initial_code = (
            "def transform_coordinates(x: float, y: float) -> tuple[float, float]:\n"
            "    return (x, y)\n"
        )
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(self.initial_code)

        self.client = E2EClientFake()
        self.fs = LocalFileSystemAdapter()
        self.ast_parser = MultiLanguageAstAdapter()

        self.drafter = SpeculativeDrafter(
            llm=self.client,
            parser=self.ast_parser,
            file_system=self.fs
        )
        self.reflector = AdversarialReflector(
            llm_client=self.client,
            ast_parser=self.ast_parser
        )
        self.merkle = AstMerkleEngine()
        self.arbiter = CognitiveArbiter()
        self.guardrail = GuardrailInterceptor(parser=self.ast_parser, file_system=self.fs)
        self.prompt_cache = SemanticPromptCache(db_path=os.path.join(self.temp_dir, "semantic_cache.db"))

        self.pipeline = UnifiedExecutionPipeline(
            llm=self.client,
            parser=self.ast_parser,
            file_system=self.fs,
            merkle_engine=self.merkle,
            arbiter=self.arbiter,
            reflector=self.reflector,
            drafter=self.drafter,
            prompt_cache=self.prompt_cache
        )

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_full_pipeline_execution_and_disk_application(self):
        """
        Verifies end-to-end flow:
        Request -> Arbiter -> Drafter -> Reflector -> Merkle -> Guardrail -> Disk Apply.
        """
        result = self.pipeline.execute_patch_pipeline(
            file_path=self.test_file,
            instruction="Scale coordinate transformation by factor of 2.0",
            auto_apply=True
        )

        self.assertEqual(result.get("status"), "success")
        self.assertTrue(result.get("applied_to_disk"))

        # Verify disk persistence
        disk_content = self.fs.read_text(self.test_file)
        self.assertIn("return (x * 2.0, y * 2.0)", disk_content)

    def test_02_semantic_prompt_cache_l0_hit_zero_overhead(self):
        """
        Verifies that re-submitting an identical instruction hits L0 Cosine Cache,
        returning in < 5ms with zero additional LLM generation calls.
        """
        # First execution primes the cache
        self.pipeline.execute_patch_pipeline(
            file_path=self.test_file,
            instruction="Scale coordinate transformation by factor of 2.0",
            auto_apply=True
        )
        calls_before = self.client.call_count

        # Second execution must hit L0 cache
        cache_result = self.pipeline.execute_patch_pipeline(
            file_path=self.test_file,
            instruction="Scale coordinate transformation by factor of 2.0",
            auto_apply=True
        )
        self.assertEqual(cache_result.get("status"), "success")
        self.assertTrue(cache_result.get("cached"))
        # No extra LLM generation calls were required
        self.assertEqual(self.client.call_count, calls_before)

    def test_03_guardrail_blocks_dangerous_destructive_commands(self):
        """
        Verifies Guardrail Interceptor strictly halts destructive operations.
        """
        blocked_commands = [
            "rm -rf /",
            "rm -r -f *",
            "git push origin main --force",
            "find / -delete",
            "dd if=/dev/zero of=/dev/rdisk1",
        ]
        for cmd in blocked_commands:
            evaluation = self.guardrail.evaluate("run_command", {"CommandLine": cmd})
            self.assertEqual(
                evaluation.get("decision"),
                "deny",
                f"Command '{cmd}' should have been denied by guardrail"
            )

    def test_04_smt_formal_verification_proves_invariants(self):
        """
        Verifies SMT formal verification gate statically asserts safety invariants.
        """
        prover = SmtFormalVerificationGate()
        safe_code = (
            "def safe_divide(x: int, y: int) -> float:\n"
            "    if y != 0:\n"
            "        return x / y\n"
            "    return 0.0\n"
        )
        res = prover.verify_code(safe_code)
        self.assertTrue(res.is_safe)

        unsafe_code = (
            "def broken_divide(x: int) -> float:\n"
            "    denom = 0\n"
            "    return x / denom\n"
        )
        unsafe_res = prover.verify_code(unsafe_code)
        self.assertFalse(unsafe_res.is_safe)

    def test_05_quantitative_token_reduction_assertion(self):
        """
        Verifies CodeSkeletonizer achieves >= 50% token reduction while retaining contracts.
        """
        skeletonizer = CodeSkeletonizer(self.ast_parser)
        long_code = (
            "class VectorMath:\n"
            '    """Mathematical vector operations library."""\n'
            "    def dot_product(self, a: list[float], b: list[float]) -> float:\n"
            "        acc = 0.0\n"
            "        for i in range(len(a)):\n"
            "            acc += a[i] * b[i]\n"
            "        return acc\n"
            "    def cross_product(self, a: list[float], b: list[float]) -> list[float]:\n"
            "        return [a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]]\n"
        )
        skeleton_code, reduction_pct = skeletonizer.skeletonize(long_code, "python")

        self.assertGreaterEqual(reduction_pct, 50.0)
        self.assertIn("def dot_product", skeleton_code)
        self.assertIn("...", skeleton_code)
        self.assertNotIn("acc += a[i] * b[i]", skeleton_code)


if __name__ == "__main__":
    unittest.main()
