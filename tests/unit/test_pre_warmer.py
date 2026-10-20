"""
Unit tests for Predictive AST Pre-Warmer (Abstraction 16).
Verifies background file change detection, proactive AST cache pre-warming,
and lifecycle management without external dependencies.
"""

import os
import shutil
import tempfile
import time
import unittest

from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.adapters.outbound.sqlite_epistemic_cache_adapter import SqliteEpistemicCacheAdapter
from src.application.code_skeletonizer import CodeSkeletonizer
from src.application.epistemic_memoizer import EpistemicMemoizer
from src.application.predictive_pre_warmer import PredictivePreWarmer


class TestPredictivePreWarmer(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_epistemic_pw.db")
        self.cache = SqliteEpistemicCacheAdapter(db_path=self.db_path, l1_max_size=50)
        self.ast_parser = MultiLanguageAstAdapter()
        self.skeletonizer = CodeSkeletonizer(parser=self.ast_parser)
        self.memoizer = EpistemicMemoizer(cache=self.cache, skeletonizer=self.skeletonizer)
        self.prewarmer = PredictivePreWarmer(
            memoizer=self.memoizer,
            watch_dirs=[self.temp_dir],
            poll_interval_s=0.05,
            debounce_s=0.02,
        )

    def tearDown(self) -> None:
        self.prewarmer.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_prewarm_file_success(self) -> None:
        file_path = os.path.join(self.temp_dir, "module_sample.py")
        code = (
            "def calculate_thrust(mass: float, acceleration: float) -> float:\n"
            "    # Newton physics\n"
            "    return mass * acceleration\n"
        )
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        success = self.prewarmer.prewarm_file(file_path)
        self.assertTrue(success)

        # Check telemetry metrics
        metrics = self.prewarmer.get_metrics()
        self.assertEqual(metrics.prewarm_events_total, 1)
        self.assertEqual(metrics.prewarmed_files_count, 1)
        self.assertEqual(metrics.last_prewarmed_file, file_path)
        self.assertGreaterEqual(metrics.avg_prewarm_latency_ms, 0.0)

        # Verify reading the file via memoizer is an instantaneous cache hit (from_cache=True)
        skel, red, from_cache = self.memoizer.memoized_skeletonize(code, "python")
        self.assertTrue(from_cache)
        self.assertIn("...", skel)

    def test_prewarm_file_unsupported_extension(self) -> None:
        doc_path = os.path.join(self.temp_dir, "notes.txt")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("Some notes")
        self.assertFalse(self.prewarmer.prewarm_file(doc_path))

    def test_watcher_detects_file_save_and_prewarms(self) -> None:
        src_file = os.path.join(self.temp_dir, "reactor.py")
        initial_code = "class Reactor:\n    def start(self):\n        pass\n"
        with open(src_file, "w", encoding="utf-8") as f:
            f.write(initial_code)

        # Start watcher thread
        self.prewarmer.start([self.temp_dir])
        self.assertTrue(self.prewarmer.get_metrics().is_active)

        # Allow initial scan
        time.sleep(0.08)

        # Modify file (simulating developer or agent save)
        updated_code = (
            "class Reactor:\n"
            "    def start(self):\n"
            "        self.power = 100\n"
            "        return self.power\n"
        )
        with open(src_file, "w", encoding="utf-8") as f:
            f.write(updated_code)

        # Wait for watcher poll + debounce
        time.sleep(0.18)

        # Metrics should show prewarm event
        metrics = self.prewarmer.get_metrics()
        self.assertGreaterEqual(metrics.prewarm_events_total, 1)

        # Memoizer query must be a cache hit
        _, _, from_cache = self.memoizer.memoized_skeletonize(updated_code, "python")
        self.assertTrue(from_cache)

        # Clean shutdown
        self.prewarmer.stop()
        self.assertFalse(self.prewarmer.get_metrics().is_active)

    def test_start_and_stop_lifecycle(self) -> None:
        self.prewarmer.start()
        self.assertTrue(self.prewarmer.get_metrics().is_active)
        # Calling start again while active should be idempotent
        self.prewarmer.start()
        self.assertTrue(self.prewarmer.get_metrics().is_active)
        self.prewarmer.stop()
        self.assertFalse(self.prewarmer.get_metrics().is_active)


if __name__ == "__main__":
    unittest.main()
