# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-07-25

First release. A typed, read-only library for reading Linux system state, extracted from
`ubuntu-doctor`.

### Added
- Eight facts, each `fact(source=None) -> Fact[...]`: `disks`, `memory`, `cpu`,
  `processes` (ranked by CPU, optional `top`), `systemd_units` (by state), `listening_ports`,
  `packages` (updates plus a broken-package tri-state), and `host`.
- The generic `Fact[T]` envelope with an explicit `ok`/`unknown` state: an expected failure
  is an `unknown` fact with a reason, never an exception and never a silent zero.
- Immutable, typed domain models and a `py.typed` marker.
- A `Source` protocol behind every fact, and a **public `FakeSource`** (in
  `linuxfacts.testing`) so consumers test their own tools offline.
- `LinuxFactsError` hierarchy; every command runs read-only, shell-free, with a timeout.
- A public-API contract test that freezes the exported surface and every fact signature.
- MkDocs documentation (usage, a testing guide, an API reference, and the compatibility
  policy) and three ADRs.
- `docs/extraction-scope.md`: the fact-vs-policy analysis deciding what was extracted from
  `ubuntu-doctor`.
- Project scaffold (`uv`, `src/` layout), a nox matrix for Python 3.11–3.13, Ruff, strict
  mypy, pre-commit, a 90% coverage floor, GitHub Actions CI and Dependabot.

[Unreleased]: https://github.com/david-oliveira-dev/linuxfacts/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/david-oliveira-dev/linuxfacts/releases/tag/v1.0.0
