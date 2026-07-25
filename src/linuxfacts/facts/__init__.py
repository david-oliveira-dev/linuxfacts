"""The facts: one function per area of system state.

Every fact takes an optional ``source`` (defaulting to the real system) and returns a
:class:`~linuxfacts.models.Fact`. They are pure with respect to the source — inject a
:class:`~linuxfacts.testing.FakeSource` and they run offline and deterministically.
"""

from __future__ import annotations

from linuxfacts.facts.cpu import cpu
from linuxfacts.facts.disk import disks
from linuxfacts.facts.host import host
from linuxfacts.facts.memory import memory
from linuxfacts.facts.network import listening_ports
from linuxfacts.facts.packages import packages
from linuxfacts.facts.process import processes
from linuxfacts.facts.systemd import systemd_units

__all__ = [
    "cpu",
    "disks",
    "host",
    "listening_ports",
    "memory",
    "packages",
    "processes",
    "systemd_units",
]
