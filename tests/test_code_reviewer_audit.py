"""Automated Code Reviewer Static Analysis & Clean Code Enforcement.

Validates the entire codebase against strict Clean Code rules using Python AST:
- No silent error swallowing (empty except: pass)
- No bare except clauses
- No boolean traps (excessive boolean positional parameters)
- No dangerous dynamic code execution (eval, exec)
- Strict type hint coverage on public methods
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Tuple
import pytest

SRC_DIR = Path("src")
SCHEMAS_DIR = Path("schemas")


def get_python_files() -> List[Path]:
    """Collects all production Python source files."""
    files = list(SRC_DIR.rglob("*.py")) + list(SCHEMAS_DIR.rglob("*.py"))
    return [f for f in files if "__pycache__" not in f.parts]


def test_no_bare_except_clauses():
    """Rule: Never use bare 'except:' clauses - must catch specific exceptions."""
    violations: List[Tuple[str, int]] = []
    for file_path in get_python_files():
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    violations.append((str(file_path), node.lineno))

    assert not violations, f"Bare except: clauses detected at: {violations}"


def test_no_silent_error_swallowing():
    """Rule: No silent error swallowing (except block with only 'pass' and no logging/comment)."""
    violations: List[Tuple[str, int]] = []
    for file_path in get_python_files():
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Check if body consists solely of `pass`
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    # Exception allowed ONLY if caught exception is expected control flow with explicit comment
                    violations.append((str(file_path), node.lineno))

    # Expect 0 unhandled silent swallows
    assert not violations, f"Silent error swallowing (except: pass) detected at: {violations}"


def test_no_boolean_traps():
    """Rule: Functions should not have 3 or more boolean parameters (Boolean Trap)."""
    violations: List[Tuple[str, str, int]] = []
    for file_path in get_python_files():
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                bool_count = 0
                for default in node.args.defaults + [d for d in node.args.kw_defaults if d]:
                    if isinstance(default, ast.Constant) and isinstance(default.value, bool):
                        bool_count += 1
                if bool_count >= 3:
                    violations.append((str(file_path), node.name, node.lineno))

    assert not violations, f"Boolean traps detected (>=3 boolean defaults): {violations}"


def test_no_dangerous_builtins_eval_exec():
    """Rule: Strict prohibition of eval() and exec() in production codebase."""
    violations: List[Tuple[str, str, int]] = []
    for file_path in get_python_files():
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec"):
                    violations.append((str(file_path), node.func.id, node.lineno))

    assert not violations, f"Dangerous dynamic execution detected: {violations}"


def test_type_annotations_coverage():
    """Rule: All top-level and class methods should define return type annotations."""
    untyped_funcs: List[Tuple[str, str, int]] = []
    for file_path in get_python_files():
        if file_path.name == "__init__.py":
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Ignore magic methods like __str__, __repr__, __eq__ if desired, but check regular functions
                if node.name.startswith("__") and node.name.endswith("__"):
                    continue
                if node.returns is None:
                    untyped_funcs.append((str(file_path), node.name, node.lineno))

    assert not untyped_funcs, f"Functions missing return type annotations: {untyped_funcs}"
