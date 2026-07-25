# Compatibility and deprecation policy

LinuxFacts follows [Semantic Versioning](https://semver.org). This page is the promise the
version number stands for.

## What is public

The public API is **exactly** what `linuxfacts` exports via `__all__`, plus `FakeSource`
from `linuxfacts.testing`:

- the eight facts and their signatures,
- the `Fact` envelope and `FactState`,
- the domain models and their fields,
- `LinuxFactsError`,
- `FakeSource` and its constructor keywords.

Anything not in that list — private modules, helper functions, the real source's internals
— is implementation detail and may change in any release (RN-005).

## The promise

Within a major version:

- No public name is removed.
- No public function's signature changes incompatibly (parameters are not removed or
  reordered; a model's fields are not removed).
- Behaviour does not change in a way that breaks a correct consumer.

A change that breaks any of these requires a **major** version bump.

## How it is enforced

A [contract test](https://github.com/david-oliveira-dev/linuxfacts/blob/main/tests/contract/test_public_api.py)
freezes the exact set of public names and the signature of every fact. Removing a symbol or
changing a signature fails CI — so a breaking change cannot ship by accident; it must be a
deliberate major bump with the contract test updated in the same commit.

## Deprecation

When a public name is going away, it is first **deprecated**, not removed:

1. It keeps working and emits a `DeprecationWarning` for at least one minor version.
2. The changelog and this page document the replacement.
3. Only then, in the next major version, is it removed.

Adding new facts, models or optional parameters is backward compatible and ships in minor
versions.
