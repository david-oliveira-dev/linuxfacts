"""Tests for the Source protocol and CommandResult.

The concrete implementations arrive later (FakeSource in phase 3, the real source in
phase 4); here we only pin the contract — a conforming object satisfies the protocol,
and a non-conforming one does not.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence

import pytest

from linuxfacts.models import CpuInfo, DiskUsage, HostInfo, MemoryInfo, ProcessInfo
from linuxfacts.sources.base import DEFAULT_TIMEOUT, CommandResult, Source


class _Conforming:
    def run_command(
        self, args: Sequence[str], *, timeout: float = DEFAULT_TIMEOUT
    ) -> CommandResult:
        return CommandResult("", "", 0)

    def read_disks(self) -> list[DiskUsage]:
        return []

    def read_memory(self) -> MemoryInfo:
        return MemoryInfo(0, 0, 0, 0.0, 0, 0, 0.0)

    def read_cpu(self) -> CpuInfo:
        return CpuInfo(0.0, 0.0, 0.0, 1)

    def read_processes(self) -> list[ProcessInfo]:
        return []

    def read_host(self) -> HostInfo:
        return HostInfo("h", "k", "d", 0.0)


class _Incomplete:
    def run_command(
        self, args: Sequence[str], *, timeout: float = DEFAULT_TIMEOUT
    ) -> CommandResult:
        return CommandResult("", "", 0)


def test_a_full_implementation_satisfies_the_protocol() -> None:
    assert isinstance(_Conforming(), Source)


def test_a_partial_implementation_does_not() -> None:
    assert not isinstance(_Incomplete(), Source)


def test_command_result_is_frozen() -> None:
    result = CommandResult("out", "err", 1)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.returncode = 0  # type: ignore[misc]


def test_default_timeout_is_positive() -> None:
    assert DEFAULT_TIMEOUT > 0
