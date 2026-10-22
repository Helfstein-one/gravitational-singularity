"""
Application Layer: Event-Driven Reactive Telemetry Bus.
Provides sub-microsecond in-memory event dispatching and bridges to SharedMemoryRingBuffer
for real-time dashboard telemetry without disk I/O polling.
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import threading
import time
from typing import Any, Callable, Dict, List, Optional


class TelemetryEventEmitter:
    """
    Thread-safe event emitter for reactive telemetry.
    Supports in-process subscribers and writes to POSIX Shared Memory.
    """

    _instance: Optional[TelemetryEventEmitter] = None
    _lock = threading.Lock()

    def __init__(self, shm_buffer: Any = None) -> None:
        self._subscribers: Dict[str, List[Callable[[str, dict[str, Any]], None]]] = {}
        self._shm = shm_buffer
        self._sub_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> TelemetryEventEmitter:
        with cls._lock:
            if cls._instance is None:
                # Lazy-import SharedMemoryRingBuffer to prevent circular dependencies
                try:
                    from src.adapters.outbound.shared_memory_adapter import SharedMemoryRingBuffer
                    shm = SharedMemoryRingBuffer(name="singularity_shm_telemetry", size=65536, create=False)
                except Exception:
                    shm = None
                cls._instance = TelemetryEventEmitter(shm_buffer=shm)
            return cls._instance

    @classmethod
    def cleanup(cls) -> None:
        with cls._lock:
            if cls._instance and cls._instance._shm:
                try:
                    cls._instance._shm.close()
                    cls._instance._shm.unlink()
                except Exception:
                    pass
                cls._instance = None

    def subscribe(self, event_type: str, callback: Callable[[str, dict[str, Any]], None]) -> None:
        with self._sub_lock:
            self._subscribers.setdefault(event_type, []).append(callback)

    def emit(self, event_type: str, data: dict[str, Any]) -> None:
        """Dispatches event to local subscribers and writes frame to shared memory."""
        payload = {
            "event": event_type,
            "timestamp": time.time(),
            **data,
        }

        # 1. Dispatch to in-memory subscribers
        with self._sub_lock:
            handlers = list(self._subscribers.get(event_type, []))
            all_handlers = list(self._subscribers.get("*", []))

        for h in handlers + all_handlers:
            try:
                h(event_type, payload)
            except Exception:
                pass

        # 2. Zero-copy write to Shared Memory Ring Buffer
        if self._shm:
            try:
                self._shm.write_event(event_type, payload)
            except Exception:
                pass

    # Convenience domain event hooks
    def on_patch_generated(self, file_path: str, model: str, attempts: int, cost_usd: float = 0.0) -> None:
        self.emit("on_patch_generated", {
            "file_path": file_path,
            "model": model,
            "attempts": attempts,
            "cost_usd": cost_usd,
        })

    def on_syntax_blocked(self, file_path: str, tool_name: str, error_message: str) -> None:
        self.emit("on_syntax_blocked", {
            "file_path": file_path,
            "tool_name": tool_name,
            "error_message": error_message,
        })

    def on_cascade_escalated(self, from_model: str, to_model: str, reason: str) -> None:
        self.emit("on_cascade_escalated", {
            "from_model": from_model,
            "to_model": to_model,
            "reason": reason,
        })

    def on_merkle_invalidation(self, file_path: str, changed_symbols: list[str], root_hash: str) -> None:
        self.emit("on_merkle_invalidation", {
            "file_path": file_path,
            "changed_symbols": changed_symbols,
            "root_hash": root_hash,
        })
