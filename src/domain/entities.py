"""
Domain Entities and Aggregates with encapsulated business invariants.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import time
from src.domain.value_objects import TokenCount, CostUSD


@dataclass
class CodeChunk:
    """A semantic chunk of code extracted via AST node partitioning."""
    file_path: str
    start_line: int
    end_line: int
    node_type: str
    name: str
    code: str
    embedding: list[float] = field(default_factory=list)


@dataclass
class SessionState:
    """The compressed epistemic state of an agentic session."""
    session_id: str
    core_objective: str
    verified_facts: list[str] = field(default_factory=list)
    constraints_and_decisions: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)

    def to_markdown(self) -> str:
        md = [
            f"# Session State: {self.session_id}",
            f"*Last Updated: {time.ctime(self.last_updated)}*",
            "",
            "## 🎯 Objetivo Central",
            self.core_objective or "Não especificado.",
            "",
            "## 🔍 Fatos Verificados",
        ]
        for f in self.verified_facts:
            md.append(f"- {f}")
        md.extend([
            "",
            "## ⚖️ Restrições & Decisões Arquiteturais",
        ])
        for d in self.constraints_and_decisions:
            md.append(f"- {d}")
        md.extend([
            "",
            "## 🚀 Próximos Passos",
        ])
        for s in self.next_steps:
            md.append(f"- {s}")
        return "\n".join(md) + "\n"


@dataclass
class StorytellingMetrics:
    """Metaphorical metrics designed for non-technical stakeholders."""
    books_saved: float
    reals_saved: float
    coffees_saved: float
    rework_prevented: int
    efficiency_ratio: float


@dataclass
class SkillMetrics:
    """Metrics tracked per specialized skill or offload mechanism."""
    name: str
    skill_type: str
    invocations: int
    tokens_saved: int


@dataclass
class TelemetrySnapshot:
    """Aggregated telemetry at a point in time."""
    timestamp: float
    active_session_id: str
    total_steps: int
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    total_tokens_consumed: int
    total_tokens_saved: int
    projected_unoptimized_tokens: int
    reduction_factor: float
    efficiency_rate_pct: float
    local_offload_pct: float
    local_tokens_saved: int
    cost_consumed_usd: float
    cost_saved_usd: float
    monthly_projected_usd: float
    terminal_lines_saved: int
    skills_breakdown: dict[str, SkillMetrics] = field(default_factory=dict)
    storytelling: StorytellingMetrics | None = None
