# 1. A Fact envelope instead of exceptions

- Status: accepted
- Date: 2026-07-25

## Context

Reading system state fails in expected ways: a mount is momentarily unreadable, a command
needs privilege the caller does not have, a binary is missing. A library has to decide how
to report "I could not determine this."

## Decision

Every fact returns a generic `Fact[T]` with an explicit `FactState` — `ok` with a value,
or `unknown` with a reason. Expected failures become an `unknown` fact, never an exception
(RN-001). Exceptions are reserved for programmer error (unwrapping an unknown fact, a
negative `top`) and genuinely unexpected failures (RN-002). Absence of information is never
conflated with a healthy reading (RN-003).

## Alternatives considered

- **Raise on permission denied / missing command** — rejected: these are expected
  conditions on real systems, and raising would force `try/except` around every call in
  every consumer.
- **Return `None` on failure** — rejected: `None` carries no reason, and it invites the
  caller to forget the check. `Fact` makes the two outcomes impossible to ignore and
  carries *why* it failed.

## Consequences

- Consumers handle `fact.is_ok` / `fact.unwrap()` explicitly; the `unwrap()` opt-in fails
  loudly when a value is demanded but unknown.
- The envelope adds one unwrap step for the common case, in exchange for never mistaking
  "don't know" for "fine" — the right trade for a diagnostic library.
- Implementation note: the public sketch used `class Fact[T]` (PEP 695), but the library
  supports Python 3.11, so `Generic[T]` is used instead. The surface is identical.
