"""
Application Use Case: Escalation Circuit Breaker.
Monitors local System 1 execution attempts, terminates thrashing after 2 failures,
and builds surgical <100 token context handoffs for System 2.
"""

from __future__ import annotations
from src.domain.value_objects import EscalationPayload
from src.ports.inbound.circuit_breaker_port import ICircuitBreaker


class EscalationCircuitBreaker(ICircuitBreaker):
    """Protects against local execution loops, tripping after max_attempts and synthesizing clean handoffs."""

    def __init__(self, max_attempts: int = 2):
        self.max_attempts = max_attempts
        self._attempts: dict[str, int] = {}
        self._last_errors: dict[str, str] = {}

    def record_attempt(self, file_path: str, is_success: bool, error_msg: str = "") -> bool:
        if is_success:
            self.reset(file_path)
            return True

        current = self._attempts.get(file_path, 0) + 1
        self._attempts[file_path] = current
        self._last_errors[file_path] = error_msg

        # Can retry if attempts < max_attempts
        return current < self.max_attempts

    def build_escalation_handoff(self, file_path: str, instruction: str) -> EscalationPayload:
        attempts = self._attempts.get(file_path, self.max_attempts)
        last_error = self._last_errors.get(file_path, "Unknown syntax or AST validation failure.")

        # Clean, concise error summary without dumping huge tracebacks
        clean_err = last_error.splitlines()[-1] if last_error else "In-memory AST validation failed"
        if len(clean_err) > 150:
            clean_err = clean_err[:147] + "..."

        payload = EscalationPayload(
            file_path=file_path,
            instruction=instruction,
            attempts_made=attempts,
            error_summary=clean_err,
            suggested_action="Review and synthesize cross-module invariants via System 2 Cloud Orchestrator."
        )

        # Reset state after handoff synthesis
        self.reset(file_path)
        return payload

    def reset(self, file_path: str) -> None:
        self._attempts.pop(file_path, None)
        self._last_errors.pop(file_path, None)
