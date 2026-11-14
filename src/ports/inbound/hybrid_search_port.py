from dataclasses import dataclass
from typing import List, Protocol, runtime_checkable

@dataclass(frozen=True)
class SearchResult:
    document_id: str
    content: str
    rrf_score: float
    vector_rank: int
    lexical_rank: int

@runtime_checkable
class IHybridSearchEngine(Protocol):
    """Port for combining vector and lexical keyword search using Reciprocal Rank Fusion."""

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Executes hybrid search combining lexical and semantic signals."""
        ...
