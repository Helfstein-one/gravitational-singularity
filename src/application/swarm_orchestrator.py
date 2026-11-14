from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from src.application.dynamic_agent_governor import DynamicAgentGovernor
from src.application.repo_map_pagerank_engine import RepoMapPageRankEngine
from src.application.hybrid_routing_engine import HybridRoutingEngine
from src.ports.inbound.hybrid_routing_port import ExecutionTier

@dataclass
class SwarmAgentTask:
    task_id: str
    role: str  # "builder", "skeptic", "scout", "distiller"
    instruction: str
    target_file: Optional[str] = None

@dataclass
class SwarmTaskResult:
    task_id: str
    role: str
    status: str
    output: Any
    vram_used_gb: float

class SwarmOrchestrator:
    """
    Coordinates an agent swarm (Builder, Skeptic, Scout, Distiller) under strict
    Apple Silicon VRAM governance (8.5 GB cap) and shared Repo-Map context.
    """

    ROLE_MODEL_MAPPING = {
        "builder": "qwen2.5-coder:7b",
        "skeptic": "deepseek-r1:1.5b",
        "scout": "nomic-embed-text",
        "distiller": "hermes3:3b",
    }

    def __init__(
        self,
        governor: Optional[DynamicAgentGovernor] = None,
        repo_map_engine: Optional[RepoMapPageRankEngine] = None,
        routing_engine: Optional[HybridRoutingEngine] = None,
    ) -> None:
        self.governor = governor or DynamicAgentGovernor(vram_budget_cap_gb=8.5)
        self.repo_map_engine = repo_map_engine or RepoMapPageRankEngine()
        self.routing_engine = routing_engine or HybridRoutingEngine()

    def plan_swarm_execution(
        self,
        user_prompt: str,
        files: Dict[str, str],
        active_file: str,
    ) -> Dict[str, Any]:
        """Analyzes prompt, generates shared repo-map and builds task delegation graph."""
        repo_map = self.repo_map_engine.build_repo_map(files, active_file=active_file, max_tokens=800)
        routing = self.routing_engine.route_task(user_prompt, code_context=files.get(active_file, ""))

        tasks: List[SwarmAgentTask] = []
        if routing.tier == ExecutionTier.TIER_0_LOCAL_DETERMINISTIC:
            tasks.append(SwarmAgentTask("task_det", "builder", "Execute deterministic in-memory AST transform", active_file))
        else:
            # Swarm pair: Builder synthesizes, Skeptic audits in adversarial loop
            tasks.append(SwarmAgentTask("task_1_scout", "scout", "Locate symbol references and relevant context chunks", active_file))
            tasks.append(SwarmAgentTask("task_2_builder", "builder", f"Synthesize surgical patch for: {user_prompt}", active_file))
            tasks.append(SwarmAgentTask("task_3_skeptic", "skeptic", "Audit proposed patch for syntax, contracts and type invariants", active_file))

        return {
            "routing_decision": routing,
            "shared_repo_map": repo_map,
            "tasks": tasks,
        }

    def execute_swarm_task(self, task: SwarmAgentTask) -> SwarmTaskResult:
        """Executes task with dynamic VRAM time-slicing."""
        model_name = self.ROLE_MODEL_MAPPING.get(task.role, "smollm2:1.7b")
        activated = self.governor.request_model_activation(model_name)
        if not activated:
            return SwarmTaskResult(task.task_id, task.role, "VRAM_EXCEEDED", "Model activation deferred due to VRAM cap", 0.0)

        vram_allocated = self.governor._active_models.get(model_name, 0.0)

        # Simulation of task execution
        result_payload = f"[{task.role.upper()} via {model_name}] Completed '{task.instruction}' on {task.target_file}"

        return SwarmTaskResult(
            task_id=task.task_id,
            role=task.role,
            status="SUCCESS",
            output=result_payload,
            vram_used_gb=vram_allocated,
        )

    def execute_swarm(
        self,
        tasks: List[SwarmAgentTask],
    ) -> List[SwarmTaskResult]:
        """Executes tasks in swarm order while respecting VRAM budget."""
        results: List[SwarmTaskResult] = []
        for t in tasks:
            res = self.execute_swarm_task(t)
            results.append(res)
        return results
