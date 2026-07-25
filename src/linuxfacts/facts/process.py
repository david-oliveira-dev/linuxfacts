"""Processes fact (RF-004).

Reports running processes ranked by CPU share, optionally limited to the top ``N``. Each
process is name and PID only — never its command line, which can hold secrets — so the
result leaks nothing sensitive.
"""

from __future__ import annotations

from linuxfacts.exceptions import SourceError
from linuxfacts.models import Fact, ProcessInfo
from linuxfacts.sources.base import Source
from linuxfacts.sources.real import RealSource

__all__ = ["processes"]


def processes(source: Source | None = None, *, top: int | None = None) -> Fact[list[ProcessInfo]]:
    """Read running processes, ranked by CPU share (highest first).

    Args:
        source: the system source; defaults to the real system.
        top: keep only the ``top`` heaviest processes. ``None`` keeps all.

    Raises:
        ValueError: ``top`` is negative — a programmer error, not a system condition
            (RN-002).

    Example:
        >>> from linuxfacts.models import ProcessInfo
        >>> from linuxfacts.testing import FakeSource
        >>> procs = [ProcessInfo(1, "a", 5.0, 1.0), ProcessInfo(2, "b", 90.0, 2.0)]
        >>> processes(FakeSource(processes=procs), top=1).unwrap()[0].name
        'b'
    """
    if top is not None and top < 0:
        raise ValueError("top must be zero or positive")
    try:
        raw = (source or RealSource()).read_processes()
    except (SourceError, OSError) as exc:
        return Fact.unknown(f"could not read processes: {exc}")
    ranked = sorted(raw, key=lambda proc: proc.cpu_percent, reverse=True)
    if top is not None:
        ranked = ranked[:top]
    return Fact.ok(ranked)
