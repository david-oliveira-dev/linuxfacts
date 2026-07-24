.PHONY: install check lint format type test matrix clean

install:
	uv sync

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

type:
	uv run mypy

test:
	uv run pytest

# The full local quality gate, matching CI for a single Python version.
check: lint type test

# The full multi-version matrix (skips interpreters that are not installed).
matrix:
	uv run nox

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .nox .coverage coverage.xml htmlcov dist build
