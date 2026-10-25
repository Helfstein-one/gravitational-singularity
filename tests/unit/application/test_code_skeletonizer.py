"""
Unit Tests: CodeSkeletonizer & Quantitative Token Reduction Estimator.
Asserts >= 60.0% token reduction across Python, TypeScript, and JSON files,
and >= 85.0% token reduction on differential AST Merkle skeletons.
"""

from __future__ import annotations
import ast
import re
import pytest
from src.application.code_skeletonizer import CodeSkeletonizer
from src.application.ast_merkle_engine import AstMerkleEngine
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter


def count_tokens(text: str) -> int:
    """Exact token counting matching word and punctuation boundaries."""
    return len(re.findall(r"\w+|[^\w\s]", text))


class TestCodeSkeletonizerReduction:
    """Rigorous quantitative test suite for context compression and token estimation."""

    def test_python_skeletonization_token_reduction_ge_60(
        self,
        skeletonizer: CodeSkeletonizer,
        sample_python_code: str
    ) -> None:
        """
        Verifies that Python code skeletonization reduces tokens by >= 60.0%
        while preserving all class signatures, methods, docstring summaries, and types.
        """
        raw_tokens = count_tokens(sample_python_code)
        skeleton, reduction_pct = skeletonizer.skeletonize(sample_python_code, "python")
        comp_tokens = count_tokens(skeleton)

        # Calculate exact measured reduction
        measured_reduction = ((raw_tokens - comp_tokens) / raw_tokens) * 100.0

        # Assertions
        assert raw_tokens > 400, "Raw code fixture should have realistic token count"
        assert comp_tokens < raw_tokens
        assert measured_reduction >= 60.0, (
            f"Expected >= 60.0% token reduction, got {measured_reduction:.1f}% "
            f"({raw_tokens} raw -> {comp_tokens} compressed tokens)"
        )

        # Verify semantic preservation
        assert "class DistributedStreamProcessor:" in skeleton
        assert "class StreamProcessingError" in skeleton
        assert "compute_partition_id" in skeleton
        assert "ingest_batch" in skeleton

        # Verify that internal loop and calculation statements were pruned
        assert "hashlib.sha256(event_key.encode" not in skeleton
        assert "accepted_records.append" not in skeleton
        assert "..." in skeleton

        # Assert compressed skeleton is valid Python syntax
        parsed_tree = ast.parse(skeleton)
        assert parsed_tree is not None

    def test_typescript_skeletonization_token_reduction_ge_60(
        self,
        skeletonizer: CodeSkeletonizer,
        sample_typescript_code: str
    ) -> None:
        """
        Verifies that TypeScript skeletonization achieves >= 60.0% token reduction
        while retaining export interfaces and method signatures.
        """
        raw_tokens = count_tokens(sample_typescript_code)
        skeleton, reduction_pct = skeletonizer.skeletonize(sample_typescript_code, "typescript")
        comp_tokens = count_tokens(skeleton)

        measured_reduction = ((raw_tokens - comp_tokens) / raw_tokens) * 100.0

        assert raw_tokens > 200
        assert measured_reduction >= 60.0, (
            f"Expected >= 60.0% token reduction for TypeScript, got {measured_reduction:.1f}% "
            f"({raw_tokens} raw -> {comp_tokens} comp tokens)"
        )

        # Contracts preserved
        assert "interface TelemetryEvent" in skeleton
        assert "interface RouterOptions" in skeleton
        assert "class TelemetryRouter" in skeleton
        assert "dispatch" in skeleton
        assert "flush" in skeleton

        # Imperative body pruned
        assert "JSON.stringify({" not in skeleton

    def test_merkle_differential_skeleton_reduction_ge_85(
        self,
        merkle_engine: AstMerkleEngine,
        sample_python_code: str
    ) -> None:
        """
        Verifies that differential AST skeletonization achieves >= 85.0% token reduction
        by retaining ONLY the targeted symbol and collapsing sibling methods into a 1-token summary.
        """
        raw_tokens = count_tokens(sample_python_code)
        diff_skeleton = merkle_engine.differential_skeletonize(
            file_path="stream_proc.py",
            source_code=sample_python_code,
            target_symbol="DistributedStreamProcessor.ingest_batch"
        )
        diff_tokens = count_tokens(diff_skeleton)
        reduction_pct = ((raw_tokens - diff_tokens) / raw_tokens) * 100.0

        assert reduction_pct >= 85.0, (
            f"Expected >= 85.0% reduction on differential Merkle diff, got {reduction_pct:.1f}% "
            f"({raw_tokens} raw -> {diff_tokens} differential tokens)"
        )

        # Target method retained
        assert "ingest_batch" in diff_skeleton
        # Sibling methods collapsed
        assert "sibling methods unchanged" in diff_skeleton

    def test_empty_and_trivial_code_boundary(
        self,
        skeletonizer: CodeSkeletonizer
    ) -> None:
        """Verifies boundary cases: empty string and single-line function."""
        empty_skel, empty_red = skeletonizer.skeletonize("", "python")
        assert empty_skel == ""
        assert empty_red == 0.0

        single_func = "def add(a: int, b: int) -> int:\n    return a + b\n"
        single_skel, single_red = skeletonizer.skeletonize(single_func, "python")
        assert "def add(a: int, b: int) -> int:" in single_skel
        assert "..." in single_skel
