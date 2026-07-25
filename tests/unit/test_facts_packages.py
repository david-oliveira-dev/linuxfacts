"""Tests for the packages fact — real apt/dpkg fixtures, offline."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from linuxfacts.exceptions import CommandNotFoundError
from linuxfacts.facts import packages
from linuxfacts.facts.packages import parse_broken, parse_upgradable
from linuxfacts.sources.base import CommandResult
from linuxfacts.testing import FakeSource
from tests.support import fixture_text

APT = fixture_text("apt_upgradable.txt")
DPKG_DENIED = fixture_text("dpkg_audit_permission_denied.txt")


def _fake(*, apt: CommandResult, dpkg: CommandResult) -> FakeSource:
    return FakeSource(commands={("apt", "list", "--upgradable"): apt, ("dpkg", "--audit"): dpkg})


def test_counts_updates_and_recognises_security() -> None:
    total, security = parse_upgradable(APT)
    assert total > 0
    assert security > 0  # the fixture has noble-security entries


def test_packages_ok_with_broken_none_when_dpkg_denied() -> None:
    fact = packages(_fake(apt=CommandResult(APT, "", 0), dpkg=CommandResult(DPKG_DENIED, "", 2)))
    status = fact.unwrap()
    assert status.total_updates > 0
    assert status.broken is None  # could not check → None, not ()


def test_packages_broken_empty_when_dpkg_clean() -> None:
    fact = packages(_fake(apt=CommandResult(APT, "", 0), dpkg=CommandResult("", "", 0)))
    assert fact.unwrap().broken == ()


def test_apt_nonzero_exit_makes_the_whole_fact_unknown() -> None:
    fake = FakeSource(commands={("apt", "list", "--upgradable"): CommandResult("", "locked", 100)})
    fact = packages(fake)
    assert fact.is_unknown
    assert "locked" in (fact.reason or "")


def test_apt_missing_makes_the_whole_fact_unknown() -> None:
    fake = FakeSource(commands={("apt",): CommandNotFoundError("no apt")})
    assert packages(fake).is_unknown


def test_parse_broken_extracts_names() -> None:
    assert parse_broken("libfoo\nlibbar extra text\n") == ("libfoo", "libbar")


def test_broken_none_when_dpkg_missing() -> None:
    fake = FakeSource(
        commands={
            ("apt", "list", "--upgradable"): CommandResult(APT, "", 0),
            ("dpkg", "--audit"): CommandNotFoundError("no dpkg"),
        }
    )
    assert packages(fake).unwrap().broken is None


@given(st.text())
def test_parsers_never_raise(text: str) -> None:
    parse_upgradable(text)
    parse_broken(text)
