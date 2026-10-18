#!/usr/bin/env python3
"""
Local Code RAG Engine (AST-Aware Semantic Search)
Uses local Ollama nomic-embed-text model for zero-token semantic code retrieval.
Zero external dependencies.
"""

import sys
import os
import ast
import json
import math
import glob
import hashlib
import urllib.request
import urllib.error

OLLAMA_EMBED_URL = "http://127.0.0.1:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
USAGE_FILE = os.path.expanduser("~/.gemini/config/local_models_usage.json")
CACHE_DIR = os.path.expanduser("~/.gemini/config/cache/code_rag")


def record_embedding_usage(tokens: int):
    try:
        usage = {}
        if os.path.isfile(USAGE_FILE):
            with open(USAGE_FILE, "r", encoding="utf-8") as f:
                usage = json.load(f)
        models = usage.setdefault("models", {})
        m_entry = models.setdefault("nomic-embed-text:latest", {"invocations": 0, "tokens": 0, "role": "Scout / Semantic RAG"})
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

def get_embedding(text: str) -> list:
    payload = json.dumps({"model": EMBED_MODEL, "prompt": text[:2000]}).encode("utf-8")
    req = urllib.request.Request(OLLAMA_EMBED_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            record_embedding_usage(max(20, len(text) // 4))
            return data.get("embedding", [])
    except Exception as e:
        sys.stderr.write(f"Error fetching embedding from Ollama: {e}\n")
        return []

def cosine_similarity(v1: list, v2: list) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def extract_python_chunks(file_path: str, code: str) -> list:
    chunks = []
    try:
        tree = ast.parse(code, filename=file_path)
    except SyntaxError:
        return extract_line_chunks(file_path, code)

    lines = code.splitlines()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno
            end = node.end_lineno or start
            chunk_text = "\n".join(lines[start - 1:end])
            docstring = ast.get_docstring(node) or ""
            chunks.append({
                "type": "class" if isinstance(node, ast.ClassDef) else "function",
                "name": node.name,
                "file": file_path,
                "start_line": start,
                "end_line": end,
                "summary": f"{node.name}: {docstring[:120]}".strip(": "),
                "content": chunk_text
            })

    if not chunks:
        return extract_line_chunks(file_path, code)
    return chunks

def extract_line_chunks(file_path: str, code: str, chunk_size: int = 50, overlap: int = 10) -> list:
    lines = code.splitlines()
    chunks = []
    total = len(lines)
    if total == 0:
        return []

    start = 0
    while start < total:
        end = min(start + chunk_size, total)
        chunk_text = "\n".join(lines[start:end])
        if chunk_text.strip():
            chunks.append({
                "type": "block",
                "name": f"lines_{start+1}_{end}",
                "file": file_path,
                "start_line": start + 1,
                "end_line": end,
                "summary": f"Lines {start+1}-{end}",
                "content": chunk_text
            })
        if end >= total:
            break
        start += (chunk_size - overlap)
    return chunks

def get_file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def index_directory(target_dir: str = ".") -> dict:
    target_dir = os.path.abspath(target_dir)
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, hashlib.md5(target_dir.encode()).hexdigest() + ".json")

    existing_index = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                existing_index = json.load(f)
        except Exception:
            existing_index = {}

    extensions = {".py", ".ts", ".js", ".jsx", ".tsx", ".sh", ".md", ".json"}
    ignore_dirs = {".git", "node_modules", ".gemini", "__pycache__", ".venv", "venv", "dist", "build"}

    indexed_chunks = []
    files_indexed = 0

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for f in files:
            ext = os.path.splitext(f)[1]
            if ext in extensions:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, target_dir)
                try:
                    fhash = get_file_hash(full_path)
                    cached = existing_index.get(rel_path)
                    if cached and cached.get("hash") == fhash:
                        indexed_chunks.extend(cached.get("chunks", []))
                        continue

                    with open(full_path, "r", encoding="utf-8", errors="ignore") as fp:
                        code = fp.read()

                    if ext == ".py":
                        chunks = extract_python_chunks(rel_path, code)
                    else:
                        chunks = extract_line_chunks(rel_path, code)

                    for chunk in chunks:
                        # Compute embedding
                        emb = get_embedding(chunk["summary"] + "\n" + chunk["content"][:1000])
                        chunk["embedding"] = emb

                    indexed_chunks.extend(chunks)
                    existing_index[rel_path] = {"hash": fhash, "chunks": chunks}
                    files_indexed += 1
                except Exception as e:
                    sys.stderr.write(f"Error indexing {rel_path}: {e}\n")

    with open(cache_file, "w") as f:
        json.dump(existing_index, f)

    return {
        "directory": target_dir,
        "files_indexed": files_indexed,
        "total_chunks": len(indexed_chunks),
        "chunks": indexed_chunks
    }

def search_index(query: str, target_dir: str = ".", top_k: int = 5) -> list:
    index_res = index_directory(target_dir)
    chunks = index_res.get("chunks", [])
    if not chunks:
        return []

    q_emb = get_embedding(query)
    if not q_emb:
        return []

    scored = []
    for c in chunks:
        emb = c.get("embedding")
        if emb:
            sim = cosine_similarity(q_emb, emb)
            scored.append((sim, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, c in scored[:top_k]:
        results.append({
            "score": round(score, 4),
            "file": c["file"],
            "type": c["type"],
            "name": c["name"],
            "start_line": c["start_line"],
            "end_line": c["end_line"],
            "snippet": c["content"][:400]
        })
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: code-rag <index [dir] | search <query> [dir] [top_k]>")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "index":
        d = sys.argv[2] if len(sys.argv) > 2 else "."
        res = index_directory(d)
        print(f"Indexed {res['files_indexed']} files, {res['total_chunks']} chunks in {res['directory']}")

    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Please provide a search query.")
            sys.exit(1)
        query = sys.argv[2]
        d = sys.argv[3] if len(sys.argv) > 3 else "."
        k = int(sys.argv[4]) if len(sys.argv) > 4 else 4
        matches = search_index(query, d, k)
        print(f"=== Semantic Search Results for: '{query}' ===")
        for i, m in enumerate(matches, 1):
            print(f"[{i}] {m['file']} (L{m['start_line']}-L{m['end_line']}) | Similarity: {m['score']}")
            first_line = m['snippet'].splitlines()[0] if m['snippet'].splitlines() else ""
            print(f"    Preview: {first_line[:80]}")
            print("-" * 60)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
