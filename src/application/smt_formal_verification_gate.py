"""SMT Formal Verification Gate - Compatibility Re-export.

NOTE: This heuristic static analysis prototype has been consolidated into
`src.experimental.smt_heuristic_prover`. Retained here for backwards compatibility.
"""

from __future__ import annotations
from src.experimental.smt_heuristic_prover import (
    FormalProofResult,
    SmtFormalVerificationGate,
    SMTFormalVerificationGate,
    SMTProofResult,
)

__all__ = [
    "FormalProofResult",
    "SmtFormalVerificationGate",
    "SMTFormalVerificationGate",
    "SMTProofResult",
]
