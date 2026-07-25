"""The facts: one function per area of system state.

Every fact takes an optional ``source`` (defaulting to the real system) and returns a
:class:`~linuxfacts.models.Fact`. They are pure with respect to the source — inject a
:class:`~linuxfacts.testing.FakeSource` and they run offline and deterministically.
"""

from __future__ import annotations

from linuxfacts.facts.cpu import cpu
from linuxfacts.facts.disk import disks
from linuxfacts.facts.memory import memory
from linuxfacts.facts.process import processes

__all__ = ["cpu", "disks", "memory", "processes"]
