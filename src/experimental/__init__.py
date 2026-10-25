"""
Event Horizon Experimental / Research Prototypes.
Contains non-production research models and conceptual heuristics:
- BitNet 1.58b ternary quantization emulation
- SMT-style syntactic static analysis heuristics
"""

from src.experimental.bitnet_quantizer import BitNetQuantizer, TernaryWeightMatrix
from src.experimental.smt_heuristic_prover import SMTFormalVerificationGate, SMTProofResult

__all__ = [
    "BitNetQuantizer",
    "TernaryWeightMatrix",
    "SMTFormalVerificationGate",
    "SMTProofResult",
]
