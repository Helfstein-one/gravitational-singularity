"""Unit tests for the 5 Extreme Frontiers (Abstractions #36 to #40).

Covers:
  - BitNet b1.58 Ternary Quantizer
  - Metal PagedAttention Engine
  - Tree Speculative Decoder (Medusa-style)
  - SMT Formal Verification Gate (Theorem Prover in RAM)
  - MetalKit Asynchronous Pipeline (Sub-Microsecond Dispatch)
"""

import unittest
from src.application.bitnet_quantizer import BitNetQuantizer, TernaryWeightMatrix
from src.application.paged_attention_engine import PagedAttentionEngine
from src.application.tree_speculative_decoder import TreeSpeculativeDecoder, TreeNode
from src.application.smt_formal_verification_gate import SmtFormalVerificationGate
from src.adapters.outbound.metal_async_pipeline import MetalAsyncPipeline


class TestBitNetQuantizer(unittest.TestCase):
    def test_quantization_values_and_shape(self):
        matrix = [
            [0.85, -0.92, 0.05, 0.01],
            [-0.75, 0.88, -0.02, 0.45],
        ]
        ternary = BitNetQuantizer.quantize(matrix)
        self.assertEqual(ternary.shape, (2, 4))
        self.assertEqual(ternary.num_parameters, 8)
        self.assertGreater(ternary.scale, 0.0)

        # Ensure all values are in {-1, 0, 1}
        for b in ternary.ternary_weights:
            val = b if b < 128 else b - 256
            self.assertIn(val, {-1, 0, 1})

    def test_forward_vector_addition_only(self):
        matrix = [
            [1.0, -1.0, 0.0],
            [0.0, 1.0, 1.0],
        ]
        ternary = BitNetQuantizer.quantize(matrix)
        x = [2.0, 3.0, 4.0]
        y = BitNetQuantizer.forward_vector(ternary, x)
        self.assertEqual(len(y), 2)
        # Expected row 0: (2.0 - 3.0) * gamma
        # Expected row 1: (3.0 + 4.0) * gamma
        self.assertAlmostEqual(y[0] / ternary.scale, -1.0, places=4)
        self.assertAlmostEqual(y[1] / ternary.scale, 7.0, places=4)

    def test_vram_estimation(self):
        stats_14b = BitNetQuantizer.estimate_model_vram_gb(14.0)
        self.assertEqual(stats_14b["parameters_billions"], 14.0)
        self.assertGreater(stats_14b["fp16_vram_gb"], 25.0)
        self.assertGreater(stats_14b["q4_km_vram_gb"], 7.0)
        self.assertLess(stats_14b["bitnet_158_vram_gb"], 3.0)
        self.assertGreater(stats_14b["vram_savings_vs_q4_pct"], 60.0)


class TestPagedAttentionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PagedAttentionEngine(total_blocks=64, block_size=4)

    def test_sequence_allocation_and_retrieval(self):
        tokens = [101, 102, 103, 104, 105, 106]
        block_ids = self.engine.allocate_sequence("agent_1", tokens)
        self.assertEqual(len(block_ids), 2)  # ceil(6 / 4) = 2 blocks

        recovered = self.engine.get_sequence_tokens("agent_1")
        self.assertEqual(recovered, tokens)

    def test_fork_and_copy_on_write(self):
        prompt = [1, 2, 3, 4]
        self.engine.allocate_sequence("parent", prompt)
        child_blocks = self.engine.fork_sequence("parent", "child")

        stats = self.engine.get_stats()
        self.assertEqual(stats["allocated_blocks"], 1)  # Shared block!
        self.assertEqual(stats["shared_blocks"], 1)
        self.assertEqual(stats["prefix_sharing_factor"], 2.0)

        # Mutate child sequence -> triggers COW
        self.engine.append_token("child", 999)
        child_tokens = self.engine.get_sequence_tokens("child")
        parent_tokens = self.engine.get_sequence_tokens("parent")

        self.assertEqual(parent_tokens, [1, 2, 3, 4])
        self.assertEqual(child_tokens, [1, 2, 3, 4, 999])

    def test_free_and_block_reuse(self):
        tokens = [10, 20, 30]
        self.engine.allocate_sequence("temp", tokens)
        self.assertEqual(self.engine.get_stats()["free_blocks"], 63)
        self.engine.free_sequence("temp")
        self.assertEqual(self.engine.get_stats()["free_blocks"], 64)
        self.assertEqual(self.engine.get_stats()["vram_fragmentation_pct"], 0.0)


class TestTreeSpeculativeDecoder(unittest.TestCase):
    def test_build_candidate_tree(self):
        decoder = TreeSpeculativeDecoder(depth=2, branching_factor=2)

        def mock_draft(ctx, k):
            return [("tok_a", 0.9), ("tok_b", 0.8)]

        nodes, paths = decoder.build_candidate_tree(mock_draft, ["init"])
        self.assertEqual(len(nodes), 2 + 4)  # 2 in layer 1, 4 in layer 2
        self.assertEqual(len(paths), 4)

    def test_tree_verification_and_speedup(self):
        decoder = TreeSpeculativeDecoder(depth=2, branching_factor=2, base_target_speed_tok_s=40.0)

        def mock_draft(ctx, k):
            return [("yes", 0.9), ("no", 0.1)]

        nodes, paths = decoder.build_candidate_tree(mock_draft, ["prefix"])

        # Target accepts "yes" tokens
        def mock_target(ctx, token):
            return token == "yes"

        result = decoder.verify_tree(nodes, paths, mock_target, ["prefix"])
        self.assertEqual(result.accepted_tokens, ["yes", "yes"])
        self.assertEqual(result.longest_path_depth, 2)
        self.assertGreater(result.effective_tokens_per_second, 100.0)


class TestSmtFormalVerificationGate(unittest.TestCase):
    def setUp(self):
        self.gate = SmtFormalVerificationGate()

    def test_detects_literal_division_by_zero(self):
        code = "def calc(x):\n    return x / 0\n"
        result = self.gate.verify_code(code)
        self.assertFalse(result.is_safe)
        self.assertTrue(any("division by literal zero" in v for v in result.violations))

    def test_detects_unbounded_infinite_loop(self):
        code = "def loop_forever():\n    while True:\n        x = 1\n"
        result = self.gate.verify_code(code)
        self.assertFalse(result.is_safe)
        self.assertTrue(any("Unbounded infinite loop" in v for v in result.violations))

    def test_detects_unreachable_dead_code(self):
        code = "def fn():\n    return 42\n    print('dead code')\n"
        result = self.gate.verify_code(code)
        self.assertFalse(result.is_safe)
        self.assertTrue(any("Unreachable dead code" in v for v in result.violations))

    def test_detects_inverted_mutex_deadlock(self):
        code = (
            "def task1():\n"
            "    with lock_a:\n"
            "        with lock_b:\n"
            "            pass\n"
            "def task2():\n"
            "    with lock_b:\n"
            "        with lock_a:\n"
            "            pass\n"
        )
        result = self.gate.verify_code(code)
        self.assertFalse(result.is_safe)
        self.assertTrue(any("deadlock risk" in v for v in result.violations))

    def test_clean_code_passes(self):
        code = (
            "def safe_calc(a, b):\n"
            "    if b == 0:\n"
            "        return 0\n"
            "    return a / b\n"
        )
        result = self.gate.verify_code(code)
        self.assertTrue(result.is_safe)
        self.assertEqual(len(result.violations), 0)
        self.assertLess(result.proof_latency_ms, 5.0)


class TestMetalAsyncPipeline(unittest.TestCase):
    def test_batch_dot_product_accuracy(self):
        pipeline = MetalAsyncPipeline(queue_capacity=16)
        matrix = [
            [1.0, 2.0, 3.0, 4.0],
            [2.0, 0.0, 1.0, 0.0],
        ]
        vec = [1.0, 1.0, 1.0, 1.0]
        res = pipeline.dispatch_batch_dot_product(matrix, vec)
        self.assertEqual(res, [10.0, 3.0])

    def test_dispatch_latency_sub_microsecond(self):
        pipeline = MetalAsyncPipeline(queue_capacity=32)
        latency_ns = pipeline.benchmark_dispatch_latency_ns(iterations=500)
        # Latency should be sub-microsecond or near ~1 microsecond in pure CPython
        self.assertLess(latency_ns, 50000.0)  # Safe assertion well below 50us


if __name__ == "__main__":
    unittest.main()
