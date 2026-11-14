"""
Inbound Adapter: CLI entrypoints for Code RAG and Session Distiller.
"""

from __future__ import annotations
import sys
import os
from src.adapters.outbound.ollama_adapter import OllamaClientAdapter
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.adapters.outbound.file_system_adapter import LocalFileSystemAdapter
from src.adapters.outbound.file_cache_adapter import JsonFileCacheAdapter
from src.adapters.outbound.transcript_file_adapter import FileTranscriptRepository
from src.application.semantic_retriever import SemanticRetriever
from src.application.epistemic_distiller import EpistemicDistiller
from src.application.dynamic_agent_governor import DynamicAgentGovernor
from src.application.hybrid_routing_engine import HybridRoutingEngine
from src.application.repo_map_pagerank_engine import RepoMapPageRankEngine
from src.application.hybrid_search_rrf import HybridSearchRRFEngine
from src.application.token_savings_estimator import TokenSavingsEstimator
from src.adapters.outbound.grammar_decoding_adapter import GrammarDecodingAdapter
from src.adapters.outbound.opentelemetry_exporter import OpenTelemetryExporter


def get_holistic_orchestrator():
    """Initializes and returns the holistic agent and routing cluster."""
    governor = DynamicAgentGovernor(vram_budget_cap_gb=8.5)
    router = HybridRoutingEngine()
    repo_map = RepoMapPageRankEngine()
    search = HybridSearchRRFEngine()
    estimator = TokenSavingsEstimator()
    grammar = GrammarDecodingAdapter()
    otel = OpenTelemetryExporter()
    return {
        "governor": governor,
        "router": router,
        "repo_map": repo_map,
        "search": search,
        "estimator": estimator,
        "grammar": grammar,
        "otel": otel,
    }


def run_code_rag_cli() -> None:
    if len(sys.argv) < 2:
        print("Usage: python code_rag.py <query> [root_dir] [top_k]")
        sys.exit(1)

    query = sys.argv[1]
    root_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 4

    llm = OllamaClientAdapter()
    parser = MultiLanguageAstAdapter()
    cache = JsonFileCacheAdapter()
    fs = LocalFileSystemAdapter()

    retriever = SemanticRetriever(parser, llm, cache, fs)
    print(f"[*] Indexing AST chunks for: {root_dir}")
    chunks = retriever.index_directory(root_dir)
    print(f"[*] Found {len(chunks)} indexed chunks. Querying '{query}'...")
    results = retriever.search(query, chunks, top_k=top_k)

    for i, (chunk, score) in enumerate(results, 1):
        print(f"\n--- [{i}] Match: {chunk.file_path} (L{chunk.start_line}-L{chunk.end_line}) | Score: {score:.3f} ---")
        print(f"Type: {chunk.node_type} {chunk.name}")
        print(chunk.code[:500] + ("..." if len(chunk.code) > 500 else ""))


def run_session_distiller_cli() -> None:
    output_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.gemini/config/session_state.md")
    llm = OllamaClientAdapter()
    repo = FileTranscriptRepository()
    fs = LocalFileSystemAdapter()

    distiller = EpistemicDistiller(llm, repo, fs)
    print("[*] Distilling active Antigravity session...")
    state = distiller.distill_active_session(output_path)
    print(f"[✓] Session state distilled to: {output_path}")
    print(f"    Objective: {state.core_objective}")
    print(f"    Verified Facts: {len(state.verified_facts)}")
    print(f"    Decisions: {len(state.constraints_and_decisions)}")
    print(f"    Next Steps: {len(state.next_steps)}")
