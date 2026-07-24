# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `docs/extraction-scope.md`: the fact-vs-policy analysis deciding what is extracted from
  `ubuntu-doctor` into the library and what stays behind.
- Project scaffold: `uv`, `src/` layout, `py.typed`, and a nox matrix for Python
  3.11–3.13.
- Tooling baseline: Ruff, mypy (strict), pre-commit, and pytest with a 90% coverage floor.
- GitHub Actions CI (lint, format check, type check, tests across Python 3.11–3.13) and
  Dependabot.

[Unreleased]: https://github.com/david-oliveira-dev/linuxfacts/commits/main
