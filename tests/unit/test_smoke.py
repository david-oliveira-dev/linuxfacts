"""Smoke test: the package imports and exposes a version.

Replaced by real coverage as the phases land; it exists so the quality gate has
something to run from the first commit.
"""

from __future__ import annotations

import linuxfacts


def test_version_is_exposed() -> None:
    assert linuxfacts.__version__ == "1.0.0"
