"""
Integration tests for Adapters (AST Parsing, Local File System, Transcript Scanning).
"""

import os
import tempfile
import unittest
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.adapters.outbound.file_system_adapter import LocalFileSystemAdapter
from src.adapters.outbound.transcript_file_adapter import FileTranscriptRepository


class TestMultiLanguageAstAdapter(unittest.TestCase):

    def setUp(self):
        self.adapter = MultiLanguageAstAdapter()

    def test_python_valid_syntax(self):
        code = "def valid_func(x: int) -> int:\n    return x * 2\n"
        res = self.adapter.validate_syntax(code, "python")
        self.assertTrue(res.is_valid)
        self.assertGreater(res.execution_time_ms, 0.0)

    def test_python_invalid_syntax(self):
        code = "def bad_func(:\n    pass\n"
        res = self.adapter.validate_syntax(code, "python")
        self.assertFalse(res.is_valid)
        self.assertIn("Python SyntaxError", res.error_message)

    def test_json_valid_and_invalid(self):
        valid_json = '{"name": "event-horizon", "version": 2}'
        self.assertTrue(self.adapter.validate_syntax(valid_json, "json").is_valid)

        invalid_json = '{"name": "event-horizon",}'
        self.assertFalse(self.adapter.validate_syntax(invalid_json, "json").is_valid)

    def test_python_skeletonize(self):
        code = (
            "class Engine:\n"
            '    """Engine docstring."""\n'
            "    def start(self, mode: str) -> bool:\n"
            "        temp = 100\n"
            "        return True\n"
        )
        skel = self.adapter.skeletonize(code, "python")
        self.assertIn("class Engine", skel)
        self.assertIn("def start(self, mode: str) -> bool:", skel)
        self.assertIn("...", skel)
        self.assertNotIn("temp = 100", skel)

    def test_extract_chunks(self):
        code = "def worker(): pass\nclass Handler:\n    def execute(): pass"
        chunks = self.adapter.extract_chunks("app.py", code)
        self.assertGreaterEqual(len(chunks), 2)
        names = [c.name for c in chunks]
        self.assertIn("worker", names)
        self.assertIn("Handler", names)


class TestLocalFileSystemAdapter(unittest.TestCase):

    def test_read_write_roundtrip(self):
        fs = LocalFileSystemAdapter()
        with tempfile.NamedTemporaryFile("w", delete=False) as tf:
            path = tf.name
        try:
            fs.write_text(path, "Hello Hexagonal World")
            self.assertTrue(fs.exists(path))
            self.assertEqual(fs.read_text(path), "Hello Hexagonal World")
        finally:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    unittest.main()
