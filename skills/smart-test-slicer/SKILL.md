---
name: smart-test-slicer
description: Filters test suite outputs (pytest, vitest, jest, cargo test, go test) to preserve only failures, tracebacks, and summaries, saving 80%+ of tokens.
---

# Smart Test Slicer

**Trigger:** Running unit, integration, or regression test commands.

**Directives:**
1. When running tests with potentially noisy outputs (`pytest`, `npm test`, `vitest`, `cargo test`), ALWAYS execute via `test-slicer` or ensure the pre-tool hook wraps it.
2. Example: `test-slicer pytest tests/` or `test-slicer npm test`.
3. Never load hundreds of passing test lines into context. Focus strictly on error assertions, file paths, and failure summaries.
