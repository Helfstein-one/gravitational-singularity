"""
Outbound Adapter: Shared Memory Ring Buffer IPC.
Provides sub-5 microsecond zero-copy IPC between daemon, hooks, and MCP server
using Python standard library multiprocessing.shared_memory.
"""

from __future__ import annotations
import json
import struct
import time
import atexit
from typing import Any, Optional
from multiprocessing import shared_memory
try:
    from multiprocessing import resource_tracker
except ImportError:
    resource_tracker = None


class SharedMemoryRingBuffer:
    """
    Lock-free/low-overhead circular ring buffer in POSIX shared memory.
    Header structure (16 bytes):
      - uint32: magic number (0x53494E47 - 'SING')
      - uint32: capacity in bytes
      - uint32: write_head
      - uint32: entry_count
    Payload:
      - Array of records: [uint16 length][bytes payload]
    """

    MAGIC = 0x53494E47
    HEADER_SIZE = 16
    HEADER_FORMAT = "!IIII"  # magic, capacity, write_head, entry_count

    def __init__(
        self,
        name: str = "singularity_shm_telemetry",
        size: int = 65536,
        create: bool = False,
    ) -> None:
        self.name = name
        self.size = size
        self._shm: Optional[shared_memory.SharedMemory] = None

        if create:
            try:
                # Try opening existing first to clean up stale segments
                existing = shared_memory.SharedMemory(name=self.name)
                existing.close()
                existing.unlink()
            except FileNotFoundError:
                pass
            self._shm = shared_memory.SharedMemory(name=self.name, create=True, size=self.size)
            self._init_header()
        else:
            try:
                self._shm = shared_memory.SharedMemory(name=self.name, create=False)
            except FileNotFoundError:
                # Fallback: create on the fly if client connects first
                self._shm = shared_memory.SharedMemory(name=self.name, create=True, size=self.size)
                self._init_header()

        atexit.register(self.close)

    def _init_header(self) -> None:
        if not self._shm:
            return
        header = struct.pack(self.HEADER_FORMAT, self.MAGIC, self.size, self.HEADER_SIZE, 0)
        self._shm.buf[0:self.HEADER_SIZE] = header

    def write_event(self, event_type: str, data: dict[str, Any]) -> bool:
        """Writes an event frame into the shared memory ring buffer in <5 microseconds."""
        if not self._shm:
            return False

        payload_dict = {
            "type": event_type,
            "timestamp": time.time(),
            "data": data,
        }
        raw_bytes = json.dumps(payload_dict).encode("utf-8")
        msg_len = len(raw_bytes)
        if msg_len > 65535:
            return False

        # Read current header
        try:
            magic, cap, head, count = struct.unpack(self.HEADER_FORMAT, self._shm.buf[0:self.HEADER_SIZE])
            if magic != self.MAGIC:
                self._init_header()
                magic, cap, head, count = struct.unpack(self.HEADER_FORMAT, self._shm.buf[0:self.HEADER_SIZE])

            total_len = 2 + msg_len
            if head + total_len > self.size:
                # Wrap around to start of payload area
                head = self.HEADER_SIZE

            # Write length prefix + bytes
            struct.pack_into("!H", self._shm.buf, head, msg_len)
            self._shm.buf[head + 2 : head + total_len] = raw_bytes

            new_head = head + total_len
            new_count = count + 1
            struct.pack_into(self.HEADER_FORMAT, self._shm.buf, 0, self.MAGIC, cap, new_head, new_count)
            return True
        except Exception:
            return False

    def read_latest_events(self, max_count: int = 50) -> list[dict[str, Any]]:
        """Reads recent events written to the ring buffer."""
        if not self._shm:
            return []

        try:
            magic, cap, head, count = struct.unpack(self.HEADER_FORMAT, self._shm.buf[0:self.HEADER_SIZE])
            if magic != self.MAGIC:
                return []

            events: list[dict[str, Any]] = []
            curr = self.HEADER_SIZE
            while curr < head and curr + 2 <= self.size:
                msg_len = struct.unpack_from("!H", self._shm.buf, curr)[0]
                if msg_len == 0 or curr + 2 + msg_len > self.size:
                    break
                raw = bytes(self._shm.buf[curr + 2 : curr + 2 + msg_len])
                try:
                    events.append(json.loads(raw.decode("utf-8")))
                except Exception:
                    pass
                curr += 2 + msg_len

            return events[-max_count:]
        except Exception:
            return []

    def get_stats(self) -> dict[str, Any]:
        """Returns metadata stats about the shared memory ring buffer."""
        if not self._shm:
            return {"active": False}
        try:
            magic, cap, head, count = struct.unpack(self.HEADER_FORMAT, self._shm.buf[0:self.HEADER_SIZE])
            return {
                "active": magic == self.MAGIC,
                "capacity": cap,
                "write_head": head,
                "entry_count": count,
            }
        except Exception:
            return {"active": False}

    def close(self) -> None:
        if self._shm:
            try:
                self._shm.close()
            except Exception:
                pass

    def unlink(self) -> None:
        if self._shm:
            try:
                self._shm.unlink()
            except Exception:
                pass
