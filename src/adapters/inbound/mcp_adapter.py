"""
Inbound Adapter: Stdio JSON-RPC MCP Server (local-llm-mcp).
Exposes local Ollama models and SpeculativeDrafter to Antigravity and external MCP clients.
"""

from __future__ import annotations
import json
import os
import sys
from typing import Any
from src.adapters.outbound.ollama_adapter import OllamaClientAdapter
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.adapters.outbound.file_system_adapter import LocalFileSystemAdapter
from src.adapters.outbound.file_cache_adapter import JsonFileCacheAdapter
from src.application.speculative_drafter import SpeculativeDrafter
from src.application.semantic_retriever import SemanticRetriever

MODEL_MAP = {
    "reasoning": "deepseek-r1:1.5b",
    "reasoning_7b": "deepseek-r1:7b",
    "coding": "qwen2.5-coder:3b",
    "coding_7b": "qwen2.5-coder:7b",
    "agentic": "hermes3:3b",
    "micro": "mau-llm-1.0-c",
    "general": "llama3.2:1b"
}

TOOLS = [
    {
        "name": "query_local_llm",
        "description": "Execute local LLM inference via Ollama (zero-token cloud cost, ultra-low latency on Mac Apple Silicon).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The prompt to send to the local LLM"},
                "model": {"type": "string", "description": "Model tag (e.g., deepseek-r1:1.5b, qwen2.5-coder:3b, hermes3:3b)", "default": "deepseek-r1:1.5b"},
                "system": {"type": "string", "description": "Optional system prompt", "default": ""}
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "local_extract_json",
        "description": "Extract structured JSON, schema, or regex patterns using local deepseek-r1:1.5b reasoning without cloud token spend.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Source text to extract information from"},
                "schema_description": {"type": "string", "description": "Description of the desired JSON schema"}
            },
            "required": ["text", "schema_description"]
        }
    },
    {
        "name": "local_format_code",
        "description": "Format, generate simple boilerplate, or perform simple lint/refactor on code snippets using local coding model.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Source code snippet"},
                "instruction": {"type": "string", "description": "Formatting or lint instruction"}
            },
            "required": ["code", "instruction"]
        }
    },
    {
        "name": "local_semantic_search",
        "description": "Performs local AST-aware semantic code search across the codebase using Ollama nomic-embed-text embeddings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language or code query to find"},
                "dir_path": {"type": "string", "description": "Directory to search", "default": "."},
                "top_k": {"type": "integer", "description": "Number of top results to return", "default": 4}
            },
            "required": ["query"]
        }
    },
    {
        "name": "local_draft_patch",
        "description": "Executes a surgical ponytail code patch locally using local qwen2.5-coder:7b with in-memory AST validation. Zero cloud token cost.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the target file to modify"},
                "instruction": {"type": "string", "description": "Specific instruction of what to modify in the code"},
                "target_symbol": {"type": "string", "description": "Optional function or class name to focus on", "default": ""}
            },
            "required": ["file_path", "instruction"]
        }
    }
]


class McpServer:
    """Handles Stdio JSON-RPC 2.0 messages for MCP protocol."""

    def __init__(self):
        self.llm = OllamaClientAdapter()
        self.parser = MultiLanguageAstAdapter()
        self.fs = LocalFileSystemAdapter()
        self.cache = JsonFileCacheAdapter()
        self.drafter = SpeculativeDrafter(self.llm, self.parser, self.fs)
        self.retriever = SemanticRetriever(self.parser, self.llm, self.cache, self.fs)

    def handle_request(self, req: dict[str, Any]) -> dict[str, Any] | None:
        method = req.get("method")
        req_id = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "local-llm-mcp", "version": "2.0.0"}
                }
            }

        if method == "notifications/initialized":
            return None

        if method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

        if method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "query_local_llm":
                prompt = args.get("prompt", "")
                model = args.get("model", MODEL_MAP["reasoning"])
                system = args.get("system", "")
                output = self.llm.generate(prompt=prompt, model=model, system_prompt=system)
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": output}]}}

            if name == "local_extract_json":
                text = args.get("text", "")
                schema = args.get("schema_description", "")
                prompt = f"Extract structured JSON from text:\nSpec: {schema}\n\nText:\n{text}\n\nOutput pure JSON."
                output = self.llm.generate(prompt=prompt, model=MODEL_MAP["reasoning"], response_format="json")
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": output}]}}

            if name == "local_format_code":
                code = args.get("code", "")
                instruction = args.get("instruction", "")
                prompt = f"Instruction: {instruction}\n\nCode:\n{code}"
                output = self.llm.generate(prompt=prompt, model=MODEL_MAP["coding"])
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": output}]}}

            if name == "local_semantic_search":
                query = args.get("query", "")
                dir_path = args.get("dir_path", ".")
                top_k = args.get("top_k", 4)
                chunks = self.retriever.index_directory(dir_path)
                results = self.retriever.search(query, chunks, top_k=top_k)
                lines = [f"Found {len(results)} relevant code blocks for: '{query}':"]
                for i, (c, score) in enumerate(results, 1):
                    lines.append(f"\n[{i}] {c.file_path} (Lines {c.start_line}-{c.end_line}) | Type: {c.node_type} {c.name} | Score: {score:.3f}")
                    lines.append(f"```\n{c.code[:400]}...\n```")
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": "\n".join(lines)}]}}

            if name == "local_draft_patch":
                file_path = args.get("file_path", "")
                instruction = args.get("instruction", "")
                target_symbol = args.get("target_symbol", "")
                auto_apply = args.get("auto_apply", True)

                report = self.drafter.draft_patch(file_path=file_path, instruction=instruction, target_lines=target_symbol)

                # Auto-apply if requested and valid
                if auto_apply and report.get("status") == "success" and "patch" in report:
                    patch = report["patch"]
                    orig_content = self.fs.read_text(file_path)
                    simulated = self.drafter._simulate_patch(orig_content, patch)
                    if simulated is not None:
                        self.fs.write_text(file_path, simulated)
                        report["applied_to_disk"] = True

                # Record local model usage & conversion telemetry
                self._record_local_usage(
                    model="qwen2.5-coder:7b",
                    tokens=3200 if report.get("status") == "success" else 500,
                    was_success=(report.get("status") == "success"),
                    attempts=report.get("attempts", 1)
                )

                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(report, indent=2)}]}}

    def _record_local_usage(self, model: str, tokens: int, was_success: bool = True, attempts: int = 1) -> None:
        usage_file = os.path.expanduser("~/.gemini/config/local_models_usage.json")
        try:
            usage = {}
            if os.path.isfile(usage_file):
                with open(usage_file, "r", encoding="utf-8") as f:
                    usage = json.load(f)
            models = usage.setdefault("models", {})
            m_entry = models.setdefault(model, {
                "invocations": 0,
                "tokens": 0,
                "success_count": 0,
                "escalations": 0,
                "role": "Speculative Local Drafter"
            })
            m_entry["invocations"] += 1
            m_entry["tokens"] += tokens
            if was_success:
                m_entry["success_count"] = m_entry.get("success_count", 0) + 1
            else:
                m_entry["escalations"] = m_entry.get("escalations", 0) + 1
            usage["total_tokens"] = usage.get("total_tokens", 0) + tokens
            usage["total_invocations"] = usage.get("total_invocations", 0) + 1
            import time
            usage["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            with open(usage_file, "w", encoding="utf-8") as f:
                json.dump(usage, f, indent=2)
        except Exception:
            pass

        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method {method} not found"}}

    def run_stdio(self) -> None:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {e}"}}
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()


def run_mcp_server() -> None:
    server = McpServer()
    server.run_stdio()


if __name__ == "__main__":
    run_mcp_server()
