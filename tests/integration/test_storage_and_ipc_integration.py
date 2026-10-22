"""
Integration tests for Persistent Storage Adapters & IPC mechanisms:
- SQLite Knowledge Graph Adapter
- Persistent Mmap Prompt Cache Adapter
- Shared Memory Ring Buffer IPC
- Multi-Language AST Adapter with Python/TypeScript/JSON
"""

import os
import tempfile
import unittest
from src.adapters.outbound.sqlite_knowledge_graph_adapter import SqliteKnowledgeGraphAdapter
from src.adapters.outbound.prompt_cache_adapter import PromptCacheAdapter
from src.adapters.outbound.shared_memory_adapter import SharedMemoryRingBuffer
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter


class TestStorageAndIPCIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_sqlite_knowledge_graph_persistence(self):
        """
        Verifies SQLite knowledge graph stores decisions with WAL mode
        and supports tag / keyword queries.
        """
        db_path = os.path.join(self.temp_dir, "test_kg.sqlite")
        kg = SqliteKnowledgeGraphAdapter(db_path=db_path)

        record = kg.record_decision(
            decision_id="ADR-001",
            title="Adopt Hexagonal Ports and Adapters",
            context="Antigravity local extension needed strict decoupling",
            decision="Isolate all domain models from I/O adapters",
            rationale="Zero cloud cost and sub-millisecond execution",
            tags=["architecture", "hexagonal", "tier-0"]
        )
        self.assertEqual(record.id, "ADR-001")

        # Query by tag
        results = kg.query_decisions(tag="hexagonal")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Adopt Hexagonal Ports and Adapters")
        self.assertIn("tier-0", results[0].tags)

        # Query by keyword
        results_kw = kg.query_decisions(keyword="decoupling")
        self.assertEqual(len(results_kw), 1)

    def test_02_prompt_cache_mmap_binary_storage(self):
        """
        Verifies persistent mmap prompt cache stores binary KV buffers
        and recovers exact token lists.
        """
        cache_dir = os.path.join(self.temp_dir, "prompt_cache")
        adapter = PromptCacheAdapter(cache_dir=cache_dir)

        prompt = "System Prompt: Event Horizon Local Guardian"
        tokens = [101, 2054, 2003, 1037, 30522, 999]

        saved_path = adapter.save_prompt_cache(prompt, tokens)
        self.assertTrue(os.path.exists(saved_path))
        self.assertTrue(saved_path.endswith(".promptex"))

        loaded = adapter.load_prompt_cache(prompt)
        self.assertIsNotNone(loaded)
        loaded_tokens, latency = loaded
        self.assertEqual(loaded_tokens, tokens)
        self.assertGreaterEqual(latency, 0.0)

    def test_03_shared_memory_ring_buffer_ipc(self):
        """
        Verifies SharedMemoryRingBuffer writes events and reads them back cleanly.
        """
        shm_name = f"test_shm_{os.getpid()}"
        buf = SharedMemoryRingBuffer(name=shm_name, size=8192, create=True)
        try:
            self.assertTrue(buf.write_event("patch_applied", {"tokens_saved": 420, "model": "qwen2.5-coder:7b"}))
            self.assertTrue(buf.write_event("syntax_audit", {"status": "APPROVED", "model": "deepseek-r1:1.5b"}))

            records = buf.read_latest_events()
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["type"], "patch_applied")
            self.assertEqual(records[1]["data"]["model"], "deepseek-r1:1.5b")
        finally:
            buf.close()
            buf.unlink()

    def test_04_ast_adapter_polygene_and_chunking(self):
        """
        Verifies MultiLanguageAstAdapter extracts code chunks and verifies multi-language syntax.
        """
        ast_adapter = MultiLanguageAstAdapter()

        py_code = (
            "import math\n\n"
            "class CircleCalculator:\n"
            "    def compute_area(self, r: float) -> float:\n"
            "        return math.pi * r * r\n"
        )
        chunks = ast_adapter.extract_chunks("calc.py", py_code)
        self.assertGreaterEqual(len(chunks), 1)
        self.assertEqual(chunks[0].name, "CircleCalculator")

        # JSON syntax checks
        valid_json = '{"system": 1, "tier": "local", "active": true}'
        res_json = ast_adapter.validate_syntax(valid_json, "json")
        self.assertTrue(res_json.is_valid)

        invalid_json = '{"system": 1, "tier": trailing_comma,}'
        res_bad_json = ast_adapter.validate_syntax(invalid_json, "json")
        self.assertFalse(res_bad_json.is_valid)


if __name__ == "__main__":
    unittest.main()
