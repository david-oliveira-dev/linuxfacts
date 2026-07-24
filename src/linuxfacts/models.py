"""Domain models: the facts and the envelope that carries them.

Every model is a frozen, slotted dataclass — a fact is a photograph of the system at a
moment, and a photograph you can edit is not evidence. The generic :class:`Fact` wraps a
value with an explicit :class:`FactState`, so "I could not determine this" is a value the
caller handles, never an exception it must catch (RN-001, RN-003).

Note on typing: the public spec sketches ``class Fact[T]`` (PEP 695), but the library
supports Python 3.11, where that syntax does not exist. The equivalent ``Generic[T]`` form
is used instead; the public surface is identical.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypeVar

from linuxfacts.exceptions import UnknownFactError

__all__ = [
    "CpuInfo",
    "DiskUsage",
    "Fact",
    "FactState",
    "HostInfo",
    "ListeningPort",
    "MemoryInfo",
    "PackageStatus",
    "ProcessInfo",
    "SystemdUnit",
]

T = TypeVar("T")


class FactState(StrEnum):
    """Whether a fact could be determined.

    ``UNKNOWN`` is never treated as ``OK``: absence of information is not absence of a
    problem (RN-003).
    """

    OK = "ok"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Fact(Generic[T]):
    """A value that was read, or an honest record that it could not be.

    A fact is either ``ok`` with a value, or ``unknown`` with a human-readable reason.
    The two constructors :meth:`ok` and :meth:`unknown` are the intended way to build one.

    Example:
        >>> Fact.ok(42).unwrap()
        42
        >>> Fact.unknown("permission denied").is_ok
        False
    """

    state: FactState
    value: T | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.state is FactState.UNKNOWN:
            if not (self.reason and self.reason.strip()):
                raise ValueError("an unknown fact requires a reason")
            if self.value is not None:
                raise ValueError("an unknown fact must not carry a value")
        elif self.value is None:
            raise ValueError("an ok fact must carry a value")

    @classmethod
    def ok(cls, value: T) -> Fact[T]:
        """Build an ``ok`` fact around ``value``."""
        return cls(state=FactState.OK, value=value)

    @classmethod
    def unknown(cls, reason: str) -> Fact[T]:
        """Build an ``unknown`` fact carrying ``reason`` (why it could not be read)."""
        return cls(state=FactState.UNKNOWN, value=None, reason=reason)

    @property
    def is_ok(self) -> bool:
        return self.state is FactState.OK

    @property
    def is_unknown(self) -> bool:
        return self.state is FactState.UNKNOWN

    def unwrap(self) -> T:
        """Return the value, or raise :class:`~linuxfacts.exceptions.UnknownFactError`.

        Unwrapping is explicit on purpose — it is how a caller states that an unknown
        fact is unacceptable here and should fail loudly rather than pass as ``None``.
        """
        if self.state is FactState.UNKNOWN or self.value is None:
            raise UnknownFactError(self.reason or "fact is unknown")
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Return the value if ``ok``, otherwise ``default``."""
        if self.is_ok and self.value is not None:
            return self.value
        return default


# ---------------------------------------------------------------------------
# The facts
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DiskUsage:
    """Usage of a single mounted filesystem."""

    mountpoint: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent_used: float


@dataclass(frozen=True, slots=True)
class MemoryInfo:
    """Virtual memory and swap.

    ``available_bytes`` is the honest measure of pressure on Linux — the kernel lends
    idle RAM to caches it will reclaim on demand, so ``available`` beats ``free``.
    """

    total_bytes: int
    available_bytes: int
    used_bytes: int
    percent_used: float
    swap_total_bytes: int
    swap_used_bytes: int
    swap_percent: float


@dataclass(frozen=True, slots=True)
class CpuInfo:
    """Load averages and core count.

    ``core_count`` is ``None`` when it could not be determined.
    """

    load1: float
    load5: float
    load15: float
    core_count: int | None


@dataclass(frozen=True, slots=True)
class ProcessInfo:
    """One process's resource share. Name and PID only — never the command line."""

    pid: int
    name: str
    cpu_percent: float
    memory_percent: float


@dataclass(frozen=True, slots=True)
class SystemdUnit:
    """A systemd unit and its reported states."""

    name: str
    load_state: str
    active_state: str
    sub_state: str
    description: str


@dataclass(frozen=True, slots=True)
class ListeningPort:
    """A single listening socket.

    ``process`` is ``None`` when the owning process cannot be named — typically because
    it belongs to another user and the reader lacks privilege (graceful degradation).
    """

    protocol: str
    local_address: str
    port: int
    process: str | None


@dataclass(frozen=True, slots=True)
class PackageStatus:
    """Package updates and broken packages.

    ``broken`` is ``None`` when broken-package status could not be determined (checking
    it needs the dpkg lock, hence privilege); an empty tuple means "checked, none broken".
    A ``None`` here is the tri-state that keeps "unknown" distinct from "none" (RN-003).
    """

    total_updates: int
    security_updates: int
    broken: tuple[str, ...] | None


@dataclass(frozen=True, slots=True)
class HostInfo:
    """Basic host identity and uptime."""

    hostname: str
    kernel: str
    distribution: str
    uptime_seconds: float
