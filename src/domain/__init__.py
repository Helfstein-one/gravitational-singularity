"""
Domain layer: Pure business models, value objects, and domain exceptions.
Free of external dependencies or I/O.
"""

from src.domain.value_objects import (
    ModelTier,
    TokenCount,
    CostUSD,
    DiffPatch,
    SyntaxValidationResult,
)
from src.domain.entities import (
    SessionState,
    CodeChunk,
    TelemetrySnapshot,
    StorytellingMetrics,
    SkillMetrics,
)
from src.domain.exceptions import (
    DomainError,
    SyntaxValidationError,
    ModelInferenceError,
    CompressionError,
    PatchApplicationError,
)

__all__ = [
    "ModelTier",
    "TokenCount",
    "CostUSD",
    "DiffPatch",
    "SyntaxValidationResult",
    "SessionState",
    "CodeChunk",
    "TelemetrySnapshot",
    "StorytellingMetrics",
    "SkillMetrics",
    "DomainError",
    "SyntaxValidationError",
    "ModelInferenceError",
    "CompressionError",
    "PatchApplicationError",
]
