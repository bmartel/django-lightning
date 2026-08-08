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
from urllib.parse import quote

import msgspec
from django_bolt import Response

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


if HAS_RUST_CORE and hasattr(rust_core, "db_query_users_json"):
    db_query_users_json = native_async(rust_core.db_query_users_json)
else:
    db_query_users_json = None

if HAS_RUST_CORE and hasattr(rust_core, "db_fetch_model_json"):
    db_fetch_model_json = native_async(rust_core.db_fetch_model_json)
else:
    db_fetch_model_json = None


def db_registered_models() -> list[str]:
    """List Django model names registered in the native Rust fetch registry."""
    if not HAS_RUST_CORE or not hasattr(rust_core, "db_registered_models"):
        return []
    return list(rust_core.db_registered_models())


def native_db_url() -> str:
    """
    Build an sqlx-compatible database URL from Django's DATABASES["default"] setting.

    Supports SQLite and PostgreSQL (matching the native `db_engine` crate backends).
    """
    from django.conf import settings

    db = settings.DATABASES["default"]
    engine = db["ENGINE"]

    if "sqlite" in engine:
        return f"sqlite://{db['NAME']}"

    if "postgres" in engine:
        user = quote(str(db.get("USER") or ""), safe="")
        password = quote(str(db.get("PASSWORD") or ""), safe="")
        host = db.get("HOST") or "localhost"
        port = db.get("PORT") or 5432
        name = db.get("NAME")
        credentials = f"{user}:{password}@" if user else ""
        return f"postgres://{credentials}{host}:{port}/{name}"

    raise RuntimeError(
        f"Native DB engine supports sqlite and postgres backends; got engine '{engine}'."
    )


def raw_json_response(
    raw_json: bytes,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> Response:
    """
    Return pre-serialized JSON bytes as an HTTP response with ZERO re-serialization.

    Rust produces the JSON bytes; Python passes the buffer straight to the response
    body without decoding or re-encoding, keeping the hot path allocation-free.
    """
    final_headers = {"content-type": "application/json"}
    if headers:
        final_headers.update(headers)
    return Response(
        raw_json,
        status_code=status_code,
        # Octet-stream body rendering passes raw bytes through untouched; the
        # explicit content-type header keeps the wire response application/json.
        media_type="application/octet-stream",
        headers=final_headers,
    )


async def fetch_model_page_response(
    model: str,
    limit: int = 100,
    after_id: int | None = None,
    max_limit: int = 1000,
) -> Response:
    """
    End-to-end native fast path: keyset-paginated model page as a raw JSON response.

    Django ORM, Python serialization, and Python JSON encoding are all bypassed:
    Rust (sqlx + serde) queries the pooled database connection, serializes rows to
    JSON bytes with sensitive columns stripped, and the bytes are returned as-is.
    """
    if not HAS_RUST_CORE or db_fetch_model_json is None:
        raise RuntimeError("rust_core native module with DB engine support is not compiled.")
    clamped = max(1, min(limit, max_limit))
    raw = await db_fetch_model_json(native_db_url(), model, clamped, after_id)
    return raw_json_response(raw)


async def query_users_native(db_url: str, limit: int = 100) -> list[dict[str, Any]]:
    """
    Query users directly using high-performance Rust DB engine and sqlx.

    Executes in Tokio runtime, releasing Python GIL, and deserializes via msgspec.
    """
    if not HAS_RUST_CORE or db_query_users_json is None:
        raise RuntimeError("rust_core native module with DB engine support is not compiled.")
    raw_bytes = await db_query_users_json(db_url, limit)
    return msgspec.json.decode(raw_bytes, type=list[dict[str, Any]])
