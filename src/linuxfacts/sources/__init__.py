"""System access: the ``Source`` protocol and its implementations.

This package is the only place that touches ``psutil``, ``subprocess`` and ``/proc``.
The facts depend on the :class:`~linuxfacts.sources.base.Source` protocol, never on a
concrete implementation.
"""
