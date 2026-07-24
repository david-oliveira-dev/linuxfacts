"""Exception hierarchy.

Every error the library raises descends from :class:`LinuxFactsError`, so a consumer
can catch the library without catching the world.

The library rarely raises. An *expected* condition — permission denied, a missing
command — is never an exception; it is a :class:`~linuxfacts.models.Fact` in the
``unknown`` state (RN-001). Exceptions are reserved for programmer error
(:class:`~linuxfacts.models.Fact.unwrap` on an unknown fact) and for the real source's
own failures, which the fact functions catch and convert to ``unknown`` (RN-002).
"""

from __future__ import annotations

__all__ = [
    "CommandNotFoundError",
    "CommandTimeoutError",
    "LinuxFactsError",
    "SourceError",
    "UnknownFactError",
]


class LinuxFactsError(Exception):
    """Base class for every error raised by linuxfacts."""


class UnknownFactError(LinuxFactsError):
    """Raised by :meth:`~linuxfacts.models.Fact.unwrap` on an unknown fact.

    Unwrapping is the explicit, opt-in way to demand a value; if the fact could not
    be determined, that demand fails loudly instead of returning ``None``.
    """


class SourceError(LinuxFactsError):
    """Base class for failures of the underlying system source."""


class CommandNotFoundError(SourceError):
    """An external command (``systemctl``, ``ss``, ``apt``) is not installed."""


class CommandTimeoutError(SourceError):
    """An external command did not finish within its timeout (RN-004)."""
