"""
Unit tests for DeterministicAstTransformer (System 0 - Zero LLM Bypass).
"""

import unittest
from src.application.deterministic_ast_transformer import DeterministicAstTransformer


class TestDeterministicAstTransformer(unittest.TestCase):

    def test_rename_variable_and_function_symbols(self):
        source = (
            "def calculate_total(items):\n"
            "    items = [x for x in items]\n"
            "    return calculate_total\n"
        )
        res = DeterministicAstTransformer.rename_symbol(source, "calculate_total", "compute_sum")
        self.assertTrue(res.is_transformed)
        self.assertEqual(res.symbols_changed, 2)
        self.assertIn("def compute_sum(items):", res.modified_code)
        self.assertIn("return compute_sum", res.modified_code)
        self.assertLess(res.execution_time_ms, 20.0)

    def test_rename_nonexistent_symbol_returns_unmodified(self):
        source = "def foo(): return 1"
        res = DeterministicAstTransformer.rename_symbol(source, "bar", "baz")
        self.assertFalse(res.is_transformed)
        self.assertEqual(res.symbols_changed, 0)
        self.assertEqual(res.modified_code, source)

    def test_update_docstring_existing(self):
        source = 'def run():\n    """Old doc."""\n    return True\n'
        res = DeterministicAstTransformer.update_docstring(source, "run", "New docstring.")
        self.assertTrue(res.is_transformed)
        self.assertIn("New docstring.", res.modified_code)
        self.assertNotIn("Old doc.", res.modified_code)

    def test_update_docstring_insert_new(self):
        source = "def run():\n    return True\n"
        res = DeterministicAstTransformer.update_docstring(source, "run", "Added docstring.")
        self.assertTrue(res.is_transformed)
        self.assertIn("Added docstring.", res.modified_code)


if __name__ == "__main__":
    unittest.main()
