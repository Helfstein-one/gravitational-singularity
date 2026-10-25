"""
Global Pytest Configuration and Fixtures for Event Horizon / Gravitational Singularity.
Supports granular test filtering: unit, integration, e2e, and benchmark.
Includes production fixtures for token reduction estimation and AST validation.
"""

from __future__ import annotations
import os
import re
import shutil
import tempfile
import pytest
from typing import Generator, Any, Callable
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.adapters.outbound.file_system_adapter import LocalFileSystemAdapter
from src.adapters.outbound.shared_memory_adapter import SharedMemoryRingBuffer
from src.application.code_skeletonizer import CodeSkeletonizer
from src.application.ast_merkle_engine import AstMerkleEngine


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """
    Automatically marks test items based on their containing subfolder:
      - tests/unit/        -> @pytest.mark.unit
      - tests/integration/ -> @pytest.mark.integration
      - tests/e2e/         -> @pytest.mark.e2e
      - tests/benchmarks/  -> @pytest.mark.benchmark
    """
    for item in items:
        fspath = str(item.fspath)
        if "/tests/unit/" in fspath:
            item.add_marker(pytest.mark.unit)
        elif "/tests/integration/" in fspath:
            item.add_marker(pytest.mark.integration)
        elif "/tests/e2e/" in fspath:
            item.add_marker(pytest.mark.e2e)
        elif "/tests/benchmarks/" in fspath or "benchmark_skills" in fspath:
            item.add_marker(pytest.mark.benchmark)


def estimate_tokens(text: str) -> int:
    """Standard token estimation matching GPT/BERT word-and-punctuation boundary tokenizer."""
    return len(re.findall(r"\w+|[^\w\s]", text))


@pytest.fixture(scope="session")
def token_counter() -> Callable[[str], int]:
    """Returns token counter utility callable."""
    return estimate_tokens


@pytest.fixture(scope="session")
def ast_adapter() -> MultiLanguageAstAdapter:
    """Shared MultiLanguageAstAdapter instance for zero-allocation testing."""
    return MultiLanguageAstAdapter()


@pytest.fixture
def skeletonizer(ast_adapter: MultiLanguageAstAdapter) -> CodeSkeletonizer:
    """Provides CodeSkeletonizer instance using real MultiLanguageAstAdapter."""
    return CodeSkeletonizer(parser=ast_adapter)


@pytest.fixture
def merkle_engine() -> AstMerkleEngine:
    """Provides AstMerkleEngine instance in pure RAM mode."""
    return AstMerkleEngine()


@pytest.fixture
def temp_workspace() -> Generator[str, None, None]:
    """Provides an isolated temporary directory cleaned up on test completion."""
    tmp = tempfile.mkdtemp(prefix="event_horizon_test_")
    try:
        yield tmp
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def file_system() -> LocalFileSystemAdapter:
    """Provides LocalFileSystemAdapter instance."""
    return LocalFileSystemAdapter()


@pytest.fixture
def isolated_shm() -> Generator[SharedMemoryRingBuffer, None, None]:
    """Provides an isolated SharedMemoryRingBuffer cleaned up on test completion."""
    shm_name = f"test_shm_{os.getpid()}_{int(tempfile.tempdir is not None)}"
    buf = SharedMemoryRingBuffer(name=shm_name, size=8192, create=True)
    try:
        yield buf
    finally:
        buf.close()
        buf.unlink()


@pytest.fixture(scope="session")
def council_models() -> dict[str, str]:
    """Returns the canonical model names assigned to the local Apple Silicon triad."""
    return {
        "builder_elite": "qwen2.5-coder:7b",
        "skeptic_auditor": "deepseek-r1:1.5b",
        "micro_worker": "smollm2:1.7b",
        "scout_rag": "nomic-embed-text",
    }


@pytest.fixture(scope="session")
def sample_python_code() -> str:
    """Production Python module with classes, inheritance, typing, and docstrings achieving >68% AST compression."""
    from tests.benchmark_skills import PYTHON_FIXTURE_CODE
    return PYTHON_FIXTURE_CODE


@pytest.fixture(scope="session")
def sample_typescript_code() -> str:
    """Production TypeScript module with interfaces, classes, and async methods achieving >68% AST compression."""
    from tests.benchmark_skills import TYPESCRIPT_FIXTURE_CODE
    return TYPESCRIPT_FIXTURE_CODE

