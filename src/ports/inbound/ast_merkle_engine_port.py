"""
Inbound Port: AST Merkle Engine.
Defines the contract for hierarchical source code decomposition into cryptographic Merkle Trees,
enabling O(1) granular invalidation and virtual composition of module skeletons.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
from src.domain.value_objects import AstMerkleTree, MerkleTreeMetrics


class IAstMerkleEngine(ABC):
    """Port for AST Merkle Tree decomposition, invalidation, and composition."""

    @abstractmethod
    def decompose(self, file_path: str, source_code: str) -> AstMerkleTree:
        """Decomposes source code into a hierarchical AstMerkleTree."""
        raise NotImplementedError

    @abstractmethod
    def reconcile_and_assemble(
        self, file_path: str, new_source_code: str
    ) -> Tuple[str, AstMerkleTree, bool]:
        """
        Reconciles new source code with cached Merkle tree.
        Only recompiles modified nodes, reuses intact cached nodes in O(1),
        and virtually recomposes the full module skeleton.
        Returns: (composed_skeleton, updated_merkle_tree, was_modified)
        """
        raise NotImplementedError

    @abstractmethod
    def get_tree(self, file_path: str) -> Optional[AstMerkleTree]:
        """Retrieves active Merkle Tree for a file if present in cache."""
        raise NotImplementedError

    @abstractmethod
    def get_metrics(self) -> MerkleTreeMetrics:
        """Returns runtime granular cache hit/miss and recomposition latency metrics."""
        raise NotImplementedError

    @abstractmethod
    def differential_skeletonize(
        self, file_path: str, source_code: str, target_symbol: str
    ) -> str:
        """
        Generates differential surgical skeleton (>96% token reduction).
        Retains container signatures and target symbol while collapsing sibling nodes.
        """
        raise NotImplementedError
