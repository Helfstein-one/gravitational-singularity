import re
from typing import Dict, List, Tuple
from src.ports.inbound.hybrid_search_port import IHybridSearchEngine, SearchResult

class HybridSearchRRFEngine(IHybridSearchEngine):
    """
    Combines semantic vector rankings with exact lexical keyword matches
    using Reciprocal Rank Fusion (RRF k=60, Continue.dev pattern).
    """

    def __init__(self, rrf_k: int = 60) -> None:
        self.rrf_k = rrf_k
        self._documents: Dict[str, str] = {}  # doc_id -> content

    def index_document(self, doc_id: str, content: str) -> None:
        self._documents[doc_id] = content

    def _lexical_search(self, query: str) -> List[Tuple[str, float]]:
        """Scores documents based on exact keyword match and symbol frequency."""
        query_terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
        if not query_terms:
            return []

        scores: List[Tuple[str, float]] = []
        for doc_id, text in self._documents.items():
            lower_text = text.lower()
            score = 0.0
            for term in query_terms:
                count = lower_text.count(term)
                if count > 0:
                    score += 1.0 + (count * 0.1)
            if score > 0:
                scores.append((doc_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def fuse_rankings(
        self,
        vector_rankings: List[str],
        lexical_rankings: List[str],
        top_k: int = 5,
    ) -> List[SearchResult]:
        rrf_scores: Dict[str, float] = {}
        vec_ranks: Dict[str, int] = {doc: i + 1 for i, doc in enumerate(vector_rankings)}
        lex_ranks: Dict[str, int] = {doc: i + 1 for i, doc in enumerate(lexical_rankings)}

        all_docs = set(vector_rankings) | set(lexical_rankings)
        for doc in all_docs:
            score = 0.0
            if doc in vec_ranks:
                score += 1.0 / (self.rrf_k + vec_ranks[doc])
            if doc in lex_ranks:
                score += 1.0 / (self.rrf_k + lex_ranks[doc])
            rrf_scores[doc] = score

        ranked_docs = sorted(all_docs, key=lambda x: rrf_scores.get(x, 0.0), reverse=True)[:top_k]

        return [
            SearchResult(
                document_id=doc,
                content=self._documents.get(doc, ""),
                rrf_score=round(rrf_scores.get(doc, 0.0), 5),
                vector_rank=vec_ranks.get(doc, 999),
                lexical_rank=lex_ranks.get(doc, 999),
            )
            for doc in ranked_docs
        ]

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        lex_results = [doc for doc, _ in self._lexical_search(query)]
        # When vector search backend is not externally provided, lexical acts as primary
        return self.fuse_rankings(vector_rankings=lex_results, lexical_rankings=lex_results, top_k=top_k)
