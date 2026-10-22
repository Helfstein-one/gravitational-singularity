"""
Unit tests for Epistemic Context Squeezer (Abstraction 15).
Verifies 3-level non-destructive virtual compaction, token ceiling enforcement,
preservation of recent turns, and telemetry aggregation.
"""

import copy
import unittest

from src.application.epistemic_context_squeezer import EpistemicContextSqueezer
from src.domain.value_objects import ContextSqueezePolicy


class TestEpistemicContextSqueezer(unittest.TestCase):
    def setUp(self) -> None:
        self.squeezer = EpistemicContextSqueezer()

    def test_empty_steps(self) -> None:
        result = self.squeezer.squeeze_transcript([])
        self.assertEqual(result.original_steps_count, 0)
        self.assertEqual(result.squeezed_tokens, 0)
        self.assertEqual(result.steps_payload, [])

    def test_non_destructive_guarantee(self) -> None:
        raw_steps = [
            {"type": "USER_INPUT", "content": "Initial prompt"},
            {
                "type": "PLANNER_RESPONSE",
                "content": "Running test suite\n" + "test_ok\n" * 50 + "exit code 0",
            },
            {"type": "PLANNER_RESPONSE", "content": "Recent step 1"},
            {"type": "PLANNER_RESPONSE", "content": "Recent step 2"},
        ]
        backup = copy.deepcopy(raw_steps)

        # Execute squeeze
        res = self.squeezer.squeeze_transcript(raw_steps)

        # Raw steps in memory must remain completely unaltered
        self.assertEqual(raw_steps, backup)
        # Squeezed steps must contain the collapsed output
        self.assertIn("Pruned Log", res.steps_payload[1]["content"])
        self.assertLess(res.squeezed_tokens, res.raw_tokens)
        self.assertGreater(res.compression_ratio_pct, 0.0)

    def test_preserves_recent_turns_and_user_input(self) -> None:
        policy = ContextSqueezePolicy(preserve_recent_turns=2)
        raw_steps = [
            {"type": "USER_INPUT", "content": "Fix the architecture"},
            {
                "type": "PLANNER_RESPONSE",
                "content": "Verbose command output: " + "data line\n" * 40,
            },
            {
                "type": "PLANNER_RESPONSE",
                "content": "Recent turn N-1 with critical code details",
            },
            {"type": "PLANNER_RESPONSE", "content": "Recent turn N final state"},
        ]

        res = self.squeezer.squeeze_transcript(raw_steps, policy)

        # Step 0 (USER_INPUT) must be intact
        self.assertEqual(res.steps_payload[0]["content"], "Fix the architecture")
        # Step 1 (older step) must be collapsed
        self.assertIn("Collapsed", res.steps_payload[1]["content"])
        # Step 2 and 3 (recent turns) must be 100% intact
        self.assertEqual(
            res.steps_payload[2]["content"],
            "Recent turn N-1 with critical code details",
        )
        self.assertEqual(
            res.steps_payload[3]["content"],
            "Recent turn N final state",
        )

    def test_respects_token_ceiling(self) -> None:
        # Create a transcript with 20 steps exceeding 200 tokens each
        policy = ContextSqueezePolicy(max_token_ceiling=150, preserve_recent_turns=2)
        raw_steps = [{"type": "USER_INPUT", "content": "Root request"}]
        for i in range(15):
            raw_steps.append(
                {
                    "type": "PLANNER_RESPONSE",
                    "content": f"Intermediary step {i} with repeated payload tokens " * 15,
                }
            )
        raw_steps.append({"type": "PLANNER_RESPONSE", "content": "Recent step N-1"})
        raw_steps.append({"type": "PLANNER_RESPONSE", "content": "Recent step N"})

        res = self.squeezer.squeeze_transcript(raw_steps, policy)

        # Squeezed tokens must be within ceiling
        self.assertLessEqual(res.squeezed_tokens, policy.max_token_ceiling)
        # Root prompt preserved
        self.assertEqual(res.steps_payload[0]["content"], "Root request")
        # Recent steps preserved
        self.assertEqual(res.steps_payload[-1]["content"], "Recent step N")
        self.assertEqual(res.steps_payload[-2]["content"], "Recent step N-1")

    def test_telemetry_metrics_aggregation(self) -> None:
        squeezer = EpistemicContextSqueezer()
        steps = [
            {"type": "USER_INPUT", "content": "Command"},
            {"type": "PLANNER_RESPONSE", "content": "pytest passed with exit code 0\n" + "line\n" * 50},
            {"type": "PLANNER_RESPONSE", "content": "Recent step N-1"},
            {"type": "PLANNER_RESPONSE", "content": "Recent step N final"},
        ]
        squeezer.squeeze_transcript(steps)
        metrics = squeezer.get_metrics()
        self.assertEqual(metrics.total_invocations, 1)
        self.assertGreater(metrics.total_tokens_pruned, 0)
        self.assertGreater(metrics.average_compression_ratio_pct, 0.0)


if __name__ == "__main__":
    unittest.main()
