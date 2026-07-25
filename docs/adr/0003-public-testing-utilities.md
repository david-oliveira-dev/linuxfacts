# 3. Testing utilities are public API

- Status: accepted
- Date: 2026-07-25

## Context

The library's injectable `Source` lets consumers test their tools offline — but only if
they have a double to inject. If everyone writes their own `FakeSource`, they all
reimplement the same thing, subtly differently, and the library's testability promise is
only half delivered.

## Decision

Ship `FakeSource` as public API, in `linuxfacts.testing`. It is a full, configurable
`Source` that returns canned readings and can be made to raise, so a consumer exercises
both the ok and unknown paths without a broken machine. It lives in a separate module, so a
production dependency on `linuxfacts` never pulls the test double into a shipped app.

## Alternatives considered

- **Keep the fake internal** — rejected: it is exactly the piece consumers need most, and
  hiding it forces every consumer to rebuild it.
- **Put it in the top-level namespace** — rejected: it would be importable from a
  production path. A dedicated `linuxfacts.testing` module keeps the intent explicit and the
  production surface clean.

## Consequences

- Testing a consumer's tool is a few lines: build a `FakeSource`, pass it, assert on the
  `Fact`. This is the library's headline selling point (UC-02), so it is documented as its
  own page.
- `FakeSource` is part of the compatibility contract: its constructor keywords are public
  and covered by SemVer like the rest.
