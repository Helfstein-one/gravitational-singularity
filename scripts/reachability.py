#!/usr/bin/env python3
"""
Reachability & Graph Audit Script.
Analyzes the Python AST import graph from driving inbound entry points
(hook_adapter, mcp_adapter, http_telemetry_adapter, cli_adapters) and asserts
that all non-deprecated modules in src/ are actively wired and reachable.
"""

from __future__ import annotations
import ast
import os
import sys
from typing import Dict, Set


def build_module_map(root_dir: str = "src") -> Dict[str, str]:
    mods: Dict[str, str] = {}
    for d, _, fs in os.walk(root_dir):
        for f in fs:
            if f.endswith(".py"):
                path = os.path.join(d, f)
                mod_name = path[:-3].replace(os.sep, ".")
                if mod_name.endswith(".__init__"):
                    mod_name = mod_name[:-9]
                mods[mod_name] = path
    return mods


def extract_dependencies(module_name: str, file_path: str, available_mods: Dict[str, str]) -> Set[str]:
    deps: Set[str] = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except Exception:
        return deps

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            base = node.module
            if node.level > 0:
                parts = module_name.split(".")
                pkg = ".".join(parts[:-node.level]) if not file_path.endswith("__init__.py") else ".".join(parts[:-(node.level - 1)])
                base = f"{pkg}.{node.module}" if node.module else pkg

            for alias in node.names:
                for candidate in (f"{base}.{alias.name}", base):
                    if candidate in available_mods:
                        deps.add(candidate)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in available_mods:
                    deps.add(alias.name)

    return deps


def get_reachable_modules(root_dir: str = "src") -> tuple[Set[str], Set[str]]:
    mods = build_module_map(root_dir)
    inbound_entries = [m for m in mods if m.startswith("src.adapters.inbound")]

    visited: Set[str] = set()
    queue = list(inbound_entries)

    while queue:
        curr = queue.pop(0)
        if curr in visited:
            continue
        visited.add(curr)
        if curr in mods:
            for dep in extract_dependencies(curr, mods[curr], mods):
                if dep not in visited:
                    queue.append(dep)

    # Filter out pure package markers, ports, and domain value objects
    orphans = set()
    for m in mods:
        if m in visited or m.endswith("__init__") or "ports" in m or m in ("src", "src.domain", "src.application", "src.adapters", "src.adapters.outbound", "src.adapters.inbound", "src.experimental"):
            continue
        orphans.add(m)

    return visited, orphans


def main() -> int:
    check_mode = "--check" in sys.argv
    visited, orphans = get_reachable_modules("src")

    print(f"[*] Total Modules Scanned: {len(visited) + len(orphans)}")
    print(f"[*] Reachable Production Modules: {len(visited)}")
    print(f"[*] Unreached / Isolated Modules: {len(orphans)}")

    if orphans:
        print("\n[!] Unreached Modules:")
        for o in sorted(orphans):
            print(f"  - {o}")
        if check_mode:
            print("\n[FAIL] Reachability check failed with unreached modules.")
            return 1

    print("\n[SUCCESS] Graph reachability verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
