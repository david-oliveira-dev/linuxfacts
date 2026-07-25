# 2. Protocol-based source injection

- Status: accepted
- Date: 2026-07-25

## Context

Every fact needs to touch the system — `psutil`, `subprocess`, `/proc`. If that access is
hard-wired, the facts cannot be tested without a real machine, and a consumer cannot test
their own tool without one either.

## Decision

All system access goes through a single `Source` protocol. The real implementation is the
default; every fact takes `source: Source | None = None`. Structured readings return domain
models; command-backed facts go through `run_command`. Because `Source` is a `Protocol`
(structural typing), any object with the right methods qualifies — no base class to inherit.

## Alternatives considered

- **Collector classes with inheritance** — rejected: a `Protocol` gives the same decoupling
  without a rigid hierarchy, and lets a consumer's own object stand in without importing us.
- **Per-function injected callables** (one `partitions=`, `usage=`, ... per fact) — rejected:
  it multiplies the seam and leaks the shape of the backend into every signature. One
  protocol is a single, stable boundary.

## Consequences

- Facts are pure with respect to the source: pass a fake and they run offline and
  deterministically.
- The boundary is the one place that changes if the backend changes (e.g. adding GitLab-
  style provider abstraction later); the facts do not.
- The protocol is small on purpose. Adding a method is a source-layer change, not a fact
  change.
