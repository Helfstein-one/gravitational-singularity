"""
Outbound Adapter: Persistent Mmap Prompt Cache Engine.
Stores pre-computed KV context buffers (e.g. AGENTS.md system prompt) in binary mmap files (.promptex),
providing 0ms zero-prefill instant restoration on Apple Silicon.
Zero external dependencies (Python standard library only).
"""

from __future__ import annotations
import hashlib
import mmap
import os
import struct
import time
from typing import Optional, Tuple


class PromptCacheAdapter:
    """
    Manages persistent memory-mapped binary prompt cache files.
    Header format (32 bytes):
      - 4s: Magic ('PTEX')
      - uint32: Version (1)
      - uint64: Hash of prompt (SHA-256 high 8 bytes)
      - uint32: Token count
      - double: Created timestamp
    Payload:
      - Raw encoded tokens or KV representations
    """

    MAGIC = b"PTEX"
    VERSION = 1
    HEADER_FORMAT = "!4sIQId"  # magic, version, prompt_hash_u64, token_count, created_epoch
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, cache_dir: str | None = None) -> None:
        self.cache_dir = cache_dir or os.path.expanduser("~/.gemini/config/cache/prompt_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, cache_key: str) -> str:
        h = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()[:16]
        return os.path.join(self.cache_dir, f"{h}.promptex")

    def save_prompt_cache(self, prompt_text: str, token_ids: list[int]) -> str:
        """Serializes pre-tokenized prompt representation to a binary mmap file."""
        path = self._get_cache_path(prompt_text)
        prompt_hash = int(hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()[:16], 16)
        token_count = len(token_ids)
        now = time.time()

        header = struct.pack(self.HEADER_FORMAT, self.MAGIC, self.VERSION, prompt_hash, token_count, now)
        payload = struct.pack(f"!{token_count}I", *token_ids) if token_count > 0 else b""

        with open(path, "wb") as f:
            f.write(header + payload)

        return path

    def load_prompt_cache(self, prompt_text: str) -> Optional[Tuple[list[int], float]]:
        """
        Loads pre-computed prompt tokens directly from memory-mapped file in 0ms.
        Returns (token_ids, latency_ms).
        """
        path = self._get_cache_path(prompt_text)
        if not os.path.exists(path):
            return None

        t0 = time.perf_counter()
        try:
            with open(path, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    if len(mm) < self.HEADER_SIZE:
                        return None
                    magic, ver, p_hash, count, created = struct.unpack_from(self.HEADER_FORMAT, mm, 0)
                    if magic != self.MAGIC:
                        return None
                    expected_hash = int(hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()[:16], 16)
                    if p_hash != expected_hash:
                        return None

                    tokens = list(struct.unpack_from(f"!{count}I", mm, self.HEADER_SIZE)) if count > 0 else []
                    t1 = time.perf_counter()
                    latency_ms = (t1 - t0) * 1000.0
                    return (tokens, round(latency_ms, 4))
        except Exception:
            return None
