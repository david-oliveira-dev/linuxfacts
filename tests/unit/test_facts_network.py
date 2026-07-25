"""Tests for the listening ports fact — real ss fixture, offline."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from linuxfacts.exceptions import CommandNotFoundError
from linuxfacts.facts import listening_ports
from linuxfacts.facts.network import parse_ports
from linuxfacts.sources.base import CommandResult
from linuxfacts.testing import FakeSource
from tests.support import fixture_text


def _fake(text: str, *, returncode: int = 0) -> FakeSource:
    return FakeSource(commands={("ss",): CommandResult(text, "", returncode)})


def test_parses_real_ss_output() -> None:
    fact = listening_ports(_fake(fixture_text("ss_tulpn.txt")))
    ports = fact.unwrap()
    assert ports  # the fixture has listening sockets
    assert all(p.port > 0 for p in ports)
    # a socket owned by a named process keeps the name; others degrade to None
    named = [p for p in ports if p.process is not None]
    assert any(p.process == "chrome" for p in named)


def test_nonzero_exit_is_unknown() -> None:
    fact = listening_ports(_fake("", returncode=1))
    assert fact.is_unknown


def test_header_only_is_ok_and_empty() -> None:
    fact = listening_ports(_fake("Netid State Recv-Q Send-Q Local Peer Process\n"))
    assert fact.is_ok
    assert fact.unwrap() == []


def test_source_failure_is_unknown() -> None:
    fake = FakeSource(commands={("ss",): CommandNotFoundError("no ss")})
    assert listening_ports(fake).is_unknown


def test_line_without_a_numeric_port_is_skipped() -> None:
    # a listening row whose local field has no numeric port is dropped, not fatal
    line = "tcp LISTEN 0 128 unix-socket-path 0.0.0.0:* users:((x))\n"
    assert parse_ports(line) == []


@given(st.text())
def test_parse_ports_never_raises(text: str) -> None:
    parse_ports(text)
