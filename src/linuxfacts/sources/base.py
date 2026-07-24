"""The ``Source`` protocol — the single seam between the library and the system.

Every fact reads through a :class:`Source`. Production uses the real one (``psutil``,
``subprocess``, ``/proc``); tests use the public :class:`~linuxfacts.testing.FakeSource`.
Because the seam is one small protocol, a consumer can substitute canned readings and test
their own code offline and deterministically — the whole point of the library (UC-02).

Structured readings return domain models directly; command-backed facts (systemd, ports,
packages) go through :meth:`Source.run_command`, and the pure parsers that turn command
output into models live with each fact, where they are property-tested.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from linuxfacts.models import CpuInfo, DiskUsage, HostInfo, MemoryInfo, ProcessInfo

__all__ = ["DEFAULT_TIMEOUT", "CommandResult", "Source"]

#: Default per-command timeout, in seconds. Every command has one (RN-004).
DEFAULT_TIMEOUT = 5.0


@dataclass(frozen=True, slots=True)
class CommandResult:
    """The captured result of a finished command."""

    stdout: str
    stderr: str
    returncode: int


@runtime_checkable
class Source(Protocol):
    """Read-only access to system state.

    Implementations must never write to the system, never require elevated privilege,
    and never run a command through a shell. A reading that cannot be performed should
    raise (the fact layer converts that into an ``unknown`` fact), except where the
    protocol says a field degrades in place (e.g. an unnamed process).
    """

    def run_command(
        self, args: Sequence[str], *, timeout: float = DEFAULT_TIMEOUT
    ) -> CommandResult:
        """Run ``args`` (a fixed list, never a shell string) and capture its output.

        Raises:
            CommandNotFoundError: the executable does not exist.
            CommandTimeoutError: it did not finish within ``timeout`` seconds.
        """
        ...

    def read_disks(self) -> list[DiskUsage]:
        """Usage for every real mounted filesystem."""
        ...

    def read_memory(self) -> MemoryInfo:
        """Virtual memory and swap figures."""
        ...

    def read_cpu(self) -> CpuInfo:
        """Load averages and core count."""
        ...

    def read_processes(self) -> list[ProcessInfo]:
        """Every process's resource share, unranked."""
        ...

    def read_host(self) -> HostInfo:
        """Host identity and uptime."""
        ...
