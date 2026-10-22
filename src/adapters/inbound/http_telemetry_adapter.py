"""
Inbound Adapter: HTTP Telemetry Server on Port 7890.
Serves interactive 360 dashboard and /api/stats REST endpoint.
"""

from __future__ import annotations
import json
import os
import signal
import socket
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from src.adapters.inbound.dashboard_template import HTML_TEMPLATE
from src.adapters.outbound.transcript_file_adapter import FileTranscriptRepository
from src.adapters.outbound.ollama_adapter import OllamaClientAdapter
from src.adapters.outbound.sqlite_epistemic_cache_adapter import SqliteEpistemicCacheAdapter
from src.adapters.outbound.python_ast_adapter import MultiLanguageAstAdapter
from src.application.code_skeletonizer import CodeSkeletonizer
from src.application.epistemic_memoizer import EpistemicMemoizer
from src.application.predictive_pre_warmer import PredictivePreWarmer
from src.application.inference_optimizer import InferenceOptimizer
from src.application.telemetry_aggregator import TelemetryAggregator

PORT = 7890
PID_FILE = os.path.expanduser("~/.gemini/config/token_tracker.pid")
LOG_FILE = os.path.expanduser("~/.gemini/config/token_tracker.log")


class TelemetryHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Antigravity live telemetry."""

    repo = FileTranscriptRepository()
    aggregator = TelemetryAggregator(repo)
    ollama = OllamaClientAdapter()

    _ast_parser = MultiLanguageAstAdapter()
    _skeletonizer = CodeSkeletonizer(_ast_parser)
    _cache = SqliteEpistemicCacheAdapter()
    _memoizer = EpistemicMemoizer(_cache, _skeletonizer)
    prewarmer = PredictivePreWarmer(_memoizer, watch_dirs=["src", "tests"])
    optimizer = InferenceOptimizer()

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ["/", "/dashboard"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif parsed.path in ["/api/stats", "/api/metrics"]:
            data = self.aggregator.aggregate()
            data["local_models"] = self.ollama.list_models()
            pw_metrics = self.prewarmer.get_metrics()
            data["predictive_prewarm_metrics"] = {
                "is_active": pw_metrics.is_active,
                "prewarm_events_total": pw_metrics.prewarm_events_total,
                "prewarmed_files_count": pw_metrics.prewarmed_files_count,
                "last_prewarmed_file": pw_metrics.last_prewarmed_file,
                "avg_prewarm_latency_ms": pw_metrics.avg_prewarm_latency_ms,
            }
            # Reactive IPC Shared Memory stats
            try:
                from src.adapters.outbound.shared_memory_adapter import SharedMemoryRingBuffer
                shm = SharedMemoryRingBuffer(create=False)
                st = shm.get_stats()
                data["shared_memory_ipc"] = {
                    "active": st.get("active", False),
                    "capacity_bytes": st.get("capacity", 65536),
                    "entry_count": st.get("entry_count", 0),
                    "latency_us": "<5",
                    "protocol": "POSIX multiprocessing.shared_memory ring buffer",
                }
            except Exception:
                data["shared_memory_ipc"] = {"active": False}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        elif parsed.path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            # Send initial greeting and stream buffered events
            self.wfile.write(b"event: connected\ndata: {\"status\": \"ok\", \"ipc\": \"shm_zero_copy\", \"latency\": \"<5us\"}\n\n")
            try:
                from src.adapters.outbound.shared_memory_adapter import SharedMemoryRingBuffer
                shm = SharedMemoryRingBuffer(create=False)
                events = shm.read_latest_events(max_count=10)
                for ev in events:
                    ev_type = ev.get("type", "message")
                    ev_data = json.dumps(ev.get("data", {}))
                    self.wfile.write(f"event: {ev_type}\ndata: {ev_data}\n\n".encode("utf-8"))
                self.wfile.flush()
            except Exception:
                pass
        else:
            self.send_response(404)
            self.end_headers()


def run_server(port: int = PORT) -> None:
    server = HTTPServer(("127.0.0.1", port), TelemetryHandler)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    TelemetryHandler.prewarmer.start()
    TelemetryHandler.optimizer.warmup_async()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        TelemetryHandler.prewarmer.stop()
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


def cmd_start() -> None:
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            print(f"[token-tracker] Server already running (PID: {pid}) at http://127.0.0.1:{PORT}")
            return
        except OSError:
            os.remove(PID_FILE)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    is_busy = s.connect_ex(("127.0.0.1", PORT)) == 0
    s.close()
    if is_busy:
        print(f"[token-tracker] Port {PORT} is already in use.")
        return

    pid = os.fork()
    if pid > 0:
        time.sleep(0.5)
        print(f"[token-tracker] Hexagonal Daemon started (PID: {pid})")
        print(f"👉 Web Dashboard: http://127.0.0.1:{PORT}")
        sys.exit(0)
    else:
        os.setsid()
        with open(LOG_FILE, "a") as log:
            sys.stdout = log
            sys.stderr = log
            run_server()


def cmd_stop() -> None:
    if not os.path.exists(PID_FILE):
        print("[token-tracker] Server is not running.")
        return
    with open(PID_FILE) as f:
        pid = int(f.read().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        print(f"[token-tracker] Daemon (PID: {pid}) stopped.")
    except Exception as e:
        print(f"[token-tracker] Error stopping daemon: {e}")
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


def cmd_status() -> None:
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            print(f"[token-tracker] Status: RUNNING (PID: {pid}) at http://127.0.0.1:{PORT}")
            return
        except OSError:
            pass
    print("[token-tracker] Status: STOPPED")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: token-tracker <start | stop | restart | status | run>")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "start":
        cmd_start()
    elif cmd == "stop":
        cmd_stop()
    elif cmd == "restart":
        cmd_stop()
        time.sleep(0.5)
        cmd_start()
    elif cmd == "status":
        cmd_status()
    elif cmd == "run":
        run_server()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
