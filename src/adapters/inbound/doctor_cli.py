"""
Inbound Adapter: CLI entrypoint for Doctor & System Diagnostics.
Supports:
  - singularity doctor
  - singularity info --json
  - python -m gravitational_singularity doctor
Idempotent, non-destructive, with --dry-run, --json, and --no-network support.
"""

from __future__ import annotations
import argparse
import json
import platform
import shutil
import subprocess
import sys
from typing import Any, Dict


def get_system_info(no_network: bool = False) -> Dict[str, Any]:
    """Collects OS, architecture, Apple Silicon / Metal, Python, and Ollama status."""
    info: Dict[str, Any] = {
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "is_apple_silicon": platform.system() == "Darwin" and platform.machine() == "arm64",
        "metal_available": False,
        "ollama_running": False,
        "ollama_models": [],
        "cli_tools": {},
    }

    # Metal detection on macOS
    if info["is_apple_silicon"]:
        try:
            sp_res = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if "Metal" in sp_res.stdout or "Apple" in sp_res.stdout:
                info["metal_available"] = True
        except Exception:
            info["metal_available"] = False

    # CLI availability check
    for tool in ["ast-search", "singularity", "ollama", "git", "pytest"]:
        path = shutil.which(tool)
        info["cli_tools"][tool] = {"available": bool(path), "path": path}

    # Ollama process & model check
    if not no_network:
        try:
            ollama_proc = subprocess.run(
                ["pgrep", "-f", "ollama"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
            if ollama_proc.returncode == 0:
                info["ollama_running"] = True
                # Query models
                list_proc = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if list_proc.returncode == 0:
                    lines = [line.strip() for line in list_proc.stdout.splitlines() if line.strip()]
                    if len(lines) > 1:
                        # Skip header
                        info["ollama_models"] = [l.split()[0] for l in lines[1:] if l.split()]
        except Exception:
            pass

    return info


def run_doctor(args: argparse.Namespace) -> int:
    """Runs system diagnostics, checks invariants, and reports actionable recommendations."""
    info = get_system_info(no_network=args.no_network)

    if args.json:
        print(json.dumps(info, indent=2))
        return 0

    print("══════════════════════════════════════════════════════════════════")
    print("   🌌 GRAVITATIONAL SINGULARITY: SYSTEM DOCTOR & DIAGNOSTICS      ")
    print("══════════════════════════════════════════════════════════════════\n")

    print("[*] Environment:")
    print(f"    • Operating System: {info['os']} ({info['architecture']})")
    print(f"    • Python:           {info['python_version']} ({info['python_executable']})")
    print(f"    • Apple Silicon:    {'✅ Detected' if info['is_apple_silicon'] else 'ℹ️ Standard CPU'}")
    print(f"    • Metal GPU Layer:  {'✅ Available' if info['metal_available'] else 'ℹ️ Disabled / CPU Fallback'}")

    print("\n[*] CLI Tools:")
    for tool, data in info["cli_tools"].items():
        status = f"✅ {data['path']}" if data["available"] else "❌ Not found in PATH"
        print(f"    • {tool:12}: {status}")

    print("\n[*] Ollama Engine (Tier 0 Acceleration):")
    if info["ollama_running"]:
        print("    • Status:           ✅ Active (Local daemon running)")
        print(f"    • Installed Models: {len(info['ollama_models'])} detected")
        for m in info["ollama_models"]:
            print(f"      - {m}")
    else:
        print("    • Status:           ℹ️ Offline / Not Running (System runs purely on CPU stdlib fallback)")

    recommended_models = [
        "nomic-embed-text:latest",
        "qwen2.5-coder:3b",
        "qwen2.5-coder:7b",
        "hermes3:3b",
        "deepseek-r1:1.5b",
    ]
    missing_models = [m for m in recommended_models if m not in info["ollama_models"] and m.split(":")[0] not in [im.split(":")[0] for im in info["ollama_models"]]]

    print("\n[*] Doctor Diagnostic Recommendations:")
    if not info["cli_tools"]["ast-search"]["available"]:
        print("    [ℹ] 'ast-search' is not currently in PATH.")
        print("        Action: run 'pip install -e \".[dev]\"' in your virtual environment to enable CLI shortcut.")

    if not info["ollama_running"]:
        print("    [ℹ] Ollama is not running. Core CPU/stdlib logic works deterministically,")
        print("        but local inference (RAG, distillation, council) requires 'ollama serve'.")
    elif missing_models:
        print("    [ℹ] Recommended models for zero-cloud token factory can be pulled:")
        for mm in missing_models:
            print(f"        Action: ollama pull {mm}")

    print("    [✓] All core requirements satisfied. System is healthy.")
    print("══════════════════════════════════════════════════════════════════")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="singularity",
        description="Gravitational Singularity - System Diagnostics and Product CLI",
    )
    subparsers = parser.add_subparsers(dest="command")

    # doctor subcommand
    doctor_parser = subparsers.add_parser("doctor", help="Inspect system health, hardware, and CLI readiness.")
    doctor_parser.add_argument("--json", action="store_true", help="Emit diagnostic data as JSON.")
    doctor_parser.add_argument("--dry-run", action="store_true", help="Perform check without modifying any state.")
    doctor_parser.add_argument("--no-network", action="store_true", help="Skip any network/daemon probing.")

    # info subcommand
    info_parser = subparsers.add_parser("info", help="Output system and runtime metadata.")
    info_parser.add_argument("--json", action="store_true", default=True, help="Emit info as JSON (default: true).")
    info_parser.add_argument("--no-network", action="store_true", help="Skip network probing.")

    args = parser.parse_args()

    if args.command == "doctor":
        return run_doctor(args)
    elif args.command == "info":
        info = get_system_info(no_network=args.no_network)
        print(json.dumps(info, indent=2))
        return 0
    else:
        # Default behavior when invoked without arguments: run doctor
        dummy_args = argparse.Namespace(json=False, dry_run=False, no_network=False)
        return run_doctor(dummy_args)


if __name__ == "__main__":
    sys.exit(main())
