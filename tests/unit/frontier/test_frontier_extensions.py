"""
Unit tests for Frontier Extensions:
- MetalComputeAdapter (Metal MSL batch compute & Accelerate BLAS dispatch)
- AsymmetricSpeculativeDecoder (Draft model + Target model speculative decoding)
- IncrementalAstAdapter (Sub-microsecond multi-language incremental AST)
- SemanticPromptCache (Cosine Cache L0 with scalar quantization)
- AgenticSelfHealingRunner (Closed loop autonomous test self-healing)
"""

import os
import tempfile
import unittest

from src.adapters.outbound.metal_compute_adapter import MetalComputeAdapter
from src.application.asymmetric_speculative_decoder import AsymmetricSpeculativeDecoder
from src.adapters.outbound.incremental_ast_adapter import IncrementalAstAdapter
from src.application.semantic_prompt_cache import SemanticPromptCache
from src.application.agentic_self_healing_runner import AgenticSelfHealingRunner
from tests.unit.application.test_use_cases import FakeLLMClient, FakeAstParser, FakeFileSystem


class TestMetalComputeAdapter(unittest.TestCase):

    def setUp(self):
        self.adapter = MetalComputeAdapter()

    def test_batch_cosine_similarity(self):
        query = [1.0, 0.0, 0.5]
        matrix = [
            [1.0, 0.0, 0.5],   # identical (1.0)
            [0.0, 1.0, 0.0],   # orthogonal (0.0)
            [0.5, 0.0, 0.25],  # parallel scaled (1.0)
        ]
        scores = self.adapter.batch_cosine_similarity(query, matrix)
        self.assertEqual(len(scores), 3)
        self.assertAlmostEqual(scores[0], 1.0, places=3)
        self.assertAlmostEqual(scores[1], 0.0, places=3)
        self.assertAlmostEqual(scores[2], 1.0, places=3)

    def test_top_k_similar(self):
        query = [1.0, 1.0]
        candidates = [
            ("node_a", [1.0, 1.0]),
            ("node_b", [-1.0, -1.0]),
            ("node_c", [1.0, 0.0]),
        ]
        top = self.adapter.top_k_similar(query, candidates, top_k=2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0][0], "node_a")


class TestAsymmetricSpeculativeDecoder(unittest.TestCase):

    def test_speculative_decode_speedup(self):
        draft_code = "def add(a, b): return a + b"
        target_code = "def add(a, b): return a + b"
        llm = FakeLLMClient(responses=[draft_code, target_code])

        decoder = AsymmetricSpeculativeDecoder(llm, draft_model="smollm2:1.7b", target_model="qwen2.5-coder:7b")
        res = decoder.decode("implement add")

        self.assertEqual(res.tokens_accepted, res.tokens_drafted)
        self.assertEqual(res.acceptance_rate, 1.0)
        self.assertGreater(res.effective_tok_s, 70.0)


class TestIncrementalAstAdapter(unittest.TestCase):

    def setUp(self):
        self.parser = IncrementalAstAdapter()

    def test_incremental_python_parse(self):
        code = "def calculate_tax(income):\n    return income * 0.2\n"
        res = self.parser.parse_incremental(
            file_path="tax.py",
            original_code=code,
            edit_start_line=2,
            edit_end_line=2,
            replacement_snippet="return income * 0.25",
        )
        self.assertTrue(res.is_valid)
        self.assertEqual(res.affected_symbol, "calculate_tax")
        self.assertEqual(res.reparsed_node_type, "function")
        self.assertLess(res.parse_latency_us, 5000.0)  # Sub-5ms

    def test_detects_syntax_error_in_edit_span(self):
        code = "def calculate_tax(income):\n    return income * 0.2\n"
        res = self.parser.parse_incremental(
            file_path="tax.py",
            original_code=code,
            edit_start_line=2,
            edit_end_line=2,
            replacement_snippet="return income * (invalid",
        )
        self.assertFalse(res.is_valid)
        self.assertIn("SyntaxError", res.error_message)


class TestSemanticPromptCache(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.mktemp(suffix=".sqlite")
        self.cache = SemanticPromptCache(db_path=self.temp_db, similarity_threshold=0.95)

    def tearDown(self):
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)

    def test_store_and_lookup_hit(self):
        prompt = "Add error handling to database connect function"
        emb = [0.1, 0.8, 0.3, 0.5]
        patch = {"TargetContent": "pass", "ReplacementContent": "try: connect() except: pass"}

        self.cache.store(prompt, emb, patch)

        # Lookup with near-identical vector (99% similarity)
        similar_emb = [0.101, 0.801, 0.301, 0.501]
        hit = self.cache.lookup("add error handling on db connect", similar_emb)

        self.assertTrue(hit.is_hit)
        self.assertGreaterEqual(hit.similarity, 0.95)
        self.assertEqual(hit.template_patch["TargetContent"], "pass")


class TestAgenticSelfHealingRunner(unittest.TestCase):

    def test_self_heals_failing_assertion(self):
        bad_code = "def add(a, b): return a - b\n"
        fs = FakeFileSystem(files={"math_util.py": bad_code})
        parser = FakeAstParser(is_valid=True)

        # Skeptic says: "Subtract should be add"
        # Builder outputs patch JSON: TargetContent: 'return a - b', ReplacementContent: 'return a + b'
        llm = FakeLLMClient(responses=[
            "Subtraction operator used instead of addition.",
            '{"TargetContent": "return a - b", "ReplacementContent": "return a + b"}'
        ])

        runner = AgenticSelfHealingRunner(llm, parser, fs, max_retries=2)

        raw_tb = """
Traceback (most recent call last):
  File "test_math.py", line 12, in test_add
    assert add(2, 3) == 5
AssertionError: assert -1 == 5
"""
        def mock_test_runner(code_under_test: str) -> bool:
            return "return a + b" in code_under_test

        res = runner.heal_test_failure(raw_tb, mock_test_runner, "math_util.py")

        self.assertTrue(res.is_healed)
        self.assertEqual(res.iterations_used, 1)
        self.assertFalse(res.cloud_escalation_needed)
        self.assertIn("return a + b", fs.read_text("math_util.py"))


if __name__ == "__main__":
    unittest.main()
