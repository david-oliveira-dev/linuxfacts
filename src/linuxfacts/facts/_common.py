"""Shared helper for structured facts.

A fact never raises for an expected failure (a source that cannot read, a missing mount):
it returns an ``unknown`` :class:`~linuxfacts.models.Fact` with a reason (RN-001). This
helper wraps a source reading in exactly that contract, so each structured fact stays a
one-liner.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from linuxfacts.exceptions import SourceError
from linuxfacts.models import Fact

_T = TypeVar("_T")


def read_or_unknown(area: str, read: Callable[[], _T]) -> Fact[_T]:
    """Return ``Fact.ok(read())``, or ``Fact.unknown`` if the reading fails expectedly."""
    try:
        return Fact.ok(read())
    except (SourceError, OSError) as exc:
        return Fact.unknown(f"could not read {area}: {exc}")
