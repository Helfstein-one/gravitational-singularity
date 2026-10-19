"""
Unit tests for Application Use Cases with pure mock/fake ports.
Zero external dependencies.
"""

import unittest
from typing import Any
from src.domain.value_objects import SyntaxValidationResult
from src.domain.entities import CodeChunk
from src.application.guardrail_interceptor import GuardrailInterceptor
from src.application.code_skeletonizer import CodeSkeletonizer
from src.application.speculative_drafter import SpeculativeDrafter


class FakeAstParser:
    def __init__(self, is_valid: bool = True, error_msg: str = ""):
        self.is_valid = is_valid
        self.error_msg = error_msg

    def validate_syntax(self, code: str, language: str) -> SyntaxValidationResult:
        return SyntaxValidationResult(
            is_valid=self.is_valid,
            language=language,
            error_message=self.error_msg,
            execution_time_ms=0.15
        )

    def skeletonize(self, code: str, language: str) -> str:
        return "class Service:\n    def run(): ..."

    def extract_chunks(self, file_path: str, code: str) -> list[CodeChunk]:
        return []


class FakeFileSystem:
    def __init__(self, files: dict[str, str] | None = None):
        self.files = files or {}

    def read_text(self, file_path: str) -> str:
        return self.files.get(file_path, "")

    def write_text(self, file_path: str, content: str) -> None:
        self.files[file_path] = content

    def exists(self, file_path: str) -> bool:
        return file_path in self.files


class FakeLLMClient:
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls = 0

    def generate(self, prompt: str, model: str, **kwargs: Any) -> str:
        resp = self.responses[min(self.calls, len(self.responses) - 1)]
        self.calls += 1
        return resp

    def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        return [0.1, 0.2, 0.3]

    def list_models(self) -> list[dict[str, Any]]:
        return []


class TestGuardrailInterceptor(unittest.TestCase):

    def test_blocks_dangerous_commands(self):
        fs = FakeFileSystem()
        parser = FakeAstParser()
        guard = GuardrailInterceptor(parser, fs)

        res = guard.evaluate("run_command", {"CommandLine": "rm -rf /"})
        self.assertEqual(res["decision"], "deny")

        res_git = guard.evaluate("run_command", {"CommandLine": "git push origin main --force"})
        self.assertEqual(res_git["decision"], "deny")

    def test_wraps_test_commands_with_test_slicer(self):
        fs = FakeFileSystem()
        parser = FakeAstParser()
        guard = GuardrailInterceptor(parser, fs)

        res = guard.evaluate("run_command", {"CommandLine": "pytest tests/"})
        self.assertEqual(res["decision"], "allow")
        self.assertEqual(res["overwrite"]["CommandLine"], "test-slicer pytest tests/")

    def test_wraps_verbose_commands_with_rtk(self):
        fs = FakeFileSystem()
        parser = FakeAstParser()
        guard = GuardrailInterceptor(parser, fs)

        res = guard.evaluate("run_command", {"CommandLine": "npm install"})
        self.assertEqual(res["decision"], "allow")
        self.assertEqual(res["overwrite"]["CommandLine"], "rtk npm install")

    def test_denies_invalid_syntax_on_replace_file(self):
        fs = FakeFileSystem(files={"app.py": "def foo(): pass"})
        invalid_parser = FakeAstParser(is_valid=False, error_msg="SyntaxError on line 1")
        guard = GuardrailInterceptor(invalid_parser, fs)

        res = guard.evaluate("replace_file_content", {
            "TargetFile": "app.py",
            "TargetContent": "pass",
            "ReplacementContent": "invalid python ("
        })
        self.assertEqual(res["decision"], "deny")
        self.assertIn("SyntaxError", res["reason"])

    def test_blocks_unsliced_view_file_on_long_files(self):
        long_content = "\n".join([f"def func_{i}(): return {i}" for i in range(150)])
        fs = FakeFileSystem(files={"service.py": long_content})
        parser = FakeAstParser()
        guard = GuardrailInterceptor(parser, fs)

        res = guard.evaluate("view_file", {"AbsolutePath": "service.py"})
        self.assertEqual(res["decision"], "deny")
        self.assertIn("Event Horizon AST Guard", res["reason"])

        # Allowed if sliced with StartLine and EndLine
        res_sliced = guard.evaluate("view_file", {"AbsolutePath": "service.py", "StartLine": 1, "EndLine": 30})
        self.assertEqual(res_sliced["decision"], "allow")


class TestCodeSkeletonizer(unittest.TestCase):

    def test_skeletonize_calculates_reduction(self):
        parser = FakeAstParser()
        skeletonizer = CodeSkeletonizer(parser)
        full_code = "class Service:\n    def run():\n        x = 1\n        y = 2\n        return x + y"
        compressed, reduction = skeletonizer.skeletonize(full_code)
        self.assertIn("...", compressed)
        self.assertGreaterEqual(reduction, 0.0)


class TestSpeculativeDrafter(unittest.TestCase):

    def test_draft_success_on_first_try(self):
        fs = FakeFileSystem(files={"app.py": "def compute(): return 10"})
        parser = FakeAstParser(is_valid=True)
        json_patch = '{"TargetContent": "return 10", "ReplacementContent": "return 42", "StartLine": 1, "EndLine": 1, "Explanation": "update"}'
        llm = FakeLLMClient(responses=[json_patch])

        drafter = SpeculativeDrafter(llm, parser, fs)
        res = drafter.draft_patch("app.py", "change 10 to 42")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["attempts"], 1)
        self.assertEqual(res["cost_cloud_usd"], 0.0)


if __name__ == "__main__":
    unittest.main()
