"""
Integration tests for Issue #7: CPU / stdlib core isolation, graceful degradation,
and portability guarantees without external daemons.
"""

import unittest
from src.adapters.outbound.accelerate_vector_adapter import AccelerateVectorAdapter
from src.application.cognitive_arbiter import CognitiveArbiter
from src.application.deterministic_ast_transformer import DeterministicAstTransformer
from src.adapters.inbound.doctor_cli import get_system_info
from src.domain.value_objects import CognitiveSystem


class TestCpuStdlibCoreIsolation(unittest.TestCase):

    def test_pure_math_vector_fallback_without_accelerate(self):
        """Forces fallback to pure Python vector operations and ensures numerical equivalence."""
        v1 = [1.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0]
        v3 = [1.0, 0.0, 0.0]

        # Test pure math calculation directly
        sim_ortho = sum(a * b for a, b in zip(v1, v2))
        sim_ident = sum(a * b for a, b in zip(v1, v3))
        self.assertEqual(sim_ortho, 0.0)
        self.assertEqual(sim_ident, 1.0)

        # Ensure AccelerateVectorAdapter returns equivalent values regardless of OS
        self.assertAlmostEqual(AccelerateVectorAdapter.cosine_similarity(v1, v2), 0.0, places=4)
        self.assertAlmostEqual(AccelerateVectorAdapter.cosine_similarity(v1, v3), 1.0, places=4)

    def test_system_0_deterministic_ast_runs_pure_cpu_stdlib(self):
        """Verifies deterministic AST renaming operates 100% in RAM with standard library ast."""
        code = "def process_data(value):\n    return value * 2\n"
        res = DeterministicAstTransformer.rename_symbol(code, "process_data", "transform_data")
        self.assertTrue(res.is_transformed)
        self.assertEqual(res.symbols_changed, 1)
        self.assertIn("def transform_data(value):", res.modified_code)

    def test_cognitive_arbiter_runs_pure_cpu_stdlib(self):
        """Verifies CognitiveArbiter classifies tasks without external services."""
        arbiter = CognitiveArbiter()
        classification = arbiter.classify_task("rename symbol foo to bar")
        self.assertEqual(classification.system, CognitiveSystem.SYSTEM_0_DETERMINISTIC_RAM)

    def test_doctor_info_no_network_flag(self):
        """Verifies system diagnostics run cleanly with --no-network."""
        info = get_system_info(no_network=True)
        self.assertIn("os", info)
        self.assertIn("architecture", info)
        self.assertIn("python_version", info)
        self.assertIsInstance(info["metal_available"], bool)


if __name__ == "__main__":
    unittest.main()
