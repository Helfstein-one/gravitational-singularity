# Empirical Benchmarks & Real-World Telemetry

This document records **measured, empirical benchmarks** captured directly from local hardware and CI runs, superseding any speculative or static estimates.

## 1. Local Model Inference Speeds (Apple Silicon M-Series, Ollama API)

Measured via `scripts/benchmark_live_ollama.py` on local machine:

| Model | Role in Singularity | Measured Throughput (tok/s) | TTFT (Time to First Token) | Resident VRAM |
| :--- | :--- | :---: | :---: | :---: |
| **`deepseek-r1:1.5b`** | Reasoning & Skeptic Micro-audit | **31.16 tok/s** | 54.41 ms | ~1.1 GB |
| **`qwen2.5-coder:3b`** | Fast Draft & Consensus Tier | **23.96 tok/s** | 123.68 ms | ~1.9 GB |
| **`qwen2.5-coder:7b`** | Builder & Local Patch Drafter | **9.65 tok/s** | 204.34 ms | 4.43 GB |
| **`nomic-embed-text`** | Semantic RAG & Merkle Vector Index | **842 ms / doc** | N/A (Embedding) | 0.31 GB |

---

## 2. In-Memory Token Optimization & AST Compression

Measured via automated 4-tier benchmark harness (`tests/benchmark_skills.py`):

| Optimization Mechanism | Implementation | Measured Reduction | Cloud Cost Impact |
| :--- | :--- | :---: | :---: |
| **System 0 Deterministic AST** | `ast.NodeTransformer` in RAM (<2ms) | **100% token bypass** | $0.00 (Zero LLM invoked) |
| **AST Merkle Differential Context** | Skeletons & cryptographic hashes | **>85% to >96%** | Eliminates full-file prefill |
| **Terminal Output Slicing** | `scripts/test-slicer` & RTK | **>90%** (<80 tokens retained) | Suppresses build/test logs |
| **Symbolic Tuple Patches** | JSON schema `(TargetContent, ReplacementContent)` | **>85% output token drop** | Eliminates markdown/conversational fluff |

---

## 3. Test Suite & Architecture Integrity

- **Total Automated Unit, Integration & E2E Tests**: **161 tests** passing (`pytest tests/`).
- **Architecture Reachability**: **71/71 modules reachable**, 0 isolated or orphan modules.
- **Portability**: 100% functional on pure CPU / Python Standard Library with automatic hardware acceleration when Apple Silicon / Metal is detected.
