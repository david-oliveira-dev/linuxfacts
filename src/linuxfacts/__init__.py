"""LinuxFacts — typed, read-only access to Linux system state.

The public API is exactly the names exported here via ``__all__``; everything else is
private and may change without a major version bump (RN-005). The eight facts, the
:class:`Fact` envelope and its state, the domain models and the base error make up the
surface. The testing double is imported separately, from :mod:`linuxfacts.testing`, so a
production dependency never pulls it in by accident.

    >>> import linuxfacts
    >>> from linuxfacts.testing import FakeSource
    >>> fake = FakeSource(memory=linuxfacts.MemoryInfo(16, 8, 8, 50.0, 0, 0, 0.0))
    >>> linuxfacts.memory(fake).unwrap().percent_used
    50.0
"""

from __future__ import annotations

from linuxfacts.exceptions import LinuxFactsError
from linuxfacts.facts import (
    cpu,
    disks,
    host,
    listening_ports,
    memory,
    packages,
    processes,
    systemd_units,
)
from linuxfacts.models import (
    CpuInfo,
    DiskUsage,
    Fact,
    FactState,
    HostInfo,
    ListeningPort,
    MemoryInfo,
    PackageStatus,
    ProcessInfo,
    SystemdUnit,
)

__version__ = "0.1.0"

__all__ = [
    "CpuInfo",
    "DiskUsage",
    "Fact",
    "FactState",
    "HostInfo",
    "LinuxFactsError",
    "ListeningPort",
    "MemoryInfo",
    "PackageStatus",
    "ProcessInfo",
    "SystemdUnit",
    "__version__",
    "cpu",
    "disks",
    "host",
    "listening_ports",
    "memory",
    "packages",
    "processes",
    "systemd_units",
]
