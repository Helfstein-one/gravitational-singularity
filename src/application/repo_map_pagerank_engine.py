import ast
import re
from typing import Dict, List, Set
from src.ports.inbound.repo_map_port import IRepoMapEngine

class RepoMapPageRankEngine(IRepoMapEngine):
    """
    Constructs a structural repository map using Personalized PageRank (Aider pattern),
    ranking symbols by topological relevance to the currently active editing file.
    """

    def __init__(self, damping: float = 0.85, max_iterations: int = 20) -> None:
        self.damping = damping
        self.max_iterations = max_iterations

    def extract_symbols(self, file_path: str, code: str) -> List[str]:
        symbols: List[str] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    symbols.append(f"{file_path}::{node.name}")
        except Exception:
            # Fallback regex for non-python or unparseable files
            for m in re.finditer(r"(?:class|def|function)\s+([a-zA-Z0-9_]+)", code):
                symbols.append(f"{file_path}::{m.group(1)}")
        return symbols

    def compute_personalized_pagerank(
        self,
        nodes: List[str],
        edges: Dict[str, Set[str]],
        active_node: str,
    ) -> Dict[str, float]:
        if not nodes:
            return {}

        n = len(nodes)
        # Personalized restart vector (50x multiplier for active node)
        p_vector: Dict[str, float] = {node: 1.0 / n for node in nodes}
        if active_node in p_vector:
            p_vector[active_node] = 50.0
            total_p = sum(p_vector.values())
            p_vector = {k: v / total_p for k, v in p_vector.items()}

        scores: Dict[str, float] = {node: 1.0 / n for node in nodes}

        # Power iteration
        for _ in range(self.max_iterations):
            new_scores: Dict[str, float] = {node: (1.0 - self.damping) * p_vector[node] for node in nodes}
            for u in nodes:
                out_edges = edges.get(u, set())
                if out_edges:
                    share = (self.damping * scores[u]) / len(out_edges)
                    for v in out_edges:
                        if v in new_scores:
                            new_scores[v] += share
                else:
                    # Dangling node distribute equally according to personalization vector
                    for v in nodes:
                        new_scores[v] += self.damping * scores[u] * p_vector[v]
            scores = new_scores

        return scores

    def build_repo_map(self, files: Dict[str, str], active_file: str, max_tokens: int = 800) -> str:
        nodes: List[str] = list(files.keys())
        if not nodes:
            return ""

        # Build reference graph
        edges: Dict[str, Set[str]] = {f: set() for f in nodes}
        file_symbols: Dict[str, List[str]] = {}

        for f, code in files.items():
            syms = self.extract_symbols(f, code)
            file_symbols[f] = syms

        # Link edges if file references another file's symbols
        for f, code in files.items():
            for target_f, syms in file_symbols.items():
                if f != target_f:
                    for sym in syms:
                        sym_name = sym.split("::")[-1]
                        if sym_name in code:
                            edges[f].add(target_f)

        scores = self.compute_personalized_pagerank(nodes, edges, active_file)
        ranked_files = sorted(nodes, key=lambda x: scores.get(x, 0.0), reverse=True)

        # Assemble compact outline respecting max_tokens (approx 4 chars per token)
        char_budget = max_tokens * 4
        lines: List[str] = ["# Repository Structural Map (Personalized PageRank)"]
        current_len = len(lines[0])

        for rf in ranked_files:
            file_header = f"\n📁 {rf} (score: {scores.get(rf, 0):.3f})"
            if current_len + len(file_header) > char_budget:
                break
            lines.append(file_header)
            current_len += len(file_header)

            syms = file_symbols.get(rf, [])[:6]  # top 6 signatures
            for sym in syms:
                sym_line = f"  • {sym.split('::')[-1]} (⋮)"
                if current_len + len(sym_line) > char_budget:
                    lines.append("  • ⋮ [rest elided to preserve token budget]")
                    return "\n".join(lines)
                lines.append(sym_line)
                current_len += len(sym_line)

        return "\n".join(lines)
