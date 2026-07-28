"""
High-Performance Native Rust Interop Layer for Django-Lightning.

Provides safe, type-hinted, GIL-releasing native bindings for API handlers and background workers.
If the rust_core module is not compiled, functions gracefully fall back to Python equivalents.
"""

from __future__ import annotations

import asyncio

try:
    from app import rust_core  # type: ignore

    HAS_RUST_CORE = True
except ImportError:
    rust_core = None  # type: ignore
    HAS_RUST_CORE = False


def is_rust_available() -> bool:
    """Check if compiled native Rust core is available in current environment."""
    return HAS_RUST_CORE


async def aparallel_transform_strings(items: list[str]) -> list[str]:
    """
    Asynchronously transform a list of strings in parallel across CPU cores using Rust.
    Releases Python GIL to ensure non-blocking execution.
    """
    if not HAS_RUST_CORE:
        # Graceful fallback for non-Rust deployments or uncompiled environments
        return [s.strip().upper() for s in items]

    return await asyncio.to_thread(rust_core.parallel_transform_strings, items)


async def aparallel_sum_floats(values: list[float]) -> float:
    """
    Asynchronously sum a list of floats in parallel across CPU cores using Rust.
    Releases Python GIL to ensure non-blocking execution.
    """
    if not HAS_RUST_CORE:
        return float(sum(values))

    return await asyncio.to_thread(rust_core.parallel_sum_floats, values)
