"""Shared pytest configuration.

Every test runs offline and deterministically. System access is exercised through the
public ``FakeSource`` (from phase 3 onward), never against the real machine, and command
parsers are fed versioned fixtures — never live output.
"""

from __future__ import annotations
