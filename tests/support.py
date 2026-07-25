"""Test-only helpers.

Kept out of ``conftest.py`` so it can be imported directly. Fixtures are real command
output captured on a Debian/Ubuntu machine (reused from ubuntu-doctor), never invented.
"""

from __future__ import annotations

from pathlib import Path

_FIXTURES = Path(__file__).parent / "fixtures"


def fixture_text(name: str) -> str:
    """Read a versioned command-output fixture as text."""
    return (_FIXTURES / name).read_text(encoding="utf-8")
