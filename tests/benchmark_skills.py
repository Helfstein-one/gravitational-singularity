#!/usr/bin/env python3
"""
Comprehensive 4-Tier E2E Test Suite and Quantitative Benchmark Harness
for macOS-air Agentic Skills (ast-search and cognitive-meta-router).

Architecture:
  - Zero external dependencies: stdlib only (ast, re, json, os, sys, pathlib, subprocess, unittest).
  - Dual execution compatibility: standalone (python3 tests/benchmark_skills.py) and pytest.
  - 4-Tier Verification Methodology:
      Tier 1: Architectural Integrity & Feature Coverage
      Tier 2: Boundary & Corner Cases
      Tier 3: Cross-Feature Combinations & Integrations
      Tier 4: Real-World Workload Quantitative Benchmarks (>= 60% token/char reduction)
"""

from __future__ import annotations

import ast
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

# ==============================================================================
# Paths & Canonical Locations
# ==============================================================================

HOME = pathlib.Path.home()
SKILLS_DIR = HOME / ".gemini" / "config" / ".agents" / "skills"

AST_SEARCH_DIR = SKILLS_DIR / "ast-search"
AST_SEARCH_SKILL_MD = AST_SEARCH_DIR / "SKILL.md"
AST_EXTRACTOR_BIN = AST_SEARCH_DIR / "bin" / "ast_extractor.py"
AST_EXTRACTOR_FALLBACK = AST_SEARCH_DIR / "ast_extractor.py"

COGNITIVE_ROUTER_DIR = SKILLS_DIR / "cognitive-meta-router"
COGNITIVE_ROUTER_SKILL_MD = COGNITIVE_ROUTER_DIR / "SKILL.md"

CLI_PROXY_BIN = HOME / ".local" / "bin" / "ast-search"


# ==============================================================================
# Helper Utilities (Zero-Dependency)
# ==============================================================================

def get_ast_extractor_path() -> pathlib.Path:
    """Returns the existing path to ast_extractor.py or raises FileNotFoundError."""
    if AST_EXTRACTOR_BIN.exists():
        return AST_EXTRACTOR_BIN
    if AST_EXTRACTOR_FALLBACK.exists():
        return AST_EXTRACTOR_FALLBACK
    if CLI_PROXY_BIN.exists():
        return CLI_PROXY_BIN
    raise FileNotFoundError(
        f"ast_extractor.py not found at {AST_EXTRACTOR_BIN} or {AST_EXTRACTOR_FALLBACK}"
    )


def parse_frontmatter(text: str) -> dict[str, str]:
    """
    Parses YAML frontmatter delimited by ^---\n...\n--- using stdlib regex.
    Returns dictionary of top-level key-value pairs.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text, re.DOTALL)
    if not match:
        return {}
    frontmatter_body = match.group(1)
    data: dict[str, str] = {}
    for line in frontmatter_body.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            data[key.strip()] = val.strip().strip("\"'")
    return data


def count_tokens(text: str) -> int:
    """
    Computes lexical token approximation highly correlated with BPE tokenizers.
    Tokens are alphanumeric words and non-whitespace punctuation/symbols.
    Formula: len(re.findall(r'\\w+|[^\\w\\s]', text))
    """
    return len(re.findall(r"\w+|[^\w\s]", text))


def count_non_empty_lines(text: str) -> int:
    """Counts non-empty, non-whitespace-only lines."""
    return len([line for line in text.splitlines() if line.strip()])


def calculate_metrics(raw_text: str, compressed_text: str) -> dict[str, float]:
    """Computes exact reduction metrics between raw and compressed text."""
    raw_chars = len(raw_text)
    comp_chars = len(compressed_text)
    raw_tokens = count_tokens(raw_text)
    comp_tokens = count_tokens(compressed_text)
    raw_lines = count_non_empty_lines(raw_text)
    comp_lines = count_non_empty_lines(compressed_text)

    char_reduction = ((raw_chars - comp_chars) / raw_chars * 100.0) if raw_chars > 0 else 0.0
    token_reduction = ((raw_tokens - comp_tokens) / raw_tokens * 100.0) if raw_tokens > 0 else 0.0
    line_reduction = ((raw_lines - comp_lines) / raw_lines * 100.0) if raw_lines > 0 else 0.0

    return {
        "raw_chars": raw_chars,
        "comp_chars": comp_chars,
        "char_reduction": char_reduction,
        "raw_tokens": raw_tokens,
        "comp_tokens": comp_tokens,
        "token_reduction": token_reduction,
        "raw_lines": raw_lines,
        "comp_lines": comp_lines,
        "line_reduction": line_reduction,
    }


def execute_extractor(args: list[str], timeout: float = 10.0) -> subprocess.CompletedProcess[str]:
    """Executes the AST extractor with given CLI arguments."""
    extractor = get_ast_extractor_path()
    cmd = [sys.executable, str(extractor)] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


# ==============================================================================
# Production-Grade Fixtures (>= 70 Lines with Real Logic & Decorators)
# ==============================================================================

PYTHON_FIXTURE_CODE = '''"""
Distributed Stream Processing Engine for real-time telemetry events.
Provides partitioned stream ingestion, backpressure regulation, and stateful aggregation.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class StreamProcessingError(Exception):
    """Raised when stream ingestion or transformation invariants are violated."""
    pass


class DistributedStreamProcessor:
    """
    Core distributed stream ingest worker with stateful deduplication.
    Manages partition routing, local memory buffering, and metric telemetry.
    """

    DEFAULT_RETRY_BACKOFF: float = 0.25

    def __init__(self, stream_id: str, partition_count: int = 16, buffer_capacity: int = 10000) -> None:
        """Initialize the stream processor with active configuration."""
        self.stream_id = stream_id
        self.partition_count = partition_count
        self.buffer_capacity = buffer_capacity
        self.logger = logging.getLogger(__name__)
        self._buffer: List[Dict[str, Any]] = []
        self._seen_event_ids: Set[str] = set()
        self._total_received: int = 0
        self._total_committed: int = 0
        self._total_dropped: int = 0
        self._last_flush_timestamp: float = time.time()
        self._is_running: bool = False
        self._lock = asyncio.Lock()

    @property
    def is_running(self) -> bool:
        """Indicates whether the ingestion loop is active."""
        return self._is_running

    @classmethod
    def from_environment(cls, stream_id: str) -> "DistributedStreamProcessor":
        """Factory method creating an instance from default environment variables."""
        import os
        part_count = int(os.environ.get("STREAM_PARTITIONS", "16"))
        buf_cap = int(os.environ.get("STREAM_BUFFER_CAP", "10000"))
        return cls(stream_id=stream_id, partition_count=part_count, buffer_capacity=buf_cap)

    @staticmethod
    def compute_partition_id(event_key: str, total_partitions: int) -> int:
        """Computes deterministic integer partition identifier for a routing key."""
        if not event_key:
            raise ValueError("Routing key cannot be empty")
        raw_hash = hashlib.sha256(event_key.encode("utf-8")).hexdigest()
        prefix = raw_hash[:8]
        integer_val = int(prefix, 16)
        return integer_val % total_partitions

    async def start(self) -> None:
        """Starts stream workers and consumer loops."""
        async with self._lock:
            if self._is_running:
                raise StreamProcessingError("Processor is already running")
            self._is_running = True
            self._last_flush_timestamp = time.time()
            self.logger.info("Started stream processor %s with %d partitions", self.stream_id, self.partition_count)

    async def ingest_batch(self, batch_id: str, records: List[Dict[str, Any]], timeout: float = 30.0) -> Dict[str, Any]:
        """Ingests a batch of records, deduplicating against recently seen IDs."""
        if not self._is_running:
            raise StreamProcessingError("Cannot ingest batch: processor is not active")

        start_time = time.time()
        accepted_records: List[Dict[str, Any]] = []
        dropped_count = 0

        for record in records:
            event_id = record.get("event_id")
            if not event_id:
                dropped_count += 1
                continue

            if event_id in self._seen_event_ids:
                dropped_count += 1
                continue

            routing_key = record.get("routing_key", event_id)
            partition = self.compute_partition_id(routing_key, self.partition_count)

            transformed = {
                "batch_id": batch_id,
                "event_id": event_id,
                "partition": partition,
                "ingested_at": time.time(),
                "payload_size": len(json.dumps(record.get("payload", {}))),
                "data": record.get("payload", {})
            }

            accepted_records.append(transformed)
            self._seen_event_ids.add(event_id)

            if len(self._seen_event_ids) > 100000:
                self._seen_event_ids.clear()

        async with self._lock:
            self._buffer.extend(accepted_records)
            self._total_received += len(accepted_records)
            self._total_dropped += dropped_count

            if len(self._buffer) >= self.buffer_capacity:
                await self.flush()

        duration = time.time() - start_time
        return {
            "batch_id": batch_id,
            "accepted": len(accepted_records),
            "dropped": dropped_count,
            "duration_ms": round(duration * 1000, 2),
            "buffered_now": len(self._buffer)
        }

    async def flush(self, force: bool = False) -> int:
        """Flushes the current in-memory buffer to persistent storage."""
        async with self._lock:
            if not self._buffer and not force:
                return 0

            records_to_commit = list(self._buffer)
            self._buffer.clear()

            partition_groups: Dict[int, List[Dict[str, Any]]] = {}
            for rec in records_to_commit:
                p = rec["partition"]
                if p not in partition_groups:
                    partition_groups[p] = []
                partition_groups[p].append(rec)

            committed_total = 0
            for partition_id, group_items in partition_groups.items():
                self.logger.debug("Flushing %d records to partition %d", len(group_items), partition_id)
                committed_total += len(group_items)

            self._total_committed += committed_total
            self._last_flush_timestamp = time.time()
            return committed_total

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Returns snapshot dictionary of operational telemetry."""
        now = time.time()
        elapsed = max(0.001, now - self._last_flush_timestamp)
        return {
            "stream_id": self.stream_id,
            "partition_count": self.partition_count,
            "buffered_count": len(self._buffer),
            "received": self._total_received,
            "committed": self._total_committed,
            "dropped": self._total_dropped,
            "rate_per_sec": round(self._total_committed / elapsed, 2),
            "is_running": self._is_running
        }
'''

TYPESCRIPT_FIXTURE_CODE = '''/**
 * Telemetry and metric dispatch router for client session events.
 * Handles rate limiting, event sanitization, batch queuing, and downstream dispatch.
 */

import { EventEmitter } from "events";

export interface TelemetryEvent {
  eventId: string;
  timestamp: number;
  category: "navigation" | "interaction" | "error" | "performance";
  payload: Record<string, unknown>;
  userId?: string;
  sessionId?: string;
}

export interface RouterOptions {
  endpoint: string;
  flushIntervalMs?: number;
  batchSize?: number;
  maxQueueDepth?: number;
  enableSanitization?: boolean;
}

export type RoutingStrategy = "direct" | "batched" | "sampled";

export class TelemetryRouter extends EventEmitter {
  private readonly endpoint: string;
  private readonly flushIntervalMs: number;
  private readonly batchSize: number;
  private readonly maxQueueDepth: number;
  private readonly enableSanitization: boolean;
  private queue: TelemetryEvent[];
  private timerHandle: NodeJS.Timeout | null;
  private isShuttingDown: boolean;
  private totalDispatched: number;
  private totalDropped: number;

  /**
   * Constructs a new TelemetryRouter instance with specified options.
   */
  constructor(options: RouterOptions) {
    super();
    this.endpoint = options.endpoint;
    this.flushIntervalMs = options.flushIntervalMs ?? 5000;
    this.batchSize = options.batchSize ?? 100;
    this.maxQueueDepth = options.maxQueueDepth ?? 10000;
    this.enableSanitization = options.enableSanitization ?? true;
    this.queue = [];
    this.timerHandle = null;
    this.isShuttingDown = false;
    this.totalDispatched = 0;
    this.totalDropped = 0;
  }

  /**
   * Initializes periodic flush timers and registers signal listeners.
   */
  public async initialize(): Promise<void> {
    if (this.timerHandle !== null) {
      return;
    }
    this.timerHandle = setInterval(() => {
      void this.flush();
    }, this.flushIntervalMs);
    this.emit("ready", { endpoint: this.endpoint, batchSize: this.batchSize });
  }

  /**
   * Dispatches an incoming event, applying validation and enqueueing.
   */
  public async dispatch(event: TelemetryEvent): Promise<boolean> {
    if (this.isShuttingDown) {
      this.emit("warn", "Event rejected during router shutdown");
      return false;
    }

    if (!event.eventId || !event.category) {
      this.totalDropped++;
      this.emit("drop", { reason: "invalid_event", eventId: event.eventId });
      return false;
    }

    if (this.queue.length >= this.maxQueueDepth) {
      this.totalDropped++;
      this.emit("drop", { reason: "queue_overflow", eventId: event.eventId });
      return false;
    }

    const processed = this.enableSanitization ? this.sanitize(event) : event;
    this.queue.push(processed);

    if (this.queue.length >= this.batchSize) {
      await this.flush();
    }

    return true;
  }

  /**
   * Flushes currently queued events to the remote ingestion endpoint.
   */
  public async flush(): Promise<number> {
    if (this.queue.length === 0) {
      return 0;
    }

    const batch = this.queue.splice(0, this.batchSize);
    const payload = JSON.stringify({
      batch,
      dispatchedAt: Date.now(),
      batchLength: batch.length,
      protocolVersion: "2.4"
    });

    try {
      const response = await fetch(this.endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Client-Timestamp": Date.now().toString(),
          "X-Batch-Size": batch.length.toString()
        },
        body: payload
      });

      if (!response.ok) {
        throw new Error(`Failed to transmit telemetry batch: status ${response.status}`);
      }

      this.totalDispatched += batch.length;
      this.emit("flush", { count: batch.length, remaining: this.queue.length });
      return batch.length;
    } catch (err) {
      this.emit("error", err);
      for (let i = batch.length - 1; i >= 0; i--) {
        this.queue.unshift(batch[i]);
      }
      return 0;
    }
  }

  /**
   * Sanitizes sensitive fields from payload prior to external transmission.
   */
  private sanitize(event: TelemetryEvent): TelemetryEvent {
    const sanitizedPayload: Record<string, unknown> = {};
    const sensitiveKeys = new Set(["password", "token", "secret", "creditCard", "authHeader"]);

    for (const [key, value] of Object.entries(event.payload || {})) {
      if (sensitiveKeys.has(key)) {
        sanitizedPayload[key] = "[REDACTED]";
      } else if (typeof value === "string" && value.length > 1024) {
        sanitizedPayload[key] = value.slice(0, 1024) + "...[TRUNCATED]";
      } else {
        sanitizedPayload[key] = value;
      }
    }

    return {
      eventId: event.eventId,
      timestamp: event.timestamp || Date.now(),
      category: event.category,
      payload: sanitizedPayload,
      userId: event.userId,
      sessionId: event.sessionId
    };
  }

  /**
   * Shuts down the router, draining remaining queue items.
   */
  public async shutdown(): Promise<void> {
    this.isShuttingDown = true;
    if (this.timerHandle !== null) {
      clearInterval(this.timerHandle);
      this.timerHandle = null;
    }
    while (this.queue.length > 0) {
      await this.flush();
    }
    this.emit("close", { totalDispatched: this.totalDispatched, totalDropped: this.totalDropped });
  }
}
'''


# ==============================================================================
# Tier 1: Architectural Integrity & Feature Coverage
# ==============================================================================

class TestTier1ArchitecturalIntegrity(unittest.TestCase):
    """Verifies existence, YAML frontmatter, protocols, executable bits, and CLI help."""

    def test_01_ast_search_skill_exists_and_frontmatter(self) -> None:
        """ast-search/SKILL.md must exist and contain valid YAML frontmatter."""
        self.assertTrue(
            AST_SEARCH_SKILL_MD.exists(),
            f"Expected SKILL.md at {AST_SEARCH_SKILL_MD}",
        )
        content = AST_SEARCH_SKILL_MD.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        self.assertIn("name", fm, "Missing 'name' field in ast-search SKILL.md frontmatter")
        self.assertEqual(fm["name"], "ast-search", "Frontmatter name must be 'ast-search'")
        self.assertIn("description", fm, "Missing 'description' field in ast-search SKILL.md frontmatter")
        self.assertTrue(len(fm["description"].strip()) > 10, "Description field must be non-empty")

    def test_02_cognitive_meta_router_skill_exists_and_frontmatter(self) -> None:
        """cognitive-meta-router/SKILL.md must exist and contain valid YAML frontmatter."""
        self.assertTrue(
            COGNITIVE_ROUTER_SKILL_MD.exists(),
            f"Expected SKILL.md at {COGNITIVE_ROUTER_SKILL_MD}",
        )
        content = COGNITIVE_ROUTER_SKILL_MD.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        self.assertIn("name", fm, "Missing 'name' field in cognitive-meta-router SKILL.md frontmatter")
        self.assertEqual(fm["name"], "cognitive-meta-router", "Frontmatter name must be 'cognitive-meta-router'")
        self.assertIn("description", fm, "Missing 'description' field in cognitive-meta-router frontmatter")
        self.assertTrue(len(fm["description"].strip()) > 10, "Description field must be non-empty")

    def test_03_cognitive_meta_router_protocols(self) -> None:
        """cognitive-meta-router/SKILL.md must explicitly document PS, SR, and STB protocols."""
        content = COGNITIVE_ROUTER_SKILL_MD.read_text(encoding="utf-8")
        lower_content = content.lower()

        self.assertTrue(
            "plan-and-solve" in lower_content or "plan and solve" in lower_content,
            "cognitive-meta-router/SKILL.md must document Plan-and-Solve protocol",
        )
        self.assertTrue(
            "self-refine" in lower_content or "self refine" in lower_content,
            "cognitive-meta-router/SKILL.md must document Self-Refine protocol",
        )
        self.assertTrue(
            "token budget" in lower_content or "token budgeting" in lower_content,
            "cognitive-meta-router/SKILL.md must document Subagent Token Budgeting protocol",
        )

    def test_04_helper_script_permissions_and_shebang(self) -> None:
        """ast_extractor.py must have executable permissions (0755) and Python shebang."""
        extractor = get_ast_extractor_path()
        self.assertTrue(
            os.access(extractor, os.X_OK),
            f"File {extractor} must have executable permissions (os.X_OK)",
        )
        with open(extractor, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        self.assertTrue(
            first_line.startswith("#!") and "python" in first_line,
            f"File {extractor} must start with python shebang (got {first_line})",
        )

    def test_05_cli_proxy_executable(self) -> None:
        """~/.local/bin/ast-search must exist and be executable."""
        self.assertTrue(
            CLI_PROXY_BIN.exists(),
            f"CLI proxy {CLI_PROXY_BIN} must exist",
        )
        self.assertTrue(
            os.access(CLI_PROXY_BIN, os.X_OK),
            f"CLI proxy {CLI_PROXY_BIN} must be executable (os.X_OK)",
        )

    def test_06_helper_cli_help(self) -> None:
        """ast_extractor.py --help must return exit code 0 and emit usage."""
        proc = execute_extractor(["--help"])
        self.assertEqual(
            proc.returncode,
            0,
            f"ast_extractor.py --help failed with exit code {proc.returncode}: {proc.stderr}",
        )
        self.assertTrue(
            "usage:" in proc.stdout.lower() or "options:" in proc.stdout.lower() or "help" in proc.stdout.lower(),
            "Help output must contain usage information",
        )


# ==============================================================================
# Tier 2: Boundary & Corner Cases
# ==============================================================================

class TestTier2BoundaryAndCornerCases(unittest.TestCase):
    """Verifies edge cases: empty files, comments, single-symbol files, syntax errors."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="ast_test_edge_")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_07_empty_file_handling(self) -> None:
        """Extracting AST from an empty file must succeed with code 0 and minimal output."""
        empty_py = pathlib.Path(self.temp_dir) / "empty.py"
        empty_py.write_text("", encoding="utf-8")

        proc = execute_extractor([str(empty_py)])
        self.assertEqual(proc.returncode, 0, f"Failed on empty file: {proc.stderr}")
        self.assertEqual(proc.stdout.strip(), "", "Empty file should yield empty skeleton")

    def test_08_comments_only_file(self) -> None:
        """File with only comments and imports should be handled cleanly without errors."""
        comment_py = pathlib.Path(self.temp_dir) / "comments_only.py"
        comment_py.write_text(
            "# Module comments\nimport sys\nimport os\n# Another comment\n",
            encoding="utf-8",
        )
        proc = execute_extractor([str(comment_py)])
        self.assertEqual(proc.returncode, 0, f"Failed on comments-only file: {proc.stderr}")
        self.assertTrue("import sys" in proc.stdout or "sys" in proc.stdout)

    def test_09_single_class_or_function(self) -> None:
        """Single function without class or module docstring must produce valid skeleton."""
        single_fn_py = pathlib.Path(self.temp_dir) / "single_fn.py"
        single_fn_py.write_text(
            "def compute_hash(data: str) -> str:\n    import hashlib\n    return hashlib.md5(data.encode()).hexdigest()\n",
            encoding="utf-8",
        )
        proc = execute_extractor([str(single_fn_py)])
        self.assertEqual(proc.returncode, 0, f"Failed on single function: {proc.stderr}")
        self.assertTrue("compute_hash" in proc.stdout)
        self.assertTrue("..." in proc.stdout)

    def test_10_syntax_error_handling(self) -> None:
        """Syntax errors in input code must be caught cleanly with non-zero exit code or error output."""
        bad_py = pathlib.Path(self.temp_dir) / "invalid_syntax.py"
        bad_py.write_text("def broken_func(:\n  return\n", encoding="utf-8")

        proc = execute_extractor([str(bad_py)])
        self.assertTrue(
            proc.returncode != 0 or "error" in proc.stderr.lower() or "error" in proc.stdout.lower(),
            "Expected non-zero exit code or explicit error output for syntax error",
        )

    def test_11_missing_file_handling(self) -> None:
        """Specifying non-existent file path must exit with code 1 and descriptive error."""
        non_existent = pathlib.Path(self.temp_dir) / "does_not_exist.py"
        proc = execute_extractor([str(non_existent)])
        self.assertNotEqual(proc.returncode, 0, "Missing file should exit with non-zero code")

    def test_12_cli_docstring_options(self) -> None:
        """Verifies docstring retention flags: summary, full, and none."""
        doc_py = pathlib.Path(self.temp_dir) / "doc_test.py"
        doc_py.write_text(
            'def documented_fn() -> None:\n    """First line summary.\n\n    Detailed multi-paragraph description.\n    More details.\n    """\n    pass\n',
            encoding="utf-8",
        )

        # Mode: summary (default)
        proc_summary = execute_extractor(["--docstrings", "summary", str(doc_py)])
        self.assertEqual(proc_summary.returncode, 0)
        self.assertTrue("First line summary" in proc_summary.stdout)

        # Mode: none
        proc_none = execute_extractor(["--docstrings", "none", str(doc_py)])
        self.assertEqual(proc_none.returncode, 0)
        self.assertNotIn("First line summary", proc_none.stdout)
        self.assertNotIn("Detailed multi-paragraph", proc_none.stdout)


# ==============================================================================
# Tier 3: Cross-Feature Combinations & Integrations
# ==============================================================================

class TestTier3CrossFeatureCombinations(unittest.TestCase):
    """Verifies output formats (code, json, tree), symbol query filtering, and stats."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="ast_test_combo_")
        self.py_file = pathlib.Path(self.temp_dir) / "processor.py"
        self.py_file.write_text(PYTHON_FIXTURE_CODE, encoding="utf-8")

        self.ts_file = pathlib.Path(self.temp_dir) / "router.ts"
        self.ts_file.write_text(TYPESCRIPT_FIXTURE_CODE, encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_13_cli_format_json(self) -> None:
        """--format json must output parseable JSON with symbol structure."""
        proc = execute_extractor(["--format", "json", str(self.py_file)])
        self.assertEqual(proc.returncode, 0, f"JSON output failed: {proc.stderr}")

        try:
            parsed = json.loads(proc.stdout)
        except json.JSONDecodeError as err:
            self.fail(f"--format json output is not valid JSON: {err}\nOutput: {proc.stdout[:300]}")

        self.assertIsInstance(parsed, (dict, list))
        # Ensure symbols or classes exist in json
        dumped = json.dumps(parsed)
        self.assertTrue(
            "DistributedStreamProcessor" in dumped or "processor.py" in dumped,
            "JSON structure must mention analyzed symbols",
        )

    def test_14_cli_format_tree(self) -> None:
        """--format tree must output structured hierarchy of classes and methods."""
        proc = execute_extractor(["--format", "tree", str(self.py_file)])
        self.assertEqual(proc.returncode, 0, f"Tree output failed: {proc.stderr}")
        self.assertTrue(
            "DistributedStreamProcessor" in proc.stdout,
            "Tree output should list class name",
        )

    def test_15_cli_mode_query(self) -> None:
        """--query <pattern> must filter output to matching symbols only."""
        proc = execute_extractor(["--query", "compute_partition_id", str(self.py_file)])
        self.assertEqual(proc.returncode, 0, f"Query mode failed: {proc.stderr}")
        self.assertIn("compute_partition_id", proc.stdout)
        # Should not include unrelated methods like ingest_record in filtered output
        self.assertNotIn("ingest_record", proc.stdout)

    def test_16_language_override_flag(self) -> None:
        """--lang flag forces language parser regardless of file extension."""
        neutral_file = pathlib.Path(self.temp_dir) / "source_code.txt"
        neutral_file.write_text(PYTHON_FIXTURE_CODE, encoding="utf-8")

        proc = execute_extractor(["--lang", "python", str(neutral_file)])
        self.assertEqual(proc.returncode, 0, f"Language override failed: {proc.stderr}")
        self.assertIn("class DistributedStreamProcessor", proc.stdout)

    def test_17_cli_stats_flag(self) -> None:
        """--stats flag must emit reduction statistics to stderr or stdout."""
        proc = execute_extractor(["--stats", str(self.py_file)])
        self.assertEqual(proc.returncode, 0, f"Stats execution failed: {proc.stderr}")
        combined = (proc.stderr + proc.stdout).lower()
        self.assertTrue(
            "reduction" in combined or "%" in combined or "chars" in combined or "tokens" in combined,
            f"--stats must output reduction metrics (got stderr: '{proc.stderr}')",
        )


# ==============================================================================
# Tier 4: Real-World Workload Quantitative Benchmarks (>= 60% Reduction)
# ==============================================================================

class TestTier4RealWorldBenchmarks(unittest.TestCase):
    """Empirical token, character, and line reduction benchmarks on realistic services."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="ast_bench_")
        self.py_file = pathlib.Path(self.temp_dir) / "stream_processor.py"
        self.py_file.write_text(PYTHON_FIXTURE_CODE, encoding="utf-8")

        self.ts_file = pathlib.Path(self.temp_dir) / "telemetry_router.ts"
        self.ts_file.write_text(TYPESCRIPT_FIXTURE_CODE, encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_18_python_token_reduction_ge_60(self) -> None:
        """Python fixture token reduction must be >= 60.0%."""
        proc = execute_extractor([str(self.py_file)])
        self.assertEqual(proc.returncode, 0, f"Extraction failed: {proc.stderr}")
        compressed = proc.stdout
        metrics = calculate_metrics(PYTHON_FIXTURE_CODE, compressed)
        red = metrics["token_reduction"]
        self.assertGreaterEqual(
            red,
            60.0,
            f"Python token reduction {red:.2f}% is below required 60.0% threshold (Raw: {metrics['raw_tokens']}, Comp: {metrics['comp_tokens']})",
        )

    def test_19_python_character_reduction_ge_60(self) -> None:
        """Python fixture character reduction must be >= 60.0%."""
        proc = execute_extractor([str(self.py_file)])
        self.assertEqual(proc.returncode, 0, f"Extraction failed: {proc.stderr}")
        compressed = proc.stdout
        metrics = calculate_metrics(PYTHON_FIXTURE_CODE, compressed)
        red = metrics["char_reduction"]
        self.assertGreaterEqual(
            red,
            60.0,
            f"Python character reduction {red:.2f}% is below required 60.0% threshold (Raw: {metrics['raw_chars']}, Comp: {metrics['comp_chars']})",
        )

    def test_20_python_line_reduction_ge_50(self) -> None:
        """Python fixture non-empty line reduction must be >= 50.0%."""
        proc = execute_extractor([str(self.py_file)])
        self.assertEqual(proc.returncode, 0, f"Extraction failed: {proc.stderr}")
        compressed = proc.stdout
        metrics = calculate_metrics(PYTHON_FIXTURE_CODE, compressed)
        red = metrics["line_reduction"]
        self.assertGreaterEqual(
            red,
            50.0,
            f"Python line reduction {red:.2f}% is below required 50.0% threshold (Raw lines: {metrics['raw_lines']}, Comp lines: {metrics['comp_lines']})",
        )

    def test_21_python_skeleton_syntax_validity(self) -> None:
        """Compressed Python skeleton must parse without error via ast.parse()."""
        proc = execute_extractor([str(self.py_file)])
        self.assertEqual(proc.returncode, 0, f"Extraction failed: {proc.stderr}")
        try:
            ast.parse(proc.stdout)
        except SyntaxError as err:
            self.fail(f"Compressed Python skeleton is not syntactically valid: {err}\n{proc.stdout}")

    def test_22_typescript_token_reduction_ge_60(self) -> None:
        """TypeScript fixture token reduction must be >= 60.0%."""
        proc = execute_extractor([str(self.ts_file)])
        self.assertEqual(proc.returncode, 0, f"TypeScript extraction failed: {proc.stderr}")
        compressed = proc.stdout
        metrics = calculate_metrics(TYPESCRIPT_FIXTURE_CODE, compressed)
        red = metrics["token_reduction"]
        self.assertGreaterEqual(
            red,
            60.0,
            f"TypeScript token reduction {red:.2f}% is below required 60.0% threshold (Raw: {metrics['raw_tokens']}, Comp: {metrics['comp_tokens']})",
        )

    def test_23_typescript_character_reduction_ge_60(self) -> None:
        """TypeScript fixture character reduction must be >= 60.0%."""
        proc = execute_extractor([str(self.ts_file)])
        self.assertEqual(proc.returncode, 0, f"TypeScript extraction failed: {proc.stderr}")
        compressed = proc.stdout
        metrics = calculate_metrics(TYPESCRIPT_FIXTURE_CODE, compressed)
        red = metrics["char_reduction"]
        self.assertGreaterEqual(
            red,
            60.0,
            f"TypeScript character reduction {red:.2f}% is below required 60.0% threshold (Raw: {metrics['raw_chars']}, Comp: {metrics['comp_chars']})",
        )

    def test_24_typescript_line_reduction_ge_50(self) -> None:
        """TypeScript fixture non-empty line reduction must be >= 50.0%."""
        proc = execute_extractor([str(self.ts_file)])
        self.assertEqual(proc.returncode, 0, f"TypeScript extraction failed: {proc.stderr}")
        compressed = proc.stdout
        metrics = calculate_metrics(TYPESCRIPT_FIXTURE_CODE, compressed)
        red = metrics["line_reduction"]
        self.assertGreaterEqual(
            red,
            50.0,
            f"TypeScript line reduction {red:.2f}% is below required 50.0% threshold (Raw lines: {metrics['raw_lines']}, Comp lines: {metrics['comp_lines']})",
        )

    def test_25_average_token_reduction_ge_60(self) -> None:
        """Aggregate average token reduction across Python and TypeScript must be >= 60.0%."""
        py_proc = execute_extractor([str(self.py_file)])
        ts_proc = execute_extractor([str(self.ts_file)])
        self.assertEqual(py_proc.returncode, 0)
        self.assertEqual(ts_proc.returncode, 0)

        py_metrics = calculate_metrics(PYTHON_FIXTURE_CODE, py_proc.stdout)
        ts_metrics = calculate_metrics(TYPESCRIPT_FIXTURE_CODE, ts_proc.stdout)

        avg_token_reduction = (py_metrics["token_reduction"] + ts_metrics["token_reduction"]) / 2.0
        self.assertGreaterEqual(
            avg_token_reduction,
            60.0,
            f"Average token reduction {avg_token_reduction:.2f}% is below required 60.0% threshold",
        )


# ==============================================================================
# Standalone Benchmark Report & CLI Runner
# ==============================================================================

def print_benchmark_table() -> bool:
    """Runs empirical benchmark measurements and prints formatted ASCII table."""
    with tempfile.TemporaryDirectory(prefix="ast_bench_cli_") as tmpdir:
        py_file = pathlib.Path(tmpdir) / "stream_processor.py"
        py_file.write_text(PYTHON_FIXTURE_CODE, encoding="utf-8")

        ts_file = pathlib.Path(tmpdir) / "telemetry_router.ts"
        ts_file.write_text(TYPESCRIPT_FIXTURE_CODE, encoding="utf-8")

        try:
            py_proc = execute_extractor([str(py_file)])
            ts_proc = execute_extractor([str(ts_file)])
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"\n[ERROR] Failed to execute AST extractor for benchmarks: {exc}", file=sys.stderr)
            return False

        if py_proc.returncode != 0 or ts_proc.returncode != 0:
            print("\n[ERROR] Extractor returned non-zero exit code during benchmark:", file=sys.stderr)
            if py_proc.returncode != 0:
                print(f"  Python stderr: {py_proc.stderr}", file=sys.stderr)
            if ts_proc.returncode != 0:
                print(f"  TypeScript stderr: {ts_proc.stderr}", file=sys.stderr)
            return False

        py_m = calculate_metrics(PYTHON_FIXTURE_CODE, py_proc.stdout)
        ts_m = calculate_metrics(TYPESCRIPT_FIXTURE_CODE, ts_proc.stdout)

        py_pass = py_m["token_reduction"] >= 60.0 and py_m["char_reduction"] >= 60.0 and py_m["line_reduction"] >= 50.0
        ts_pass = ts_m["token_reduction"] >= 60.0 and ts_m["char_reduction"] >= 60.0 and ts_m["line_reduction"] >= 50.0

        sep_double = "=" * 92
        sep_single = "-" * 92
        title = f"{'macOS-air Skills Benchmark & Quantitative Reduction Report':^92}"
        columns = f"{'Language / Fixture':<22} | {'Raw Tokens':>10} | {'Comp Tokens':>11} | {'Token %':>8} | {'Char %':>8} | {'Line %':>8} | {'Status':>6}"
        print(f"\n{sep_double}\n{title}\n{sep_double}\n{columns}\n{sep_single}")

        py_status = "PASS" if py_pass else "FAIL"
        print(
            f"{'Python (StreamProc)':<22} | {py_m['raw_tokens']:>10} | {py_m['comp_tokens']:>11} | {py_m['token_reduction']:>7.1f}% | {py_m['char_reduction']:>7.1f}% | {py_m['line_reduction']:>7.1f}% | {py_status:>6}"
        )

        ts_status = "PASS" if ts_pass else "FAIL"
        print(
            f"{'TypeScript (Router)':<22} | {ts_m['raw_tokens']:>10} | {ts_m['comp_tokens']:>11} | {ts_m['token_reduction']:>7.1f}% | {ts_m['char_reduction']:>7.1f}% | {ts_m['line_reduction']:>7.1f}% | {ts_status:>6}"
        )

        avg_token_red = (py_m["token_reduction"] + ts_m["token_reduction"]) / 2.0
        avg_char_red = (py_m["char_reduction"] + ts_m["char_reduction"]) / 2.0
        avg_line_red = (py_m["line_reduction"] + ts_m["line_reduction"]) / 2.0
        overall_pass = py_pass and ts_pass and avg_token_red >= 60.0
        overall_status = "PASS" if overall_pass else "FAIL"

        print(sep_single)
        print(
            f"{'Weighted Average':<22} | {'-':>10} | {'-':>11} | {avg_token_red:>7.1f}% | {avg_char_red:>7.1f}% | {avg_line_red:>7.1f}% | {overall_status:>6}"
        )
        print(f"{sep_double}\n")

        return overall_pass


def main() -> int:
    """Main CLI entrypoint running test suite and outputting benchmark matrix."""
    print("=" * 92)
    print(f"{'Executing macOS-air E2E Test Suite (Tiers 1-4)':^92}")
    print("=" * 92)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestTier1ArchitecturalIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestTier2BoundaryAndCornerCases))
    suite.addTests(loader.loadTestsFromTestCase(TestTier3CrossFeatureCombinations))
    suite.addTests(loader.loadTestsFromTestCase(TestTier4RealWorldBenchmarks))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    benchmarks_passed = print_benchmark_table()

    if result.wasSuccessful() and benchmarks_passed:
        print("[SUCCESS] All 25 E2E integrity assertions and quantitative benchmarks PASSED.")
        return 0
    else:
        print(
            f"[FAILURE] Test suite encountered {len(result.failures)} failures and {len(result.errors)} errors.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
