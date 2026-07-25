"""The facts: one function per area of system state.

Every fact takes an optional ``source`` (defaulting to the real system) and returns a
:class:`~linuxfacts.models.Fact`. They are pure with respect to the source — inject a
:class:`~linuxfacts.testing.FakeSource` and they run offline and deterministically.
"""

from __future__ import annotations

from linuxfacts.facts.disk import disks

__all__ = ["disks"]
