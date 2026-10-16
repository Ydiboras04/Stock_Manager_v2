"""The core must only depend on the Python standard library and itself."""

import ast
import sys
from pathlib import Path

import stock.core

CORE_DIR = Path(stock.core.__file__).parent


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_core_only_imports_stdlib_or_core():
    for path in CORE_DIR.rglob("*.py"):
        for module in imported_modules(path):
            top = module.split(".")[0]
            allowed = top in sys.stdlib_module_names or module.startswith("stock.core")
            assert allowed, f"{path.name} imports '{module}'"
