from typing import Dict, Protocol, runtime_checkable

@runtime_checkable
class IRepoMapEngine(Protocol):
    """Port for building repository-wide context maps using Personalized PageRank."""

    def build_repo_map(self, files: Dict[str, str], active_file: str, max_tokens: int = 800) -> str:
        """Generates compact structural repo-map ranked by relevance to active_file."""
        ...
