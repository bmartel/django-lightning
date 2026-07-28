"""
High-Performance Native Rust Interop Module for Django-Lightning.

Provides explicit, type-safe async wrappers and ultra-efficient memory transfer utilities
for native PyO3 Rust extensions.
"""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar

import msgspec

P = ParamSpec("P")
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


def native_async[**P, R](func: Callable[P, R]) -> Callable[P, Awaitable[R]]:
    """
    Wraps a synchronous PyO3 Rust function into a fully type-safe, non-blocking async function

    pre-configured for threadpool execution with GIL releasing.

    Preserves exact parameter type hints, IDE autocomplete, and docstrings.

    Usage:
        process_batch = native_async(rust_core.process_batch)

        results = await process_batch(items)
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if not HAS_RUST_CORE:
            raise RuntimeError(
                f"rust_core native module is not compiled. Cannot execute '{func.__name__}'."
            )
        if kwargs:
            return await asyncio.to_thread(func, *args, **kwargs)
        return await asyncio.to_thread(func, *args)

    return wrapper


def native_json[In, Out](
    rust_func: Callable[[bytes], bytes],
    response_type: type[Out],
) -> Callable[[In], Awaitable[Out]]:
    """
    Wraps a PyO3 Rust byte-buffer function into an ultra-fast, type-safe async native function

    operating on msgspec JSON byte buffers.

    Serializes input structs directly to UTF-8 bytes using msgspec, passes raw memory slices
    to Rust (`serde_json`), executes in a threadpool with GIL released, and decodes the result.

    Usage:
        process_payload = native_json(rust_core.process_payload, response_type=OutputStruct)

        response = await process_payload(payload)
    """

    async def wrapper(payload: In) -> Out:
        if not HAS_RUST_CORE:
            raise RuntimeError("rust_core native module is not compiled.")

        input_bytes = msgspec.json.encode(payload)
        output_bytes = await asyncio.to_thread(rust_func, input_bytes)
        return msgspec.json.decode(output_bytes, type=response_type)

    return wrapper


async def run_native[R](func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
    """
    Execute a native PyO3 Rust function asynchronously in a background thread pool.
    Releases GIL and prevents blocking Python's event loop.
    """
    if not HAS_RUST_CORE:
        raise RuntimeError("rust_core native module is not compiled.")
    if kwargs:
        return await asyncio.to_thread(func, *args, **kwargs)
    return await asyncio.to_thread(func, *args)
