"""Public testing utilities.

`FakeSource` is a full, hand-configured :class:`~linuxfacts.sources.base.Source` that
returns canned readings instead of touching the machine. It is exported deliberately as
part of the public API — a library whose readings are injectable is only half useful if
consumers have to write their own double. With this, a consumer tests their own tool
offline and deterministically:

    >>> from linuxfacts.models import MemoryInfo
    >>> from linuxfacts.testing import FakeSource
    >>> source = FakeSource(memory=MemoryInfo(16_000, 8_000, 8_000, 50.0, 0, 0, 0.0))
    >>> source.read_memory().percent_used
    50.0

Any reading can be made to fail by passing an exception instead of a value, which is how
a consumer exercises the ``unknown`` path without a broken machine:

    >>> from linuxfacts.exceptions import CommandNotFoundError
    >>> source = FakeSource(commands={("systemctl",): CommandNotFoundError("no systemctl")})

A reading that is never configured raises only if it is actually called, so a test needs
to set up just the facts its code under test reads.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypeVar

from linuxfacts.models import CpuInfo, DiskUsage, HostInfo, MemoryInfo, ProcessInfo
from linuxfacts.sources.base import DEFAULT_TIMEOUT, CommandResult

__all__ = ["FakeSource"]

_T = TypeVar("_T")


class FakeSource:
    """A configurable, offline :class:`~linuxfacts.sources.base.Source` for tests.

    Each structured reading is supplied as a value or as an exception to raise. Commands
    are matched against the ``commands`` mapping: a key of the full argument tuple matches
    that exact call, and a single-element key ``(program,)`` matches any call to that
    program. An unmatched command raises :class:`LookupError`, so a forgotten stub fails
    loudly rather than silently.
    """

    def __init__(
        self,
        *,
        disks: list[DiskUsage] | BaseException | None = None,
        memory: MemoryInfo | BaseException | None = None,
        cpu: CpuInfo | BaseException | None = None,
        processes: list[ProcessInfo] | BaseException | None = None,
        host: HostInfo | BaseException | None = None,
        commands: Mapping[Sequence[str], CommandResult | BaseException] | None = None,
    ) -> None:
        self._disks = disks
        self._memory = memory
        self._cpu = cpu
        self._processes = processes
        self._host = host
        self._commands: dict[tuple[str, ...], CommandResult | BaseException] = {
            tuple(key): value for key, value in (commands or {}).items()
        }

    def run_command(
        self, args: Sequence[str], *, timeout: float = DEFAULT_TIMEOUT
    ) -> CommandResult:
        del timeout  # a fake does not wait
        key = tuple(args)
        entry = self._commands.get(key)
        if entry is None and key:
            entry = self._commands.get((key[0],))
        if entry is None:
            raise LookupError(f"FakeSource has no canned result for command: {' '.join(args)}")
        if isinstance(entry, BaseException):
            raise entry
        return entry

    def read_disks(self) -> list[DiskUsage]:
        return self._resolve("disks", self._disks)

    def read_memory(self) -> MemoryInfo:
        return self._resolve("memory", self._memory)

    def read_cpu(self) -> CpuInfo:
        return self._resolve("cpu", self._cpu)

    def read_processes(self) -> list[ProcessInfo]:
        return self._resolve("processes", self._processes)

    def read_host(self) -> HostInfo:
        return self._resolve("host", self._host)

    @staticmethod
    def _resolve(name: str, value: _T | BaseException | None) -> _T:
        if value is None:
            raise LookupError(f"FakeSource.{name} was not configured for this test")
        if isinstance(value, BaseException):
            raise value
        return value
