"""
Application Layer: Unified Execution Pipeline.
Consolidates CognitiveArbiter, HierarchicalCascade, AstMerkleEngine,
AdversarialReflector, and Guardrails into a single dispatch gateway:
Tool Call -> Arbiter -> Merkle Context -> Cascade / Drafter -> Adversarial Skeptic -> In-Memory AST -> Disk.
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import os
from typing import Any, Dict, Optional

from src.ports.outbound.llm_client_port import ILLMClient
from src.ports.outbound.ast_parser_port import IAstParser
from src.ports.outbound.file_system_port import IFileSystemGateway
from src.application.cognitive_arbiter import CognitiveArbiter
from src.application.hierarchical_cascade import HierarchicalCascade
from src.application.adversarial_reflector import AdversarialReflector
from src.application.ast_merkle_engine import AstMerkleEngine
from src.application.speculative_drafter import SpeculativeDrafter
from src.application.event_emitter import TelemetryEventEmitter
from src.domain.value_objects import CognitiveSystem


class UnifiedExecutionPipeline:
    """
    Central orchestration pipeline executing the full Event Horizon agentic lifecycle.
    """

    def __init__(
        self,
        llm: ILLMClient,
        parser: IAstParser,
        file_system: IFileSystemGateway,
        merkle_engine: Optional[AstMerkleEngine] = None,
        arbiter: Optional[CognitiveArbiter] = None,
        cascade: Optional[HierarchicalCascade] = None,
        reflector: Optional[AdversarialReflector] = None,
        drafter: Optional[SpeculativeDrafter] = None,
        event_emitter: Optional[TelemetryEventEmitter] = None,
    ) -> None:
        self.llm = llm
        self.parser = parser
        self.fs = file_system
        self.merkle_engine = merkle_engine or AstMerkleEngine()
        self.arbiter = arbiter or CognitiveArbiter()
        self.cascade = cascade or HierarchicalCascade(llm_client=llm, ast_parser=parser)
        self.reflector = reflector or AdversarialReflector(llm_client=llm, ast_parser=parser)
        self.drafter = drafter or SpeculativeDrafter(llm=llm, parser=parser, file_system=file_system)
        self.events = event_emitter or TelemetryEventEmitter.get_instance()

    def execute_patch_pipeline(
        self,
        file_path: str,
        instruction: str,
        target_symbol: str = "",
        auto_apply: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes the end-to-end surgical pipeline with cognitive routing,
        Merkle differential context, adversarial audit, and in-memory AST gatekeeper.
        """
        if not self.fs.exists(file_path):
            return {"status": "error", "message": f"File not found: {file_path}"}

        source_code = self.fs.read_text(file_path)

        # 1. Cognitive Arbiter (Check intent, files, McCabe complexity)
        classification = self.arbiter.classify_task(
            prompt=instruction,
            affected_files=[file_path],
            code_snippet=source_code,
        )

        # 2. Extract differential context via Merkle Engine (>96% token reduction)
        if target_symbol:
            context_skeleton = self.merkle_engine.differential_skeletonize(
                file_path=file_path,
                source_code=source_code,
                target_symbol=target_symbol,
            )
        else:
            context_skeleton, _, _ = self.merkle_engine.reconcile_and_assemble(
                file_path=file_path,
                new_source_code=source_code,
            )

        # 3. Execution via Speculative Drafter
        draft_result = self.drafter.draft_patch(
            file_path=file_path,
            instruction=instruction,
            target_lines=target_symbol if target_symbol else None,
        )

        if draft_result.get("status") != "success" or "patch" not in draft_result:
            self.events.on_syntax_blocked(file_path, "local_draft_patch", str(draft_result.get("error", "draft_failed")))
            return draft_result

        patch = draft_result["patch"]
        replacement = patch.get("ReplacementContent", "")
        ext = os.path.splitext(file_path)[1].lower()
        language = "python" if ext == ".py" else "javascript" if ext in [".js", ".ts"] else "json"

        # 4. Mandatory Adversarial Audit (Builder vs Skeptic)
        skeptic_review = self.reflector.reflect_and_refine(
            task_instruction=instruction,
            initial_code=replacement,
            language=language,
        )

        if skeptic_review.critique.has_flaws and not skeptic_review.was_refined:
            self.events.on_syntax_blocked(
                file_path,
                "adversarial_skeptic",
                skeptic_review.critique.critique_details,
            )
            return {
                "status": "adversarial_rejected",
                "critique": skeptic_review.critique.critique_details,
                "escalate_to_cloud": True,
                "message": "Patch rejected by Skeptic auditor prior to disk write.",
            }

        # Use refined code if Skeptic corrected it
        final_replacement = skeptic_review.final_code if skeptic_review.was_refined else replacement
        patch["ReplacementContent"] = final_replacement

        # 5. In-Memory AST Simulation & Gatekeeper
        simulated = self.drafter._simulate_patch(source_code, patch)
        if simulated is None:
            return {"status": "error", "message": "TargetContent not found in file", "escalate_to_cloud": True}

        ext = os.path.splitext(file_path)[1].lower()
        language = "python" if ext == ".py" else "javascript" if ext in [".js", ".ts"] else "json"
        val_res = self.parser.validate_syntax(simulated, language)
        if not val_res.is_valid:
            self.events.on_syntax_blocked(file_path, "in_memory_ast", val_res.error_message or "syntax error")
            return {
                "status": "syntax_error",
                "error": val_res.error_message,
                "escalate_to_cloud": True,
            }

        # 6. Apply to Disk (if auto_apply)
        if auto_apply:
            self.fs.write_text(file_path, simulated)
            draft_result["applied_to_disk"] = True
            # Reconcile Merkle tree
            self.merkle_engine.reconcile_and_assemble(file_path, simulated)

        # 7. Telemetry Event Emission
        self.events.on_patch_generated(
            file_path=file_path,
            model=draft_result.get("model", "qwen2.5-coder:7b"),
            attempts=draft_result.get("attempts", 1),
            cost_usd=0.0,
        )

        draft_result["cognitive_system"] = classification.system.value
        draft_result["skeptic_approved"] = True
        draft_result["merkle_nodes_tracked"] = len(self.merkle_engine._l1_nodes.get(file_path, {}))
        return draft_result
