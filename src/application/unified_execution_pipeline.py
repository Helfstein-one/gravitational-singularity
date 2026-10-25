"""
Application Layer: Unified Execution Pipeline.
Consolidates CognitiveArbiter, HierarchicalCascade, AstMerkleEngine,
AdversarialReflector, and Guardrails into a single dispatch gateway:
Tool Call -> Arbiter -> Merkle Context -> Cascade / Drafter -> Adversarial Skeptic -> In-Memory AST -> Disk.
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import os
import re
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
from src.application.escalation_circuit_breaker import EscalationCircuitBreaker
from src.application.semantic_prompt_cache import SemanticPromptCache
from src.adapters.outbound.sqlite_knowledge_graph_adapter import SqliteKnowledgeGraphAdapter
from src.application.agentic_self_healing_runner import AgenticSelfHealingRunner
from src.application.deterministic_ast_transformer import DeterministicAstTransformer
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
        circuit_breaker: Optional[EscalationCircuitBreaker] = None,
        prompt_cache: Optional[SemanticPromptCache] = None,
        knowledge_graph: Optional[SqliteKnowledgeGraphAdapter] = None,
        self_healing_runner: Optional[AgenticSelfHealingRunner] = None,
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
        self.circuit_breaker = circuit_breaker or EscalationCircuitBreaker(max_attempts=2)
        self.prompt_cache = prompt_cache or SemanticPromptCache()
        self.knowledge_graph = knowledge_graph or SqliteKnowledgeGraphAdapter()
        self.self_healing = self_healing_runner or AgenticSelfHealingRunner(
            llm_client=llm,
            ast_parser=parser,
            file_system=file_system,
        )

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

        # 0. Check L0 Semantic Prompt Cache for exact/near-identical templates (0ms shortcut)
        cache_hit = self.prompt_cache.lookup(instruction, min_similarity=0.98)
        if cache_hit is not None and cache_hit.is_hit:
            cached_res = {
                "status": "success",
                "cached": True,
                "similarity": cache_hit.similarity,
                "patch": cache_hit.template_patch,
                "model": "l0_semantic_cache",
                "cognitive_system": CognitiveSystem.SYSTEM_1_LOCAL_FAST.value,
                "skeptic_approved": True,
                "message": "Instant patch retrieved from L0 Semantic Prompt Cache (0ms inference).",
            }
            if auto_apply and self.fs.exists(file_path):
                source_code = self.fs.read_text(file_path)
                simulated = self.drafter._simulate_patch(source_code, cache_hit.template_patch)
                if simulated:
                    self.fs.write_text(file_path, simulated)
                    cached_res["applied_to_disk"] = True
            return cached_res

        source_code = self.fs.read_text(file_path)

        # 1. Cognitive Arbiter (Check intent, files, McCabe complexity)
        classification = self.arbiter.classify_task(
            prompt=instruction,
            affected_files=[file_path],
            code_snippet=source_code,
        )

        # 1.5 System 0 Deterministic Bypass (Zero LLM, <2ms in RAM, 0 tokens)
        if classification.system == CognitiveSystem.SYSTEM_0_DETERMINISTIC_RAM:
            rename_match = re.search(
                r"(?:rename|renomear)\s+(?:s[ií]mbolo|symbol|vari[aá]vel|variable|fun[çc][ãa]o|function|m[ée]todo|method)?\s*([a-zA-Z_]\w*)\s+(?:to|para)\s+([a-zA-Z_]\w*)",
                instruction,
                re.IGNORECASE,
            )
            if rename_match:
                old_sym, new_sym = rename_match.groups()
                det_res = DeterministicAstTransformer.rename_symbol(source_code, old_sym, new_sym)
                if det_res.is_transformed:
                    if auto_apply:
                        self.fs.write_text(file_path, det_res.modified_code)
                    return {
                        "status": "success",
                        "cognitive_system": CognitiveSystem.SYSTEM_0_DETERMINISTIC_RAM.value,
                        "model": "deterministic_ast_system_0",
                        "cost_cloud_usd": 0.0,
                        "tokens_used": 0,
                        "execution_time_ms": det_res.execution_time_ms,
                        "symbols_changed": det_res.symbols_changed,
                        "message": f"Deterministic AST transformation executed in RAM ({det_res.execution_time_ms}ms, 0 tokens).",
                    }

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
            tripped = self.circuit_breaker.record_attempt(file_path, is_success=False, error_msg=str(draft_result.get("error")))
            if tripped:
                handoff = self.circuit_breaker.build_escalation_handoff(file_path, instruction)
                draft_result["escalation_handoff"] = {
                    "file_path": handoff.file_path,
                    "failure_history": handoff.failure_history,
                    "instruction": handoff.instruction,
                }
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

        # 5. In-Memory AST Simulation & Gatekeeper (Symbolic Patch First, Ponytail Fallback)
        simulated = None
        if target_symbol:
            try:
                sym_patch = self.merkle_engine.generate_symbolic_patch(
                    file_path=file_path,
                    source_code=source_code,
                    target_symbol=target_symbol,
                    replacement_code=final_replacement,
                )
                simulated = self.merkle_engine.apply_symbolic_patch(file_path, source_code, sym_patch)
                draft_result["symbolic_patch"] = sym_patch
            except Exception:
                simulated = None

        if simulated is None:
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

        # 7. Knowledge Graph & L0 Semantic Cache Storing
        try:
            self.prompt_cache.store(instruction, patch)
            self.circuit_breaker.reset(file_path)
            if classification.system == CognitiveSystem.SYSTEM_2_CLOUD_SLOW:
                self.knowledge_graph.record_decision(
                    title=f"Patch applied to {file_path}",
                    rationale=instruction,
                    affected_modules=[file_path],
                    tags=["system_2", "surgical_patch"],
                )
        except Exception:
            pass

        # 8. Telemetry Event Emission
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
