"""
Inbound Port: Unified Speculative Engine Interface.
Unifies single-model speculative drafting, consensus majority voting,
asymmetric draft-verify, and tree-speculative decoding.
"""

from __future__ import annotations
from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class ISpeculativeEngine(Protocol):
    """Unified abstraction for speculative drafting, consensus, and decoding."""

    def execute_speculation(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Executes a speculative inference pass, returning a dictionary containing:
        - status: str ("success", "consensus_approved", "fallback", "error")
        - effective_tok_s: float
        - tokens_saved: int
        - result: Any (code, tokens, or patch payload)
        """
        ...
