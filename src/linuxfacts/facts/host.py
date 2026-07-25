"""Host info fact (RF-008).

Reports host identity and uptime: hostname, kernel release, distribution and uptime in
seconds. The distribution comes from ``/etc/os-release``; when it is unreadable the
distribution reads ``unknown`` but the rest of the host info is still returned.
"""

from __future__ import annotations

from linuxfacts.facts._common import read_or_unknown
from linuxfacts.models import Fact, HostInfo
from linuxfacts.sources.base import Source
from linuxfacts.sources.real import RealSource

__all__ = ["host"]


def host(source: Source | None = None) -> Fact[HostInfo]:
    """Read host identity and uptime.

    Example:
        >>> from linuxfacts.models import HostInfo
        >>> from linuxfacts.testing import FakeSource
        >>> fake = FakeSource(host=HostInfo("box", "6.8.0", "Ubuntu 24.04", 3600.0))
        >>> host(fake).unwrap().hostname
        'box'
    """
    return read_or_unknown("host", (source or RealSource()).read_host)
