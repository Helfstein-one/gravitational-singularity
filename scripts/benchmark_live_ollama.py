#!/usr/bin/env python3
"""
Live Ollama Performance Benchmark Harness.
Directly probes local Ollama engine (http://127.0.0.1:11434) to capture
empirical measurements: actual tokens/s, Time-to-First-Token (TTFT),
embedding latency, and resident VRAM via /api/ps.
No hand-written or formulaic approximations.
"""

from __future__ import annotations
import json
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List


def query_ollama(model: str, prompt: str, system: str = "") -> Dict[str, Any]:
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": -1,
        "options": {
            "temperature": 0.0,
            "num_predict": 64,
        }
    }
    if system:
        payload["system"] = system

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def query_embeddings(model: str, text: str) -> Tuple[float, int]:
    url = "http://127.0.0.1:11434/api/embeddings"
    payload = {"model": model, "prompt": text}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return elapsed_ms, len(data.get("embedding", []))


def query_resident_vram() -> Dict[str, float]:
    url = "http://127.0.0.1:11434/api/ps"
    req = urllib.request.Request(url)
    vram_map = {}
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for m in data.get("models", []):
                name = m.get("name", "")
                bytes_vram = m.get("size_vram", 0)
                vram_map[name] = round(bytes_vram / (1024**3), 2)
    except Exception:
        pass
    return vram_map


def main() -> None:
    print("=" * 80)
    print("      Event Horizon: Live Apple Silicon Hardware Benchmark (Ollama API)      ")
    print("=" * 80)

    # 1. Check connectivity
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/version", timeout=3) as resp:
            version = json.loads(resp.read().decode("utf-8")).get("version", "unknown")
            print(f"[*] Ollama Daemon: Online (Version {version})")
    except Exception as e:
        print(f"[!] Ollama not reachable at http://127.0.0.1:11434: {e}")
        return

    test_models = [
        "smollm2:1.7b",
        "deepseek-r1:1.5b",
        "qwen2.5-coder:3b",
        "qwen2.5-coder:7b",
    ]

    bench_results: List[Dict[str, Any]] = []

    prompt = "Write a python function `is_prime(n: int) -> bool` with type hints and concise docstring."

    for model in test_models:
        print(f"\n[*] Probing model: {model}...")
        try:
            # Warm up
            _ = query_ollama(model, "hi")

            # Benchmark run
            data = query_ollama(model, prompt)
            eval_count = data.get("eval_count", 0)
            eval_dur_ns = data.get("eval_duration", 1)
            prompt_eval_dur_ns = data.get("prompt_eval_duration", 0)

            tok_per_sec = (eval_count / (eval_dur_ns / 1e9)) if eval_dur_ns > 0 else 0.0
            ttft_ms = prompt_eval_dur_ns / 1e6

            bench_results.append({
                "model": model,
                "eval_tokens": eval_count,
                "measured_tok_s": round(tok_per_sec, 2),
                "ttft_ms": round(ttft_ms, 2),
                "eval_duration_ms": round(eval_dur_ns / 1e6, 2),
            })
            print(f"    -> Speed: {tok_per_sec:.2f} tokens/s | TTFT: {ttft_ms:.2f} ms ({eval_count} tokens generated)")
        except Exception as e:
            print(f"    [!] Error benchmarking {model}: {e}")

    # 2. Embedding Benchmark
    print("\n[*] Probing embedding model: nomic-embed-text...")
    try:
        embed_ms, dims = query_embeddings("nomic-embed-text", "def calculate_hash(data: str) -> str:")
        print(f"    -> Latency: {embed_ms:.2f} ms | Dimensions: {dims}")
    except Exception as e:
        print(f"    [!] Embedding benchmark failed: {e}")
        embed_ms, dims = 0.0, 0

    # 3. VRAM Resident Check
    vram_map = query_resident_vram()

    # 4. Print Summary Table
    print("\n" + "=" * 80)
    print(f"{'Model':<20} | {'Measured tok/s':<16} | {'TTFT (ms)':<12} | {'VRAM (GB)':<10} | {'Status'}")
    print("-" * 80)
    for res in bench_results:
        m_name = res["model"]
        vram = vram_map.get(m_name, vram_map.get(f"{m_name}:latest", "-"))
        print(f"{m_name:<20} | {res['measured_tok_s']:>14.2f} t/s | {res['ttft_ms']:>10.2f} ms | {str(vram):>8} GB | OK (Measured)")
    if embed_ms > 0:
        emb_vram = vram_map.get("nomic-embed-text:latest", vram_map.get("nomic-embed-text", "-"))
        print(f"{'nomic-embed-text':<20} | {embed_ms:>14.2f} ms | {'-':>10}    | {str(emb_vram):>8} GB | OK (Measured)")
    print("=" * 80)


if __name__ == "__main__":
    main()
