"""CPU fact (RF-003).

Reports the 1/5/15-minute load averages and the core count. The core count is ``None``
when it cannot be determined; the caller decides what to make of load relative to cores —
the library reports the numbers, not a judgement.
"""

from __future__ import annotations

from linuxfacts.facts._common import read_or_unknown
from linuxfacts.models import CpuInfo, Fact
from linuxfacts.sources.base import Source
from linuxfacts.sources.real import RealSource

__all__ = ["cpu"]


def cpu(source: Source | None = None) -> Fact[CpuInfo]:
    """Read load averages and core count.

    Example:
        >>> from linuxfacts.models import CpuInfo
        >>> from linuxfacts.testing import FakeSource
        >>> cpu(FakeSource(cpu=CpuInfo(0.5, 0.6, 0.7, 8))).unwrap().core_count
        8
    """
    return read_or_unknown("cpu", (source or RealSource()).read_cpu)
