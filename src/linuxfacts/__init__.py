"""LinuxFacts — typed, read-only access to Linux system state.

The public API is exactly what this module exports via ``__all__``; everything else
is private and may change without a major version bump (RN-005). The surface is filled
in phase by phase — models and the ``Fact`` envelope first, then one fact at a time.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
