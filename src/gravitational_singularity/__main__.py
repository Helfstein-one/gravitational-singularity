"""
CLI entry point for `python -m gravitational_singularity`.
"""

from __future__ import annotations
import sys
from src.adapters.inbound.doctor_cli import main

if __name__ == "__main__":
    sys.exit(main())
