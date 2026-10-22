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
from src.application.cognitive_arbiter import CognitiveArbiter
from src.application.escalation_circuit_breaker import EscalationCircuitBreaker
from src.domain.value_objects import CognitiveSystem, TaskScope


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


class TestCognitiveArbiter(unittest.TestCase):

    def setUp(self):
        self.arbiter = CognitiveArbiter()

    def test_classifies_mechanical_prompt_as_system_1(self):
        res = self.arbiter.classify_task("Corrigir typo na função compute", affected_files=["utils.py"])
        self.assertEqual(res.system, CognitiveSystem.SYSTEM_1_LOCAL_FAST)
        self.assertEqual(res.scope, TaskScope.ISOLATED_MODULE)
        self.assertGreater(res.confidence, 0.8)

    def test_classifies_cross_module_prompt_as_system_2(self):
        res = self.arbiter.classify_task(
            "Reestruturar arquitetura e quebra de contrato",
            affected_files=["auth.py", "database.py", "gateway.py"]
        )
        self.assertEqual(res.system, CognitiveSystem.SYSTEM_2_CLOUD_SLOW)
        self.assertEqual(res.scope, TaskScope.CROSS_MODULE_ARCHITECTURE)

    def test_classifies_high_cyclomatic_complexity_as_system_2(self):
        # Snippet with McCabe complexity > 10 (11 branches)
        high_cc_code = """
def complex_fn(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                return 1
            elif c == 0:
                return 2
        elif b == 0:
            return 3
    elif a == 0:
        while b > 0:
            b -= 1
            if c:
                return 4
    for x in range(10):
        if x == 5:
            return 5
    return 0
"""
        res = self.arbiter.classify_task("ajuste simples", affected_files=["app.py"], code_snippet=high_cc_code)
        self.assertEqual(res.system, CognitiveSystem.SYSTEM_2_CLOUD_SLOW)
        self.assertIn("McCabe", res.rationale)

    def test_token_budget_calculation(self):
        classif_sys1 = self.arbiter.classify_task("ajustar pep8", affected_files=["app.py"])
        budget_sys1 = self.arbiter.calculate_budget(classif_sys1)
        self.assertEqual(budget_sys1.max_system_2_tokens, 0)

        classif_sys2 = self.arbiter.classify_task("redesenhar arquitetura do cluster")
        budget_sys2 = self.arbiter.calculate_budget(classif_sys2)
        self.assertEqual(budget_sys2.max_system_2_tokens, 8000)
        self.assertEqual(budget_sys2.blueprint_budget, 500)


class TestEscalationCircuitBreaker(unittest.TestCase):

    def setUp(self):
        self.breaker = EscalationCircuitBreaker(max_attempts=2)

    def test_allows_retry_on_first_failure(self):
        can_retry = self.breaker.record_attempt("app.py", is_success=False, error_msg="SyntaxError line 10")
        self.assertTrue(can_retry)

    def test_trips_on_second_failure_and_synthesizes_handoff(self):
        self.breaker.record_attempt("app.py", is_success=False, error_msg="SyntaxError line 10")
        can_retry = self.breaker.record_attempt("app.py", is_success=False, error_msg="IndentationError line 12")
        self.assertFalse(can_retry)

        handoff = self.breaker.build_escalation_handoff("app.py", "add feature")
        self.assertEqual(handoff.file_path, "app.py")
        self.assertEqual(handoff.attempts_made, 2)
        self.assertIn("IndentationError", handoff.error_summary)
        summary_text = handoff.to_handoff_summary()
        self.assertIn("[SYSTEM 1 HANDOFF TO SYSTEM 2]", summary_text)
        self.assertIn("Stopped by Circuit Breaker", summary_text)


if __name__ == "__main__":
    unittest.main()

