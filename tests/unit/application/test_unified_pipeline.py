"""
Unit tests for UnifiedExecutionPipeline, SmartErrorSlicer, and TelemetryEventEmitter.
Verifies end-to-end integration of Arbiter, Merkle, Skeptic, and Event Emitter.
"""

import unittest
from src.application.unified_execution_pipeline import UnifiedExecutionPipeline
from src.application.error_slicer import SmartErrorSlicer
from src.application.event_emitter import TelemetryEventEmitter
from tests.unit.application.test_use_cases import FakeLLMClient, FakeAstParser, FakeFileSystem


class TestUnifiedExecutionPipeline(unittest.TestCase):

    def test_pipeline_executes_with_adversarial_approval(self):
        code = "class Service:\n    def run(self):\n        return 1\n"
        fs = FakeFileSystem(files={"service.py": code})
        parser = FakeAstParser(is_valid=True)

        # Responses: 1 for Drafter patch, 1 for Skeptic review (clean)
        patch_json = '{"TargetContent": "return 1", "ReplacementContent": "return 42", "StartLine": 3, "EndLine": 3, "Explanation": "update"}'
        skeptic_json = '{"has_flaws": false, "flaw_category": "none", "critique": "clean"}'
        llm = FakeLLMClient(responses=[patch_json, skeptic_json])

        pipeline = UnifiedExecutionPipeline(llm=llm, parser=parser, file_system=fs)
        res = pipeline.execute_patch_pipeline(
            file_path="service.py",
            instruction="change 1 to 42",
            target_symbol="run",
            auto_apply=True
        )

        self.assertEqual(res.get("status"), "success")
        self.assertTrue(res.get("skeptic_approved"))
        self.assertTrue(res.get("applied_to_disk"))
        self.assertIn("return 42", fs.read_text("service.py"))

    def test_pipeline_executes_system_0_deterministic_rename_without_llm(self):
        code = "def calculate_old():\n    return 42\n"
        fs = FakeFileSystem(files={"calc.py": code})
        parser = FakeAstParser(is_valid=True)
        # Empty LLM responses - zero LLM inference needed!
        llm = FakeLLMClient(responses=[])

        pipeline = UnifiedExecutionPipeline(llm=llm, parser=parser, file_system=fs)
        res = pipeline.execute_patch_pipeline(
            file_path="calc.py",
            instruction="rename symbol calculate_old to calculate_new",
            auto_apply=True
        )

        self.assertEqual(res.get("status"), "success")
        self.assertEqual(res.get("cognitive_system"), "system_0_deterministic_ram")
        self.assertEqual(res.get("tokens_used"), 0)
        self.assertIn("calculate_new", fs.read_text("calc.py"))


class TestSmartErrorSlicer(unittest.TestCase):

    def test_slices_pytest_verbose_traceback(self):
        raw_tb = """
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/_pytest/runner.py", line 341, in from_call
    result: Optional[TResult] = func()
  File "/Users/dev/project/tests/test_auth.py", line 42, in test_login
    assert user.is_authenticated == True
AssertionError: assert False == True
"""
        sliced = SmartErrorSlicer.slice_traceback(raw_tb)
        self.assertIn("test_auth.py:42", sliced)
        self.assertIn("assert user.is_authenticated == True", sliced)
        self.assertIn("assert False == True", sliced)
        self.assertNotIn("_pytest/runner.py", sliced)


class TestTelemetryEventEmitter(unittest.TestCase):

    def test_event_subscription_and_dispatch(self):
        emitter = TelemetryEventEmitter(shm_buffer=None)
        captured = []

        def on_event(ev_type, payload):
            captured.append(payload)

        emitter.subscribe("test_topic", on_event)
        emitter.emit("test_topic", {"hello": "world"})

        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0]["hello"], "world")


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    TelemetryEventEmitter.cleanup()
