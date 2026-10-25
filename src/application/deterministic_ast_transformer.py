"""
Application Use Case: Deterministic AST Transformer (System 0 - Zero LLM Bypass).
Applies purely mechanical code edits (symbol rename, docstring update, import cleanup)
directly in RAM via Python standard library ast.NodeTransformer in <2ms with zero tokens.
"""

from __future__ import annotations
import ast
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class TransformationResult:
    is_transformed: bool
    modified_code: str
    symbols_changed: int
    execution_time_ms: float
    error_message: Optional[str] = None


class _SymbolRenameTransformer(ast.NodeTransformer):
    def __init__(self, old_name: str, new_name: str) -> None:
        self.old_name = old_name
        self.new_name = new_name
        self.count = 0

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == self.old_name:
            self.count += 1
            return ast.copy_location(ast.Name(id=self.new_name, ctx=node.ctx), node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        if node.name == self.old_name:
            self.count += 1
            node.name = self.new_name
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        if node.name == self.old_name:
            self.count += 1
            node.name = self.new_name
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        if node.name == self.old_name:
            self.count += 1
            node.name = self.new_name
        self.generic_visit(node)
        return node


class DeterministicAstTransformer:
    """Deterministic in-memory AST code transformations (System 0)."""

    @classmethod
    def rename_symbol(cls, source_code: str, old_symbol: str, new_symbol: str) -> TransformationResult:
        """Renames identifiers across variables, functions, and classes in RAM."""
        import time
        start_ns = time.perf_counter_ns()
        try:
            tree = ast.parse(source_code)
            transformer = _SymbolRenameTransformer(old_symbol, new_symbol)
            new_tree = transformer.visit(tree)
            if transformer.count == 0:
                ms = (time.perf_counter_ns() - start_ns) / 1e6
                return TransformationResult(
                    is_transformed=False,
                    modified_code=source_code,
                    symbols_changed=0,
                    execution_time_ms=round(ms, 3),
                )
            ast.fix_missing_locations(new_tree)
            modified = ast.unparse(new_tree)
            ms = (time.perf_counter_ns() - start_ns) / 1e6
            return TransformationResult(
                is_transformed=True,
                modified_code=modified,
                symbols_changed=transformer.count,
                execution_time_ms=round(ms, 3),
            )
        except Exception as e:
            ms = (time.perf_counter_ns() - start_ns) / 1e6
            return TransformationResult(
                is_transformed=False,
                modified_code=source_code,
                symbols_changed=0,
                execution_time_ms=round(ms, 3),
                error_message=str(e),
            )

    @classmethod
    def update_docstring(cls, source_code: str, function_name: str, new_docstring: str) -> TransformationResult:
        """Updates or injects a docstring on a target function in RAM."""
        import time
        start_ns = time.perf_counter_ns()
        try:
            tree = ast.parse(source_code)
            changed = False
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node.name == function_name:
                        doc_node = ast.Expr(value=ast.Constant(value=new_docstring))
                        if (
                            node.body
                            and isinstance(node.body[0], ast.Expr)
                            and isinstance(node.body[0].value, ast.Constant)
                            and isinstance(node.body[0].value.value, str)
                        ):
                            node.body[0] = doc_node
                        else:
                            node.body.insert(0, doc_node)
                        changed = True
                        break

            if changed:
                ast.fix_missing_locations(tree)
                modified = ast.unparse(tree)
                ms = (time.perf_counter_ns() - start_ns) / 1e6
                return TransformationResult(
                    is_transformed=True,
                    modified_code=modified,
                    symbols_changed=1,
                    execution_time_ms=round(ms, 3),
                )
            ms = (time.perf_counter_ns() - start_ns) / 1e6
            return TransformationResult(
                is_transformed=False,
                modified_code=source_code,
                symbols_changed=0,
                execution_time_ms=round(ms, 3),
                error_message=f"Function or class '{function_name}' not found",
            )
        except Exception as e:
            ms = (time.perf_counter_ns() - start_ns) / 1e6
            return TransformationResult(
                is_transformed=False,
                modified_code=source_code,
                symbols_changed=0,
                execution_time_ms=round(ms, 3),
                error_message=str(e),
            )
