"""
Application Use Case: Epistemic Distiller.
Condenses long execution logs into concise, persistent SessionState markdown documents.
"""

from __future__ import annotations
import json
import re
from src.domain.entities import SessionState
from src.ports.outbound.llm_client_port import ILLMClient
from src.ports.outbound.transcript_repo_port import ITranscriptRepository
from src.ports.outbound.file_system_port import IFileSystemGateway
from src.application.epistemic_context_squeezer import EpistemicContextSqueezer


class EpistemicDistiller:
    """Condenses multi-turn transcript sessions using local hermes3:3b."""

    def __init__(
        self,
        llm: ILLMClient,
        repo: ITranscriptRepository,
        file_system: IFileSystemGateway,
        distiller_model: str = "hermes3:3b",
        squeezer: Optional[EpistemicContextSqueezer] = None,
    ):
        self.llm = llm
        self.repo = repo
        self.fs = file_system
        self.distiller_model = distiller_model
        self.squeezer = squeezer or EpistemicContextSqueezer()

    def distill_active_session(self, output_path: str) -> SessionState:
        session_id = self.repo.get_latest_session_id()
        raw_records = list(self.repo.iter_session_records(session_id))

        # Squeeze raw transcript under 8k token envelope preserving essential turns
        squeezed = self.squeezer.squeeze_transcript(raw_records)
        records = squeezed.steps_payload

        # Extract recent user inputs and tool events
        user_prompts = []
        tools_used = []
        for r in records:
            if r.get("source") == "USER_EXPLICIT" and r.get("content"):
                user_prompts.append(r.get("content", ""))
            for t in r.get("tool_calls", []):
                tools_used.append(t.get("name", ""))

        summary_input = (
            f"User Goals:\n" + "\n".join(user_prompts[-5:]) + "\n\n"
            f"Key Tools Executed: {', '.join(set(tools_used))}\n"
        )

        system_prompt = (
            "You are an epistemic distiller. Output a JSON object with this structure:\n"
            "{\n"
            '  "core_objective": "1-2 sentence core goal",\n'
            '  "verified_facts": ["fact 1", "fact 2"],\n'
            '  "constraints": ["constraint 1"],\n'
            '  "next_steps": ["step 1"]\n'
            "}\n"
            "Pure JSON only."
        )

        raw = self.llm.generate(
            prompt=summary_input,
            model=self.distiller_model,
            system_prompt=system_prompt,
            response_format="json"
        )

        try:
            cleaned = re.sub(r"^```json\s*", "", raw.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            parsed = json.loads(cleaned)
        except Exception:
            parsed = {
                "core_objective": user_prompts[-1] if user_prompts else "Active session",
                "verified_facts": [f"Total steps: {len(records)}"],
                "constraints": ["Local-first execution"],
                "next_steps": ["Continue engineering sprint"]
            }

        state = SessionState(
            session_id=session_id,
            core_objective=parsed.get("core_objective", "Ongoing task"),
            verified_facts=parsed.get("verified_facts", []),
            constraints_and_decisions=parsed.get("constraints", []),
            next_steps=parsed.get("next_steps", [])
        )

        self.fs.write_text(output_path, state.to_markdown())
        return state
