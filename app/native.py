"""
High-Performance Native Rust Interop Module for Django-Lightning.

Provides type-safe, non-blocking wrappers and ultra-efficient memory transfer utilities
between Python and native PyO3 Rust extensions.
"""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import Any

import msgspec

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


def native_async[**P, R](func: Callable[P, R]) -> Callable[P, Awaitable[R]]:
    """
    Decorator that wraps a synchronous PyO3 Rust function (or Python fallback) into a fully
    type-safe, non-blocking async function pre-configured for threadpool execution.

    Preserves exact parameter type hints, IDE autocomplete, and docstrings.

    Usage:
        process_batch = native_async(rust_core.process_batch)
        results = await process_batch(items)
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if kwargs:
            return await asyncio.to_thread(func, *args, **kwargs)
        return await asyncio.to_thread(func, *args)

    return wrapper


def native_json[In, Out](
    rust_func: Callable[[bytes], bytes] | None,
    response_type: type[Out],
    fallback: Callable[[In], Out] | Callable[[In], Awaitable[Out]] | None = None,
) -> Callable[[In], Awaitable[Out]]:
    """
    Creates an ultra-fast, type-safe async native function operating on msgspec JSON byte buffers.

    Bypasses PyDict/PyList FFI allocation overhead by serializing input structs directly to UTF-8
    bytes, passing raw memory slices to Rust (`serde_json`), executing in a threadpool with GIL
    released, and decoding the returned bytes back to response_type.

    Usage:
        process_payload = native_json(
            rust_core.process_payload if HAS_RUST_CORE else None,
            response_type=OutputStruct,
            fallback=python_fallback_fn,
        )

        response = await process_payload(payload)
    """

    async def wrapper(payload: In) -> Out:
        if rust_func is None or not HAS_RUST_CORE:
            if fallback is not None:
                res = fallback(payload)
                if asyncio.iscoroutine(res):
                    return await res
                return res
            raise RuntimeError("rust_core native extension module is not compiled or available.")

        input_bytes = msgspec.json.encode(payload)
        output_bytes = await asyncio.to_thread(rust_func, input_bytes)
        return msgspec.json.decode(output_bytes, type=response_type)

    return wrapper


async def run_native[R](func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
    """
    Execute a native PyO3 Rust function asynchronously in a background thread pool.
    Releases GIL and prevents blocking Python's event loop.
    """
    if kwargs:
        return await asyncio.to_thread(func, *args, **kwargs)
    return await asyncio.to_thread(func, *args)
