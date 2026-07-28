"""
High-Performance Native Rust Interop Module for Django-Lightning.

Provides core utility functions to safely execute native Rust routines from async API handlers
and SAQ background worker tasks with zero event-loop blocking.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, TypeVar

R = TypeVar("R")

try:
    from app import rust_core

    HAS_RUST_CORE = True
except ImportError:
    rust_core = None
    HAS_RUST_CORE = False


def is_rust_available() -> bool:
    """Check if compiled native Rust core is available in the current environment."""
    return HAS_RUST_CORE


def get_rust_core_version() -> str | None:
    """Return the compiled Rust crate version, or None if Rust is not available."""
    if not HAS_RUST_CORE:
        return None
    return rust_core.rust_core_version()


async def run_native(func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
    """
    Execute a native PyO3 Rust function asynchronously in a background thread.

    Use this helper in async handlers or SAQ tasks when invoking GIL-releasing Rust functions.
    """
    if kwargs:
        return await asyncio.to_thread(func, *args, **kwargs)
    return await asyncio.to_thread(func, *args)
