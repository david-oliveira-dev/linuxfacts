"""Local multi-version test matrix.

Runs the suite across the supported Python versions with `uv` as the backend, so a
developer can reproduce the CI matrix locally with `uv run nox`. Missing interpreters
are skipped rather than failing, so it is usable on a machine with only one Python.
"""

from __future__ import annotations

import nox

nox.options.default_venv_backend = "uv"
nox.options.error_on_missing_interpreters = False
nox.options.sessions = ["lint", "typecheck", "tests"]

PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite with coverage."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pytest")


@nox.session
def lint(session: nox.Session) -> None:
    """Lint and format-check."""
    session.install("ruff")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session
def typecheck(session: nox.Session) -> None:
    """Strict type checking."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("mypy")
