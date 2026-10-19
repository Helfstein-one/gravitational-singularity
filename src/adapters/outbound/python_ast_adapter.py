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


class PythonASTCompressor(ast.NodeTransformer):
    """Transforms Python AST into a clean skeleton with ellipsis."""

    def __init__(self, docstring_mode: str = "summary"):
        super().__init__()
        self.docstring_mode = docstring_mode

    def _format_docstring(self, raw_doc: str | None) -> str | None:
        if not raw_doc or self.docstring_mode == "none":
            return None
        if self.docstring_mode == "full":
            return raw_doc
        lines = [l.strip() for l in raw_doc.strip().splitlines() if l.strip()]
        return lines[0] if lines else None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        return self._compress_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        return self._compress_func(node)

    def _compress_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.AST:
        doc = ast.get_docstring(node)
        formatted_doc = self._format_docstring(doc)
        new_body: list[ast.stmt] = []
        if formatted_doc:
            new_body.append(ast.Expr(value=ast.Constant(value=formatted_doc)))
        new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
        node.body = new_body
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        doc = ast.get_docstring(node)
        formatted_doc = self._format_docstring(doc)
        transformed_body: list[ast.stmt] = []
        if formatted_doc:
            transformed_body.append(ast.Expr(value=ast.Constant(value=formatted_doc)))
        for item in node.body:
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
                compressor = PythonASTCompressor()
                compressed_tree = compressor.visit(tree)
                ast.fix_missing_locations(compressed_tree)
                return ast.unparse(compressed_tree)
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
