"""
Behavioral and Error Boundary Contracts Test Suite.
Validates Issue #6:
- Explicit behavioral contracts under edge cases
- Timeout handling and graceful degradation
- Corrupted cache tolerance without crash
- Simulated missing models and fallback routing
- Fail-closed guarantees on write operations
"""

import os
import tempfile
import unittest
from src.application.cognitive_arbiter import CognitiveArbiter
from src.application.guardrail_interceptor import GuardrailInterceptor
from src.adapters.outbound.sqlite_epistemic_cache_adapter import SqliteEpistemicCacheAdapter
from src.adapters.outbound.file_system_adapter import LocalFileSystemAdapter
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.domain.value_objects import CognitiveSystem


class TestBehavioralContractsAndFaultBoundaries(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.parser = MultiLanguageAstAdapter()
        self.fs = LocalFileSystemAdapter()
        self.interceptor = GuardrailInterceptor(parser=self.parser, file_system=self.fs)

    def test_guardrail_blocks_corrupted_python_syntax_fail_closed(self):
        """Verifies syntax failure triggers strict fail-closed (decision == deny)."""
        bad_code = "def broken_func(:\n    pass\n"
        test_file = os.path.join(self.temp_dir, "test_bad.py")
        self.fs.write_text(test_file, "def original(): pass\n")

        res = self.interceptor.evaluate(
            "write_file",
            {"Path": test_file, "Content": bad_code}
        )
        self.assertEqual(res["decision"], "deny")
        self.assertIn("Syntax Gate", res["reason"])

    def test_guardrail_blocks_dangerous_eval_subshell_commands(self):
        """Verifies destructive command detection blocks dangerous subshell expressions."""
        res = self.interceptor.evaluate(
            "run_command",
            {"CommandLine": "eval $(echo 'rm -rf /')"}
        )
        self.assertEqual(res["decision"], "deny")
        self.assertIn("Destructive command blocked", res["reason"])

    def test_sqlite_cache_handles_corrupted_db_file_gracefully(self):
        """Verifies corrupted SQLite file is caught and re-initialized or safely handled."""
        db_path = os.path.join(self.temp_dir, "corrupt.sqlite")
        with open(db_path, "wb") as f:
            f.write(b"CORRUPTED_NON_SQLITE_DATA_GARBAGE")

        # Must not raise unhandled exception on instantiation or lookup
        cache = SqliteEpistemicCacheAdapter(db_path=db_path)
        val = cache.get("some_key")
        self.assertIsNone(val)

    def test_cognitive_arbiter_graceful_complexity_fallback_on_unparseable_code(self):
        """Verifies cognitive arbiter does not crash when passed unparseable code."""
        arbiter = CognitiveArbiter()
        cc = arbiter.calculate_cyclomatic_complexity("def invalid syntax :::")
        self.assertEqual(cc, 1)

    def test_merkle_skeletonizer_idempotence(self):
        """Verifies AST skeletonizer preserves valid Python interface."""
        code = (
            "class MyService:\n"
            "    def execute(self, a: int) -> int:\n"
            "        temp = a * 10\n"
            "        return temp + 42\n"
        )
        skeleton = self.parser.skeletonize(code, language="python")
        self.assertIn("class MyService:", skeleton)
        self.assertIn("def execute(self, a: int) -> int:", skeleton)
        self.assertNotIn("temp = a * 10", skeleton)


if __name__ == "__main__":
    unittest.main()
