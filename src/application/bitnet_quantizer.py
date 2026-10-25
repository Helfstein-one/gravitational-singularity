"""BitNet b1.58 Ternary Quantization - Compatibility Re-export.

NOTE: This research module has been consolidated into `src.experimental.bitnet_quantizer`.
Retained here for backwards compatibility.
"""

from __future__ import annotations
from src.experimental.bitnet_quantizer import (
    BitNetQuantizer,
    TernaryWeightMatrix,
)

__all__ = ["BitNetQuantizer", "TernaryWeightMatrix"]
