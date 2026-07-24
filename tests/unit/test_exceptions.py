"""Tests for the exception hierarchy.

The property that matters: everything descends from LinuxFactsError, so a consumer can
catch the library in one clause, and the source errors form their own sub-hierarchy.
"""

from __future__ import annotations

import pytest

from linuxfacts.exceptions import (
    CommandNotFoundError,
    CommandTimeoutError,
    LinuxFactsError,
    SourceError,
    UnknownFactError,
)

ALL_ERRORS = [
    UnknownFactError,
    SourceError,
    CommandNotFoundError,
    CommandTimeoutError,
]


@pytest.mark.parametrize("error_type", ALL_ERRORS)
def test_every_error_descends_from_the_base(error_type: type[LinuxFactsError]) -> None:
    assert issubclass(error_type, LinuxFactsError)


@pytest.mark.parametrize("error_type", [CommandNotFoundError, CommandTimeoutError])
def test_command_errors_are_source_errors(error_type: type[SourceError]) -> None:
    assert issubclass(error_type, SourceError)


def test_catching_the_base_catches_everything() -> None:
    with pytest.raises(LinuxFactsError):
        raise CommandTimeoutError("systemctl timed out")


def test_unwrap_error_is_not_a_source_error() -> None:
    # A programmer unwrapping an unknown fact is distinct from a system failure.
    assert not issubclass(UnknownFactError, SourceError)
