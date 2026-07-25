"""Tests for the systemd units fact — real systemctl fixtures, offline."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from linuxfacts.exceptions import CommandNotFoundError
from linuxfacts.facts import systemd_units
from linuxfacts.facts.systemd import parse_units
from linuxfacts.sources.base import CommandResult
from linuxfacts.testing import FakeSource
from tests.support import fixture_text


def _fake(text: str = "", *, returncode: int = 0) -> FakeSource:
    return FakeSource(commands={("systemctl",): CommandResult(text, "", returncode)})


def test_parses_a_failed_unit() -> None:
    fact = systemd_units(_fake(fixture_text("systemctl_failed.txt")))
    units = fact.unwrap()
    assert units[0].name == "virtualbox.service"
    assert units[0].active_state == "failed"
    assert "VirtualBox" in units[0].description


def test_parses_multiple_running_units() -> None:
    fact = systemd_units(_fake(fixture_text("systemctl_running_sample.txt")), state="running")
    names = [u.name for u in fact.unwrap()]
    assert names == ["accounts-daemon.service", "avahi-daemon.service", "bluetooth.service"]


def test_empty_output_is_ok_and_empty() -> None:
    fact = systemd_units(_fake(""))
    assert fact.is_ok
    assert fact.unwrap() == []


def test_nonzero_exit_is_unknown() -> None:
    fact = systemd_units(FakeSource(commands={("systemctl",): CommandResult("", "boom", 1)}))
    assert fact.is_unknown
    assert "boom" in (fact.reason or "")


def test_missing_systemctl_is_unknown() -> None:
    fake = FakeSource(commands={("systemctl",): CommandNotFoundError("no systemctl")})
    assert systemd_units(fake).is_unknown


def test_state_none_omits_the_filter() -> None:
    # A single-element command key matches regardless of args, so this just checks it runs.
    assert systemd_units(_fake(""), state=None).is_ok


@given(st.text())
def test_parse_units_never_raises(text: str) -> None:
    parse_units(text)  # must tolerate arbitrary input
