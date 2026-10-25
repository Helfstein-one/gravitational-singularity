"""
Application Use Case: Speculative Local-First Drafter.
Generates zero-cloud surgical patches via Qwen 7B with in-memory AST validation and 1-shot self-refine.
"""

from __future__ import annotations
import json
import os
import re
from typing import Any, Optional
from src.ports.outbound.llm_client_port import ILLMClient
from src.ports.outbound.ast_parser_port import IAstParser
from src.ports.outbound.file_system_port import IFileSystemGateway
from src.application.token_entropy_guard import TokenEntropyGuard


SURGICAL_PATCH_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "node_id": {"type": "string"},
        "target_symbol": {"type": "string"},
        "TargetContent": {"type": "string"},
        "ReplacementContent": {"type": "string"},
    },
    "required": ["TargetContent", "ReplacementContent"],
}


class SpeculativeDrafter:
    """Coordinates local model drafting, AST dry-run testing and fallback escalation."""

    def __init__(
        self,
        llm: ILLMClient,
        parser: IAstParser,
        file_system: IFileSystemGateway,
        model_name: str = "qwen2.5-coder:7b",
        entropy_guard: Optional[TokenEntropyGuard] = None,
    ):
        self.llm = llm
        self.parser = parser
        self.fs = file_system
        self.model_name = model_name
        self.entropy_guard = entropy_guard or TokenEntropyGuard()

    def execute_speculation(self, **kwargs: Any) -> dict[str, Any]:
        """Unified speculative engine execution conforming to ISpeculativeEngine."""
        file_path = kwargs.get("file_path", "")
        instruction = kwargs.get("instruction", "")
        target_lines = kwargs.get("target_lines")
        res = self.draft_patch(file_path=file_path, instruction=instruction, target_lines=target_lines)
        return {
            "status": "success" if res.get("status") in ("success", "fallback") else "error",
            "effective_tok_s": 40.0,
            "tokens_saved": 0,
            "result": res,
        }

    def draft_patch(
        self,
        file_path: str,
        instruction: str,
        target_lines: str | None = None
    ) -> dict[str, Any]:
        """Generates patch, dry-runs AST in memory, applies or escalates."""
        if not self.fs.exists(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}

        full_content = self.fs.read_text(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        language = "python" if ext == ".py" else "javascript" if ext in [".js", ".ts"] else "json"

        # Construct concise prefix-cached prompt (<35 tokens system prompt)
        system_prompt = (
            "You are an expert local code editor executing surgical Ponytail patches. "
            "Output strictly valid JSON with keys TargetContent and ReplacementContent. "
            "Zero conversational filler or markdown."
        )

        user_prompt = f"File: {file_path}\nInstruction: {instruction}\n"
        if target_lines:
            user_prompt += f"Target Range: {target_lines}\n"
        user_prompt += f"File Content:\n```\n{full_content}\n```"

        # Attempt 1
        raw_resp = self.llm.generate(
            prompt=user_prompt,
            model=self.model_name,
            system_prompt=system_prompt,
            response_format=SURGICAL_PATCH_SCHEMA
        )

        patch = self._parse_json(raw_resp)
        if not patch:
            return {"status": "error", "message": "Failed to parse JSON response from local model", "escalate_to_cloud": True}

        # Dry-run validation
        simulated = self._simulate_patch(full_content, patch)
        if simulated is None:
            return {"status": "error", "message": "TargetContent not found in file", "escalate_to_cloud": True}

        val_res = self.parser.validate_syntax(simulated, language)
        if val_res.is_valid:
            return self._build_success(patch, val_res.execution_time_ms, attempts=1)

        # Attempt 2: 1-shot self-refine retry
        retry_prompt = (
            f"{user_prompt}\n\n"
            f"PREVIOUS ATTEMPT FAILED SYNTAX VALIDATION:\n"
            f"Error: {val_res.error_message}\n"
            f"Fix the error, ensure strict indentation/syntax, and output the corrected JSON patch."
        )
        raw_resp2 = self.llm.generate(
            prompt=retry_prompt,
            model=self.model_name,
            system_prompt=system_prompt,
            response_format=SURGICAL_PATCH_SCHEMA
        )
        patch2 = self._parse_json(raw_resp2)
        if patch2:
            simulated2 = self._simulate_patch(full_content, patch2)
            if simulated2 is not None:
                val_res2 = self.parser.validate_syntax(simulated2, language)
                if val_res2.is_valid:
                    return self._build_success(patch2, val_res2.execution_time_ms, attempts=2)

        return {
            "status": "failed_validation",
            "error": val_res.error_message,
            "escalate_to_cloud": True,
            "message": "Local patch failed in-memory AST validation after retry. Escalating to cloud."
        }

    def _parse_json(self, raw_resp: str) -> dict[str, Any] | None:
        try:
            cleaned = re.sub(r"^```json\s*", "", raw_resp.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned)
        except Exception:
            return None

    def _simulate_patch(self, original: str, patch: dict[str, Any]) -> str | None:
        tgt = patch.get("TargetContent") or patch.get("target_content", "")
        rep = patch.get("ReplacementContent") or patch.get("new_code", "")
        if tgt and tgt in original:
            return original.replace(tgt, rep, 1)
        return None

    def _build_success(self, patch: dict[str, Any], val_ms: float, attempts: int) -> dict[str, Any]:
        return {
            "status": "success",
            "model": self.model_name,
            "cost_cloud_usd": 0.0,
            "validation_ms": val_ms,
            "attempts": attempts,
            "patch": patch
        }
