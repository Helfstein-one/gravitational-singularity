"""
Immutable Value Objects representing core domain concepts.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import hashlib


class ModelTier(str, Enum):
    """Execution tiers across local Apple Silicon and Google Cloud."""
    LOCAL_TIER_0 = "tier_0_local"       # $0.00 / Zero-Cloud (Ollama Metal)
    CLOUD_FLASH_LITE = "tier_1_flash_lite" # $0.075 / 1M (-95% vs Pro)
    CLOUD_FLASH = "tier_2_flash"           # $0.100 / 1M (-93% vs Pro)
    CLOUD_PRO = "tier_3_pro"               # $1.500 / 1M (Orchestrator base)


@dataclass(frozen=True)
class TokenCount:
    """Encapsulates token volume with validation and conversion helpers."""
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Token count cannot be negative")

    def to_books(self, words_per_token: float = 0.75, pages_per_book: int = 300, words_per_page: int = 250) -> float:
        """Converts raw tokens into equivalent human books of 300 pages."""
        words = self.value * words_per_token
        pages = words / words_per_page
        return round(pages / pages_per_book, 1)


@dataclass(frozen=True)
class CostUSD:
    """Financial value in USD with conversions to BRL and coffee units."""
    value: float

    def to_brl(self, usd_brl_rate: float = 5.60) -> float:
        return round(self.value * usd_brl_rate, 2)

    def to_coffees(self, coffee_price_brl: float = 12.00, usd_brl_rate: float = 5.60) -> float:
        return round(self.to_brl(usd_brl_rate) / coffee_price_brl, 1)


@dataclass(frozen=True)
class DiffPatch:
    """Represents a surgical contiguous code replacement (Ponytail patch)."""
    target_file: str
    target_content: str
    replacement_content: str
    start_line: int
    end_line: int

    def __post_init__(self):
        if self.start_line <= 0 or self.end_line < self.start_line:
            raise ValueError(f"Invalid line range: [{self.start_line}, {self.end_line}]")


@dataclass(frozen=True)
class SyntaxValidationResult:
    """Result of an in-memory syntax check."""
    is_valid: bool
    language: str
    error_message: str = ""
    error_line: int | None = None
    execution_time_ms: float = 0.0


class CognitiveSystem(str, Enum):
    """Dual/Multi-Process Cognitive Architecture Systems."""
    SYSTEM_0_DETERMINISTIC_RAM = "system_0_deterministic_ram" # Deterministic AST transforms (<2ms, $0.00, 0 tokens)
    SYSTEM_1_LOCAL_FAST = "system_1_local_fast"       # Zero-Cloud / Metal (<100ms, $0.00)
    SYSTEM_2_CLOUD_SLOW = "system_2_cloud_slow"       # Gemini Pro Deliberative / Architecture


class TaskScope(str, Enum):
    """Scope of impact for an engineering task."""
    ISOLATED_MODULE = "isolated_module"
    CROSS_MODULE_ARCHITECTURE = "cross_module_architecture"


@dataclass(frozen=True)
class TaskClassification:
    """Decision output produced by the Cognitive Arbiter."""
    system: CognitiveSystem
    scope: TaskScope
    confidence: float
    rationale: str


@dataclass(frozen=True)
class EscalationPayload:
    """Surgical context handoff payload emitted when System 1 hits circuit breaker."""
    file_path: str
    instruction: str
    attempts_made: int
    error_summary: str
    suggested_action: str = ""

    def to_handoff_summary(self) -> str:
        return (
            f"[SYSTEM 1 HANDOFF TO SYSTEM 2]\n"
            f"Target: {self.file_path}\n"
            f"Goal: {self.instruction}\n"
            f"Local Attempts: {self.attempts_made} (Stopped by Circuit Breaker)\n"
            f"Residual Issue: {self.error_summary}\n"
            f"Directive: Take over architectural synthesis via System 2."
        )


@dataclass(frozen=True)
class TokenBudgetEnvelope:
    """Rigid token pacing envelope for System 2 deliberative execution."""
    max_system_2_tokens: int = 8000
    blueprint_budget: int = 500
    audit_budget: int = 300


@dataclass(frozen=True)
class CacheKey:
    """Triple compound cache key for deterministic epistemic memoization."""
    content_sha256: str
    prompt_hash: str
    tool_spec: str

    @property
    def composite_digest(self) -> str:
        raw = f"{self.content_sha256}:{self.prompt_hash}:{self.tool_spec}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CacheEntry:
    """Memoized epistemic payload with cost and token savings metadata."""
    key: str
    payload: str
    tokens_saved: int
    computation_latency_ms: float
    created_at_epoch: float


@dataclass(frozen=True)
class CacheMetrics:
    """Aggregated telemetry metrics for Epistemic Cache performance."""
    l1_hits: int = 0
    l2_hits: int = 0
    misses: int = 0
    total_tokens_saved: int = 0
    total_latency_saved_ms: float = 0.0

    @property
    def total_requests(self) -> int:
        return self.l1_hits + self.l2_hits + self.misses

    @property
    def hit_rate_pct(self) -> float:
        tot = self.total_requests
        return round(((self.l1_hits + self.l2_hits) / tot) * 100.0, 1) if tot > 0 else 0.0


@dataclass(frozen=True)
class ContextSqueezePolicy:
    """Policy rules governing 3-level in-memory context compaction."""
    max_token_ceiling: int = 8000
    preserve_recent_turns: int = 2
    collapse_command_outputs: bool = True
    collapse_file_views: bool = True


@dataclass(frozen=True)
class SqueezedContext:
    """Virtual in-memory non-destructive projection of conversation history."""
    original_steps_count: int
    squeezed_steps_count: int
    raw_tokens: int
    squeezed_tokens: int
    steps_payload: list[dict]

    @property
    def tokens_pruned(self) -> int:
        return max(0, self.raw_tokens - self.squeezed_tokens)

    @property
    def compression_ratio_pct(self) -> float:
        if self.raw_tokens == 0:
            return 0.0
        return round((1.0 - (self.squeezed_tokens / self.raw_tokens)) * 100.0, 1)


@dataclass(frozen=True)
class SqueezeMetrics:
    """Telemetry metrics tracking context compaction throughput."""
    total_invocations: int = 0
    total_tokens_pruned: int = 0
    average_compression_ratio_pct: float = 0.0


@dataclass(frozen=True)
class PreWarmEvent:
    """Represents a predictive AST cache pre-warming event triggered by file change."""
    file_path: str
    content_sha256: str
    tokens_saved: int
    prewarm_latency_ms: float
    timestamp_epoch: float


@dataclass(frozen=True)
class PreWarmMetrics:
    """Telemetry metrics tracking predictive cache pre-warming throughput."""
    is_active: bool = False
    prewarm_events_total: int = 0
    prewarmed_files_count: int = 0
    last_prewarmed_file: str = ""
    avg_prewarm_latency_ms: float = 0.0


@dataclass(frozen=True)
class ReflectionCritique:
    """Skeptic model critique and adversarial flaw assessment."""
    has_flaws: bool
    flaw_category: str
    critique_details: str
    confidence_score: float = 1.0


@dataclass(frozen=True)
class ReflectionResult:
    """Result of a local Builder vs Skeptic reflection cycle."""
    original_code: str
    final_code: str
    critique: ReflectionCritique
    was_refined: bool
    syntax_valid: bool
    latency_ms: float


@dataclass(frozen=True)
class AdversarialMetrics:
    """Telemetry tracking the performance of the local adversarial reflection loop."""
    total_reflection_cycles: int = 0
    skeptic_flaws_intercepted: int = 0
    successful_self_refinements: int = 0
    zero_cloud_cost_saved_usd: float = 0.0

    @property
    def self_refine_success_pct(self) -> float:
        if self.skeptic_flaws_intercepted == 0:
            return 100.0
        return round(
            (self.successful_self_refinements / self.skeptic_flaws_intercepted) * 100.0,
            1,
        )


class CascadeTaskLevel(str, Enum):
    """Task complexity tiers within local Tier 0 inference."""
    MICRO_TASK = "micro_task"        # Handled by smollm2:1.7b (~120 tok/s)
    STRUCTURAL_TASK = "structural"   # Handled by qwen2.5-coder:7b (~38 tok/s)


@dataclass(frozen=True)
class CascadeResult:
    """Result of a tiered hierarchical cascade resolution."""
    task_level: CascadeTaskLevel
    resolved_by_model: str
    was_promoted: bool
    code: str
    syntax_valid: bool
    latency_ms: float


@dataclass(frozen=True)
class CascadeMetrics:
    """Telemetry metrics tracking local cascade performance and promotions."""
    total_cascade_requests: int = 0
    smollm_micro_resolved: int = 0
    promoted_to_7b: int = 0
    avg_cascade_latency_ms: float = 0.0

    @property
    def micro_resolution_rate_pct(self) -> float:
        total_micro = self.smollm_micro_resolved + self.promoted_to_7b
        if total_micro == 0:
            return 100.0
        return round((self.smollm_micro_resolved / total_micro) * 100.0, 1)


class MerkleNodeType(str, Enum):
    """Categorization of individual AST Merkle nodes."""
    MODULE_HEADER = "module_header"
    IMPORT_BLOCK = "import_block"
    FUNCTION = "function"
    ASYNC_FUNCTION = "async_function"
    CLASS = "class"
    METHOD = "method"
    ASYNC_METHOD = "async_method"
    JSON_KEY = "json_key"
    RAW_CHUNK = "raw_chunk"


@dataclass(frozen=True)
class AstMerkleNode:
    """An individual granular node in an AST Merkle Tree with its isolated hash and skeleton."""
    node_id: str
    file_path: str
    symbol_path: str
    node_type: MerkleNodeType
    content_hash: str
    parent_symbol: str | None
    start_line: int
    end_line: int
    skeleton: str
    children_hashes: tuple[str, ...] = ()


@dataclass(frozen=True)
class AstMerkleTree:
    """A hierarchical cryptographic Merkle Tree representing a file's AST symbols."""
    file_path: str
    root_hash: str
    nodes: dict[str, AstMerkleNode]
    total_nodes: int
    updated_at: float


@dataclass(frozen=True)
class MerkleTreeMetrics:
    """Telemetry tracking granular AST cache hits, invalidation and virtual recomposition."""
    total_files_tracked: int = 0
    total_merkle_nodes: int = 0
    granular_cache_hits: int = 0
    granular_cache_misses: int = 0
    avg_recomposition_latency_ms: float = 0.0

    @property
    def granular_hit_ratio_pct(self) -> float:
        total = self.granular_cache_hits + self.granular_cache_misses
        if total == 0:
            return 100.0
        return round((self.granular_cache_hits / total) * 100.0, 1)


@dataclass(frozen=True)
class AgentRoleVramProfile:
    """Pre-calibrated VRAM and KV-cache profile for a resident agent model."""
    role_name: str
    model_name: str
    vram_footprint_gb: float
    keep_alive_seconds: int = -1
    default_num_keep: int = 128


@dataclass(frozen=True)
class VramCoResidenceState:
    """Snapshot of active models co-residing in Apple Silicon Metal VRAM."""
    active_models: tuple[str, ...]
    total_vram_allocated_gb: float
    vram_budget_limit_gb: float = 7.0

    @property
    def is_budget_respected(self) -> bool:
        return self.total_vram_allocated_gb <= self.vram_budget_limit_gb

    @property
    def all_core_models_resident(self) -> bool:
        core = {"smollm2:1.7b", "deepseek-r1:1.5b", "qwen2.5-coder:7b"}
        active_set = {m.split(":")[0] for m in self.active_models}
        return {"smollm2", "deepseek-r1", "qwen2.5-coder"}.issubset(active_set)


@dataclass(frozen=True)
class InferenceOptimizationMetrics:
    """Telemetry tracking zero cold-swap and KV-cache prefill elimination."""
    total_optimized_inferences: int = 0
    prefill_tokens_reused: int = 0
    cold_swaps_prevented: int = 0
    estimated_ttft_saved_ms: float = 0.0
    active_vram_gb: float = 0.0








