"""
Unit Tests: VRAM Co-Residence & KV-Cache Optimizer (Abstraction 20).
Verifies calibrated num_keep injection, keep_alive: -1 zero cold-swap,
VRAM budget validation (<7.0 GB), and non-blocking warmup threading.
"""

import threading
import unittest

from src.application.inference_optimizer import InferenceOptimizer, CORE_PROFILES
from src.domain.value_objects import VramCoResidenceState


class TestInferenceOptimizer(unittest.TestCase):
    """Test suite for InferenceOptimizer and VramCoResidenceState."""

    def setUp(self) -> None:
        self.optimizer = InferenceOptimizer(ollama_base_url="http://127.0.0.1:11434")

    def test_build_request_options_injects_keep_alive_and_calibrated_num_keep(self) -> None:
        """Verifies injection of keep_alive: -1 and calibrated num_keep matching prompt size."""
        prompt_short = "You are a micro-worker."
        options_short = self.optimizer.build_request_options("smollm2:1.7b", prompt_short)

        self.assertEqual(options_short["keep_alive"], -1)
        self.assertTrue(options_short["f16_kv"])
        self.assertEqual(options_short["num_ctx"], 16384)
        # Should be at least default_num_keep (150)
        self.assertGreaterEqual(options_short["num_keep"], 150)

        # Longer prompt must yield higher num_keep
        prompt_long = "You are a meticulous skeptical code reviewer. " * 50
        options_long = self.optimizer.build_request_options("deepseek-r1:1.5b", prompt_long)
        self.assertGreater(options_long["num_keep"], options_short["num_keep"])

    def test_vram_coresidence_budget_validation(self) -> None:
        """Verifies budget limits and detection of all 3 core models resident in Metal GPU."""
        # 1. Compliant state (<7.0 GB)
        valid_state = VramCoResidenceState(
            active_models=("smollm2:1.7b", "deepseek-r1:1.5b", "qwen2.5-coder:7b"),
            total_vram_allocated_gb=6.8,
            vram_budget_limit_gb=7.0,
        )
        self.assertTrue(valid_state.is_budget_respected)
        self.assertTrue(valid_state.all_core_models_resident)

        # 2. Exceeded budget (>7.0 GB)
        exceeded_state = VramCoResidenceState(
            active_models=("smollm2:1.7b", "deepseek-r1:1.5b", "qwen2.5-coder:7b", "llama3:8b"),
            total_vram_allocated_gb=11.5,
            vram_budget_limit_gb=7.0,
        )
        self.assertFalse(exceeded_state.is_budget_respected)

        # 3. Incomplete trinity
        partial_state = VramCoResidenceState(
            active_models=("smollm2:1.7b", "qwen2.5-coder:7b"),
            total_vram_allocated_gb=5.7,
            vram_budget_limit_gb=7.0,
        )
        self.assertFalse(partial_state.all_core_models_resident)

    def test_telemetry_metrics_accumulation(self) -> None:
        """Verifies metrics tracking for cold swaps prevented and prefill tokens reused."""
        self.optimizer.build_request_options("smollm2:1.7b", "System prompt 1")
        self.optimizer.build_request_options("qwen2.5-coder:7b", "System prompt 2")

        metrics = self.optimizer.get_metrics()
        self.assertEqual(metrics.total_optimized_inferences, 2)
        self.assertEqual(metrics.cold_swaps_prevented, 2)
        self.assertGreater(metrics.prefill_tokens_reused, 400)
        self.assertGreater(metrics.estimated_ttft_saved_ms, 150.0)
        self.assertLessEqual(metrics.active_vram_gb, 7.0)

    def test_inspect_vram_fallback_and_core_profiles(self) -> None:
        """Verifies that inspect_vram returns a valid state and core profiles are configured."""
        self.assertIn("smollm2:1.7b", CORE_PROFILES)
        self.assertIn("deepseek-r1:1.5b", CORE_PROFILES)
        self.assertIn("qwen2.5-coder:7b", CORE_PROFILES)

        state = self.optimizer.inspect_vram()
        self.assertIsInstance(state, VramCoResidenceState)
        self.assertTrue(state.is_budget_respected)

    def test_warmup_async_starts_daemon_thread(self) -> None:
        """Verifies that warmup_async launches a non-blocking daemon thread."""
        thread = self.optimizer.warmup_async()
        self.assertIsInstance(thread, threading.Thread)
        self.assertTrue(thread.daemon)
        self.assertEqual(thread.name, "VramWarmupThread")


if __name__ == "__main__":
    unittest.main()
