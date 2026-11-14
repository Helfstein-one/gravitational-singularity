import json
import sys
from typing import Any, Dict
from src.application.dynamic_agent_governor import DynamicAgentGovernor
from src.application.hybrid_routing_engine import HybridRoutingEngine
from src.application.repo_map_pagerank_engine import RepoMapPageRankEngine
from src.application.hybrid_search_rrf import HybridSearchRRFEngine
from src.application.token_savings_estimator import TokenSavingsEstimator
from src.application.code_skeletonizer import CodeSkeletonizer
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter

class UniversalMCPServer:
    """
    Standard Model Context Protocol (MCP) server for Antigravity, Cursor,
    and Claude Desktop, exposing the hybrid token factory over Stdio JSON-RPC.
    """

    def __init__(self) -> None:
        self.governor = DynamicAgentGovernor(vram_budget_cap_gb=8.5)
        self.router = HybridRoutingEngine()
        self.repo_map = RepoMapPageRankEngine()
        self.search = HybridSearchRRFEngine()
        self.estimator = TokenSavingsEstimator()
        self.skeletonizer = CodeSkeletonizer(MultiLanguageAstAdapter())

    def get_tool_definitions(self) -> Dict[str, Any]:
        return {
            "tools": [
                {
                    "name": "compress_ast",
                    "description": "Prunes implementation bodies preserving type signatures (>68% token reduction)",
                    "parameters": {
                        "type": "object",
                        "properties": {"code": {"type": "string"}, "language": {"type": "string"}},
                        "required": ["code"],
                    },
                },
                {
                    "name": "generate_repo_map",
                    "description": "Builds repository structural outline ranked by Personalized PageRank (<800 tokens)",
                    "parameters": {
                        "type": "object",
                        "properties": {"files": {"type": "object"}, "active_file": {"type": "string"}},
                        "required": ["files", "active_file"],
                    },
                },
                {
                    "name": "route_task",
                    "description": "Evaluates task complexity and picks optimal tier (Tier 0 local vs Gemini Pro)",
                    "parameters": {
                        "type": "object",
                        "properties": {"prompt": {"type": "string"}, "context": {"type": "string"}},
                        "required": ["prompt"],
                    },
                },
                {
                    "name": "hybrid_search",
                    "description": "Performs Reciprocal Rank Fusion of vector and lexical keyword search",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}, "top_k": {"type": "integer"}},
                        "required": ["query"],
                    },
                },
                {
                    "name": "get_vram_status",
                    "description": "Reports active models, current VRAM allocation and free memory cap",
                    "parameters": {"type": "object"},
                },
            ]
        }

    def dispatch_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "compress_ast":
            code = arguments.get("code", "")
            pruned, reduction = self.skeletonizer.skeletonize(code, language=arguments.get("language", "python"))
            return {"compressed_code": pruned, "reduction_pct": reduction}

        elif tool_name == "generate_repo_map":
            rmap = self.repo_map.build_repo_map(arguments.get("files", {}), arguments.get("active_file", ""), max_tokens=800)
            return {"repo_map": rmap}

        elif tool_name == "route_task":
            dec = self.router.route_task(arguments.get("prompt", ""), arguments.get("context", ""))
            return {
                "tier": dec.tier.value,
                "confidence": dec.confidence,
                "target_model": dec.target_model,
                "reason": dec.reason,
            }

        elif tool_name == "hybrid_search":
            results = self.search.search(arguments.get("query", ""), top_k=arguments.get("top_k", 5))
            return {"results": [{"id": r.document_id, "score": r.rrf_score} for r in results]}

        elif tool_name == "get_vram_status":
            return self.governor.get_vram_status()

        return {"error": f"Unknown tool: {tool_name}"}

    def handle_json_rpc(self, request_str: str) -> str:
        try:
            req = json.loads(request_str)
            method = req.get("method")
            req_id = req.get("id")

            if method == "tools/list":
                res = {"jsonrpc": "2.0", "id": req_id, "result": self.get_tool_definitions()}
            elif method == "tools/call":
                params = req.get("params", {})
                call_res = self.dispatch_call(params.get("name", ""), params.get("arguments", {}))
                res = {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(call_res)}]}}
            else:
                res = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
            return json.dumps(res)
        except Exception as e:
            return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}})

    def run_stdio(self) -> None:
        """Runs the MCP server over standard input/output."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            response = self.handle_json_rpc(line)
            sys.stdout.write(response + "\n")
            sys.stdout.flush()
