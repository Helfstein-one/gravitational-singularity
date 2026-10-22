"""Metal PagedAttention Engine.

Implements non-fragmenting virtual memory paging for KV-cache on Apple Silicon,
enabling multi-subagent prefix sharing with zero duplicate VRAM allocation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class PhysicalBlock:
    """A physical fixed-size KV memory block."""
    block_id: int
    block_size: int = 16
    tokens: List[int] = field(default_factory=list)
    ref_count: int = 0

    @property
    def is_full(self) -> bool:
        return len(self.tokens) >= self.block_size

    @property
    def remaining_capacity(self) -> int:
        return self.block_size - len(self.tokens)


class PagedAttentionEngine:
    """Manages virtual page tables for KV-cache blocks across subagents."""

    def __init__(self, total_blocks: int = 256, block_size: int = 16) -> None:
        self.block_size = block_size
        self.total_blocks = total_blocks
        self._physical_blocks: List[PhysicalBlock] = [
            PhysicalBlock(block_id=i, block_size=block_size)
            for i in range(total_blocks)
        ]
        self._free_block_ids: List[int] = list(range(total_blocks - 1, -1, -1))
        # Map: sequence_id -> list of physical block IDs
        self._block_tables: Dict[str, List[int]] = {}

    def allocate_sequence(self, seq_id: str, initial_tokens: List[int]) -> List[int]:
        """Allocates physical blocks for a new sequence and loads initial tokens."""
        if seq_id in self._block_tables:
            raise ValueError(f"Sequence {seq_id} already exists in page table.")

        block_ids: List[int] = []
        token_offset = 0
        total_tokens = len(initial_tokens)

        while token_offset < total_tokens:
            if not self._free_block_ids:
                raise MemoryError("PagedAttention: Out of physical KV blocks (VRAM exhausted).")
            b_id = self._free_block_ids.pop()
            block = self._physical_blocks[b_id]
            block.ref_count = 1
            chunk = initial_tokens[token_offset : token_offset + self.block_size]
            block.tokens = list(chunk)
            token_offset += len(chunk)
            block_ids.append(b_id)

        # Ensure at least one empty block exists if initial_tokens is empty
        if not block_ids:
            if not self._free_block_ids:
                raise MemoryError("PagedAttention: Out of physical KV blocks.")
            b_id = self._free_block_ids.pop()
            block = self._physical_blocks[b_id]
            block.ref_count = 1
            block.tokens = []
            block_ids.append(b_id)

        self._block_tables[seq_id] = block_ids
        return block_ids

    def fork_sequence(self, parent_seq_id: str, child_seq_id: str) -> List[int]:
        """Forks a sequence for a parallel subagent with zero copy (Copy-On-Write)."""
        if parent_seq_id not in self._block_tables:
            raise KeyError(f"Parent sequence {parent_seq_id} does not exist.")
        if child_seq_id in self._block_tables:
            raise ValueError(f"Child sequence {child_seq_id} already exists.")

        parent_block_ids = self._block_tables[parent_seq_id]
        child_block_ids: List[int] = []

        for b_id in parent_block_ids:
            block = self._physical_blocks[b_id]
            block.ref_count += 1
            child_block_ids.append(b_id)

        self._block_tables[child_seq_id] = child_block_ids
        return child_block_ids

    def append_token(self, seq_id: str, token: int) -> None:
        """Appends a generated token to the sequence, handling COW if shared."""
        if seq_id not in self._block_tables:
            raise KeyError(f"Sequence {seq_id} not found in page table.")

        block_ids = self._block_tables[seq_id]
        last_block_id = block_ids[-1]
        last_block = self._physical_blocks[last_block_id]

        # Case 1: Last block is full -> allocate new block
        if last_block.is_full:
            if not self._free_block_ids:
                raise MemoryError("PagedAttention: Out of physical KV blocks.")
            new_id = self._free_block_ids.pop()
            new_block = self._physical_blocks[new_id]
            new_block.ref_count = 1
            new_block.tokens = [token]
            block_ids.append(new_id)
            return

        # Case 2: Last block has space but is shared (ref_count > 1) -> Copy-On-Write
        if last_block.ref_count > 1:
            if not self._free_block_ids:
                raise MemoryError("PagedAttention: Out of physical KV blocks for COW.")
            new_id = self._free_block_ids.pop()
            new_block = self._physical_blocks[new_id]
            new_block.ref_count = 1
            new_block.tokens = list(last_block.tokens) + [token]
            last_block.ref_count -= 1
            block_ids[-1] = new_id
            return

        # Case 3: Last block has space and is exclusive (ref_count == 1) -> append in-place
        last_block.tokens.append(token)

    def free_sequence(self, seq_id: str) -> None:
        """Frees all blocks associated with a sequence."""
        if seq_id not in self._block_tables:
            return

        block_ids = self._block_tables.pop(seq_id)
        for b_id in block_ids:
            block = self._physical_blocks[b_id]
            block.ref_count -= 1
            if block.ref_count <= 0:
                block.ref_count = 0
                block.tokens.clear()
                self._free_block_ids.append(b_id)

    def get_sequence_tokens(self, seq_id: str) -> List[int]:
        """Reconstructs the full token stream from physical blocks."""
        if seq_id not in self._block_tables:
            return []
        tokens: List[int] = []
        for b_id in self._block_tables[seq_id]:
            tokens.extend(self._physical_blocks[b_id].tokens)
        return tokens

    def get_stats(self) -> dict:
        """Returns physical allocation statistics and memory efficiency."""
        allocated_blocks = [b for b in self._physical_blocks if b.ref_count > 0]
        shared_blocks = [b for b in allocated_blocks if b.ref_count > 1]
        virtual_block_references = sum(len(tbl) for tbl in self._block_tables.values())
        physical_blocks_used = len(allocated_blocks)

        memory_saved_ratio = (
            (virtual_block_references / physical_blocks_used)
            if physical_blocks_used > 0
            else 1.0
        )

        return {
            "total_blocks": self.total_blocks,
            "allocated_blocks": physical_blocks_used,
            "free_blocks": len(self._free_block_ids),
            "shared_blocks": len(shared_blocks),
            "virtual_block_references": virtual_block_references,
            "prefix_sharing_factor": round(memory_saved_ratio, 2),
            "vram_fragmentation_pct": 0.0,  # PagedAttention guarantees 0% external fragmentation
        }
