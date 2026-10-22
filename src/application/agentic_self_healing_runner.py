"""
Application Use Case: Agentic Self-Healing Test Runner (Closed Local Loop).
Upon detecting unit test assertion failure, the Skeptic (1.5B) and Builder (7B)
collaborate autonomously in an in-memory sandbox to synthesize and re-test corrections
(maximum 2 local turns, $0 cloud cost), delivering verified green code.
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from src.ports.outbound.llm_client_port import ILLMClient
from src.ports.outbound.ast_parser_port import IAstParser
from src.ports.outbound.file_system_port import IFileSystemGateway
from src.application.error_slicer import SmartErrorSlicer


@dataclass(frozen=True)
class SelfHealingResult:
    is_healed: bool
    iterations_used: int
    culprit_file: str
    original_error: str
    applied_patch: Optional[Dict[str, Any]]
    cloud_escalation_needed: bool
    status_summary: str


class AgenticSelfHealingRunner:
    """
    Closed loop autonomous repair engine for test failures.
    """

    def __init__(
        self,
        llm_client: ILLMClient,
        ast_parser: IAstParser,
        file_system: IFileSystemGateway,
        max_retries: int = 2,
    ) -> None:
        self.llm = llm_client
        self.parser = ast_parser
        self.fs = file_system
        self.max_retries = max_retries

    def heal_test_failure(
        self,
        raw_traceback: str,
        test_executor: Callable[[str], bool],
        target_file: str,
    ) -> SelfHealingResult:
        """
        Executes autonomous self-healing loop in RAM.
        `test_executor` is a callback that runs the test and returns True if passing.
        """
        sliced_error = SmartErrorSlicer.slice_traceback(raw_traceback)

        if not self.fs.exists(target_file):
            return SelfHealingResult(
                is_healed=False,
                iterations_used=0,
                culprit_file=target_file,
                original_error=sliced_error,
                applied_patch=None,
                cloud_escalation_needed=True,
                status_summary=f"File not found: {target_file}",
            )

        current_code = self.fs.read_text(target_file)

        for attempt in range(1, self.max_retries + 1):
            # 1. Skeptic analyzes the invariant flaw
            skeptic_prompt = (
                f"Analyze this test assertion failure and identify the exact code defect:\n"
                f"Error:\n{sliced_error}\n\n"
                f"Target Code:\n{current_code}\n\n"
                f"State the root cause in 1 sentence."
            )
            analysis = self.llm.generate(prompt=skeptic_prompt, model="deepseek-r1:1.5b")

            # 2. Builder synthesizes the surgical fix
            builder_prompt = (
                f"Synthesize the surgical correction for this flaw:\n"
                f"Analysis: {analysis}\n"
                f"Source:\n{current_code}\n\n"
                f"Output strictly JSON with format:\n"
                f'{{"TargetContent": "old_code", "ReplacementContent": "new_code"}}'
            )
            patch_raw = self.llm.generate(prompt=builder_prompt, model="qwen2.5-coder:7b", response_format="json")

            import json
            try:
                patch = json.loads(patch_raw)
            except Exception:
                continue

            target_c = patch.get("TargetContent", "")
            replace_c = patch.get("ReplacementContent", "")

            if target_c in current_code:
                candidate_code = current_code.replace(target_c, replace_c, 1)

                # 3. In-memory AST syntax validation
                val_res = self.parser.validate_syntax(candidate_code, "python")
                if not val_res.is_valid:
                    continue

                # 4. Simulate test execution
                if test_executor(candidate_code):
                    # Test passed! Commit candidate to disk
                    self.fs.write_text(target_file, candidate_code)
                    return SelfHealingResult(
                        is_healed=True,
                        iterations_used=attempt,
                        culprit_file=target_file,
                        original_error=sliced_error,
                        applied_patch=patch,
                        cloud_escalation_needed=False,
                        status_summary=f"Self-healed autonomously on iteration {attempt} ($0 cloud cost).",
                    )

        # Retries exhausted: escalate to cloud
        return SelfHealingResult(
            is_healed=False,
            iterations_used=self.max_retries,
            culprit_file=target_file,
            original_error=sliced_error,
            applied_patch=None,
            cloud_escalation_needed=True,
            status_summary="Autonomous repair exhausted 2 attempts; escalating to Gemini Pro.",
        )
