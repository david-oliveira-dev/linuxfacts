"""Disk usage fact (RF-001).

Reports usage for every real mounted filesystem. Pseudo filesystems (snap squashfs
mounts, tmpfs, ...) are excluded by the source, so a read-only 100%-full snap mount never
shows up as a full disk.
"""

from __future__ import annotations

from linuxfacts.facts._common import read_or_unknown
from linuxfacts.models import DiskUsage, Fact
from linuxfacts.sources.base import Source
from linuxfacts.sources.real import RealSource

__all__ = ["disks"]


def disks(source: Source | None = None) -> Fact[list[DiskUsage]]:
    """Read usage for every mounted real filesystem.

    Returns an ``ok`` fact with one :class:`~linuxfacts.models.DiskUsage` per mount, or an
    ``unknown`` fact if the reading fails.

    Example:
        >>> from linuxfacts.models import DiskUsage
        >>> from linuxfacts.testing import FakeSource
        >>> fake = FakeSource(disks=[DiskUsage("/", 100, 40, 60, 40.0)])
        >>> disks(fake).unwrap()[0].mountpoint
        '/'
    """
    return read_or_unknown("disks", (source or RealSource()).read_disks)
