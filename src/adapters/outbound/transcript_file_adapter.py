"""
Outbound Adapter: Transcript File Repository Adapter.
Implements ITranscriptRepository scanning local Antigravity JSONL session logs.
"""

from __future__ import annotations
import glob
import json
import os
from typing import Any, Iterator
from src.ports.outbound.transcript_repo_port import ITranscriptRepository


class FileTranscriptRepository(ITranscriptRepository):
    """Scans and streams Antigravity JSONL transcripts from brain directory."""

    def __init__(self, data_dir: str | None = None):
        self.data_dir = data_dir or os.path.expanduser("~/.gemini/antigravity/brain")

    def get_all_transcript_paths(self) -> list[str]:
        pattern = os.path.join(self.data_dir, "*", ".system_generated", "logs", "transcript.jsonl")
        files = glob.glob(pattern)
        files.sort(key=lambda p: os.path.getmtime(p))
        return files

    def get_latest_session_id(self) -> str:
        files = self.get_all_transcript_paths()
        if not files:
            return "unknown"
        # path is /.../brain/<session_id>/.system_generated/logs/transcript.jsonl
        return os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(files[-1]))))

    def iter_session_records(self, session_id: str | None = None) -> Iterator[dict[str, Any]]:
        files = self.get_all_transcript_paths()
        for path in files:
            curr_id = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(path))))
            if session_id and curr_id != session_id:
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                yield json.loads(line)
                            except Exception:
                                continue
            except Exception:
                continue
