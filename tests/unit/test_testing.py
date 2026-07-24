"""Tests for the public FakeSource.

FakeSource is itself part of the public contract (UC-02), so it gets first-class tests:
it must satisfy the Source protocol, serve canned readings, raise configured exceptions,
match commands exactly and by program name, and fail loudly when a reading is called
without being configured.
"""

from __future__ import annotations

import pytest

from linuxfacts.exceptions import CommandNotFoundError
from linuxfacts.models import CpuInfo, DiskUsage, HostInfo, MemoryInfo, ProcessInfo
from linuxfacts.sources.base import CommandResult, Source
from linuxfacts.testing import FakeSource

DISKS = [DiskUsage("/", 100, 40, 60, 40.0)]
MEMORY = MemoryInfo(16_000, 8_000, 8_000, 50.0, 0, 0, 0.0)
CPU = CpuInfo(0.5, 0.6, 0.7, 8)
PROCESSES = [ProcessInfo(1, "init", 0.1, 0.2)]
HOST = HostInfo("host", "6.8.0", "Ubuntu 24.04", 123.0)


def test_fake_source_satisfies_the_protocol() -> None:
    assert isinstance(FakeSource(), Source)


def test_serves_canned_structured_readings() -> None:
    source = FakeSource(disks=DISKS, memory=MEMORY, cpu=CPU, processes=PROCESSES, host=HOST)
    assert source.read_disks() == DISKS
    assert source.read_memory() == MEMORY
    assert source.read_cpu() == CPU
    assert source.read_processes() == PROCESSES
    assert source.read_host() == HOST


def test_unconfigured_reading_fails_loudly_only_when_called() -> None:
    source = FakeSource(memory=MEMORY)  # only memory configured
    assert source.read_memory() == MEMORY  # configured: fine
    with pytest.raises(LookupError, match="disks was not configured"):
        source.read_disks()


def test_reading_can_be_made_to_raise() -> None:
    source = FakeSource(disks=PermissionError("denied"))
    with pytest.raises(PermissionError, match="denied"):
        source.read_disks()


def test_command_matches_exact_argument_tuple() -> None:
    result = CommandResult("out", "", 0)
    source = FakeSource(commands={("systemctl", "list-units", "--failed"): result})
    assert source.run_command(["systemctl", "list-units", "--failed"]) is result


def test_command_matches_by_program_name() -> None:
    result = CommandResult("anything", "", 0)
    source = FakeSource(commands={("ss",): result})
    assert source.run_command(["ss", "-tulpn"]) is result


def test_exact_match_wins_over_program_match() -> None:
    exact = CommandResult("exact", "", 0)
    generic = CommandResult("generic", "", 0)
    source = FakeSource(commands={("apt", "list", "--upgradable"): exact, ("apt",): generic})
    assert source.run_command(["apt", "list", "--upgradable"]).stdout == "exact"
    assert source.run_command(["apt", "moo"]).stdout == "generic"


def test_command_can_be_made_to_raise() -> None:
    source = FakeSource(commands={("systemctl",): CommandNotFoundError("no systemctl")})
    with pytest.raises(CommandNotFoundError, match="no systemctl"):
        source.run_command(["systemctl", "list-units"])


def test_unmatched_command_fails_loudly() -> None:
    source = FakeSource()
    with pytest.raises(LookupError, match="no canned result for command: ss -tulpn"):
        source.run_command(["ss", "-tulpn"])


def test_timeout_is_accepted_and_ignored() -> None:
    result = CommandResult("out", "", 0)
    source = FakeSource(commands={("uptime",): result})
    assert source.run_command(["uptime"], timeout=0.001) is result
