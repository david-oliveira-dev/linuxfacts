"""Memory fact (RF-002).

Reports virtual memory and swap. Pressure is measured by *available* memory, not *free*:
the Linux kernel lends idle RAM to caches it reclaims on demand, so ``available`` is the
honest figure (see :class:`~linuxfacts.models.MemoryInfo`).
"""

from __future__ import annotations

from linuxfacts.facts._common import read_or_unknown
from linuxfacts.models import Fact, MemoryInfo
from linuxfacts.sources.base import Source
from linuxfacts.sources.real import RealSource

__all__ = ["memory"]


def memory(source: Source | None = None) -> Fact[MemoryInfo]:
    """Read virtual memory and swap.

    Example:
        >>> from linuxfacts.models import MemoryInfo
        >>> from linuxfacts.testing import FakeSource
        >>> fake = FakeSource(memory=MemoryInfo(16, 8, 8, 50.0, 0, 0, 0.0))
        >>> memory(fake).unwrap().percent_used
        50.0
    """
    return read_or_unknown("memory", (source or RealSource()).read_memory)
