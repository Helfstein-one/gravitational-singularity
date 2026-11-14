# Portability & Hardware Execution Matrix

This matrix documents the runtime tiering and hardware acceleration contracts of **Gravitational Singularity**.

| Tier / Feature | Minimal Path (CPU / Stdlib) | Apple Silicon (macOS arm64) | Cloud SaaS / Gemini API |
| :--- | :--- | :--- | :--- |
| **System 0: Deterministic Bypass** | ✅ Pure Python `ast` / `cst` (<2ms, 0 tokens) | ✅ Pure Python `ast` / `cst` (<2ms, 0 tokens) | Not invoked (100% saved) |
| **AST Merkle Context Slicing** | ✅ Python `ast` + `hashlib` (>96% token reduction) | ✅ Hardware vectorized AST Merkle comparison | Not invoked (100% saved) |
| **Vector Similarity (RAG)** | ✅ Pure Python math fallback | ✅ Apple Accelerate Framework (`vecLib` BLAS `cblas_ddot`) | Not invoked ($0.00 cloud cost) |
| **Inference Optimizer & KV-Cache** | ⚠️ Emulated / skipped without local Ollama | ✅ Local Ollama with unified memory (`num_keep` locked) | Fallback to Gemini 2.0 Flash / Pro |
| **Guardrails & Fail-Closed Gates** | ✅ `shlex` lexer + In-memory AST dry-run | ✅ `shlex` lexer + In-memory AST dry-run | Filters outbound payloads to SaaS |
| **Speculative Decoding** | ✅ Sequential CPU simulation | ✅ Asymmetric / Tree speculation in unified RAM | Escalates to Cloud SaaS only on structural divergence |
| **Operating Systems** | ✅ Linux, macOS (Intel & ARM), Windows WSL | ✅ macOS Apple Silicon (M1/M2/M3/M4) | Any OS with Internet access |

---

## Portability Guarantees

1. **Zero Mandatory External Binaries**: The entire core runtime (`src/`) operates strictly with Python Standard Library.
2. **Graceful Acceleration Degradation**:
   - If macOS Accelerate framework is not found: automatically degrades to pure Python vector dot products and cosine similarity.
   - If Ollama is offline or uninstalled: doctor warns the user, and tasks gracefully escalate to Cloud SaaS or deterministic transformations without crashing.
   - If shared memory IPC is unavailable: file-based fallback caches are used.
3. **Hardware Diagnostic Tool**:
   Run `python -m gravitational_singularity doctor` or `singularity info --json` to inspect your active hardware tier at any moment.
