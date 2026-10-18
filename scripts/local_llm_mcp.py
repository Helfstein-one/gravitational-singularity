#!/usr/bin/env python3
"""
Local LLM MCP Server (Stdio JSON-RPC)
Zero external dependencies. Bridges Antigravity to local Ollama models.
"""

import sys
import os
import json
import urllib.request
import urllib.error

sys.path.append(os.path.dirname(__file__))
try:
    import code_rag
except ImportError:
    code_rag = None

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

MODEL_MAP = {
    "reasoning": "deepseek-r1:1.5b",
    "reasoning_7b": "deepseek-r1:7b",
    "coding": "qwen2.5-coder:3b",
    "coding_7b": "qwen2.5-coder:7b",
    "agentic": "hermes3:3b",
    "micro": "mau-llm-1.0-c",
    "general": "llama3.2:1b"
}

USAGE_FILE = os.path.expanduser("~/.gemini/config/local_models_usage.json")

def record_model_usage(model: str, tokens: int):
    try:
        usage = {}
        if os.path.isfile(USAGE_FILE):
            with open(USAGE_FILE, "r", encoding="utf-8") as f:
                usage = json.load(f)
        models = usage.setdefault("models", {})
        m_entry = models.setdefault(model, {"invocations": 0, "tokens": 0})
        m_entry["invocations"] = m_entry.get("invocations", 0) + 1
        m_entry["tokens"] = m_entry.get("tokens", 0) + tokens
        usage["total_tokens"] = usage.get("total_tokens", 0) + tokens
        usage["total_invocations"] = usage.get("total_invocations", 0) + 1
        import time
        usage["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(usage, f, indent=2)
    except Exception:
        pass

def query_ollama(model: str, prompt: str, system: str = "") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    if system:
        payload["system"] = system

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tok_in = data.get("prompt_eval_count", 0)
            tok_out = data.get("eval_count", 0)
            record_model_usage(model, tok_in + tok_out)
            return data.get("response", "").strip()
    except urllib.error.HTTPError as he:
        if he.code == 404:
            # Fallback to base model
            if "7b" in model:
                fallback = "qwen2.5-coder:3b" if "coder" in model else "deepseek-r1:1.5b"
            else:
                fallback = "mau-llm-1.0-c" if "coder" in model else "deepseek-r1:1.5b"
            if model != fallback:
                return query_ollama(fallback, prompt, system)
        return f"Error contacting local Ollama: {str(he)}"
    except Exception as e:
        return f"Error contacting local Ollama: {str(e)}"

TOOLS = [
    {
        "name": "query_local_llm",
        "description": "Send a prompt to a local Ollama model to save cloud tokens. Default model is deepseek-r1:1.5b.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "User instruction or prompt"},
                "model": {
                    "type": "string",
                    "description": "Ollama model name (e.g. deepseek-r1:1.5b, mau-llm-1.0-c, llama3.2:1b)",
                    "default": "deepseek-r1:1.5b"
                },
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
        "description": "Format, generate simple boilerplate, or perform simple lint/refactor on code snippets using local mau-llm-1.0-c (coding model).",
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
        "description": "Performs local AST-aware semantic code search across the codebase using Ollama nomic-embed-text embeddings, finding exact file paths and line ranges with 0 cloud token spend.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language or code query to find"},
                "dir_path": {"type": "string", "description": "Directory to search (default: current directory)", "default": "."},
                "top_k": {"type": "integer", "description": "Number of top results to return", "default": 4}
            },
            "required": ["query"]
        }
    }
]

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "local-llm-mcp",
                    "version": "1.0.0"
                }
            }
        }

    if method == "notifications/initialized":
        return None

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }

    if method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "query_local_llm":
            prompt = args.get("prompt", "")
            model = args.get("model", MODEL_MAP["reasoning"])
            system = args.get("system", "")
            output = query_ollama(model, prompt, system)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": output}]
                }
            }

        elif tool_name == "local_extract_json":
            text = args.get("text", "")
            schema = args.get("schema_description", "")
            prompt = f"Extract structured JSON from the following text based on this specification:\nSpec: {schema}\n\nText:\n{text}\n\nReturn ONLY raw JSON."
            system = "You are a JSON extraction engine. Output strictly valid JSON."
            output = query_ollama(MODEL_MAP["reasoning"], prompt, system)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": output}]
                }
            }

        elif tool_name == "local_format_code":
            code = args.get("code", "")
            instruction = args.get("instruction", "")
            prompt = f"Instruction: {instruction}\n\nCode:\n{code}"
            system = "You are an ultra-fast programming assistant. Generate clean, optimal code."
            output = query_ollama(MODEL_MAP["coding"], prompt, system)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": output}]
                }
            }

        elif tool_name == "local_semantic_search":
            query = args.get("query", "")
            dir_path = args.get("dir_path", ".")
            top_k = args.get("top_k", 4)
            if code_rag:
                matches = code_rag.search_index(query, dir_path, top_k)
                output = json.dumps(matches, indent=2)
            else:
                output = "code_rag module not loaded"
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": output}]
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not implemented"}
    }

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            if res is not None:
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
