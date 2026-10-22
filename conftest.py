"""
Global Pytest Configuration and Fixtures for Event Horizon / Gravitational Singularity.
Supports granular test filtering: unit, integration, e2e, and benchmark.
"""

from __future__ import annotations
import os
import shutil
import tempfile
import pytest
from typing import Generator, Any
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.adapters.outbound.file_system_adapter import LocalFileSystemAdapter
from src.adapters.outbound.shared_memory_adapter import SharedMemoryRingBuffer


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


@pytest.fixture(scope="session")
def ast_adapter() -> MultiLanguageAstAdapter:
    """Shared MultiLanguageAstAdapter instance for zero-allocation testing."""
    return MultiLanguageAstAdapter()


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
    """Returns the canonical model names assigned to the multi-agent council."""
    return {
        "builder_elite": "qwen2.5-coder:7b",
        "skeptic_auditor": "deepseek-r1:1.5b",
        "micro_worker": "smollm2:1.7b",
        "builder_agil": "qwen2.5-coder:3b",
        "scout_rag": "nomic-embed-text",
        "scribe_distiller": "hermes3:3b",
        "cloud_orchestrator": "gemini-2.0-pro",
    }
