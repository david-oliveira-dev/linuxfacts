"""Run every docstring example as a test.

The documentation renders these same docstrings (via mkdocstrings), so proving the
examples execute here is proving the docs are not lying. A failing example fails the
suite (RNF-009: every public function has a docstring with a runnable example).
"""

from __future__ import annotations

import doctest
import importlib
import pkgutil
from types import ModuleType

import linuxfacts


def _all_modules() -> list[ModuleType]:
    modules = [linuxfacts]
    for info in pkgutil.walk_packages(linuxfacts.__path__, "linuxfacts."):
        modules.append(importlib.import_module(info.name))
    return modules


def test_all_docstring_examples_execute() -> None:
    for module in _all_modules():
        result = doctest.testmod(module, verbose=False)
        assert result.failed == 0, f"doctest failures in {module.__name__}"
