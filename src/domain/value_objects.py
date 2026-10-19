"""
Immutable Value Objects representing core domain concepts.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


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
