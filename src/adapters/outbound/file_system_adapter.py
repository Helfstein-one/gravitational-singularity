"""
Outbound Adapter: File System Gateway Adapter.
Implements IFileSystemGateway using Python standard library.
"""

from __future__ import annotations
import os
from src.ports.outbound.file_system_port import IFileSystemGateway


class LocalFileSystemAdapter(IFileSystemGateway):
    """Concrete implementation of IFileSystemGateway using OS file APIs."""

    def read_text(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def write_text(self, file_path: str, content: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def exists(self, file_path: str) -> bool:
        return os.path.exists(file_path)
