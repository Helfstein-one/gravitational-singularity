"""
Unit tests for Domain Entities, Value Objects, and Domain Invariants.
Zero external dependencies (unittest only).
"""

import unittest
from src.domain.value_objects import TokenCount, CostUSD, DiffPatch, ModelTier, SyntaxValidationResult
from src.domain.entities import SessionState, CodeChunk, StorytellingMetrics, SkillMetrics
from src.domain.exceptions import SyntaxValidationError, PatchApplicationError, ModelInferenceError


class TestDomainValueObjects(unittest.TestCase):

    def test_token_count_positive_and_conversion(self):
        tc = TokenCount(100_000)
        self.assertEqual(tc.value, 100_000)
        books = tc.to_books()
        self.assertGreater(books, 0.0)

    def test_token_count_negative_raises_value_error(self):
        with self.assertRaises(ValueError):
            TokenCount(-5)

    def test_cost_usd_conversions(self):
        cost = CostUSD(10.0)
        self.assertEqual(cost.to_brl(usd_brl_rate=5.50), 55.0)
        self.assertEqual(cost.to_coffees(coffee_price_brl=11.0, usd_brl_rate=5.50), 5.0)

    def test_diff_patch_validation(self):
        patch = DiffPatch(
            target_file="app.py",
            target_content="def foo(): pass",
            replacement_content="def foo(): return 42",
            start_line=1,
            end_line=2
        )
        self.assertEqual(patch.target_file, "app.py")

        with self.assertRaises(ValueError):
            DiffPatch("app.py", "a", "b", start_line=0, end_line=2)

        with self.assertRaises(ValueError):
            DiffPatch("app.py", "a", "b", start_line=5, end_line=3)

    def test_model_tier_values(self):
        self.assertEqual(ModelTier.LOCAL_TIER_0.value, "tier_0_local")
        self.assertEqual(ModelTier.CLOUD_FLASH_LITE.value, "tier_1_flash_lite")


class TestDomainEntities(unittest.TestCase):

    def test_session_state_to_markdown(self):
        state = SessionState(
            session_id="test-session-123",
            core_objective="Modularizar arquitetura em Hexagonal",
            verified_facts=["Python 3.14 ativo", "Porta 7890 operacional"],
            constraints_and_decisions=["Zero libs externas", "Thin facades em scripts/"],
            next_steps=["Testar unitários", "Atualizar README"]
        )
        md = state.to_markdown()
        self.assertIn("Modularizar arquitetura em Hexagonal", md)
        self.assertIn("Python 3.14 ativo", md)
        self.assertIn("Zero libs externas", md)
        self.assertIn("Testar unitários", md)

    def test_code_chunk_creation(self):
        chunk = CodeChunk(
            file_path="src/main.py",
            start_line=10,
            end_line=25,
            node_type="function",
            name="process_event",
            code="def process_event(): pass"
        )
        self.assertEqual(chunk.name, "process_event")
        self.assertEqual(len(chunk.embedding), 0)


if __name__ == "__main__":
    unittest.main()
