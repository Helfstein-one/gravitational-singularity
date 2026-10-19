"""
Outbound Port: File System Gateway Interface.
"""

from typing import Protocol


class IFileSystemGateway(Protocol):
    """Abstract interface for atomic file system operations."""

    def read_text(self, file_path: str) -> str:
        """Reads file contents with UTF-8 encoding."""
        ...

    def write_text(self, file_path: str, content: str) -> None:
        """Writes file contents safely."""
        ...

    def exists(self, file_path: str) -> bool:
        """Checks if file or directory exists."""
        ...
