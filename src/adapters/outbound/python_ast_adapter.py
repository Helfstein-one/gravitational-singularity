"""
Outbound Adapter: Multi-Language AST Parser Adapter.
Implements IAstParser using Python native `ast` module and JS/TS tokenizer.
Zero external dependencies.
"""

from __future__ import annotations
import ast
import json
import re
import subprocess
import time
from typing import Any
from src.ports.outbound.ast_parser_port import IAstParser
from src.domain.value_objects import SyntaxValidationResult
from src.domain.entities import CodeChunk


def format_docstring(raw_doc: str | None, mode: str = "summary") -> str | None:
    """Format docstring according to requested retention mode: summary, full, none."""
    if not raw_doc or mode == "none":
        return None
    if mode == "full":
        return raw_doc
    lines = [l.strip() for l in raw_doc.strip().splitlines() if l.strip()]
    if not lines:
        return None
    first_line = lines[0]
    m = re.match(r"^(.*?\.)(?:\s+|$)", first_line)
    if m and len(m.group(1)) > 5:
        return m.group(1)
    return first_line


class PythonASTCompressor(ast.NodeTransformer):
    """Transforms Python AST into a clean skeleton with ellipsis."""

    def __init__(self, docstring_mode: str = "summary"):
        super().__init__()
        self.docstring_mode = docstring_mode

    def visit_Module(self, node: ast.Module) -> ast.Module:
        raw_doc = ast.get_docstring(node, clean=True)
        summary_doc = format_docstring(raw_doc, self.docstring_mode)

        new_body: list[ast.stmt] = []
        if summary_doc and self.docstring_mode != "none":
            new_body.append(ast.Expr(value=ast.Constant(value=summary_doc)))

        start_idx = 1 if raw_doc else 0
        for stmt in node.body[start_idx:]:
            if isinstance(stmt, (ast.Import, ast.ImportFrom, ast.AnnAssign)):
                new_body.append(stmt)
            elif isinstance(stmt, ast.Assign):
                if any(isinstance(target, ast.Name) and target.id.isupper() for target in stmt.targets):
                    new_body.append(stmt)
                elif any(isinstance(target, ast.Name) and target.id in ("__all__", "__version__") for target in stmt.targets):
                    new_body.append(stmt)
            elif isinstance(stmt, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                transformed = self.visit(stmt)
                if transformed:
                    new_body.append(transformed)

        node.body = new_body
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        return self._compress_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        return self._compress_func(node)

    def _compress_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.AST:
        raw_doc = ast.get_docstring(node, clean=True)
        formatted_doc = format_docstring(raw_doc, self.docstring_mode)
        new_body: list[ast.stmt] = []
        if formatted_doc:
            new_body.append(ast.Expr(value=ast.Constant(value=formatted_doc)))
        new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
        node.body = new_body
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        raw_doc = ast.get_docstring(node, clean=True)
        formatted_doc = format_docstring(raw_doc, self.docstring_mode)
        transformed_body: list[ast.stmt] = []
        if formatted_doc:
            transformed_body.append(ast.Expr(value=ast.Constant(value=formatted_doc)))
        start_idx = 1 if raw_doc else 0
        for item in node.body[start_idx:]:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                res = self.visit(item)
                if res:
                    transformed_body.append(res)
            elif isinstance(item, (ast.AnnAssign, ast.Assign)):
                transformed_body.append(item)
        if not transformed_body:
            transformed_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
        node.body = transformed_body
        return node


class JSTSScanner:
    """Brace-matching syntax extractor and skeletonizer for JS/TS."""

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

    def __init__(self, docstring_mode: str = "summary"):
        self.docstring_mode = docstring_mode

    def compress(self, source: str) -> str:
        tokens = []
        for m in self.TOKEN_REGEX.finditer(source):
            tokens.append((m.lastgroup, m.group(0)))

        out = []
        brace_depth = 0
        skip_until_depth = None
        recent_text: list[str] = []

        def is_function_header(accum: str) -> bool:
            txt = accum.strip()
            if not txt:
                return False
            parts = re.split(r"[;{}]", txt)
            sig = parts[-1].strip()
            if re.search(r"\b(class|interface|enum|namespace)\s+[A-Za-z0-9_$]+", sig):
                return False
            if re.search(r"=>\s*$", sig):
                return True
            if re.search(r"\b(if|for|while|switch|catch)\s*\([^\)]*\)\s*$", sig):
                return False
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

        return "".join(out)


class MultiLanguageAstAdapter(IAstParser):
    """Concrete AST Parser adapter implementing IAstParser."""

    def validate_syntax(self, code: str, language: str) -> SyntaxValidationResult:
        start_t = time.perf_counter()
        lang = language.lower()

        if lang in ["python", "py"]:
            try:
                ast.parse(code)
                elapsed = (time.perf_counter() - start_t) * 1000
                return SyntaxValidationResult(is_valid=True, language="python", execution_time_ms=round(elapsed, 3))
            except SyntaxError as e:
                elapsed = (time.perf_counter() - start_t) * 1000
                line_str = f"'{e.text.strip()}'" if e.text else ""
                err = f"Python SyntaxError on line {e.lineno}: {e.msg} ({line_str})"
                return SyntaxValidationResult(
                    is_valid=False,
                    language="python",
                    error_message=err,
                    error_line=e.lineno,
                    execution_time_ms=round(elapsed, 3)
                )

        if lang in ["json"]:
            try:
                json.loads(code)
                elapsed = (time.perf_counter() - start_t) * 1000
                return SyntaxValidationResult(is_valid=True, language="json", execution_time_ms=round(elapsed, 3))
            except json.JSONDecodeError as e:
                elapsed = (time.perf_counter() - start_t) * 1000
                err = f"JSON SyntaxError on line {e.lineno}, col {e.colno}: {e.msg}"
                return SyntaxValidationResult(
                    is_valid=False,
                    language="json",
                    error_message=err,
                    error_line=e.lineno,
                    execution_time_ms=round(elapsed, 3)
                )

        if lang in ["javascript", "js", "typescript", "ts"]:
            try:
                res = subprocess.run(
                    ["node", "--input-type=module", "--check"],
                    input=code,
                    text=True,
                    capture_output=True,
                    timeout=3
                )
                elapsed = (time.perf_counter() - start_t) * 1000
                if res.returncode == 0:
                    return SyntaxValidationResult(is_valid=True, language=lang, execution_time_ms=round(elapsed, 3))
                err_line = res.stderr.splitlines()[-1] if res.stderr else "Syntax error"
                return SyntaxValidationResult(
                    is_valid=False,
                    language=lang,
                    error_message=f"JavaScript SyntaxError: {err_line}",
                    execution_time_ms=round(elapsed, 3)
                )
            except Exception:
                pass

        elapsed = (time.perf_counter() - start_t) * 1000
        return SyntaxValidationResult(is_valid=True, language=lang, execution_time_ms=round(elapsed, 3))

    def skeletonize(self, code: str, language: str) -> str:
        lang = language.lower()
        if lang in ["python", "py"]:
            try:
                tree = ast.parse(code)
                compressor = PythonASTCompressor(docstring_mode="summary")
                compressed_tree = compressor.visit(tree)
                ast.fix_missing_locations(compressed_tree)
                return ast.unparse(compressed_tree)
            except Exception:
                return code
        elif lang in ["typescript", "ts", "javascript", "js", "tsx", "jsx"]:
            try:
                scanner = JSTSScanner(docstring_mode="summary")
                return scanner.compress(code)
            except Exception:
                return code
        return code

    def extract_chunks(self, file_path: str, code: str) -> list[CodeChunk]:
        chunks: list[CodeChunk] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    start = getattr(node, "lineno", 1)
                    end = getattr(node, "end_lineno", start)
                    node_type = "class" if isinstance(node, ast.ClassDef) else "function"
                    node_code = ast.unparse(node)
                    chunks.append(CodeChunk(
                        file_path=file_path,
                        start_line=start,
                        end_line=end,
                        node_type=node_type,
                        name=node.name,
                        code=node_code
                    ))
        except Exception:
            pass
        return chunks
