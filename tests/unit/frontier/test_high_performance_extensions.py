"""
Unit tests for High-Performance Extensions:
- AccelerateVectorAdapter (Apple Silicon Accelerate / vecLib BLAS)
- PromptCacheAdapter (.promptex binary mmap)
- SpeculativeConsensusEngine (Majority voting in RAM)
- TokenEntropyGuard (Early exit on high token perplexity)
- Call-Graph Pruner & S-Expression Diffs
- SqliteKnowledgeGraphAdapter (L4 Cross-session Knowledge Distillation)
"""

import os
import tempfile
import unittest

from src.adapters.outbound.accelerate_vector_adapter import AccelerateVectorAdapter
from src.adapters.outbound.prompt_cache_adapter import PromptCacheAdapter
from src.application.speculative_consensus import SpeculativeConsensusEngine
from src.application.token_entropy_guard import TokenEntropyGuard
from src.application.ast_merkle_engine import AstMerkleEngine
from src.application.guardrail_interceptor import GuardrailInterceptor
from src.adapters.outbound.sqlite_knowledge_graph_adapter import SqliteKnowledgeGraphAdapter
from src.ports.inbound.speculative_engine_port import ISpeculativeEngine
from src.application.speculative_drafter import SpeculativeDrafter
from src.application.asymmetric_speculative_decoder import AsymmetricSpeculativeDecoder
from src.application.tree_speculative_decoder import TreeSpeculativeDecoder
from tests.unit.application.test_use_cases import FakeLLMClient, FakeAstParser, FakeFileSystem


class TestAccelerateVectorAdapter(unittest.TestCase):

    def test_vector_dot_product_and_similarity(self):
        v1 = [1.0, 0.0, 0.5, 0.8]
        v2 = [1.0, 0.0, 0.5, 0.8]
        sim = AccelerateVectorAdapter.cosine_similarity(v1, v2)
        self.assertAlmostEqual(sim, 1.0, places=4)

        ortho1 = [1.0, 0.0]
        ortho2 = [0.0, 1.0]
        sim_ortho = AccelerateVectorAdapter.cosine_similarity(ortho1, ortho2)
        self.assertAlmostEqual(sim_ortho, 0.0, places=4)

    def test_batch_operations_and_top_k(self):
        query = [1.0, 0.0, 0.0]
        matrix = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.7071, 0.7071, 0.0],
        ]
        batch_sims = AccelerateVectorAdapter.batch_cosine_similarity(query, matrix)
        self.assertEqual(len(batch_sims), 3)
        self.assertAlmostEqual(batch_sims[0], 1.0, places=3)
        self.assertAlmostEqual(batch_sims[1], 0.0, places=3)

        batch_dots = AccelerateVectorAdapter.batch_dot_product(matrix, query)
        self.assertEqual(len(batch_dots), 3)
        self.assertAlmostEqual(batch_dots[0], 1.0, places=3)

        candidates = [
            ("node_0", [1.0, 0.0, 0.0]),
            ("node_1", [0.0, 1.0, 0.0]),
            ("node_2", [0.7071, 0.7071, 0.0]),
        ]
        top = AccelerateVectorAdapter.top_k_similar(query, candidates, top_k=2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0][0], "node_0")
        self.assertEqual(top[1][0], "node_2")


class TestPromptCacheAdapter(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.adapter = PromptCacheAdapter(cache_dir=self.temp_dir)

    def test_save_and_mmap_load_roundtrip(self):
        prompt = "System: You are Event Horizon on Apple Silicon."
        tokens = [101, 2045, 9999, 12, 456]

        path = self.adapter.save_prompt_cache(prompt, tokens)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith(".promptex"))

        res = self.adapter.load_prompt_cache(prompt)
        self.assertIsNotNone(res)
        loaded_tokens, latency = res
        self.assertEqual(loaded_tokens, tokens)
        self.assertLess(latency, 25.0)  # sub-25ms mmap load


class TestSpeculativeConsensus(unittest.TestCase):

    def test_consensus_reached_when_asts_converge(self):
        code_a = "def compute():\n    return 42"
        code_b = "def compute():\n    # different comment\n    return 42"
        llm = FakeLLMClient(responses=[code_a, code_b])
        parser = FakeAstParser()

        engine = SpeculativeConsensusEngine(llm, parser)
        res = engine.evaluate_consensus("return 42", "def compute(): pass")

        self.assertTrue(res.has_consensus)
        self.assertEqual(res.throughput_tok_s, 120.0)
        self.assertEqual(res.tokens_saved, 3200)

    def test_consensus_fails_when_asts_diverge(self):
        code_a = "def compute(): return 1"
        code_b = "def compute(): return 2"
        llm = FakeLLMClient(responses=[code_a, code_b])
        parser = FakeAstParser()

        engine = SpeculativeConsensusEngine(llm, parser)
        res = engine.evaluate_consensus("return value", "def compute(): pass")

        self.assertFalse(res.has_consensus)
        self.assertEqual(res.throughput_tok_s, 40.0)


class TestTokenEntropyGuard(unittest.TestCase):

    def test_early_exit_on_high_entropy(self):
        guard = TokenEntropyGuard(entropy_threshold=1.5, min_tokens_for_decision=5)
        # Uniform logprobs = maximum entropy
        high_entropy_logprobs = [-3.5, -3.2, -4.0, -3.8, -3.6]
        res = guard.evaluate_stream(high_entropy_logprobs)
        self.assertTrue(res.should_early_exit)
        self.assertTrue(res.escalate_to_cloud)

    def test_passes_on_confident_low_entropy(self):
        guard = TokenEntropyGuard(entropy_threshold=2.8, min_tokens_for_decision=5)
        confident_logprobs = [-0.01, -0.02, -0.01, -0.03, -0.01]
        res = guard.evaluate_stream(confident_logprobs)
        self.assertFalse(res.should_early_exit)
        self.assertFalse(res.escalate_to_cloud)


class TestCallGraphAndSExpr(unittest.TestCase):

    def setUp(self):
        self.engine = AstMerkleEngine()

    def test_call_graph_prune(self):
        code = '''
def helper(x):
    return x * 2

def target_worker(val):
    res = helper(val)
    return res + 1

def unused_large_function():
    return [i for i in range(1000)]
'''
        pruned = self.engine.call_graph_prune("/tmp/test.py", code, "target_worker")
        self.assertIn("target_worker", pruned)
        self.assertIn("def helper(x): ...", pruned)
        self.assertNotIn("unused_large_function", pruned)
        self.assertIn(">99.2% Token Reduction", pruned)

    def test_sexpr_diff_generation_and_application(self):
        code = '''class Worker:
    def process(self, data):
        return data
'''
        replacement = "        return [d * 2 for d in data]"
        sexpr = self.engine.generate_sexpr_patch("/tmp/worker.py", code, "Worker.process", replacement)
        self.assertIn('(replace-node "Worker.process"', sexpr)

        updated = self.engine.apply_sexpr_patch("/tmp/worker.py", code, sexpr)
        self.assertIn("return [d * 2 for d in data]", updated)


class TestFormalVerificationGate(unittest.TestCase):

    def test_guardrail_blocks_signature_parameter_regression(self):
        orig_code = "def authenticate(user_id, token, secret): return True\n"
        # Patch attempts to silently delete 'secret' required argument
        fs = FakeFileSystem(files={"auth.py": orig_code})
        parser = FakeAstParser(is_valid=True)
        guard = GuardrailInterceptor(parser, fs)

        res = guard.evaluate("replace_file_content", {
            "TargetFile": "auth.py",
            "TargetContent": "def authenticate(user_id, token, secret): return True",
            "ReplacementContent": "def authenticate(user_id): return True"
        })
        self.assertEqual(res["decision"], "deny")
        self.assertIn("Formal Verification Gate", res["reason"])
        self.assertIn("required parameter count dropped", res["reason"])


class TestSqliteKnowledgeGraph(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.mktemp(suffix=".sqlite")
        self.kg = SqliteKnowledgeGraphAdapter(db_path=self.temp_db)

    def tearDown(self):
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)

    def test_record_and_query_decisions(self):
        self.kg.record_decision(
            decision_id="ADR-001",
            title="Shared Memory IPC over TCP Loopback",
            context="Inter-process communication between hook and daemon.",
            decision="Adopt multiprocessing.shared_memory ring buffer.",
            rationale="Reduces latency from ~1.5ms to <5us with zero-copy.",
            tags=["ipc", "hardware", "apple-silicon"],
        )

        results = self.kg.query_decisions(tag="ipc")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "ADR-001")
        self.assertIn("Shared Memory", results[0].title)


class TestSpeculativeEngineConsolidation(unittest.TestCase):

    def test_all_engines_implement_ispeculative_engine(self):
        llm = FakeLLMClient(responses=["def foo(): return 1", "def foo(): return 1"])
        parser = FakeAstParser()
        fs = FakeFileSystem({"foo.py": "def foo(): pass\n"})

        drafter = SpeculativeDrafter(llm, parser, fs)
        consensus = SpeculativeConsensusEngine(llm, parser)
        asym = AsymmetricSpeculativeDecoder(llm)
        tree = TreeSpeculativeDecoder()

        self.assertIsInstance(drafter, ISpeculativeEngine)
        self.assertIsInstance(consensus, ISpeculativeEngine)
        self.assertIsInstance(asym, ISpeculativeEngine)
        self.assertIsInstance(tree, ISpeculativeEngine)

        res_consensus = consensus.execute_speculation(instruction="fix bug", code="a = 1")
        self.assertIn("status", res_consensus)
        self.assertIn("effective_tok_s", res_consensus)

        res_tree = tree.execute_speculation()
        self.assertEqual(res_tree["status"], "error")


if __name__ == "__main__":
    unittest.main()
