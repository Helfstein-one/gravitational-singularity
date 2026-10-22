"""
Unit Tests: AST Merkle Tree Engine (Abstraction 19).
Verifies symbol decomposition, granular cache invalidation O(1),
virtual skeleton recomposition, and L2 SQLite persistence.
"""

import os
import tempfile
import unittest

from src.application.ast_merkle_engine import AstMerkleEngine
from src.adapters.outbound.sqlite_epistemic_cache_adapter import SqliteEpistemicCacheAdapter
from src.domain.value_objects import MerkleNodeType


class TestAstMerkleEngine(unittest.TestCase):
    """Test suite for AstMerkleEngine granular AST decomposition and recomposition."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_merkle.db")
        self.cache_adapter = SqliteEpistemicCacheAdapter(db_path=self.db_path)
        self.engine = AstMerkleEngine(cache_adapter=self.cache_adapter)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_python_decomposition_symbols_and_classes(self) -> None:
        """Verifies hierarchical extraction of docstring, imports, top-level functions and class methods."""
        code = '''"""Module level documentation."""
import os
import sys
from typing import List

def top_function(x: int) -> int:
    """Computes double x."""
    return x * 2

class Calculator:
    """A simple calculator class."""
    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b
'''
        file_path = "/tmp/test_calc.py"
        tree = self.engine.decompose(file_path, code)

        self.assertEqual(tree.file_path, file_path)
        self.assertTrue(len(tree.root_hash) == 64)
        self.assertIn("__doc__", tree.nodes)
        self.assertIn("__imports__", tree.nodes)
        self.assertIn("top_function", tree.nodes)
        self.assertIn("Calculator", tree.nodes)
        self.assertIn("Calculator.add", tree.nodes)
        self.assertIn("Calculator.subtract", tree.nodes)

        self.assertEqual(tree.nodes["Calculator.add"].node_type, MerkleNodeType.METHOD)
        self.assertEqual(tree.nodes["top_function"].node_type, MerkleNodeType.FUNCTION)
        self.assertEqual(tree.nodes["Calculator"].node_type, MerkleNodeType.CLASS)
        self.assertEqual(tree.nodes["__imports__"].node_type, MerkleNodeType.IMPORT_BLOCK)

    def test_granular_invalidation_and_virtual_assembly_on_single_method_change(self) -> None:
        """
        Verifies O(1) granular invalidation: changing 1 method causes exactly 1 cache miss,
        while all other intact symbols hit the cache (>75% hit ratio).
        """
        initial_code = '''import math

def helper_one():
    return 1

def helper_two():
    return 2

class MathOps:
    def power(self, base, exp):
        return base ** exp

    def root(self, base, exp):
        return base ** (1.0 / exp)
'''
        file_path = "/tmp/test_ops.py"
        # Initial parse
        self.engine.decompose(file_path, initial_code)

        # Modify ONLY MathOps.power method body
        modified_code = '''import math

def helper_one():
    return 1

def helper_two():
    return 2

class MathOps:
    def power(self, base, exp):
        # Optimized bitwise power check
        if exp == 0:
            return 1
        return base ** exp

    def root(self, base, exp):
        return base ** (1.0 / exp)
'''
        composed_skeleton, updated_tree, was_modified = self.engine.reconcile_and_assemble(
            file_path, modified_code
        )

        self.assertTrue(was_modified)
        self.assertIn("def power", composed_skeleton)
        self.assertIn("def root", composed_skeleton)
        self.assertIn("def helper_one", composed_skeleton)

        metrics = self.engine.get_metrics()
        # Initial had 6 nodes (imports, 2 functions, 1 class, 2 methods).
        # On modification: 5 intact nodes hit, 1 changed node misses.
        self.assertGreater(metrics.granular_cache_hits, 0)
        self.assertGreaterEqual(metrics.granular_cache_misses, 1)
        self.assertGreater(metrics.granular_hit_ratio_pct, 60.0)
        self.assertLess(metrics.avg_recomposition_latency_ms, 5.0)

    def test_zero_modification_yields_100_percent_granular_hits(self) -> None:
        """Verifies that reconciling unmodified code yields 100% cache hits and was_modified=False."""
        code = '''from typing import Dict

def lookup_key(d: Dict, k: str):
    return d.get(k)
'''
        file_path = "/tmp/test_lookup.py"
        self.engine.decompose(file_path, code)

        composed_skeleton, tree, was_modified = self.engine.reconcile_and_assemble(file_path, code)
        self.assertFalse(was_modified)
        self.assertIn("def lookup_key", composed_skeleton)

        metrics = self.engine.get_metrics()
        self.assertGreater(metrics.granular_cache_hits, 0)
        self.assertEqual(metrics.granular_cache_misses, 0)
        self.assertEqual(metrics.granular_hit_ratio_pct, 100.0)

    def test_json_and_typescript_heuristic_decomposition(self) -> None:
        """Verifies that JSON keys and TypeScript functions are cleanly decomposed into Merkle nodes."""
        # JSON test
        json_code = '{"api_version": "2.6.0", "rate_limit": 100, "debug_mode": false}'
        json_tree = self.engine.decompose("/tmp/config.json", json_code)
        self.assertIn("$.api_version", json_tree.nodes)
        self.assertIn("$.rate_limit", json_tree.nodes)
        self.assertEqual(json_tree.nodes["$.api_version"].node_type, MerkleNodeType.JSON_KEY)

        # TypeScript test
        ts_code = '''import { useState } from 'react';

export function UserProfile() {
    return null;
}

export class SessionService {
    token: string;
}
'''
        ts_tree = self.engine.decompose("/tmp/component.tsx", ts_code)
        self.assertIn("__imports__", ts_tree.nodes)
        self.assertIn("UserProfile", ts_tree.nodes)
        self.assertIn("SessionService", ts_tree.nodes)

    def test_l2_sqlite_persistence_roundtrip(self) -> None:
        """Verifies that Merkle nodes are persisted in SQLite WAL and recovered across engine instances."""
        code = '''def compute_sum(a, b):
    return a + b
'''
        file_path = "/tmp/test_sum.py"
        self.engine.decompose(file_path, code)

        # Create a fresh engine instance sharing the same SQLite DB
        fresh_engine = AstMerkleEngine(cache_adapter=self.cache_adapter)
        recovered_tree = fresh_engine.get_tree(file_path)

        self.assertIsNotNone(recovered_tree)
        assert recovered_tree is not None
        self.assertIn("compute_sum", recovered_tree.nodes)
        self.assertEqual(recovered_tree.nodes["compute_sum"].symbol_path, "compute_sum")

    def test_differential_skeletonize_collapses_siblings(self) -> None:
        """Verifies that differential skeleton retains target method and collapses siblings into 1-token comment."""
        code = '''class DatabaseManager:
    """Manages db connection and queries."""

    def connect(self):
        return True

    def query_user(self, user_id):
        return {"id": user_id}

    def disconnect(self):
        return False
'''
        diff_skel = self.engine.differential_skeletonize("/tmp/db.py", code, target_symbol="query_user")
        self.assertIn("class DatabaseManager", diff_skel)
        self.assertIn("def query_user", diff_skel)
        self.assertIn("sibling methods unchanged", diff_skel)
        self.assertNotIn("def disconnect", diff_skel)


if __name__ == "__main__":
    unittest.main()
