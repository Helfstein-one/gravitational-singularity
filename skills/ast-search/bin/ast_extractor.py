#!/usr/bin/env python3
"""
ast_extractor.py — AST Context Compressor and Symbol Search Engine
Zero runtime external dependencies (Python stdlib only: ast, re, json, argparse, sys, pathlib, os).
Supports Python (.py) via native ast and JavaScript/TypeScript (.js, .jsx, .ts, .tsx) via syntax scanner.
"""

import argparse
import ast
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Tuple, Union


# ---------------------------------------------------------------------------
# Metric / Token Estimation Utilities
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """Heuristic token counter matching word and non-whitespace symbol boundaries."""
    return len(re.findall(r"\w+|[^\w\s]", text))


def count_non_empty_lines(text: str) -> int:
    """Count lines containing non-whitespace content."""
    return len([l for l in text.splitlines() if l.strip()])


def calculate_stats(original: str, compressed: str) -> Dict[str, Any]:
    """Compute exact character, line, and token reduction metrics."""
    orig_chars = len(original)
    comp_chars = len(compressed)
    orig_lines = count_non_empty_lines(original)
    comp_lines = count_non_empty_lines(compressed)
    orig_tokens = estimate_tokens(original)
    comp_tokens = estimate_tokens(compressed)

    char_red = (1.0 - (comp_chars / orig_chars)) * 100.0 if orig_chars > 0 else 0.0
    line_red = (1.0 - (comp_lines / orig_lines)) * 100.0 if orig_lines > 0 else 0.0
    token_red = (1.0 - (comp_tokens / orig_tokens)) * 100.0 if orig_tokens > 0 else 0.0

    return {
        "original_chars": orig_chars,
        "compressed_chars": comp_chars,
        "char_reduction_pct": round(char_red, 2),
        "original_lines": orig_lines,
        "compressed_lines": comp_lines,
        "line_reduction_pct": round(line_red, 2),
        "original_tokens": orig_tokens,
        "compressed_tokens": comp_tokens,
        "token_reduction_pct": round(token_red, 2),
        "reduction_pct": round(token_red, 2),
    }


def format_docstring(raw_doc: Optional[str], mode: str) -> Optional[str]:
    """Format docstring according to requested retention mode: summary, full, none."""
    if not raw_doc or mode == "none":
        return None
    if mode == "full":
        return raw_doc
    # summary mode: extract first sentence or first non-empty line
    lines = [l.strip() for l in raw_doc.strip().splitlines() if l.strip()]
    if not lines:
        return None
    first_line = lines[0]
    # If the first line doesn't end with a period, but has a sentence boundary inside, truncate at first period
    m = re.match(r"^(.*?\.)(?:\s+|$)", first_line)
    if m and len(m.group(1)) > 5:
        return m.group(1)
    return first_line


# ---------------------------------------------------------------------------
# Python AST Extraction Engine
# ---------------------------------------------------------------------------

class PythonASTCompressor(ast.NodeTransformer):
    """
    Transforms Python AST into a clean skeleton:
    - Retains imports, classes, functions, decorators, type hints, and docstrings.
    - Replaces method/function bodies with ellipsis `...`.
    - Filters top-level procedural statements while preserving annotations/constants.
    - Optionally filters by query substring/regex.
    """

    def __init__(self, docstring_mode: str = "summary", query: Optional[str] = None):
        super().__init__()
        self.docstring_mode = docstring_mode
        self.query = query
        self.query_re = re.compile(query, re.IGNORECASE) if query else None

    def _matches_query(self, name: str) -> bool:
        if not self.query_re:
            return True
        return bool(self.query_re.search(name))

    def visit_Module(self, node: ast.Module) -> ast.Module:
        # Handle module-level docstring
        raw_doc = ast.get_docstring(node, clean=True)
        summary_doc = format_docstring(raw_doc, self.docstring_mode)

        new_body: List[ast.stmt] = []
        if summary_doc and self.docstring_mode != "none":
            new_body.append(ast.Expr(value=ast.Constant(value=summary_doc)))

        # Process statements
        start_idx = 1 if raw_doc else 0
        for stmt in node.body[start_idx:]:
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                new_body.append(stmt)
            elif isinstance(stmt, ast.AnnAssign):
                new_body.append(stmt)
            elif isinstance(stmt, ast.Assign):
                # Keep top-level constants / type assignments, drop complex procedural calls
                if any(isinstance(target, ast.Name) and target.id.isupper() for target in stmt.targets):
                    new_body.append(stmt)
                elif any(isinstance(target, ast.Name) and target.id in ("__all__", "__version__") for target in stmt.targets):
                    new_body.append(stmt)
            elif isinstance(stmt, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                transformed = self.visit(stmt)
                if transformed:
                    if isinstance(transformed, list):
                        new_body.extend(transformed)
                    else:
                        new_body.append(transformed)

        node.body = new_body
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> Optional[ast.ClassDef]:
        class_matches = self._matches_query(node.name)

        # Handle class docstring
        raw_doc = ast.get_docstring(node, clean=True)
        summary_doc = format_docstring(raw_doc, self.docstring_mode)

        new_body: List[ast.stmt] = []
        if summary_doc and self.docstring_mode != "none":
            new_body.append(ast.Expr(value=ast.Constant(value=summary_doc)))

        # Process class items
        start_idx = 1 if raw_doc else 0
        matching_method_found = False

        for item in node.body[start_idx:]:
            if isinstance(item, ast.AnnAssign):
                new_body.append(item)
            elif isinstance(item, ast.Assign):
                # Retain class attributes
                new_body.append(item)
            elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_matches = self._matches_query(item.name)
                if class_matches or method_matches:
                    transformed_method = self._compress_function(item)
                    new_body.append(transformed_method)
                    matching_method_found = True
            elif isinstance(item, ast.ClassDef):
                transformed_subclass = self.visit(item)
                if transformed_subclass:
                    new_body.append(transformed_subclass)
                    matching_method_found = True

        # Query filter decision
        if self.query and not class_matches and not matching_method_found:
            return None

        if not new_body:
            new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))

        node.body = new_body
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Optional[ast.FunctionDef]:
        if not self._matches_query(node.name):
            return None
        return self._compress_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Optional[ast.AsyncFunctionDef]:
        if not self._matches_query(node.name):
            return None
        return self._compress_function(node)

    def _compress_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> Union[ast.FunctionDef, ast.AsyncFunctionDef]:
        raw_doc = ast.get_docstring(node, clean=True)
        summary_doc = format_docstring(raw_doc, self.docstring_mode)

        new_body: List[ast.stmt] = []
        if summary_doc and self.docstring_mode != "none":
            new_body.append(ast.Expr(value=ast.Constant(value=summary_doc)))

        new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
        node.body = new_body
        return node


def compress_python_code(source: str, docstring_mode: str = "summary", query: Optional[str] = None) -> str:
    """Parse and unparse Python source into valid skeleton code."""
    tree = ast.parse(source)
    compressor = PythonASTCompressor(docstring_mode=docstring_mode, query=query)
    transformed_tree = compressor.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    return ast.unparse(transformed_tree)


def extract_python_symbols(source: str, filepath: str, docstring_mode: str = "summary", query: Optional[str] = None) -> Dict[str, Any]:
    """Extract structured symbol dictionary from Python source."""
    tree = ast.parse(source)
    query_re = re.compile(query, re.IGNORECASE) if query else None

    classes_list = []
    functions_list = []

    def matches(name: str) -> bool:
        return bool(query_re.search(name)) if query_re else True

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_matches = matches(node.name)
            methods_list = []

            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if class_matches or matches(item.name):
                        methods_list.append({
                            "name": item.name,
                            "async": isinstance(item, ast.AsyncFunctionDef),
                            "decorators": [ast.unparse(d) for d in item.decorator_list],
                            "params": [ast.unparse(a) for a in item.args.args],
                            "returns": ast.unparse(item.returns) if item.returns else None,
                            "docstring": format_docstring(ast.get_docstring(item, clean=True), docstring_mode),
                            "line": item.lineno,
                        })

            if class_matches or methods_list:
                fields = []
                for item in node.body:
                    if isinstance(item, ast.AnnAssign):
                        fields.append(ast.unparse(item))

                classes_list.append({
                    "name": node.name,
                    "bases": [ast.unparse(b) for b in node.bases],
                    "decorators": [ast.unparse(d) for d in node.decorator_list],
                    "docstring": format_docstring(ast.get_docstring(node, clean=True), docstring_mode),
                    "fields": fields,
                    "methods": methods_list,
                    "line": node.lineno,
                })

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if matches(node.name):
                functions_list.append({
                    "name": node.name,
                    "async": isinstance(node, ast.AsyncFunctionDef),
                    "decorators": [ast.unparse(d) for d in node.decorator_list],
                    "params": [ast.unparse(a) for a in node.args.args],
                    "returns": ast.unparse(node.returns) if node.returns else None,
                    "docstring": format_docstring(ast.get_docstring(node, clean=True), docstring_mode),
                    "line": node.lineno,
                })

    compressed = compress_python_code(source, docstring_mode=docstring_mode, query=query)
    stats = calculate_stats(source, compressed)

    return {
        "path": filepath,
        "language": "python",
        "stats": stats,
        "classes": classes_list,
        "functions": functions_list,
    }


def build_python_tree(symbols: Dict[str, Any]) -> str:
    """Build ASCII tree representation for Python symbols."""
    lines = [f"File: {symbols['path']} ({symbols['language']})"]
    items = []
    for cls in symbols.get("classes", []):
        bases_str = f"({', '.join(cls['bases'])})" if cls.get("bases") else ""
        cls_node = [f"class {cls['name']}{bases_str}"]
        for m in cls.get("methods", []):
            async_pfx = "async " if m.get("async") else ""
            ret_sfx = f" -> {m['returns']}" if m.get("returns") else ""
            params_str = ", ".join(m.get("params", []))
            cls_node.append(f"def {async_pfx}{m['name']}({params_str}){ret_sfx}")
        items.append(cls_node)

    for fn in symbols.get("functions", []):
        async_pfx = "async " if fn.get("async") else ""
        ret_sfx = f" -> {fn['returns']}" if fn.get("returns") else ""
        params_str = ", ".join(fn.get("params", []))
        items.append([f"def {async_pfx}{fn['name']}({params_str}){ret_sfx}"])

    for i, item in enumerate(items):
        is_last_item = (i == len(items) - 1)
        prefix = "└── " if is_last_item else "├── "
        child_indent = "    " if is_last_item else "│   "

        lines.append(f"{prefix}{item[0]}")
        for j, child in enumerate(item[1:]):
            is_last_child = (j == len(item[1:]) - 1)
            child_prefix = "└── " if is_last_child else "├── "
            lines.append(f"{child_indent}{child_prefix}{child}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# JavaScript & TypeScript AST Scanner Engine
# ---------------------------------------------------------------------------

class JSTSScanner:
    """
    Self-contained zero-dependency lexer & brace-matching syntax extractor for JS/TS.
    Preserves:
    - import statements
    - export interface ... { ... }
    - export type ... = ...
    - export enum ... { ... }
    - export class ... with fields and method signatures
    - function declarations and arrow functions
    - docstrings / JSDocs (summary/full/none)
    Replaces executable function bodies with `{ /* ... */ }`.
    """

    TOKEN_REGEX = re.compile(
        r"(?P<BLOCK_COMMENT>/\*[\s\S]*?\*/)"
        r"|(?P<LINE_COMMENT>//[^\n]*)"
        r"|(?P<TEMPLATE>`(?:\\.|[^`\\])*`)"
        r"|(?P<STRING_DQ>\"(?:\\.|[^\"\\])*\")"
        r"|(?P<STRING_SQ>'(?:\\.|[^'\\])*')"
        r"|(?P<LBRACE>\{)"
        r"|(?P<RBRACE>\})"
        r"|(?P<OTHER>[^{}`\"'/]+|/(?![/*]))"
    )

    def __init__(self, docstring_mode: str = "summary", query: Optional[str] = None):
        self.docstring_mode = docstring_mode
        self.query = query
        self.query_re = re.compile(query, re.IGNORECASE) if query else None

    def _matches_query(self, text: str) -> bool:
        if not self.query_re:
            return True
        return bool(self.query_re.search(text))

    def compress(self, source: str) -> str:
        tokens = []
        for m in self.TOKEN_REGEX.finditer(source):
            tokens.append((m.lastgroup, m.group(0)))

        out = []
        brace_depth = 0
        skip_until_depth = None
        recent_text: List[str] = []

        def is_function_header(accum: str) -> bool:
            txt = accum.strip()
            if not txt:
                return False

            parts = re.split(r"[;{}]", txt)
            sig = parts[-1].strip()

            # Exclude class, interface, enum, namespace declaration level
            if re.search(r"\b(class|interface|enum|namespace)\s+[A-Za-z0-9_$]+", sig):
                return False

            # Arrow function: ends with '=>'
            if re.search(r"=>\s*$", sig):
                return True

            # Control flow statements should not be treated as class methods, but if inside, they will be skipped
            if re.search(r"\b(if|for|while|switch|catch)\s*\([^\)]*\)\s*$", sig):
                return False

            # Method or function declaration: identifier/keywords followed by (...) and optional return type
            if re.search(r"\)\s*(:\s*[\w<>[\]|&,.\s*?]+)?\s*$", sig):
                if re.search(r"(\bfunction\b|\bconstructor\b|\b(async|get|set|public|private|protected|static|readonly)\b|[A-Za-z0-9_$]+)\s*(<[^>]+>)?\s*\([^\)]*\)", sig):
                    return True

            return False

        for kind, val in tokens:
            if skip_until_depth is not None:
                if kind == "LBRACE":
                    brace_depth += 1
                elif kind == "RBRACE":
                    brace_depth -= 1
                    if brace_depth == skip_until_depth:
                        out.append(" { /* ... */ }")
                        skip_until_depth = None
                        recent_text = []
                continue

            if kind == "BLOCK_COMMENT":
                if self.docstring_mode == "none":
                    continue
                if val.startswith("/**") and self.docstring_mode == "summary":
                    lines = [l.strip().lstrip("/*").rstrip("*/").strip() for l in val.splitlines()]
                    lines = [l for l in lines if l]
                    if lines:
                        out.append(f"/** {lines[0]} */")
                    else:
                        out.append("/** ... */")
                else:
                    out.append(val)
                continue

            if kind == "LINE_COMMENT":
                if self.docstring_mode == "none":
                    continue
                out.append(val)
                continue

            if kind == "LBRACE":
                brace_depth += 1
                accum = "".join(recent_text)
                if is_function_header(accum):
                    skip_until_depth = brace_depth - 1
                    continue
                out.append(val)
                recent_text = []
            elif kind == "RBRACE":
                brace_depth -= 1
                out.append(val)
                recent_text = []
            else:
                out.append(val)
                recent_text.append(val)
                if len(recent_text) > 40:
                    recent_text = recent_text[-40:]

        result = "".join(out)

        # Apply query filtering if query was specified
        if self.query:
            result = self._filter_by_query(result)

        return result

    def _filter_by_query(self, code: str) -> str:
        """Filter TS/JS code blocks to retain only symbols matching query."""
        lines = code.splitlines()
        filtered_lines = []
        in_matching_block = False
        block_brace_depth = 0

        for line in lines:
            stripped = line.strip()
            # Always keep imports
            if stripped.startswith("import ") or stripped.startswith("import{"):
                filtered_lines.append(line)
                continue

            # Check if block declaration
            if re.search(r"\b(class|interface|enum|type|function)\s+([A-Za-z0-9_$]+)", stripped):
                sym_match = re.search(r"\b(class|interface|enum|type|function)\s+([A-Za-z0-9_$]+)", stripped)
                sym_name = sym_match.group(2) if sym_match else ""
                if self._matches_query(sym_name):
                    in_matching_block = True
                    block_brace_depth = line.count("{") - line.count("}")
                    filtered_lines.append(line)
                    if block_brace_depth <= 0 and "{" in line:
                        in_matching_block = False
                    continue

            if in_matching_block:
                filtered_lines.append(line)
                block_brace_depth += line.count("{") - line.count("}")
                if block_brace_depth <= 0:
                    in_matching_block = False
                continue

            # Check standalone method or arrow function
            if self._matches_query(stripped):
                filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def extract_symbols(self, source: str, filepath: str) -> Dict[str, Any]:
        """Extract structured symbol dictionary from JS/TS source."""
        classes = []
        interfaces = []
        types = []
        functions = []

        compressed = self.compress(source)
        stats = calculate_stats(source, compressed)

        # Regex symbol mining on compressed code
        # 1. Interfaces
        for m in re.finditer(r"(?:export\s+)?interface\s+([A-Za-z0-9_$]+)(?:<[^>]+>)?(?:\s+extends\s+[^{]+)?\s*\{([\s\S]*?)\}", compressed):
            name = m.group(1)
            body = m.group(2)
            fields = [line.strip() for line in body.splitlines() if line.strip() and not line.strip().startswith("//") and not line.strip().startswith("/*")]
            if not self.query or self._matches_query(name):
                interfaces.append({"name": name, "fields": fields})

        # 2. Types
        for m in re.finditer(r"(?:export\s+)?type\s+([A-Za-z0-9_$]+)(?:<[^>]+>)?\s*=\s*([^;]+);", compressed):
            name = m.group(1)
            val = m.group(2).strip()
            if not self.query or self._matches_query(name):
                types.append({"name": name, "definition": val})

        # 3. Classes
        for m in re.finditer(r"(?:export\s+)?class\s+([A-Za-z0-9_$]+)(?:<[^>]+>)?(?:\s+extends\s+([A-Za-z0-9_$]+))?(?:\s+implements\s+([^{]+))?\s*\{([\s\S]*?)\n\}", compressed):
            cls_name = m.group(1)
            extends_cls = m.group(2)
            implements_ifaces = [s.strip() for s in m.group(3).split(",")] if m.group(3) else []
            body = m.group(4)

            methods = []
            fields = []

            for line in body.splitlines():
                sline = line.strip()
                if not sline or sline.startswith("//") or sline.startswith("/*") or sline.startswith("*"):
                    continue
                # Method match
                mm = re.search(r"((?:public|private|protected|static|async|get|set|readonly)\s+)*([A-Za-z0-9_$]+)\s*(<[^>]+>)?\s*\((.*?)\)(?:\s*:\s*([^;{]+))?", sline)
                if mm and "{" in sline:
                    m_name = mm.group(2)
                    m_params = mm.group(4).strip()
                    m_ret = mm.group(5).strip() if mm.group(5) else None
                    if not self.query or self._matches_query(cls_name) or self._matches_query(m_name):
                        methods.append({
                            "name": m_name,
                            "params": [p.strip() for p in m_params.split(",") if p.strip()],
                            "returns": m_ret,
                        })
                elif ";" in sline and not sline.startswith("constructor"):
                    fields.append(sline)

            if not self.query or self._matches_query(cls_name) or methods:
                classes.append({
                    "name": cls_name,
                    "extends": extends_cls,
                    "implements": implements_ifaces,
                    "fields": fields,
                    "methods": methods,
                })

        # 4. Standalone functions
        for m in re.finditer(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\((.*?)\)(?:\s*:\s*([^{]+))?\s*\{", compressed):
            fn_name = m.group(1)
            fn_params = m.group(2).strip()
            fn_ret = m.group(3).strip() if m.group(3) else None
            if not self.query or self._matches_query(fn_name):
                functions.append({
                    "name": fn_name,
                    "params": [p.strip() for p in fn_params.split(",") if p.strip()],
                    "returns": fn_ret,
                })

        return {
            "path": filepath,
            "language": "typescript" if filepath.endswith((".ts", ".tsx")) else "javascript",
            "stats": stats,
            "interfaces": interfaces,
            "types": types,
            "classes": classes,
            "functions": functions,
        }


def build_jsts_tree(symbols: Dict[str, Any]) -> str:
    """Build ASCII tree representation for JS/TS symbols."""
    lines = [f"File: {symbols['path']} ({symbols['language']})"]
    items = []

    for iface in symbols.get("interfaces", []):
        items.append([f"interface {iface['name']}"])

    for typ in symbols.get("types", []):
        items.append([f"type {typ['name']}"])

    for cls in symbols.get("classes", []):
        ext = f" extends {cls['extends']}" if cls.get("extends") else ""
        cls_node = [f"class {cls['name']}{ext}"]
        for m in cls.get("methods", []):
            ret_sfx = f": {m['returns']}" if m.get("returns") else ""
            params_str = ", ".join(m.get("params", []))
            cls_node.append(f"{m['name']}({params_str}){ret_sfx}")
        items.append(cls_node)

    for fn in symbols.get("functions", []):
        ret_sfx = f": {fn['returns']}" if fn.get("returns") else ""
        params_str = ", ".join(fn.get("params", []))
        items.append([f"function {fn['name']}({params_str}){ret_sfx}"])

    for i, item in enumerate(items):
        is_last_item = (i == len(items) - 1)
        prefix = "└── " if is_last_item else "├── "
        child_indent = "    " if is_last_item else "│   "

        lines.append(f"{prefix}{item[0]}")
        for j, child in enumerate(item[1:]):
            is_last_child = (j == len(item[1:]) - 1)
            child_prefix = "└── " if is_last_child else "├── "
            lines.append(f"{child_indent}{child_prefix}{child}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Language Detection and File Processing
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
}


def detect_language(path: Path, override_lang: Optional[str] = None) -> Optional[str]:
    """Detect language from override or file extension."""
    if override_lang:
        return override_lang.lower()
    return SUPPORTED_EXTENSIONS.get(path.suffix.lower())


def collect_target_files(paths: List[str], lang_override: Optional[str] = None) -> List[Path]:
    """Collect all valid source files from specified paths or directories."""
    collected = []
    for p_str in paths:
        p = Path(p_str).expanduser().resolve()
        if not p.exists():
            sys.stderr.write(f"Error: Path not found: {p_str}\n")
            continue

        if p.is_file():
            lang = detect_language(p, lang_override)
            if lang or lang_override:
                collected.append(p)
            else:
                sys.stderr.write(f"Warning: Unsupported file type: {p_str}\n")
        elif p.is_dir():
            for root, _, files in os.walk(p):
                for f in files:
                    fp = Path(root) / f
                    if detect_language(fp, lang_override):
                        collected.append(fp)

    return sorted(list(set(collected)))


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ast-search",
        description="AST-based context compressor and symbol search tool for Python and JavaScript/TypeScript.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="One or more file or directory paths to process.",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["code", "json", "tree"],
        default="code",
        help="Output format: code (skeleton), json (structured data), or tree (ASCII hierarchy). Default: code.",
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["outline", "query"],
        default="outline",
        help="Execution mode: outline (full structure) or query (filter symbols). Default: outline.",
    )
    parser.add_argument(
        "-q", "--query",
        type=str,
        default=None,
        help="Filter symbols by substring or regular expression.",
    )
    parser.add_argument(
        "-d", "--docstrings",
        choices=["summary", "full", "none"],
        default="summary",
        help="Docstring retention level: summary (first line), full, or none. Default: summary.",
    )
    parser.add_argument(
        "-l", "--lang",
        choices=["python", "javascript", "typescript"],
        default=None,
        help="Language override (defaults to extension-based auto-detection).",
    )
    parser.add_argument(
        "-s", "--stats",
        action="store_true",
        default=False,
        help="Print compression reduction statistics to stderr.",
    )

    args = parser.parse_args()

    if not args.paths:
        parser.print_help(sys.stderr)
        return 1

    files = collect_target_files(args.paths, args.lang)
    if not files:
        sys.stderr.write("Error: No valid source files found to process.\n")
        return 1

    query = args.query
    if args.mode == "query" and not query:
        sys.stderr.write("Error: --mode query requires --query <string>.\n")
        return 1

    all_symbols = []
    total_orig_chars = 0
    total_comp_chars = 0
    total_orig_lines = 0
    total_comp_lines = 0
    total_orig_tokens = 0
    total_comp_tokens = 0

    had_error = False

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            sys.stderr.write(f"Error reading {file_path}: {e}\n")
            had_error = True
            continue

        lang = detect_language(file_path, args.lang)

        try:
            if lang == "python":
                if args.format == "code":
                    output = compress_python_code(content, docstring_mode=args.docstrings, query=query)
                    if output.strip() or not query:
                        if len(files) > 1:
                            print(f"# --- File: {file_path} ---")
                        print(output)
                    stats = calculate_stats(content, output)
                else:
                    syms = extract_python_symbols(content, str(file_path), docstring_mode=args.docstrings, query=query)
                    all_symbols.append(syms)
                    stats = syms["stats"]
                    if args.format == "tree":
                        print(build_python_tree(syms))

            elif lang in ("javascript", "typescript"):
                scanner = JSTSScanner(docstring_mode=args.docstrings, query=query)
                if args.format == "code":
                    output = scanner.compress(content)
                    if output.strip() or not query:
                        if len(files) > 1:
                            print(f"// --- File: {file_path} ---")
                        print(output)
                    stats = calculate_stats(content, output)
                else:
                    syms = scanner.extract_symbols(content, str(file_path))
                    all_symbols.append(syms)
                    stats = syms["stats"]
                    if args.format == "tree":
                        print(build_jsts_tree(syms))
            else:
                sys.stderr.write(f"Warning: Skipping unknown language for {file_path}\n")
                continue

            total_orig_chars += stats["original_chars"]
            total_comp_chars += stats["compressed_chars"]
            total_orig_lines += stats["original_lines"]
            total_comp_lines += stats["compressed_lines"]
            total_orig_tokens += stats["original_tokens"]
            total_comp_tokens += stats["compressed_tokens"]

        except SyntaxError as se:
            sys.stderr.write(f"SyntaxError in {file_path}:{se.lineno}:{se.offset}: {se.msg}\n")
            had_error = True
        except Exception as e:
            sys.stderr.write(f"Error processing {file_path}: {e}\n")
            had_error = True

    if args.format == "json":
        json_output = {"files": all_symbols}
        print(json.dumps(json_output, indent=2))

    if args.stats:
        char_red = (1.0 - (total_comp_chars / total_orig_chars)) * 100.0 if total_orig_chars > 0 else 0.0
        line_red = (1.0 - (total_comp_lines / total_orig_lines)) * 100.0 if total_orig_lines > 0 else 0.0
        tok_red = (1.0 - (total_comp_tokens / total_orig_tokens)) * 100.0 if total_orig_tokens > 0 else 0.0
        sys.stderr.write(
            f"\n[ast-search compression stats]\n"
            f"Original:   {total_orig_chars} chars | {total_orig_lines} lines | {total_orig_tokens} tokens\n"
            f"Compressed: {total_comp_chars} chars | {total_comp_lines} lines | {total_comp_tokens} tokens\n"
            f"Reduction:  {char_red:.1f}% chars | {line_red:.1f}% lines | {tok_red:.1f}% tokens\n"
        )

    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
