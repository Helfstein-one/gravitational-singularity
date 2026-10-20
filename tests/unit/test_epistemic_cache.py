"""
Unit tests for Dual-Tier Epistemic Cache and Memoizer.
Verifies L1 RAM LRU, L2 SQLite WAL persistence, deterministic invalidation, and token savings.
"""

import os
import shutil
import tempfile
import unittest

from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.adapters.outbound.sqlite_epistemic_cache_adapter import SqliteEpistemicCacheAdapter
from src.application.code_skeletonizer import CodeSkeletonizer
from src.application.epistemic_memoizer import EpistemicMemoizer
from src.domain.value_objects import CacheKey


class TestSqliteEpistemicCacheAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_epistemic.db")
        self.adapter = SqliteEpistemicCacheAdapter(db_path=self.db_path, l1_max_size=2)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_l1_and_l2_roundtrip(self) -> None:
        key = CacheKey(
            content_sha256="abc123hash",
            prompt_hash="prompt_test",
            tool_spec="ast_parser:python",
        )
        self.assertIsNone(self.adapter.get(key))
        metrics = self.adapter.get_metrics()
        self.assertEqual(metrics.misses, 1)

        # Store entry
        self.adapter.put(key, payload="def hello(): pass", tokens_saved=45, computation_latency_ms=1.2)

        # First retrieval should be L1 Hit
        entry = self.adapter.get(key)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.payload, "def hello(): pass")
        self.assertEqual(entry.tokens_saved, 45)

        metrics = self.adapter.get_metrics()
        self.assertEqual(metrics.l1_hits, 1)
        self.assertEqual(metrics.total_tokens_saved, 45)

    def test_l2_promotion_on_l1_eviction(self) -> None:
        k1 = CacheKey("h1", "p1", "tool")
        k2 = CacheKey("h2", "p2", "tool")
        k3 = CacheKey("h3", "p3", "tool")

        self.adapter.put(k1, "payload1", 10, 0.5)
        self.adapter.put(k2, "payload2", 20, 0.5)
        # Adding 3rd item evicts k1 from L1 (since l1_max_size=2)
        self.adapter.put(k3, "payload3", 30, 0.5)

        # Retrieving k1 should be an L2 hit and promote back to L1
        entry1 = self.adapter.get(k1)
        self.assertIsNotNone(entry1)
        self.assertEqual(entry1.payload, "payload1")

        metrics = self.adapter.get_metrics()
        self.assertEqual(metrics.l2_hits, 1)

    def test_invalidation_by_content_hash(self) -> None:
        k = CacheKey("target_content_hash", "p", "tool")
        self.adapter.put(k, "some_code", 15, 0.3)

        self.assertIsNotNone(self.adapter.get(k))

        # Invalidate
        deleted = self.adapter.invalidate("target_content_hash")
        self.assertEqual(deleted, 1)

        # Now get should miss
        self.assertIsNone(self.adapter.get(k))


class TestEpistemicMemoizer(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_epistemic_memo.db")
        self.cache = SqliteEpistemicCacheAdapter(db_path=self.db_path, l1_max_size=10)
        self.ast_parser = MultiLanguageAstAdapter()
        self.skeletonizer = CodeSkeletonizer(parser=self.ast_parser)
        self.memoizer = EpistemicMemoizer(cache=self.cache, skeletonizer=self.skeletonizer)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_memoized_skeletonize_cache_hit(self) -> None:
        code = (
            "def calculate_trajectory(v: float, t: float) -> float:\n"
            "    # Complex orbital physics\n"
            "    g = 9.80665\n"
            "    return v * t - 0.5 * g * (t ** 2)\n"
        )
        # First call: computes skeleton, misses cache
        skel1, red1, from_cache1 = self.memoizer.memoized_skeletonize(code, "python")
        self.assertFalse(from_cache1)
        self.assertIn("...", skel1)
        self.assertGreater(red1, 0.0)

        # Second call with identical content: instantaneous cache hit
        skel2, red2, from_cache2 = self.memoizer.memoized_skeletonize(code, "python")
        self.assertTrue(from_cache2)
        self.assertEqual(skel1, skel2)
        self.assertEqual(red1, red2)

        metrics = self.memoizer.get_metrics()
        self.assertEqual(metrics.l1_hits, 1)
        self.assertGreater(metrics.total_tokens_saved, 0)

    def test_memoized_call_arbitrary_function(self) -> None:
        call_count = 0

        def heavy_computation():
            nonlocal call_count
            call_count += 1
            return "computed_result_data", 120

        # Call 1
        res1, from_cache1 = self.memoizer.memoized_call(
            content="repo_blob_content",
            query="find_symbols",
            tool_spec="semantic_indexer",
            computation=heavy_computation,
        )
        self.assertEqual(res1, "computed_result_data")
        self.assertFalse(from_cache1)
        self.assertEqual(call_count, 1)

        # Call 2 (cached)
        res2, from_cache2 = self.memoizer.memoized_call(
            content="repo_blob_content",
            query="find_symbols",
            tool_spec="semantic_indexer",
            computation=heavy_computation,
        )
        self.assertEqual(res2, "computed_result_data")
        self.assertTrue(from_cache2)
        # Verify heavy_computation was NOT invoked again
        self.assertEqual(call_count, 1)


if __name__ == "__main__":
    unittest.main()
